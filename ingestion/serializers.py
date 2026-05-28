"""
Django REST Framework serializers for API endpoints.

Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    ClientCompany,
    DataSource,
    RawDataRecord,
    NormalizedRecord,
    SuspiciousFlag,
    AuditTrailEvent,
    ValidationRule
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ClientCompanySerializer(serializers.ModelSerializer):
    """Serializer for ClientCompany model."""
    
    class Meta:
        model = ClientCompany
        fields = ['id', 'name', 'created_at', 'audit_lock_date']
        read_only_fields = ['id', 'created_at']


class DataSourceSerializer(serializers.ModelSerializer):
    """Serializer for DataSource model."""
    
    client_company_name = serializers.CharField(source='client_company.name', read_only=True)
    
    class Meta:
        model = DataSource
        fields = [
            'id', 'client_company', 'client_company_name', 'source_type', 
            'name', 'configuration', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RawDataRecordSerializer(serializers.ModelSerializer):
    """Serializer for RawDataRecord model."""
    
    class Meta:
        model = RawDataRecord
        fields = [
            'id', 'client_company', 'data_source', 'raw_data', 
            'ingestion_timestamp', 'parsing_status', 'parsing_error'
        ]
        read_only_fields = ['id', 'ingestion_timestamp']


class SuspiciousFlagSerializer(serializers.ModelSerializer):
    """Serializer for SuspiciousFlag model."""
    
    dismissed_by_username = serializers.CharField(source='dismissed_by.username', read_only=True)
    
    class Meta:
        model = SuspiciousFlag
        fields = [
            'id', 'record', 'flag_type', 'description', 'status',
            'dismissed_by', 'dismissed_by_username', 'dismissed_at', 
            'dismissal_justification', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'dismissed_by', 'dismissed_at']


class AuditTrailEventSerializer(serializers.ModelSerializer):
    """Serializer for AuditTrailEvent model."""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = AuditTrailEvent
        fields = [
            'id', 'record', 'action_type', 'action_type_display', 
            'user', 'user_username', 'timestamp', 'field_name', 
            'old_value', 'new_value', 'justification'
        ]
        read_only_fields = '__all__'  # Audit trail is read-only


class NormalizedRecordSerializer(serializers.ModelSerializer):
    """Serializer for NormalizedRecord model with related data."""
    
    client_company_name = serializers.CharField(source='client_company.name', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)
    emission_scope_display = serializers.CharField(source='get_emission_scope_display', read_only=True)
    approval_status_display = serializers.CharField(source='get_approval_status_display', read_only=True)
    flags = SuspiciousFlagSerializer(many=True, read_only=True)
    
    class Meta:
        model = NormalizedRecord
        fields = [
            'id', 'client_company', 'client_company_name', 'raw_record',
            'activity_date', 'emission_scope', 'emission_scope_display',
            'activity_type', 'quantity', 'unit', 'location',
            'original_quantity', 'original_unit', 'conversion_factor',
            'approval_status', 'approval_status_display', 'approved_by', 
            'approved_by_username', 'approved_at', 'flags',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'approved_by', 'approved_at']


class NormalizedRecordListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    
    client_company_name = serializers.CharField(source='client_company.name', read_only=True)
    emission_scope_display = serializers.CharField(source='get_emission_scope_display', read_only=True)
    approval_status_display = serializers.CharField(source='get_approval_status_display', read_only=True)
    flag_count = serializers.SerializerMethodField()
    
    class Meta:
        model = NormalizedRecord
        fields = [
            'id', 'client_company_name', 'activity_date', 'emission_scope', 
            'emission_scope_display', 'activity_type', 'quantity', 'unit',
            'approval_status', 'approval_status_display', 'flag_count'
        ]
    
    def get_flag_count(self, obj):
        """Return count of active flags."""
        return obj.flags.filter(status='ACTIVE').count()


class ValidationRuleSerializer(serializers.ModelSerializer):
    """Serializer for ValidationRule model."""
    
    rule_type_display = serializers.CharField(source='get_rule_type_display', read_only=True)
    
    class Meta:
        model = ValidationRule
        fields = [
            'id', 'client_company', 'rule_type', 'rule_type_display',
            'field_name', 'configuration', 'error_message', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ApprovalRequestSerializer(serializers.Serializer):
    """Serializer for approval action requests."""
    
    justification = serializers.CharField(required=False, allow_blank=True)
    force = serializers.BooleanField(required=False, default=False)


class BulkApprovalRequestSerializer(serializers.Serializer):
    """Serializer for bulk approval requests."""
    
    record_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        allow_empty=False
    )
    justification = serializers.CharField(required=False, allow_blank=True)
    force = serializers.BooleanField(required=False, default=False)


class DismissFlagRequestSerializer(serializers.Serializer):
    """Serializer for flag dismissal requests."""
    
    flag_id = serializers.UUIDField(required=True)
    justification = serializers.CharField(required=True, allow_blank=False)
