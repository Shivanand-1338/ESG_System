"""
Data models for the Breathe ESG Data Ingestion System.

This module contains all database models for multi-tenant emissions data ingestion,
normalization, validation, and approval workflow.
"""

import uuid
from django.db import models
from django.contrib.auth.models import User


class ClientCompany(models.Model):
    """
    Represents a tenant organization whose emissions data is being tracked.
    
    Requirements: 3.1, 3.4
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    audit_lock_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date after which approved records cannot be unapproved"
    )
    
    class Meta:
        db_table = 'client_companies'
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name = 'Client Company'
        verbose_name_plural = 'Client Companies'
    
    def __str__(self):
        return self.name


class DataSource(models.Model):
    """
    Represents an external system providing emissions or activity data.
    
    Requirements: 1.6, 3.4
    """
    SOURCE_TYPES = [
        ('SAP_IDOC', 'SAP IDoc'),
        ('SAP_CSV', 'SAP CSV'),
        ('GREEN_BUTTON', 'Green Button XML'),
        ('CONCUR_API', 'Concur API'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_company = models.ForeignKey(
        ClientCompany,
        on_delete=models.CASCADE,
        related_name='data_sources'
    )
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    name = models.CharField(max_length=255)
    configuration = models.JSONField(
        default=dict,
        help_text="Parser-specific configuration (e.g., column mappings, custom conversions)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'data_sources'
        indexes = [
            models.Index(fields=['client_company', 'source_type']),
        ]
        verbose_name = 'Data Source'
        verbose_name_plural = 'Data Sources'
    
    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class RawDataRecord(models.Model):
    """
    Stores unparsed data from external sources for audit purposes.
    
    Requirements: 1.4, 1.5
    """
    PARSING_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_company = models.ForeignKey(
        ClientCompany,
        on_delete=models.CASCADE,
        related_name='raw_records'
    )
    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.CASCADE,
        related_name='raw_records'
    )
    raw_data = models.JSONField(help_text="Unparsed input data")
    ingestion_timestamp = models.DateTimeField(auto_now_add=True)
    parsing_status = models.CharField(
        max_length=20,
        choices=PARSING_STATUS_CHOICES,
        default='PENDING'
    )
    parsing_error = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'raw_data_records'
        indexes = [
            models.Index(fields=['client_company', 'ingestion_timestamp']),
            models.Index(fields=['data_source', 'parsing_status']),
        ]
        verbose_name = 'Raw Data Record'
        verbose_name_plural = 'Raw Data Records'
    
    def __str__(self):
        return f"Raw Record {self.id} - {self.parsing_status}"


class NormalizedRecord(models.Model):
    """
    Stores normalized emissions and activity data with standardized units and formats.
    
    Requirements: 4.1, 4.2, 4.7, 5.1, 8.2
    """
    EMISSION_SCOPES = [
        ('SCOPE_1', 'Scope 1: Direct Emissions'),
        ('SCOPE_2', 'Scope 2: Purchased Electricity'),
        ('SCOPE_3', 'Scope 3: Value Chain'),
    ]
    
    APPROVAL_STATUS = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('FLAGGED', 'Flagged for Review'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_company = models.ForeignKey(
        ClientCompany,
        on_delete=models.CASCADE,
        related_name='normalized_records'
    )
    raw_record = models.OneToOneField(
        RawDataRecord,
        on_delete=models.CASCADE,
        related_name='normalized_record'
    )
    
    # Normalized fields
    activity_date = models.DateField()
    emission_scope = models.CharField(max_length=20, choices=EMISSION_SCOPES)
    activity_type = models.CharField(
        max_length=100,
        help_text="e.g., fuel_combustion, electricity_consumption, air_travel"
    )
    quantity = models.DecimalField(max_digits=15, decimal_places=4)
    unit = models.CharField(max_length=50, help_text="Standardized unit")
    location = models.CharField(max_length=255, null=True, blank=True)
    
    # Source attribution - preserves original values for audit trail
    original_quantity = models.DecimalField(max_digits=15, decimal_places=4)
    original_unit = models.CharField(max_length=50)
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=6)
    
    # Workflow fields
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default='PENDING'
    )
    approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_records'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'normalized_records'
        indexes = [
            models.Index(fields=['client_company', 'activity_date']),
            models.Index(fields=['client_company', 'emission_scope']),
            models.Index(fields=['client_company', 'approval_status']),
        ]
        verbose_name = 'Normalized Record'
        verbose_name_plural = 'Normalized Records'
    
    def __str__(self):
        return f"{self.activity_type} - {self.activity_date} ({self.approval_status})"


class SuspiciousFlag(models.Model):
    """
    Flags data quality issues for analyst review.
    
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
    """
    FLAG_TYPES = [
        ('OUTLIER', 'Statistical Outlier'),
        ('MISSING_FIELD', 'Missing Required Field'),
        ('INVALID_DATE', 'Invalid Date Range'),
        ('CONVERSION_FAILURE', 'Unit Conversion Failed'),
        ('DUPLICATE', 'Duplicate Record'),
        ('VALIDATION_RULE', 'Validation Rule Violation'),
    ]
    
    FLAG_STATUS = [
        ('ACTIVE', 'Active'),
        ('DISMISSED', 'Dismissed'),
        ('RESOLVED', 'Resolved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(
        NormalizedRecord,
        on_delete=models.CASCADE,
        related_name='flags'
    )
    flag_type = models.CharField(max_length=50, choices=FLAG_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=FLAG_STATUS, default='ACTIVE')
    dismissed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='dismissed_flags'
    )
    dismissed_at = models.DateTimeField(null=True, blank=True)
    dismissal_justification = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'suspicious_flags'
        indexes = [
            models.Index(fields=['record', 'status']),
        ]
        verbose_name = 'Suspicious Flag'
        verbose_name_plural = 'Suspicious Flags'
    
    def __str__(self):
        return f"{self.get_flag_type_display()} - {self.status}"


class AuditTrailEvent(models.Model):
    """
    Immutable audit log capturing all data modifications and approvals.
    
    Requirements: 9.1, 9.2, 9.5, 9.7
    """
    ACTION_TYPES = [
        ('CREATE', 'Record Created'),
        ('UPDATE', 'Record Updated'),
        ('APPROVE', 'Record Approved'),
        ('UNAPPROVE', 'Record Unapproved'),
        ('FLAG_CREATE', 'Flag Created'),
        ('FLAG_DISMISS', 'Flag Dismissed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(
        NormalizedRecord,
        on_delete=models.CASCADE,
        related_name='audit_events'
    )
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    field_name = models.CharField(max_length=100, null=True, blank=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    justification = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'audit_trail_events'
        indexes = [
            models.Index(fields=['record', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
        ordering = ['-timestamp']
        verbose_name = 'Audit Trail Event'
        verbose_name_plural = 'Audit Trail Events'
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.timestamp}"
    
    def save(self, *args, **kwargs):
        """Override save to enforce append-only behavior."""
        if self.pk is not None:
            raise ValueError("Audit trail events cannot be modified after creation")
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to prevent deletion of audit trail events."""
        raise ValueError("Audit trail events cannot be deleted")


