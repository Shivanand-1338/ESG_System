"""
Validation rule engine and anomaly detection.

Requirements: 7.1, 7.2, 7.3, 7.5, 15.1, 15.2, 15.3, 15.4, 15.6
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional
from django.db.models import Avg, StdDev, Count


class ValidationEngine:
    """
    Applies configurable validation rules and detects anomalies.
    
    Requirements: 15.1, 15.2, 15.3, 15.4, 15.6
    """
    
    def validate_record(self, record, validation_rules) -> List[Dict[str, Any]]:
        """
        Apply all active validation rules to a record.
        
        Returns list of violations found.
        """
        violations = []
        
        for rule in validation_rules:
            if not rule.is_active:
                continue
            
            violation = self._apply_rule(record, rule)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _apply_rule(self, record, rule) -> Optional[Dict[str, Any]]:
        """Apply a single validation rule."""
        field_value = getattr(record, rule.field_name, None)
        config = rule.configuration
        
        if rule.rule_type == 'NUMERIC_RANGE':
            return self._validate_numeric_range(field_value, config, rule)
        elif rule.rule_type == 'REQUIRED_FIELD':
            return self._validate_required_field(field_value, config, rule)
        elif rule.rule_type == 'DATE_RANGE':
            return self._validate_date_range(field_value, config, rule)
        elif rule.rule_type == 'ENUM_VALUES':
            return self._validate_enum_values(field_value, config, rule)
        
        return None
    
    def _validate_numeric_range(self, value, config, rule) -> Optional[Dict]:
        """Check if numeric value is within range."""
        if value is None:
            return None
        
        try:
            num_value = float(value)
        except (TypeError, ValueError):
            return {
                'flag_type': 'VALIDATION_RULE',
                'description': f"{rule.field_name}: {rule.error_message}",
                'rule_id': str(rule.id)
            }
        
        min_val = config.get('min')
        max_val = config.get('max')
        
        if min_val is not None and num_value < float(min_val):
            return {
                'flag_type': 'VALIDATION_RULE',
                'description': f"{rule.field_name} value {num_value} below minimum {min_val}. {rule.error_message}",
                'rule_id': str(rule.id)
            }
        
        if max_val is not None and num_value > float(max_val):
            return {
                'flag_type': 'VALIDATION_RULE',
                'description': f"{rule.field_name} value {num_value} above maximum {max_val}. {rule.error_message}",
                'rule_id': str(rule.id)
            }
        
        return None
    
    def _validate_required_field(self, value, config, rule) -> Optional[Dict]:
        """Check if required field has a value."""
        if value is None or (isinstance(value, str) and not value.strip()):
            return {
                'flag_type': 'MISSING_FIELD',
                'description': f"{rule.field_name} is required. {rule.error_message}",
                'rule_id': str(rule.id)
            }
        return None
    
    def _validate_date_range(self, value, config, rule) -> Optional[Dict]:
        """Check if date is within acceptable range."""
        if value is None:
            return None
        
        today = date.today()
        
        # Check future dates
        if value > today:
            return {
                'flag_type': 'INVALID_DATE',
                'description': f"{rule.field_name} is in the future ({value}). {rule.error_message}",
                'rule_id': str(rule.id)
            }
        
        # Check too old dates (default 5 years)
        max_age_days = config.get('max_age_days', 1825)
        oldest_allowed = today - timedelta(days=max_age_days)
        
        if value < oldest_allowed:
            return {
                'flag_type': 'INVALID_DATE',
                'description': f"{rule.field_name} is too old ({value}). {rule.error_message}",
                'rule_id': str(rule.id)
            }
        
        return None
    
    def _validate_enum_values(self, value, config, rule) -> Optional[Dict]:
        """Check if value is in allowed values list."""
        if value is None:
            return None
        
        allowed = config.get('allowed_values', [])
        if str(value) not in [str(v) for v in allowed]:
            return {
                'flag_type': 'VALIDATION_RULE',
                'description': f"{rule.field_name} value '{value}' not in allowed values. {rule.error_message}",
                'rule_id': str(rule.id)
            }
        
        return None


class AnomalyDetector:
    """
    Detects statistical outliers using z-score analysis.
    
    Requirements: 7.1
    """
    
    MINIMUM_SAMPLE_SIZE = 30
    Z_SCORE_THRESHOLD = 3
    
    def detect_outliers(self, record, NormalizedRecord) -> List[Dict[str, Any]]:
        """
        Check if record quantity is a statistical outlier.
        
        Args:
            record: The record to check
            NormalizedRecord: The model class for querying historical data
            
        Returns:
            List of anomaly flags
        """
        flags = []
        
        # Get historical data for same client, activity type, and unit
        historical = NormalizedRecord.objects.filter(
            client_company=record.client_company,
            activity_type=record.activity_type,
            unit=record.unit,
            approval_status='APPROVED'
        ).exclude(id=record.id)
        
        stats = historical.aggregate(
            count=Count('id'),
            mean=Avg('quantity'),
            stddev=StdDev('quantity')
        )
        
        count = stats['count'] or 0
        
        # Need minimum sample size
        if count < self.MINIMUM_SAMPLE_SIZE:
            return flags
        
        mean = float(stats['mean'])
        stddev = float(stats['stddev']) if stats['stddev'] else 0
        
        # Edge case: all historical values identical
        if stddev == 0:
            if float(record.quantity) != mean:
                flags.append({
                    'flag_type': 'OUTLIER',
                    'description': (
                        f"Value {record.quantity} differs from historical constant "
                        f"value {mean} for {record.activity_type}/{record.unit}"
                    )
                })
            return flags
        
        # Calculate z-score
        z_score = (float(record.quantity) - mean) / stddev
        
        if abs(z_score) > self.Z_SCORE_THRESHOLD:
            flags.append({
                'flag_type': 'OUTLIER',
                'description': (
                    f"Statistical outlier detected: z-score={z_score:.2f} "
                    f"(threshold: ±{self.Z_SCORE_THRESHOLD}). "
                    f"Value: {record.quantity}, Mean: {mean:.2f}, StdDev: {stddev:.2f}"
                )
            })
        
        return flags
    
    def detect_duplicates(self, record, NormalizedRecord) -> List[Dict[str, Any]]:
        """
        Detect duplicate records.
        
        Requirements: 7.5
        """
        flags = []
        
        duplicates = NormalizedRecord.objects.filter(
            client_company=record.client_company,
            raw_record__data_source=record.raw_record.data_source,
            activity_date=record.activity_date,
            activity_type=record.activity_type,
            quantity=record.quantity
        ).exclude(id=record.id)
        
        if duplicates.exists():
            flags.append({
                'flag_type': 'DUPLICATE',
                'description': (
                    f"Possible duplicate: {duplicates.count()} other record(s) "
                    f"with same source, date, type, and quantity"
                )
            })
        
        return flags
    
    def detect_date_issues(self, record) -> List[Dict[str, Any]]:
        """
        Detect date-related issues.
        
        Requirements: 7.3
        """
        flags = []
        today = date.today()
        
        if record.activity_date > today:
            flags.append({
                'flag_type': 'INVALID_DATE',
                'description': f"Activity date {record.activity_date} is in the future"
            })
        
        five_years_ago = today - timedelta(days=1825)
        if record.activity_date < five_years_ago:
            flags.append({
                'flag_type': 'INVALID_DATE',
                'description': f"Activity date {record.activity_date} is more than 5 years in the past"
            })
        
        return flags
