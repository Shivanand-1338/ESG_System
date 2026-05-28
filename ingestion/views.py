"""
Django REST Framework API views for the Breathe ESG system.

Requirements: 11.1-11.8
"""

import json
from datetime import datetime
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import (
    ClientCompany, DataSource, RawDataRecord,
    NormalizedRecord, SuspiciousFlag, AuditTrailEvent, ValidationRule
)
from .serializers import (
    NormalizedRecordSerializer, NormalizedRecordListSerializer,
    SuspiciousFlagSerializer, AuditTrailEventSerializer,
    RawDataRecordSerializer, ApprovalRequestSerializer,
    BulkApprovalRequestSerializer, DismissFlagRequestSerializer
)
from .permissions import IsTenantAuthorized, IsAnalyst, IsApprovalAuthorized
from .parsers import FormatRouter, ParsingError
from .audit_service import AuditTrailService
from .validation_engine import ValidationEngine, AnomalyDetector


class StandardPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============ Health Check ============

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint.
    Requirements: 12.6
    """
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return Response({
        'status': 'healthy' if db_status == 'connected' else 'unhealthy',
        'database': db_status,
        'timestamp': timezone.now().isoformat()
    })


# ============ Data Ingestion Endpoints ============

def _get_tenant(request):
    """Extract and validate tenant from request."""
    tenant_id = request.headers.get('X-Tenant-ID') or request.query_params.get('tenant_id')
    if not tenant_id:
        return None, Response(
            {'error': 'X-Tenant-ID header is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        tenant = ClientCompany.objects.get(id=tenant_id)
        return tenant, None
    except ClientCompany.DoesNotExist:
        return None, Response(
            {'error': f'Client company {tenant_id} not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ingest_sap(request):
    """
    POST /api/v1/ingest/sap/
    Ingest SAP data (IDoc XML or CSV).
    Requirements: 1.1, 1.4, 1.6
    """
    tenant, error = _get_tenant(request)
    if error:
        return error
    
    return _process_ingestion(request, tenant, 'SAP_IDOC')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ingest_greenbutton(request):
    """
    POST /api/v1/ingest/greenbutton/
    Ingest Green Button XML data.
    Requirements: 1.2, 1.4, 1.6
    """
    tenant, error = _get_tenant(request)
    if error:
        return error
    
    return _process_ingestion(request, tenant, 'GREEN_BUTTON')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ingest_concur(request):
    """
    POST /api/v1/ingest/concur/
    Ingest Concur trip data.
    Requirements: 1.3, 1.4, 1.6
    """
    tenant, error = _get_tenant(request)
    if error:
        return error
    
    return _process_ingestion(request, tenant, 'CONCUR_API')


def _process_ingestion(request, tenant, source_type):
    """Common ingestion processing logic."""
    # Get or create data source
    data_source, _ = DataSource.objects.get_or_create(
        client_company=tenant,
        source_type=source_type,
        defaults={'name': f'{source_type} Source'}
    )
    
    # Get raw data from request
    if request.content_type and 'multipart' in request.content_type:
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        raw_data = file.read().decode('utf-8')
    else:
        raw_data = request.body.decode('utf-8')
    
    if not raw_data:
        return Response(
            {'error': 'No data provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Store raw data
    raw_record = RawDataRecord.objects.create(
        client_company=tenant,
        data_source=data_source,
        raw_data={'content': raw_data, 'content_type': request.content_type},
        parsing_status='PENDING'
    )
    
    # Parse data
    router = FormatRouter()
    try:
        parsed_records, detected_type = router.route_and_parse(
            raw_data,
            content_type=request.content_type,
            source_type=source_type,
            configuration=data_source.configuration
        )
        raw_record.parsing_status = 'SUCCESS'
        raw_record.save()
    except ParsingError as e:
        raw_record.parsing_status = 'FAILED'
        raw_record.parsing_error = str(e)
        raw_record.save()
        return Response(
            {'error': f'Parsing failed: {str(e)}', 'raw_record_id': str(raw_record.id)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({
        'message': 'Data ingested successfully',
        'raw_record_id': str(raw_record.id),
        'records_parsed': len(parsed_records),
        'source_type': detected_type
    }, status=status.HTTP_201_CREATED)


# ============ Data Retrieval Endpoints ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def record_list(request):
    """
    GET /api/v1/records/
    List records with filtering and pagination.
    Requirements: 6.1, 11.2
    """
    queryset = NormalizedRecord.objects.all()
    
    # Tenant filter
    tenant_id = request.headers.get('X-Tenant-ID') or request.query_params.get('tenant_id')
    if tenant_id:
        queryset = queryset.filter(client_company_id=tenant_id)
    
    # Filters
    source_type = request.query_params.get('source_type')
    if source_type:
        queryset = queryset.filter(raw_record__data_source__source_type=source_type)
    
    start_date = request.query_params.get('start_date')
    if start_date:
        queryset = queryset.filter(activity_date__gte=start_date)
    
    end_date = request.query_params.get('end_date')
    if end_date:
        queryset = queryset.filter(activity_date__lte=end_date)
    
    scope = request.query_params.get('scope')
    if scope:
        queryset = queryset.filter(emission_scope=scope)
    
    approval_status = request.query_params.get('status')
    if approval_status:
        queryset = queryset.filter(approval_status=approval_status.upper())
    
    # Ordering
    ordering = request.query_params.get('ordering', '-created_at')
    queryset = queryset.order_by(ordering)
    
    # Pagination
    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = NormalizedRecordListSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def record_detail(request, record_id):
    """
    GET /api/v1/records/{id}/
    Get full record details.
    Requirements: 6.5, 11.2
    """
    try:
        record = NormalizedRecord.objects.get(id=record_id)
    except NormalizedRecord.DoesNotExist:
        return Response(
            {'error': 'Record not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = NormalizedRecordSerializer(record)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def suspicious_records(request):
    """
    GET /api/v1/records/suspicious/
    List records with active suspicious flags.
    Requirements: 6.3, 11.3
    """
    queryset = NormalizedRecord.objects.filter(
        flags__status='ACTIVE'
    ).distinct()
    
    tenant_id = request.headers.get('X-Tenant-ID') or request.query_params.get('tenant_id')
    if tenant_id:
        queryset = queryset.filter(client_company_id=tenant_id)
    
    flag_type = request.query_params.get('flag_type')
    if flag_type:
        queryset = queryset.filter(flags__flag_type=flag_type)
    
    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = NormalizedRecordSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def record_audit_trail(request, record_id):
    """
    GET /api/v1/records/{id}/audit-trail/
    Get audit trail for a record.
    Requirements: 6.6, 9.6, 11.6
    """
    events = AuditTrailEvent.objects.filter(record_id=record_id).order_by('-timestamp')
    serializer = AuditTrailEventSerializer(events, many=True)
    return Response(serializer.data)


# ============ Approval Workflow Endpoints ============

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAnalyst])
def approve_record(request, record_id):
    """
    POST /api/v1/records/{id}/approve/
    Approve a single record.
    Requirements: 8.1, 8.2, 8.3, 8.5, 8.6, 11.4
    """
    try:
        record = NormalizedRecord.objects.get(id=record_id)
    except NormalizedRecord.DoesNotExist:
        return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ApprovalRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Check for unresolved flags
    active_flags = record.flags.filter(status='ACTIVE')
    if active_flags.exists() and not serializer.validated_data.get('force', False):
        return Response({
            'error': 'Record has unresolved suspicious flags',
            'active_flags': SuspiciousFlagSerializer(active_flags, many=True).data
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Approve
    record.approval_status = 'APPROVED'
    record.approved_by = request.user
    record.approved_at = timezone.now()
    record.save()
    
    # Log audit event
    AuditTrailService.log_approve(
        record, request.user,
        serializer.validated_data.get('justification')
    )
    
    return Response(NormalizedRecordSerializer(record).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAnalyst])
def bulk_approve(request):
    """
    POST /api/v1/records/bulk-approve/
    Approve multiple records.
    Requirements: 8.4, 11.4
    """
    serializer = BulkApprovalRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    record_ids = serializer.validated_data['record_ids']
    force = serializer.validated_data.get('force', False)
    justification = serializer.validated_data.get('justification', '')
    
    approved = []
    failed = []
    
    with transaction.atomic():
        for record_id in record_ids:
            try:
                record = NormalizedRecord.objects.get(id=record_id)
                
                # Check flags
                active_flags = record.flags.filter(status='ACTIVE')
                if active_flags.exists() and not force:
                    failed.append({
                        'id': str(record_id),
                        'reason': 'Unresolved suspicious flags'
                    })
                    continue
                
                record.approval_status = 'APPROVED'
                record.approved_by = request.user
                record.approved_at = timezone.now()
                record.save()
                
                AuditTrailService.log_approve(record, request.user, justification)
                approved.append(str(record_id))
                
            except NormalizedRecord.DoesNotExist:
                failed.append({'id': str(record_id), 'reason': 'Not found'})
    
    return Response({
        'approved_count': len(approved),
        'failed_count': len(failed),
        'approved': approved,
        'failed': failed
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAnalyst])
def unapprove_record(request, record_id):
    """
    POST /api/v1/records/{id}/unapprove/
    Unapprove a record.
    Requirements: 8.7, 11.4
    """
    try:
        record = NormalizedRecord.objects.get(id=record_id)
    except NormalizedRecord.DoesNotExist:
        return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
    
    justification = request.data.get('justification')
    if not justification:
        return Response(
            {'error': 'Justification is required for unapproval'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check audit lock date
    if record.client_company.audit_lock_date:
        if record.activity_date <= record.client_company.audit_lock_date:
            return Response(
                {'error': 'Cannot unapprove: record is past audit lock date'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    record.approval_status = 'PENDING'
    record.approved_by = None
    record.approved_at = None
    record.save()
    
    AuditTrailService.log_unapprove(record, request.user, justification)
    
    return Response(NormalizedRecordSerializer(record).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAnalyst])
def dismiss_flag(request, record_id):
    """
    POST /api/v1/records/{id}/dismiss-flag/
    Dismiss a suspicious flag.
    Requirements: 7.6, 11.5
    """
    serializer = DismissFlagRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    flag_id = serializer.validated_data['flag_id']
    justification = serializer.validated_data['justification']
    
    try:
        flag = SuspiciousFlag.objects.get(id=flag_id, record_id=record_id)
    except SuspiciousFlag.DoesNotExist:
        return Response({'error': 'Flag not found'}, status=status.HTTP_404_NOT_FOUND)
    
    flag.status = 'DISMISSED'
    flag.dismissed_by = request.user
    flag.dismissed_at = timezone.now()
    flag.dismissal_justification = justification
    flag.save()
    
    AuditTrailService.log_flag_dismiss(
        flag.record, request.user, flag.flag_type, justification
    )
    
    record = NormalizedRecord.objects.get(id=record_id)
    return Response(NormalizedRecordSerializer(record).data)


# ============ Statistics Endpoints ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statistics_summary(request):
    """
    GET /api/v1/statistics/summary/
    Get summary statistics.
    Requirements: 6.7, 11.7
    """
    queryset = NormalizedRecord.objects.all()
    
    tenant_id = request.headers.get('X-Tenant-ID') or request.query_params.get('tenant_id')
    if tenant_id:
        queryset = queryset.filter(client_company_id=tenant_id)
    
    start_date = request.query_params.get('start_date')
    if start_date:
        queryset = queryset.filter(activity_date__gte=start_date)
    
    end_date = request.query_params.get('end_date')
    if end_date:
        queryset = queryset.filter(activity_date__lte=end_date)
    
    total = queryset.count()
    approved = queryset.filter(approval_status='APPROVED').count()
    pending = queryset.filter(approval_status='PENDING').count()
    flagged = queryset.filter(approval_status='FLAGGED').count()
    suspicious = queryset.filter(flags__status='ACTIVE').distinct().count()
    
    failed_records = RawDataRecord.objects.filter(parsing_status='FAILED')
    if tenant_id:
        failed_records = failed_records.filter(client_company_id=tenant_id)
    failed = failed_records.count()
    
    return Response({
        'total_records': total,
        'approved_records': approved,
        'pending_records': pending,
        'flagged_records': flagged,
        'suspicious_records': suspicious,
        'failed_records': failed
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statistics_by_scope(request):
    """
    GET /api/v1/statistics/by-scope/
    Get statistics grouped by emission scope.
    Requirements: 6.7, 11.7
    """
    queryset = NormalizedRecord.objects.all()
    
    tenant_id = request.headers.get('X-Tenant-ID') or request.query_params.get('tenant_id')
    if tenant_id:
        queryset = queryset.filter(client_company_id=tenant_id)
    
    start_date = request.query_params.get('start_date')
    if start_date:
        queryset = queryset.filter(activity_date__gte=start_date)
    
    end_date = request.query_params.get('end_date')
    if end_date:
        queryset = queryset.filter(activity_date__lte=end_date)
    
    return Response({
        'scope_1_count': queryset.filter(emission_scope='SCOPE_1').count(),
        'scope_2_count': queryset.filter(emission_scope='SCOPE_2').count(),
        'scope_3_count': queryset.filter(emission_scope='SCOPE_3').count()
    })
