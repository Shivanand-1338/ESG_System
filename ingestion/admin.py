"""
Django admin configuration for ingestion models.
"""

from django.contrib import admin
from .models import (
    ClientCompany,
    DataSource,
    RawDataRecord,
    NormalizedRecord,
    SuspiciousFlag,
    AuditTrailEvent,
    ValidationRule
)


@admin.register(ClientCompany)
class ClientCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'audit_lock_date')
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at')


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'client_company', 'created_at')
    list_filter = ('source_type', 'client_company')
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at')


@admin.register(RawDataRecord)
class RawDataRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_company', 'data_source', 'parsing_status', 'ingestion_timestamp')
    list_filter = ('parsing_status', 'client_company', 'data_source')
    readonly_fields = ('id', 'ingestion_timestamp')
    search_fields = ('id',)


@admin.register(NormalizedRecord)
class NormalizedRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_company', 'activity_type', 'activity_date', 'emission_scope', 'approval_status')
    list_filter = ('emission_scope', 'approval_status', 'client_company')
    search_fields = ('activity_type', 'location')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'activity_date'


@admin.register(SuspiciousFlag)
class SuspiciousFlagAdmin(admin.ModelAdmin):
    list_display = ('id', 'record', 'flag_type', 'status', 'created_at')
    list_filter = ('flag_type', 'status')
    readonly_fields = ('id', 'created_at')
    search_fields = ('description',)


@admin.register(AuditTrailEvent)
class AuditTrailEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'record', 'action_type', 'user', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    readonly_fields = ('id', 'record', 'action_type', 'user', 'timestamp', 'field_name', 'old_value', 'new_value', 'justification')
    search_fields = ('record__id',)
    
    def has_add_permission(self, request):
        """Prevent manual creation of audit events."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent modification of audit events."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit events."""
        return False


@admin.register(ValidationRule)
class ValidationRuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_company', 'rule_type', 'field_name', 'is_active', 'created_at')
    list_filter = ('rule_type', 'is_active', 'client_company')
    search_fields = ('field_name', 'error_message')
    readonly_fields = ('id', 'created_at')
