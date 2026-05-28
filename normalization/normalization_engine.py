"""
Normalization engine that orchestrates data transformation.

Requirements: 4.1, 4.2, 4.4, 4.5, 4.6, 4.7
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional
from .unit_converter import UnitConverter, ConversionError
from .scope_classifier import ScopeClassifier


class NormalizationError(Exception):
    """Exception raised when normalization fails."""
    pass


class NormalizationEngine:
    """
    Orchestrates the normalization pipeline: extraction → conversion → classification.
    
    Requirements: 4.1, 4.2, 4.4, 4.5, 4.6, 4.7
    """
    
    def __init__(self):
        """Initialize engine with converter and classifier."""
        self.unit_converter = UnitConverter()
        self.scope_classifier = ScopeClassifier()
    
    def normalize(
        self,
        parsed_records: list[Dict[str, Any]],
        source_type: str,
        custom_config: Optional[Dict] = None
    ) -> list[Dict[str, Any]]:
        """
        Normalize a list of parsed records.
        
        Args:
            parsed_records: List of parsed data dictionaries
            source_type: Source system type
            custom_config: Optional client-specific configuration
            
        Returns:
            List of normalized record dictionaries
        """
        normalized_records = []
        
        for record in parsed_records:
            try:
                normalized = self._normalize_single_record(
                    record, source_type, custom_config
                )
                normalized_records.append(normalized)
            except NormalizationError as e:
                # Log error but continue processing other records
                print(f"Normalization error for record: {e}")
                continue
        
        return normalized_records
    
    def _normalize_single_record(
        self,
        record: Dict[str, Any],
        source_type: str,
        custom_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Normalize a single record.
        
        Args:
            record: Parsed data dictionary
            source_type: Source system type
            custom_config: Optional configuration
            
        Returns:
            Normalized record dictionary
        """
        # Extract fields based on source type
        extracted = self._extract_fields(record, source_type)
        
        # Standardize date format
        activity_date = self._standardize_date(extracted.get('date'))
        
        # Convert units to standard
        quantity, unit, conversion_result = self._convert_units(
            extracted.get('quantity'),
            extracted.get('unit'),
            custom_config
        )
        
        # Classify emission scope
        activity_type = extracted.get('activity_type', 'unknown')
        scope, is_ambiguous = self.scope_classifier.classify(
            activity_type, source_type, record
        )
        
        # Build normalized record
        normalized = {
            'activity_date': activity_date,
            'emission_scope': scope,
            'activity_type': activity_type,
            'quantity': quantity,
            'unit': unit,
            'location': extracted.get('location'),
            'original_quantity': extracted.get('quantity'),
            'original_unit': extracted.get('unit'),
            'conversion_factor': conversion_result['factor'],
            'metadata': {
                'scope_is_ambiguous': is_ambiguous,
                'conversion_method': conversion_result.get('method', 'standard'),
                'source_fields': extracted.get('source_fields', {})
            }
        }
        
        return normalized
    
    def _extract_fields(
        self, 
        record: Dict[str, Any], 
        source_type: str
    ) -> Dict[str, Any]:
        """
        Extract relevant fields based on source type.
        
        Args:
            record: Parsed record
            source_type: Source system type
            
        Returns:
            Dictionary of extracted fields
        """
        if source_type == 'SAP_IDOC':
            return self._extract_sap_idoc_fields(record)
        elif source_type == 'SAP_CSV':
            return self._extract_sap_csv_fields(record)
        elif source_type == 'GREEN_BUTTON':
            return self._extract_green_button_fields(record)
        elif source_type == 'CONCUR_API':
            return self._extract_concur_fields(record)
        else:
            raise NormalizationError(f"Unknown source type: {source_type}")
    
    def _extract_sap_idoc_fields(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract fields from SAP IDoc record."""
        return {
            'date': record.get('transaction_date'),
            'quantity': record.get('quantity'),
            'unit': record.get('unit'),
            'activity_type': self._infer_activity_type_from_material(
                record.get('material_number', '')
            ),
            'location': record.get('plant') or record.get('storage_location'),
            'source_fields': {
                'material_number': record.get('material_number'),
                'cost_center': record.get('cost_center')
            }
        }
    
    def _extract_sap_csv_fields(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract fields from SAP CSV record."""
        return {
            'date': record.get('transaction_date'),
            'quantity': record.get('quantity'),
            'unit': record.get('unit'),
            'activity_type': self._infer_activity_type_from_material(
                record.get('material_number', '')
            ),
            'location': record.get('plant'),
            'source_fields': {
                'material_number': record.get('material_number'),
                'description': record.get('description')
            }
        }
    
    def _extract_green_button_fields(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract fields from Green Button record."""
        # Convert Unix timestamp to date if needed
        start_time = record.get('start_time', '')
        if start_time.isdigit():
            date = datetime.fromtimestamp(int(start_time)).date()
        else:
            date = start_time
        
        return {
            'date': date,
            'quantity': record.get('value'),
            'unit': record.get('reading_type', 'kwh'),
            'activity_type': 'electricity_consumption',
            'location': record.get('usage_point_id'),
            'source_fields': {
                'usage_point_id': record.get('usage_point_id'),
                'duration': record.get('duration')
            }
        }
    
    def _extract_concur_fields(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract fields from Concur record."""
        # Determine activity type from travel mode
        travel_mode = record.get('travel_mode', '').lower()
        segment_type = record.get('segment_type', '').lower()
        
        if 'air' in travel_mode or 'flight' in segment_type:
            activity_type = 'air_travel'
        elif 'rail' in travel_mode or 'train' in segment_type:
            activity_type = 'rail_travel'
        elif 'car' in travel_mode or 'rental' in segment_type:
            activity_type = 'car_rental'
        else:
            activity_type = 'business_travel'
        
        # Use emissions if available, otherwise use distance
        if record.get('emissions'):
            quantity = record.get('emissions')
            unit = record.get('emissions_unit', 'kg_co2e')
        else:
            quantity = record.get('distance')
            unit = record.get('distance_unit', 'miles')
        
        return {
            'date': record.get('start_date'),
            'quantity': quantity,
            'unit': unit,
            'activity_type': activity_type,
            'location': f"{record.get('origin', '')} to {record.get('destination', '')}",
            'source_fields': {
                'trip_id': record.get('trip_id'),
                'carrier': record.get('carrier')
            }
        }
    
    def _infer_activity_type_from_material(self, material_number: str) -> str:
        """
        Infer activity type from SAP material number.
        
        This is a simplified heuristic. In production, this would use
        a material master data lookup table.
        """
        material_lower = material_number.lower()
        
        if 'fuel' in material_lower or 'diesel' in material_lower or 'gas' in material_lower:
            return 'fuel_combustion'
        elif 'electric' in material_lower or 'power' in material_lower:
            return 'electricity_consumption'
        else:
            return 'procurement'
    
    def _standardize_date(self, date_value: Any) -> str:
        """
        Standardize date to ISO 8601 format (YYYY-MM-DD).
        
        Requirements: 4.4
        """
        if not date_value:
            return datetime.now().date().isoformat()
        
        # Already a date object
        if hasattr(date_value, 'isoformat'):
            return date_value.isoformat()
        
        # String date - try common formats
        date_str = str(date_value).strip()
        
        formats = [
            '%Y-%m-%d',           # ISO format
            '%Y%m%d',             # SAP format (YYYYMMDD)
            '%m/%d/%Y',           # US format
            '%d/%m/%Y',           # European format
            '%Y-%m-%dT%H:%M:%S',  # ISO datetime
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.date().isoformat()
            except ValueError:
                continue
        
        # Fallback to current date
        return datetime.now().date().isoformat()
    
    def _convert_units(
        self,
        quantity: Any,
        unit: str,
        custom_config: Optional[Dict] = None
    ) -> tuple[Decimal, str, Dict]:
        """
        Convert quantity to standard unit.
        
        Requirements: 4.1, 4.2, 4.7
        """
        if not quantity or not unit:
            return Decimal('0'), 'unknown', {'factor': Decimal('1'), 'method': 'none'}
        
        try:
            quantity_decimal = Decimal(str(quantity))
        except (ValueError, TypeError):
            return Decimal('0'), unit, {'factor': Decimal('1'), 'method': 'error'}
        
        # Get standard unit for this unit category
        standard_unit = self.unit_converter.get_standard_unit(unit)
        
        if not standard_unit:
            # Unknown unit - keep original
            return quantity_decimal, unit, {'factor': Decimal('1'), 'method': 'no_conversion'}
        
        # Convert to standard unit
        try:
            custom_conversions = None
            if custom_config and 'unit_conversions' in custom_config:
                custom_conversions = custom_config['unit_conversions']
            
            converted_value, factor = self.unit_converter.convert(
                float(quantity),
                unit,
                standard_unit,
                custom_conversions
            )
            
            return converted_value, standard_unit, {
                'factor': factor,
                'method': 'standard'
            }
            
        except ConversionError as e:
            # Conversion failed - keep original with error flag
            return quantity_decimal, unit, {
                'factor': Decimal('1'),
                'method': 'conversion_failed',
                'error': str(e)
            }
