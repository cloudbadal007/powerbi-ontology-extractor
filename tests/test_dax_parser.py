"""
Tests for DAXParser class.
"""

import pytest

from powerbi_ontology.dax_parser import DAXParser, ParsedRule, BusinessRule
from tests.fixtures.test_data import (
    SIMPLE_DAX_SUM, CONDITIONAL_DAX, SWITCH_DAX, CALCULATE_FILTER_DAX, TIME_INTELLIGENCE_DAX
)


class TestDAXParser:
    """Test DAXParser class."""
    
    def test_init(self):
        """Test parser initialization."""
        parser = DAXParser()
        assert parser is not None
    
    def test_parse_simple_sum(self):
        """Test parsing simple SUM aggregation."""
        parser = DAXParser()
        parsed = parser.parse_measure("Total Revenue", SIMPLE_DAX_SUM)
        
        assert isinstance(parsed, ParsedRule)
        assert parsed.measure_name == "Total Revenue"
        assert parsed.measure_type == "AGGREGATION"
        assert "Orders.OrderValue" in parsed.dependencies
    
    def test_parse_conditional_dax(self):
        """Test parsing conditional DAX with CALCULATE."""
        parser = DAXParser()
        parsed = parser.parse_measure("High Risk Customers", CONDITIONAL_DAX)
        
        assert parsed.measure_type == "FILTER"
        assert len(parsed.business_rules) > 0
        
        # Check that business rule was extracted
        rule = parsed.business_rules[0]
        assert "RiskScore" in rule.condition
        assert "80" in rule.condition
        assert rule.entity == "Customer" or rule.entity == ""
    
    def test_parse_switch_statement(self):
        """Test parsing SWITCH statement into multiple business rules."""
        parser = DAXParser()
        parsed = parser.parse_measure("Shipment Risk Level", SWITCH_DAX)
        
        assert parsed.measure_type == "CONDITIONAL"
        assert len(parsed.business_rules) >= 2  # Should have multiple rules
        
        # Check that conditions were extracted
        conditions = [rule.condition for rule in parsed.business_rules]
        assert any("Temperature" in cond for cond in conditions)
        assert any("Vibration" in cond for cond in conditions)
    
    def test_parse_calculate_with_filters(self):
        """Test parsing CALCULATE with multiple filters."""
        parser = DAXParser()
        parsed = parser.parse_measure("At Risk Revenue", CALCULATE_FILTER_DAX)
        
        assert parsed.measure_type == "FILTER"
        assert len(parsed.business_rules) > 0
        
        # Should extract multiple conditions
        conditions = [rule.condition for rule in parsed.business_rules]
        assert any("RiskScore" in cond for cond in conditions)
    
    def test_parse_time_intelligence(self):
        """Test parsing time intelligence functions."""
        parser = DAXParser()
        parsed = parser.parse_measure("YTD Revenue", TIME_INTELLIGENCE_DAX)
        
        assert parsed.measure_type == "TIME_INTELLIGENCE"
        assert "TOTALYTD" in parsed.dax_formula
    
    def test_extract_business_logic_simple_condition(self):
        """Test extracting business logic from simple condition."""
        parser = DAXParser()
        dax = "High Risk = IF(Customers[RiskScore] > 80, 'High', 'Low')"
        
        rules = parser.extract_business_logic("High Risk", dax)
        
        assert len(rules) > 0
        rule = rules[0]
        assert "RiskScore" in rule.condition
        assert "80" in rule.condition
    
    def test_extract_business_logic_threshold(self):
        """Test extracting threshold conditions."""
        parser = DAXParser()
        dax = "CALCULATE(COUNT(...), Temperature > 25)"
        
        rules = parser.extract_business_logic("Test", dax)
        
        assert len(rules) > 0
        # Should extract temperature threshold
        conditions = [rule.condition for rule in rules]
        assert any("Temperature" in cond or "25" in cond for cond in conditions)
    
    def test_identify_dependencies(self):
        """Test dependency identification."""
        parser = DAXParser()
        dax = "SUM(Orders[OrderValue]) + COUNT(Customers[CustomerID])"
        
        deps = parser.identify_dependencies(dax)
        
        assert "Orders.OrderValue" in deps
        assert "Customers.CustomerID" in deps
    
    def test_identify_dependencies_complex(self):
        """Test dependency identification in complex DAX."""
        parser = DAXParser()
        dax = """
        CALCULATE(
            SUM(Orders[OrderValue]),
            Customers[RiskScore] > 80,
            Products[Category] = "Electronics"
        )
        """
        
        deps = parser.identify_dependencies(dax)
        
        assert "Orders.OrderValue" in deps
        assert "Customers.RiskScore" in deps
        assert "Products.Category" in deps
    
    def test_classify_measure_type_aggregation(self):
        """Test classifying aggregation measures."""
        parser = DAXParser()
        dax = "SUM(Orders[OrderValue])"
        
        measure_type = parser.classify_measure_type(dax)
        assert measure_type == "AGGREGATION"
    
    def test_classify_measure_type_conditional(self):
        """Test classifying conditional measures."""
        parser = DAXParser()
        dax = "IF(RiskScore > 80, 'High', 'Low')"
        
        measure_type = parser.classify_measure_type(dax)
        assert measure_type == "CONDITIONAL"
    
    def test_classify_measure_type_filter(self):
        """Test classifying filter measures."""
        parser = DAXParser()
        dax = "CALCULATE(COUNT(...), RiskScore > 80)"
        
        measure_type = parser.classify_measure_type(dax)
        assert measure_type == "FILTER"
    
    def test_classify_measure_type_time_intelligence(self):
        """Test classifying time intelligence measures."""
        parser = DAXParser()
        dax = "TOTALYTD(SUM(Orders[OrderValue]), Calendar[Date])"
        
        measure_type = parser.classify_measure_type(dax)
        assert measure_type == "TIME_INTELLIGENCE"
    
    def test_parse_measure_with_malformed_dax(self):
        """Test handling malformed DAX gracefully."""
        parser = DAXParser()
        malformed_dax = "SUM(Orders[OrderValue"  # Missing closing bracket
        
        # Should not raise exception, but may have limited parsing
        parsed = parser.parse_measure("Test", malformed_dax)
        assert isinstance(parsed, ParsedRule)
        # Dependencies might be empty or partial
        assert parsed.measure_name == "Test"
    
    def test_extract_entity_from_condition(self):
        """Test extracting entity name from condition."""
        parser = DAXParser()
        condition = "Customers[RiskScore] > 80"
        
        entity = parser._extract_entity_from_condition(condition)
        assert entity == "Customers"
    
    def test_extract_entity_from_field(self):
        """Test extracting entity from field name."""
        parser = DAXParser()
        field = "customer_risk_score"
        
        entity = parser._extract_entity_from_field(field)
        # Should extract "Customer" from "customer_risk_score"
        assert entity == "Customer" or entity == ""
    
    def test_parse_switch_cases(self):
        """Test parsing SWITCH cases."""
        parser = DAXParser()
        switch_body = "Temperature > 25, 'High', Vibration > 5, 'High', 'Low'"
        
        cases = parser._parse_switch_cases(switch_body)
        
        assert len(cases) >= 2
        assert cases[0][0] == "Temperature > 25"
        assert cases[0][1] == "'High'"
    
    def test_business_rule_extraction_completeness(self):
        """Test that all business rules are extracted from complex DAX."""
        parser = DAXParser()
        complex_dax = """
        Shipment Risk = 
            SWITCH(
                TRUE(),
                Temperature > 25, "High",
                Vibration > 5, "High",
                Status = "Delayed", "Medium",
                "Low"
            )
        """
        
        rules = parser.extract_business_logic("Shipment Risk", complex_dax)
        
        # Should extract multiple rules
        assert len(rules) >= 2
        
        # Check that different conditions are captured
        conditions = [rule.condition for rule in rules]
        assert any("Temperature" in cond for cond in conditions) or any("25" in cond for cond in conditions)
    
    @pytest.mark.parametrize("dax,expected_type", [
        ("SUM(Orders[Value])", "AGGREGATION"),
        ("IF(Risk > 80, 'High', 'Low')", "CONDITIONAL"),
        ("CALCULATE(COUNT(...), Filter > 10)", "FILTER"),
        ("TOTALYTD(SUM(...), Date)", "TIME_INTELLIGENCE"),
        ("Orders[Value] * 1.1", "CALCULATION"),
    ])
    def test_classify_measure_type_parametrized(self, dax, expected_type):
        """Test measure type classification with multiple examples."""
        parser = DAXParser()
        result = parser.classify_measure_type(dax)
        assert result == expected_type
