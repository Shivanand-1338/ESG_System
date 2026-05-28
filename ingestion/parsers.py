"""
Data parsers for heterogeneous source formats.

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
"""

import xml.etree.ElementTree as ET
import csv
import json
import io
from typing import Dict, List, Any, Optional
from datetime import datetime


class ParsingError(Exception):
    """Custom exception for parsing errors."""
    pass


class SAPIdocParser:
    """
    Parser for SAP IDoc XML format.
    
    Requirements: 1.1
    """
    
    def parse(self, raw_data: str) -> List[Dict[str, Any]]:
        """
        Parse SAP IDoc XML format.
        
        Args:
            raw_data: XML string containing IDoc data
            
        Returns:
            List of dictionaries containing parsed data
            
        Raises:
            ParsingError: If parsing fails
        """
        try:
            root = ET.fromstring(raw_data)
            records = []
            
            # Parse IDoc structure: EDI_DC40 control record + data segments
            for idoc in root.findall('.//IDOC'):
                control = idoc.find('EDI_DC40')
                if control is None:
                    continue
                
                # Extract data segments
                for segment in idoc.findall('.//E1*'):  # All segments starting with E1
                    record = {
                        'source_type': 'SAP_IDOC',
                        'message_type': control.findtext('MESTYP', ''),
                        'sender': control.findtext('SNDPRN', ''),
                        'material_number': segment.findtext('MATNR', ''),
                        'quantity': segment.findtext('MENGE', ''),
                        'unit': segment.findtext('MEINS', ''),
                        'cost_center': segment.findtext('KOSTL', ''),
                        'transaction_date': segment.findtext('BUDAT', ''),
                        'plant': segment.findtext('WERKS', ''),
                        'storage_location': segment.findtext('LGORT', ''),
                    }
                    
                    # Remove empty fields
                    record = {k: v for k, v in record.items() if v}
                    
                    if record.get('material_number'):
                        records.append(record)
            
            if not records:
                raise ParsingError("No valid IDoc segments found in XML")
            
            return records
            
        except ET.ParseError as e:
            raise ParsingError(f"Invalid XML format: {str(e)}")
        except Exception as e:
            raise ParsingError(f"IDoc parsing failed: {str(e)}")


