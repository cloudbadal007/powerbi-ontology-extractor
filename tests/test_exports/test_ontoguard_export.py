"""
Tests for OntoGuardExporter.
"""

import pytest

from powerbi_ontology.export.ontoguard import OntoGuardExporter
from powerbi_ontology.ontology_generator import Ontology, OntologyEntity, OntologyProperty, Constraint


class TestOntoGuardExporter:
    """Test OntoGuardExporter class."""
    
    def test_init(self, sample_ontology):
        """Test exporter initialization."""
        exporter = OntoGuardExporter(sample_ontology)
        assert exporter.ontology == sample_ontology
    
    def test_export(self, sample_ontology):
        """Test exporting to OntoGuard format."""
        exporter = OntoGuardExporter(sample_ontology)
        ontoguard_json = exporter.export()
        
        assert isinstance(ontoguard_json, dict)
        assert "ontology" in ontoguard_json
        assert "validationRules" in ontoguard_json
        assert "schemaBindings" in ontoguard_json
        assert "firewallRules" in ontoguard_json
    
    def test_generate_validation_rules(self, sample_ontology):
        """Test generating validation rules."""
        exporter = OntoGuardExporter(sample_ontology)
        rules = exporter.generate_validation_rules()
        
        assert isinstance(rules, list)
        # May have rules if ontology has constraints
    
    def test_generate_validation_rules_with_constraints(self):
        """Test validation rules from ontology constraints."""
        # Create ontology with constraints
        entity = OntologyEntity(
            name="Shipment",
            properties=[
                OntologyProperty(
                    name="Temperature",
                    data_type="Decimal",
                    constraints=[
                        Constraint(
                            type="range",
                            value={"min": -20, "max": 40},
                            message="Temperature must be between -20 and 40"
                        )
                    ]
                )
            ]
        )
        
        ontology = Ontology(
            name="TestOntology",
            entities=[entity]
        )
        
        exporter = OntoGuardExporter(ontology)
        rules = exporter.generate_validation_rules()
        
        assert len(rules) > 0
        temp_rule = next((r for r in rules if "Temperature" in r.get("property", "")), None)
        if temp_rule:
            assert temp_rule["validation"]["type"] == "range"
    
    def test_generate_schema_bindings(self, sample_ontology):
        """Test generating schema bindings."""
        exporter = OntoGuardExporter(sample_ontology)
        bindings = exporter.generate_schema_bindings()
        
        assert isinstance(bindings, dict)
        # Should have bindings for each entity
        assert len(bindings) > 0
    
    def test_generate_schema_bindings_expected_columns(self, sample_ontology):
        """Test that schema bindings include expected columns."""
        exporter = OntoGuardExporter(sample_ontology)
        bindings = exporter.generate_schema_bindings()
        
        for entity_name, binding in bindings.items():
            assert "expectedColumns" in binding
            assert isinstance(binding["expectedColumns"], list)
            assert len(binding["expectedColumns"]) > 0
    
    def test_generate_firewall_config(self, sample_ontology):
        """Test generating firewall configuration."""
        exporter = OntoGuardExporter(sample_ontology)
        firewall_rules = exporter.generate_firewall_config()
        
        assert isinstance(firewall_rules, list)
        # May have rules if ontology has risk/alert business rules
    
    def test_generate_firewall_config_with_risk_rules(self):
        """Test firewall rules from risk-related business rules."""
        from powerbi_ontology.ontology_generator import BusinessRule, Ontology
        
        rule = BusinessRule(
            name="HighRiskShipment",
            entity="Shipment",
            condition="Temperature > 25",
            action="alert_operations"
        )
        
        ontology = Ontology(
            name="TestOntology",
            business_rules=[rule]
        )
        
        exporter = OntoGuardExporter(ontology)
        firewall_rules = exporter.generate_firewall_config()
        
        # Should generate firewall rule for risk-related business rule
        assert len(firewall_rules) > 0
        risk_rule = next((r for r in firewall_rules if "risk" in r.get("name", "").lower()), None)
        if risk_rule:
            assert "trigger" in risk_rule
            assert "checks" in risk_rule
    
    def test_export_contract(self, sample_ontology):
        """Test exporting contract to OntoGuard format."""
        from powerbi_ontology.contract_builder import ContractBuilder
        
        builder = ContractBuilder(sample_ontology)
        contract = builder.build_contract("TestAgent", {"read": ["Shipment"]})
        
        exporter = OntoGuardExporter(sample_ontology)
        contract_json = exporter.export_contract(contract)
        
        assert isinstance(contract_json, str)
        assert "TestAgent" in contract_json or "agentContract" in contract_json.lower()
