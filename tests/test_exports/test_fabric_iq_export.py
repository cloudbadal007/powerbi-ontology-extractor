"""
Tests for FabricIQExporter.
"""

import json
import pytest

from powerbi_ontology.export.fabric_iq import FabricIQExporter
from powerbi_ontology.ontology_generator import Ontology, OntologyEntity, OntologyProperty


class TestFabricIQExporter:
    """Test FabricIQExporter class."""
    
    def test_init(self, sample_ontology):
        """Test exporter initialization."""
        exporter = FabricIQExporter(sample_ontology)
        assert exporter.ontology == sample_ontology
    
    def test_export(self, sample_ontology):
        """Test exporting to Fabric IQ format."""
        exporter = FabricIQExporter(sample_ontology)
        fabric_json = exporter.export()
        
        assert isinstance(fabric_json, dict)
        assert "ontologyItem" in fabric_json
        assert "version" in fabric_json
        assert "entities" in fabric_json
        assert "relationships" in fabric_json
        assert "businessRules" in fabric_json
    
    def test_export_required_fields(self, sample_ontology):
        """Test that all required fields are present."""
        exporter = FabricIQExporter(sample_ontology)
        fabric_json = exporter.export()
        
        required_fields = ["ontologyItem", "version", "source", "entities"]
        for field in required_fields:
            assert field in fabric_json
    
    def test_format_entity(self, sample_ontology):
        """Test formatting entity for Fabric IQ."""
        exporter = FabricIQExporter(sample_ontology)
        entity = sample_ontology.entities[0]
        
        formatted = exporter.format_entity(entity)
        
        assert isinstance(formatted, dict)
        assert formatted["name"] == entity.name
        assert "properties" in formatted
        assert "relationships" in formatted
    
    def test_format_entity_properties(self, sample_ontology):
        """Test that entity properties are correctly formatted."""
        exporter = FabricIQExporter(sample_ontology)
        entity = sample_ontology.entities[0]
        
        formatted = exporter.format_entity(entity)
        
        assert len(formatted["properties"]) == len(entity.properties)
        prop = formatted["properties"][0]
        assert "name" in prop
        assert "type" in prop
        assert "required" in prop
    
    def test_format_relationship(self, sample_ontology):
        """Test formatting relationship for Fabric IQ."""
        exporter = FabricIQExporter(sample_ontology)
        if sample_ontology.relationships:
            rel = sample_ontology.relationships[0]
            formatted = exporter.format_relationship(rel)
            
            assert isinstance(formatted, dict)
            assert "from" in formatted
            assert "to" in formatted
            assert "type" in formatted
    
    def test_format_business_rule(self, sample_ontology):
        """Test formatting business rule for Fabric IQ."""
        exporter = FabricIQExporter(sample_ontology)
        if sample_ontology.business_rules:
            rule = sample_ontology.business_rules[0]
            formatted = exporter.format_business_rule(rule)
            
            assert isinstance(formatted, dict)
            assert "name" in formatted
            assert "condition" in formatted
            assert "entity" in formatted
    
    def test_validate_export(self, sample_ontology):
        """Test validating Fabric IQ export."""
        exporter = FabricIQExporter(sample_ontology)
        fabric_json = exporter.export()
        
        is_valid = exporter.validate_export(fabric_json)
        assert is_valid is True
    
    def test_validate_export_missing_fields(self, sample_ontology):
        """Test validation fails for missing required fields."""
        exporter = FabricIQExporter(sample_ontology)
        invalid_json = {"name": "Test"}  # Missing required fields
        
        is_valid = exporter.validate_export(invalid_json)
        assert is_valid is False
    
    def test_generate_semantic_bindings(self, sample_ontology):
        """Test generating semantic bindings."""
        exporter = FabricIQExporter(sample_ontology)
        schema_mappings = {
            "Shipment": "OneLake.supply_chain.shipments",
            "Customer": "OneLake.supply_chain.customers"
        }
        
        bindings = exporter.generate_semantic_bindings(schema_mappings)
        
        assert isinstance(bindings, dict)
        assert "Shipment" in bindings
        assert "Customer" in bindings
    
    def test_export_contract(self, sample_ontology):
        """Test exporting contract to Fabric IQ format."""
        from powerbi_ontology.contract_builder import ContractBuilder
        
        builder = ContractBuilder(sample_ontology)
        contract = builder.build_contract("TestAgent", {"read": ["Shipment"]})
        
        exporter = FabricIQExporter(sample_ontology)
        contract_json = exporter.export_contract(contract)
        
        assert isinstance(contract_json, str)
        assert "TestAgent" in contract_json
    
    def test_extract_triggers(self, sample_ontology):
        """Test extracting trigger actions from business rules."""
        exporter = FabricIQExporter(sample_ontology)
        
        from powerbi_ontology.ontology_generator import BusinessRule
        
        rule = BusinessRule(
            name="NotifyRule",
            entity="Shipment",
            condition="Temperature > 25",
            action="notify_operations"
        )
        
        triggers = exporter._extract_triggers(rule)
        assert isinstance(triggers, list)
        # May include "NotifyOperations" if action contains "notify"