class SAPCSVParser:
    """
    Parser for SAP CSV exports with configurable column mappings.
    
    Requirements: 1.1, 10.4
    """
    
    def __init__(self, column_mapping: Optional[Dict[str, str]] = None):
        """
        Initialize parser with optional column mapping.
        
        Args:
            column_mapping: Dict mapping standard field names to CSV column names
        """
        self.column_mapping = column_mapping or {
            'material_number': 'Material',
            'quantity': 'Quantity',
            'unit': 'Unit',
            'cost_center': 'Cost Center',
            'transaction_date': 'Date',
            'plant': 'Plant',
            'description': 'Description',
        }
    
    def parse(self, raw_data: str, configuration: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Parse SAP CSV format.
        
        Args:
            raw_data: CSV string
            configuration: Optional configuration with custom column mappings
            
        Returns:
            List of dictionaries containing parsed data
            
        Raises:
            ParsingError: If parsing fails
        """
        try:
            # Use custom mapping if provided in configuration
            if configuration and 'column_mapping' in configuration:
                mapping = configuration['column_mapping']
            else:
                mapping = self.column_mapping
            
            # Reverse mapping for lookup
            reverse_mapping = {v: k for k, v in mapping.items()}
            
            # Parse CSV
            csv_file = io.StringIO(raw_data)
            reader = csv.DictReader(csv_file)
            
            records = []
            for row_num, row in enumerate(reader, start=2):
                record = {'source_type': 'SAP_CSV', 'row_number': row_num}
                
                # Map columns to standard field names
                for csv_col, value in row.items():
                    if csv_col in reverse_mapping:
                        standard_field = reverse_mapping[csv_col]
                        record[standard_field] = value.strip() if value else ''
                
                # Validate required fields
                if not record.get('material_number') and not record.get('quantity'):
                    continue  # Skip empty rows
                
                records.append(record)
            
            if not records:
                raise ParsingError("No valid data rows found in CSV")
            
            return records
            
        except csv.Error as e:
            raise ParsingError(f"Invalid CSV format: {str(e)}")
        except Exception as e:
            raise ParsingError(f"CSV parsing failed: {str(e)}")


class GreenButtonParser:
    """
    Parser for Green Button XML (Atom/ESPI format).
    
    Requirements: 1.2
    """
    
    # XML namespaces for Green Button
    NAMESPACES = {
        'atom': 'http://www.w3.org/2005/Atom',
        'espi': 'http://naesb.org/espi',
    }
    
    def parse(self, raw_data: str) -> List[Dict[str, Any]]:
        """
        Parse Green Button XML format.
        
        Args:
            raw_data: XML string containing Green Button data
            
        Returns:
            List of dictionaries containing parsed usage data
            
        Raises:
            ParsingError: If parsing fails
        """
        try:
            root = ET.fromstring(raw_data)
            records = []
            
            # Find all UsagePoint entries
            for entry in root.findall('.//atom:entry', self.NAMESPACES):
                content = entry.find('atom:content', self.NAMESPACES)
                if content is None:
                    continue
                
                # Extract UsagePoint
                usage_point = content.find('espi:UsagePoint', self.NAMESPACES)
                if usage_point is not None:
                    usage_point_id = usage_point.findtext('espi:ServiceCategory/espi:kind', '', self.NAMESPACES)
                
                # Extract MeterReading and IntervalBlocks
                meter_reading = content.find('espi:MeterReading', self.NAMESPACES)
                if meter_reading is not None:
                    for interval_block in meter_reading.findall('.//espi:IntervalBlock', self.NAMESPACES):
                        interval = interval_block.find('espi:interval', self.NAMESPACES)
                        
                        if interval is not None:
                            start = interval.findtext('espi:start', '', self.NAMESPACES)
                            duration = interval.findtext('espi:duration', '', self.NAMESPACES)
                        
                        # Extract readings
                        for reading in interval_block.findall('.//espi:IntervalReading', self.NAMESPACES):
                            record = {
                                'source_type': 'GREEN_BUTTON',
                                'usage_point_id': usage_point_id,
                                'start_time': start,
                                'duration': duration,
                                'value': reading.findtext('espi:value', '', self.NAMESPACES),
                                'reading_type': reading.findtext('espi:ReadingType/espi:uom', '', self.NAMESPACES),
                                'power_of_ten': reading.findtext('espi:ReadingType/espi:powerOfTenMultiplier', '', self.NAMESPACES),
                            }
                            
                            # Remove empty fields
                            record = {k: v for k, v in record.items() if v}
                            
                            if record.get('value'):
                                records.append(record)
            
            if not records:
                raise ParsingError("No valid usage data found in Green Button XML")
            
            return records
            
        except ET.ParseError as e:
            raise ParsingError(f"Invalid XML format: {str(e)}")
        except Exception as e:
            raise ParsingError(f"Green Button parsing failed: {str(e)}")


class ConcurParser:
    """
    Parser for Concur API JSON format.
    
    Requirements: 1.3
    """
    
    def parse(self, raw_data: str) -> List[Dict[str, Any]]:
        """
        Parse Concur trip data JSON format.
        
        Args:
            raw_data: JSON string containing Concur trip data
            
        Returns:
            List of dictionaries containing parsed trip segments
            
        Raises:
            ParsingError: If parsing fails
        """
        try:
            data = json.loads(raw_data)
            records = []
            
            # Handle both single trip and list of trips
            trips = data if isinstance(data, list) else [data]
            
            for trip in trips:
                trip_id = trip.get('TripId', trip.get('id', ''))
                trip_name = trip.get('TripName', trip.get('name', ''))
                
                # Extract trip segments
                segments = trip.get('Segments', trip.get('segments', []))
                
                for segment in segments:
                    record = {
                        'source_type': 'CONCUR_API',
                        'trip_id': trip_id,
                        'trip_name': trip_name,
                        'segment_type': segment.get('SegmentType', segment.get('type', '')),
                        'travel_mode': segment.get('ClassOfService', segment.get('travelMode', '')),
                        'origin': segment.get('StartLocation', segment.get('origin', '')),
                        'destination': segment.get('EndLocation', segment.get('destination', '')),
                        'start_date': segment.get('StartDate', segment.get('startDate', '')),
                        'end_date': segment.get('EndDate', segment.get('endDate', '')),
                        'distance': segment.get('Distance', segment.get('distance', '')),
                        'distance_unit': segment.get('DistanceUnit', segment.get('distanceUnit', '')),
                        'emissions': segment.get('CarbonEmissions', segment.get('emissions', '')),
                        'emissions_unit': segment.get('EmissionsUnit', segment.get('emissionsUnit', 'kg CO2e')),
                        'carrier': segment.get('Carrier', segment.get('carrier', '')),
                    }
                    
                    # Remove empty fields
                    record = {k: v for k, v in record.items() if v}
                    
                    if record.get('travel_mode') or record.get('segment_type'):
                        records.append(record)
            
            if not records:
                raise ParsingError("No valid trip segments found in Concur data")
            
            return records
            
        except json.JSONDecodeError as e:
            raise ParsingError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise ParsingError(f"Concur parsing failed: {str(e)}")


class FormatRouter:
    """
    Routes incoming data to the appropriate parser based on format detection.
    
    Requirements: 1.1, 1.2, 1.3
    """
    
    def __init__(self):
        self.sap_idoc_parser = SAPIdocParser()
        self.sap_csv_parser = SAPCSVParser()
        self.greenbutton_parser = GreenButtonParser()
        self.concur_parser = ConcurParser()
    
    def route_and_parse(
        self, 
        raw_data: str, 
        content_type: Optional[str] = None,
        source_type: Optional[str] = None,
        configuration: Optional[Dict] = None
    ) -> tuple[List[Dict[str, Any]], str]:
        """
        Detect format and route to appropriate parser.
        
        Args:
            raw_data: Raw input data
            content_type: HTTP content-type header
            source_type: Explicit source type hint
            configuration: Parser configuration
            
        Returns:
            Tuple of (parsed_records, detected_source_type)
            
        Raises:
            ParsingError: If format cannot be detected or parsing fails
        """
        # Explicit source type routing
        if source_type:
            return self._parse_by_source_type(raw_data, source_type, configuration)
        
        # Content-type based routing
        if content_type:
            if 'xml' in content_type.lower():
                return self._try_xml_parsers(raw_data)
            elif 'json' in content_type.lower():
                return self._try_json_parsers(raw_data)
            elif 'csv' in content_type.lower():
                return self._try_csv_parsers(raw_data, configuration)
        
        # Heuristic detection
        raw_data_stripped = raw_data.strip()
        
        # Try XML parsers
        if raw_data_stripped.startswith('<'):
            return self._try_xml_parsers(raw_data)
        
        # Try JSON parsers
        if raw_data_stripped.startswith('{') or raw_data_stripped.startswith('['):
            return self._try_json_parsers(raw_data)
        
        # Try CSV parsers
        if ',' in raw_data or '\t' in raw_data:
            return self._try_csv_parsers(raw_data, configuration)
        
        raise ParsingError("Unable to detect data format")
    
    def _parse_by_source_type(
        self, 
        raw_data: str, 
        source_type: str, 
        configuration: Optional[Dict]
    ) -> tuple[List[Dict[str, Any]], str]:
        """Parse using explicit source type."""
        if source_type == 'SAP_IDOC':
            return self.sap_idoc_parser.parse(raw_data), 'SAP_IDOC'
        elif source_type == 'SAP_CSV':
            return self.sap_csv_parser.parse(raw_data, configuration), 'SAP_CSV'
        elif source_type == 'GREEN_BUTTON':
            return self.greenbutton_parser.parse(raw_data), 'GREEN_BUTTON'
        elif source_type == 'CONCUR_API':
            return self.concur_parser.parse(raw_data), 'CONCUR_API'
        else:
            raise ParsingError(f"Unknown source type: {source_type}")
    
    def _try_xml_parsers(self, raw_data: str) -> tuple[List[Dict[str, Any]], str]:
        """Try XML-based parsers."""
        # Try IDoc first
        try:
            if 'IDOC' in raw_data or 'EDI_DC40' in raw_data:
                return self.sap_idoc_parser.parse(raw_data), 'SAP_IDOC'
        except ParsingError:
            pass
        
        # Try Green Button
        try:
            if 'espi' in raw_data.lower() or 'UsagePoint' in raw_data:
                return self.greenbutton_parser.parse(raw_data), 'GREEN_BUTTON'
        except ParsingError:
            pass
        
        raise ParsingError("XML format not recognized as SAP IDoc or Green Button")
    
    def _try_json_parsers(self, raw_data: str) -> tuple[List[Dict[str, Any]], str]:
        """Try JSON-based parsers."""
        try:
            return self.concur_parser.parse(raw_data), 'CONCUR_API'
        except ParsingError as e:
            raise ParsingError(f"JSON format not recognized as Concur: {str(e)}")
    
    def _try_csv_parsers(
        self, 
        raw_data: str, 
        configuration: Optional[Dict]
    ) -> tuple[List[Dict[str, Any]], str]:
        """Try CSV-based parsers."""
        try:
            return self.sap_csv_parser.parse(raw_data, configuration), 'SAP_CSV'
        except ParsingError as e:
            raise ParsingError(f"CSV format not recognized as SAP: {str(e)}")
