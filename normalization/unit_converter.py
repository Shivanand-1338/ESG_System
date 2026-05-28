"""
Unit conversion registry and converter.

Requirements: 4.1, 4.3
"""

from decimal import Decimal
from typing import Dict, Tuple, Optional


class ConversionError(Exception):
    """Exception raised when unit conversion fails."""
    pass


class UnitConverter:
    """
    Handles unit conversions with a registry of conversion factors.
    
    Requirements: 4.1, 4.3
    """
    
    def __init__(self):
        """Initialize converter with standard conversion factors."""
        self.conversion_registry: Dict[Tuple[str, str], Decimal] = {}
        self._register_standard_conversions()
    
    def _register_standard_conversions(self):
        """Register standard unit conversions."""
        
        # Volume conversions (to liters)
        self.register('gallons_us', 'liters', Decimal('3.78541'))
        self.register('gallons_uk', 'liters', Decimal('4.54609'))
        self.register('cubic_meters', 'liters', Decimal('1000'))
        self.register('cubic_feet', 'liters', Decimal('28.3168'))
        
        # Energy conversions (to kWh)
        self.register('kwh', 'mwh', Decimal('0.001'))
        self.register('mwh', 'kwh', Decimal('1000'))
        self.register('btu', 'kwh', Decimal('0.000293071'))
        self.register('therms', 'kwh', Decimal('29.3001'))
        self.register('joules', 'kwh', Decimal('0.000000277778'))
        self.register('mj', 'kwh', Decimal('0.277778'))
        self.register('gj', 'kwh', Decimal('277.778'))
        
        # Distance conversions (to kilometers)
        self.register('miles', 'kilometers', Decimal('1.60934'))
        self.register('nautical_miles', 'kilometers', Decimal('1.852'))
        self.register('feet', 'meters', Decimal('0.3048'))
        self.register('meters', 'kilometers', Decimal('0.001'))
        
        # Mass conversions (to kilograms)
        self.register('pounds', 'kilograms', Decimal('0.453592'))
        self.register('short_tons', 'metric_tonnes', Decimal('0.907185'))
        self.register('metric_tonnes', 'kilograms', Decimal('1000'))
        self.register('ounces', 'kilograms', Decimal('0.0283495'))
        
        # Emissions conversions (to kg CO2e)
        self.register('tonnes_co2e', 'kg_co2e', Decimal('1000'))
        self.register('lbs_co2e', 'kg_co2e', Decimal('0.453592'))
        
        # Common aliases
        self.register('gal', 'liters', Decimal('3.78541'))  # Assume US gallons
        self.register('l', 'liters', Decimal('1'))
        self.register('km', 'kilometers', Decimal('1'))
        self.register('mi', 'kilometers', Decimal('1.60934'))
        self.register('kg', 'kilograms', Decimal('1'))
        self.register('lb', 'kilograms', Decimal('0.453592'))
    
    def register(self, from_unit: str, to_unit: str, factor: Decimal):
        """
        Register a conversion factor.
        
        Args:
            from_unit: Source unit (normalized to lowercase)
            to_unit: Target unit (normalized to lowercase)
            factor: Multiplication factor to convert from source to target
        """
        from_unit = from_unit.lower().strip()
        to_unit = to_unit.lower().strip()
        self.conversion_registry[(from_unit, to_unit)] = factor
        
        # Also register reverse conversion
        if factor != 0:
            self.conversion_registry[(to_unit, from_unit)] = Decimal('1') / factor
    
    def convert(
        self, 
        value: float, 
        from_unit: str, 
        to_unit: str,
        custom_conversions: Optional[Dict] = None
    ) -> Tuple[Decimal, Decimal]:
        """
        Convert a value from one unit to another.
        
        Args:
            value: Numeric value to convert
            from_unit: Source unit
            to_unit: Target unit
            custom_conversions: Optional client-specific conversion factors
            
        Returns:
            Tuple of (converted_value, conversion_factor)
            
        Raises:
            ConversionError: If conversion is not possible
        """
        from_unit = from_unit.lower().strip()
        to_unit = to_unit.lower().strip()
        
        # Same unit - no conversion needed
        if from_unit == to_unit:
            return Decimal(str(value)), Decimal('1')
        
        # Try custom conversions first
        if custom_conversions:
            key = f"{from_unit}_to_{to_unit}"
            if key in custom_conversions:
                factor = Decimal(str(custom_conversions[key]))
                converted = Decimal(str(value)) * factor
                return converted, factor
        
        # Try standard conversions
        conversion_key = (from_unit, to_unit)
        if conversion_key in self.conversion_registry:
            factor = self.conversion_registry[conversion_key]
            converted = Decimal(str(value)) * factor
            return converted, factor
        
        # Try multi-step conversion through common intermediate units
        intermediate_units = ['liters', 'kwh', 'kilometers', 'kilograms', 'kg_co2e']
        
        for intermediate in intermediate_units:
            from_to_intermediate = (from_unit, intermediate)
            intermediate_to_target = (intermediate, to_unit)
            
            if (from_to_intermediate in self.conversion_registry and 
                intermediate_to_target in self.conversion_registry):
                
                factor1 = self.conversion_registry[from_to_intermediate]
                factor2 = self.conversion_registry[intermediate_to_target]
                total_factor = factor1 * factor2
                converted = Decimal(str(value)) * total_factor
                return converted, total_factor
        
        # Conversion not found
        raise ConversionError(
            f"No conversion available from '{from_unit}' to '{to_unit}'"
        )
    
    def get_standard_unit(self, unit: str) -> Optional[str]:
        """
        Get the standard unit for a given unit category.
        
        Args:
            unit: Input unit
            
        Returns:
            Standard unit name or None if not found
        """
        unit = unit.lower().strip()
        
        # Volume units -> liters
        volume_units = ['gallons_us', 'gallons_uk', 'gal', 'cubic_meters', 'cubic_feet', 'l', 'liters']
        if unit in volume_units:
            return 'liters'
        
        # Energy units -> kWh
        energy_units = ['kwh', 'mwh', 'btu', 'therms', 'joules', 'mj', 'gj']
        if unit in energy_units:
            return 'kwh'
        
        # Distance units -> kilometers
        distance_units = ['miles', 'mi', 'nautical_miles', 'feet', 'meters', 'km', 'kilometers']
        if unit in distance_units:
            return 'kilometers'
        
        # Mass units -> kilograms
        mass_units = ['pounds', 'lb', 'short_tons', 'metric_tonnes', 'ounces', 'kg', 'kilograms']
        if unit in mass_units:
            return 'kilograms'
        
        # Emissions units -> kg CO2e
        emissions_units = ['tonnes_co2e', 'lbs_co2e', 'kg_co2e']
        if unit in emissions_units:
            return 'kg_co2e'
        
        return None