class ValidationRule(models.Model):
    """
    Configurable validation rules for data quality enforcement.
    
    Requirements: 15.1, 15.2, 15.3, 15.4, 15.5
    """
    RULE_TYPES = [
        ('NUMERIC_RANGE', 'Numeric Range'),
        ('REQUIRED_FIELD', 'Required Field'),
        ('DATE_RANGE', 'Date Range'),
        ('ENUM_VALUES', 'Enumerated Values'),
        ('CUSTOM', 'Custom Rule'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_company = models.ForeignKey(
        ClientCompany,
        on_delete=models.CASCADE,
        related_name='validation_rules'
    )
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES)
    field_name = models.CharField(
        max_length=100,
        help_text="Name of the field to validate (e.g., 'quantity', 'activity_date')"
    )
    configuration = models.JSONField(
        help_text="Rule configuration (e.g., {'min': 0, 'max': 1000} or {'allowed_values': ['A', 'B']})"
    )
    error_message = models.TextField(
        help_text="Error message to display when validation fails"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this rule is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'validation_rules'
        indexes = [
            models.Index(fields=['client_company', 'is_active']),
        ]
        verbose_name = 'Validation Rule'
        verbose_name_plural = 'Validation Rules'
    
    def __str__(self):
        return f"{self.get_rule_type_display()} for {self.field_name} ({self.client_company.name})"
