"""
Audit trail service for immutable event logging.

Requirements: 9.1, 9.2, 9.5, 9.7
"""

from django.contrib.auth.models import User
from .models import AuditTrailEvent, NormalizedRecord


class AuditTrailService:
    """
    Service for creating immutable audit trail events.
    
    Requirements: 9.1, 9.2, 9.5, 9.7
    """
    
    @staticmethod
    def log_create(record: NormalizedRecord, user: User = None):
        """Log record creation event."""
        AuditTrailEvent.objects.create(
            record=record,
            action_type='CREATE',
            user=user,
            new_value=f"Record created: {record.activity_type} on {record.activity_date}"
        )
    
    @staticmethod
    def log_update(
        record: NormalizedRecord,
        user: User,
        field_name: str,
        old_value: str,
        new_value: str,
        justification: str = None
    ):
        """Log record field update event."""
        AuditTrailEvent.objects.create(
            record=record,
            action_type='UPDATE',
            user=user,
            field_name=field_name,
            old_value=str(old_value),
            new_value=str(new_value),
            justification=justification
        )
    
    @staticmethod
    def log_approve(record: NormalizedRecord, user: User, justification: str = None):
        """Log record approval event."""
        AuditTrailEvent.objects.create(
            record=record,
            action_type='APPROVE',
            user=user,
            field_name='approval_status',
            old_value='PENDING',
            new_value='APPROVED',
            justification=justification
        )
    
    @staticmethod
    def log_unapprove(record: NormalizedRecord, user: User, justification: str):
        """Log record unapproval event."""
        AuditTrailEvent.objects.create(
            record=record,
            action_type='UNAPPROVE',
            user=user,
            field_name='approval_status',
            old_value='APPROVED',
            new_value='PENDING',
            justification=justification
        )
    
    @staticmethod
    def log_flag_create(record: NormalizedRecord, flag_type: str, description: str):
        """Log suspicious flag creation event."""
        AuditTrailEvent.objects.create(
            record=record,
            action_type='FLAG_CREATE',
            new_value=f"{flag_type}: {description}"
        )
    
    @staticmethod
    def log_flag_dismiss(
        record: NormalizedRecord,
        user: User,
        flag_type: str,
        justification: str
    ):
        """Log suspicious flag dismissal event."""
        AuditTrailEvent.objects.create(
            record=record,
            action_type='FLAG_DISMISS',
            user=user,
            field_name='flag_status',
            old_value='ACTIVE',
            new_value='DISMISSED',
            justification=justification
        )
