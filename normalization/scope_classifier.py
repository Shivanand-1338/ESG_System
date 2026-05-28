"""
Emission scope classifier for GHG Protocol categorization.

Requirements: 5.1, 5.2, 5.3, 5.4
"""

from typing import Optional, Dict, Any


class ScopeClassifier:
    """
    Classifies emissions data into GHG Protocol scopes (1, 2, or 3).
    
    Requirements: 5.1, 5.2, 5.3, 5.4
    """
    
    def __init__(self):
        """Initialize classifier with activity type mappings."""
        self._initialize_mappings()
    
    def _initialize_mappings(self):
        """Define activity type to scope mappings."""
        
        # Scope 1: Direct emissions
        self.scope_1_keywords = [
            'fuel_combustion', 'natural_gas', 'diesel', 'gasoline', 'propane',
            'refrigerant', 'fugitive', 'process_emissions', 'combustion',
            'company_vehicle', 'fleet', 'on_site_fuel'
        ]
        
        # Scope 2: Purchased electricity
        self.scope_2_keywords = [
            'electricity', 'purchased_electricity', 'grid_electricity',
            'purchased_steam', 'purchased_heating', 'purchased_cooling',
            'kwh', 'power_consumption', 'utility'
        ]
        
        # Scope 3: Value chain
        self.scope_3_keywords = [
            'air_travel', 'flight', 'rail_travel', 'train', 'car_rental',
            'hotel', 'accommodation', 'business_travel', 'employee_commute',
            'purchased_goods', 'procurement', 'supply_chain', 'supplier',
            'waste', 'disposal', 'transportation', 'shipping', 'freight',
            'downstream', 'upstream'
        ]
    
    def classify(
        self, 
        activity_type: str,
        data_source_type: Optional[str] = None,
        parsed_data: Optional[Dict[str, Any]] = None
    ) -> tuple[str, bool]:
        """
        Classify emission scope based on activity type and context.
        
        Args:
            activity_type: Type of activity (e.g., 'fuel_combustion', 'air_travel')
            data_source_type: Source system type (SAP, Green Button, Concur)
            parsed_data: Additional parsed data for context
            
        Returns:
            Tuple of (scope, is_ambiguous)
            - scope: 'SCOPE_1', 'SCOPE_2', or 'SCOPE_3'
            - is_ambiguous: True if classification is uncertain
        """
        activity_lower = activity_type.lower().strip()
        
        # Data source-based classification
        if data_source_type:
            source_scope = self._classify_by_source(data_source_type)
            if source_scope:
                return source_scope, False
        
        # Activity type keyword matching
        scope_1_score = self._calculate_keyword_score(activity_lower, self.scope_1_keywords)
        scope_2_score = self._calculate_keyword_score(activity_lower, self.scope_2_keywords)
        scope_3_score = self._calculate_keyword_score(activity_lower, self.scope_3_keywords)
        
        scores = {
            'SCOPE_1': scope_1_score,
            'SCOPE_2': scope_2_score,
            'SCOPE_3': scope_3_score
        }
        
        max_score = max(scores.values())
        
        # No clear match
        if max_score == 0:
            return 'SCOPE_3', True  # Default to Scope 3 with ambiguity flag
        
        # Check for ambiguity (multiple high scores)
        high_scores = [scope for scope, score in scores.items() if score == max_score]
        is_ambiguous = len(high_scores) > 1
        
        # Return highest scoring scope
        best_scope = max(scores, key=scores.get)
        
        return best_scope, is_ambiguous
    
    def _classify_by_source(self, source_type: str) -> Optional[tuple[str, bool]]:
        """
        Classify based on data source type.
        
        Args:
            source_type: Data source type
            
        Returns:
            Tuple of (scope, is_ambiguous) or None if source doesn't determine scope
        """
        source_upper = source_type.upper()
        
        # Green Button is typically Scope 2 (purchased electricity)
        if 'GREEN_BUTTON' in source_upper:
            return 'SCOPE_2', False
        
        # Concur is typically Scope 3 (business travel)
        if 'CONCUR' in source_upper:
            return 'SCOPE_3', False
        
        # SAP can be any scope - need activity type
        return None
    
    def _calculate_keyword_score(self, activity: str, keywords: list) -> int:
        """
        Calculate matching score for activity against keyword list.
        
        Args:
            activity: Activity type string
            keywords: List of keywords to match
            
        Returns:
            Score (number of keyword matches)
        """
        score = 0
        for keyword in keywords:
            if keyword in activity:
                score += 1
        return score
    
    def get_scope_description(self, scope: str) -> str:
        """
        Get human-readable description of scope.
        
        Args:
            scope: Scope identifier ('SCOPE_1', 'SCOPE_2', 'SCOPE_3')
            
        Returns:
            Description string
        """
        descriptions = {
            'SCOPE_1': 'Scope 1: Direct Emissions',
            'SCOPE_2': 'Scope 2: Purchased Electricity',
            'SCOPE_3': 'Scope 3: Value Chain'
        }
        return descriptions.get(scope, 'Unknown Scope')
