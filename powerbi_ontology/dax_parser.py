"""
DAX Parser

Parses DAX formulas to extract business rules and semantic meaning.
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Set

from pyparsing import (
    CaselessKeyword, Word, alphanums, nums, oneOf, opAssoc, infixNotation,
    ParseException, Suppress, Optional as Opt, Group
)

logger = logging.getLogger(__name__)


@dataclass
class BusinessRule:
    """Represents a business rule extracted from DAX."""
    name: str
    condition: str
    action: str = ""
    priority: int = 1
    description: str = ""
    entity: str = ""
    classification: str = ""


@dataclass
class ParsedRule:
    """Parsed DAX measure with extracted information."""
    measure_name: str
    dax_formula: str
    business_rules: List[BusinessRule]
    dependencies: List[str]
    measure_type: str  # AGGREGATION, CALCULATION, CONDITIONAL, FILTER, TIME_INTELLIGENCE


class DAXParser:
    """
    Parses DAX formulas to extract business logic and semantic meaning.
    
    Background: DAX measures contain business logic that should be extracted
    as formal business rules. For example:
    - HighRiskCustomers = CALCULATE(COUNT(...), RiskScore > 80)
    - This becomes: BusinessRule(condition="RiskScore > 80", classification="HighRisk")
    """

    def __init__(self):
        """Initialize DAX parser."""
        self._setup_parser()

    def _setup_parser(self):
        """Setup pyparsing grammar for DAX."""
        # Basic tokens
        identifier = Word(alphanums + "_")
        number = Word(nums + ".-")
        
        # DAX functions
        calculate = CaselessKeyword("CALCULATE")
        sum_func = CaselessKeyword("SUM")
        count_func = CaselessKeyword("COUNT")
        distinctcount = CaselessKeyword("DISTINCTCOUNT")
        if_func = CaselessKeyword("IF")
        switch_func = CaselessKeyword("SWITCH")
        
        # Operators
        gt = ">"
        lt = "<"
        eq = "="
        ge = ">="
        le = "<="
        and_op = CaselessKeyword("AND")
        or_op = CaselessKeyword("OR")
        
        # Store for later use
        self.identifier = identifier
        self.number = number

    def parse_measure(self, measure_name: str, dax_formula: str) -> ParsedRule:
        """
        Parse a DAX measure to extract business rules.
        
        Args:
            measure_name: Name of the measure
            dax_formula: DAX formula string
            
        Returns:
            ParsedRule with extracted information
        """
        logger.debug(f"Parsing measure: {measure_name}")
        
        business_rules = []
        dependencies = self.identify_dependencies(dax_formula)
        measure_type = self.classify_measure_type(dax_formula)
        
        # Extract business logic
        extracted_rules = self.extract_business_logic(measure_name, dax_formula)
        business_rules.extend(extracted_rules)
        
        return ParsedRule(
            measure_name=measure_name,
            dax_formula=dax_formula,
            business_rules=business_rules,
            dependencies=dependencies,
            measure_type=measure_type
        )

    def extract_business_logic(self, measure_name: str, dax_formula: str) -> List[BusinessRule]:
        """
        Extract business logic from DAX formula.
        
        Args:
            measure_name: Name of the measure
            dax_formula: DAX formula string
            
        Returns:
            List of BusinessRule objects
        """
        rules = []
        dax_upper = dax_formula.upper()
        
        # Pattern 1: CALCULATE with filter conditions
        # Example: CALCULATE(COUNT(...), RiskScore > 80)
        calculate_pattern = r'CALCULATE\s*\([^,]+,\s*([^)]+)\)'
        calculate_matches = re.finditer(calculate_pattern, dax_formula, re.IGNORECASE)
        
        for match in calculate_matches:
            filter_condition = match.group(1).strip()
            # Extract condition parts
            condition = self._parse_condition(filter_condition)
            if condition:
                rule = BusinessRule(
                    name=f"{measure_name}_Filter",
                    condition=condition,
                    action="filter",
                    description=f"Filter condition from {measure_name}: {condition}",
                    entity=self._normalize_entity_name(self._extract_entity_from_condition(condition))
                )
                rules.append(rule)
        
        # Pattern 2: IF conditions
        # Example: IF(RiskScore > 80, "High", "Low")
        if_pattern = r'IF\s*\(\s*([^,]+),\s*([^,]+),\s*([^)]+)\)'
        if_matches = re.finditer(if_pattern, dax_formula, re.IGNORECASE)
        
        for match in if_matches:
            condition = match.group(1).strip()
            true_value = match.group(2).strip()
            false_value = match.group(3).strip()
            
            parsed_condition = self._parse_condition(condition)
            if parsed_condition:
                rule = BusinessRule(
                    name=f"{measure_name}_Condition",
                    condition=parsed_condition,
                    action=f"classify_as_{true_value.replace('\"', '').replace(' ', '_').lower()}",
                    classification=true_value.replace('"', '').strip(),
                    description=f"IF condition: {parsed_condition} then {true_value} else {false_value}",
                    entity=self._normalize_entity_name(self._extract_entity_from_condition(condition))
                )
                rules.append(rule)
        
        # Pattern 3: SWITCH statements
        # Example: SWITCH(TRUE(), RiskScore > 80, "High", RiskScore > 50, "Medium", "Low")
        switch_pattern = r'SWITCH\s*\([^,]+,\s*([^)]+)\)'
        switch_matches = re.finditer(switch_pattern, dax_formula, re.IGNORECASE)
        
        for match in switch_matches:
            switch_body = match.group(1)
            # Parse switch cases
            cases = self._parse_switch_cases(switch_body)
            for case_condition, case_value in cases:
                parsed_condition = self._parse_condition(case_condition)
                if parsed_condition:
                    rule = BusinessRule(
                        name=f"{measure_name}_Switch_{case_value.replace('\"', '').replace(' ', '_')}",
                        condition=parsed_condition,
                        action=f"classify_as_{case_value.replace('\"', '').replace(' ', '_').lower()}",
                        classification=case_value.replace('"', '').strip(),
                        description=f"SWITCH case: {parsed_condition} -> {case_value}",
                        entity=self._normalize_entity_name(self._extract_entity_from_condition(case_condition))
                    )
                    rules.append(rule)
        
        # Pattern 4: Simple threshold conditions
        # Example: RiskScore > 80
        threshold_pattern = r'(\w+)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)'
        threshold_matches = re.finditer(threshold_pattern, dax_formula)
        
        for match in threshold_matches:
            field = match.group(1)
            operator = match.group(2)
            value = match.group(3)
            
            # Only add if not already captured by other patterns
            if not any(field in r.condition for r in rules):
                rule = BusinessRule(
                    name=f"{measure_name}_Threshold",
                    condition=f"{field} {operator} {value}",
                    action="threshold_check",
                    description=f"Threshold condition: {field} {operator} {value}",
                    entity=self._extract_entity_from_field(field)
                )
                rules.append(rule)
        
        return rules

    def _parse_condition(self, condition: str) -> Optional[str]:
        """Parse a condition string and normalize it."""
        # Clean up the condition
        condition = condition.strip()
        # Remove extra whitespace
        condition = re.sub(r'\s+', ' ', condition)
        return condition if condition else None

    def _parse_switch_cases(self, switch_body: str) -> List[tuple]:
        """Parse SWITCH cases from switch body."""
        cases = []
        # Simple parsing - split by comma and pair up
        parts = [p.strip() for p in switch_body.split(',')]
        # SWITCH format: condition1, value1, condition2, value2, ..., default_value
        i = 0
        while i < len(parts) - 1:
            condition = parts[i]
            value = parts[i + 1]
            cases.append((condition, value))
            i += 2
        return cases

    def _extract_entity_from_condition(self, condition: str) -> str:
        """Extract entity name from condition (e.g., 'Customer[RiskScore]' -> 'Customer')."""
        # Match table[column] pattern
        match = re.search(r'(\w+)\[', condition)
        if match:
            return match.group(1)
        return ""

    def _normalize_entity_name(self, entity: str) -> str:
        """Normalize extracted entity name for rule output."""
        if entity.endswith("s") and len(entity) > 1:
            return entity[:-1]
        return entity

    def _extract_entity_from_field(self, field: str) -> str:
        """Extract entity from field name (heuristic)."""
        # If field contains underscore, might be entity_field
        if '_' in field:
            parts = field.split('_')
            return parts[0].capitalize()
        return ""

    def identify_dependencies(self, dax_formula: str) -> List[str]:
        """
        Identify table/column dependencies from DAX formula.
        
        Args:
            dax_formula: DAX formula string
            
        Returns:
            List of dependencies in format "Table.Column"
        """
        dependencies = set()
        
        # Match table[column] patterns
        pattern = r'(\w+)\[(\w+)\]'
        matches = re.findall(pattern, dax_formula)
        for table, column in matches:
            dependencies.add(f"{table}.{column}")
        
        # Also match table references (without column)
        table_pattern = r'\b([A-Z][a-zA-Z0-9_]*)\['
        table_matches = re.findall(table_pattern, dax_formula)
        for table in table_matches:
            if table.upper() not in ['IF', 'CALCULATE', 'SUM', 'COUNT', 'AVG', 'MAX', 'MIN']:
                dependencies.add(f"{table}.*")
        
        return sorted(list(dependencies))

    def classify_measure_type(self, dax_formula: str) -> str:
        """
        Classify the type of DAX measure.
        
        Returns:
            MeasureType: AGGREGATION, CALCULATION, CONDITIONAL, FILTER, TIME_INTELLIGENCE
        """
        dax_upper = dax_formula.upper()
        
        # Time intelligence functions
        time_intel_keywords = ['DATEADD', 'TOTALYTD', 'TOTALQTD', 'TOTALMTD', 'SAMEPERIODLASTYEAR']
        if any(keyword in dax_upper for keyword in time_intel_keywords):
            return "TIME_INTELLIGENCE"
        
        # Conditional logic
        if 'IF' in dax_upper or 'SWITCH' in dax_upper:
            return "CONDITIONAL"
        
        # Filter logic
        if 'CALCULATE' in dax_upper and ('FILTER' in dax_upper or '>' in dax_formula or '<' in dax_formula):
            return "FILTER"
        
        # Aggregation functions
        agg_keywords = ['SUM', 'COUNT', 'AVG', 'AVERAGE', 'MAX', 'MIN', 'DISTINCTCOUNT']
        if any(keyword in dax_upper for keyword in agg_keywords):
            return "AGGREGATION"
        
        # Default to calculation
        return "CALCULATION"
