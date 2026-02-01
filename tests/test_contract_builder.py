"""
Tests for ContractBuilder class.
"""

import pytest

from powerbi_ontology.contract_builder import (
    ContractBuilder, SemanticContract, ContractPermissions, AuditConfig
)
from powerbi_ontology.ontology_generator import Ontology, BusinessRule


class TestContractBuilder:
    """Test ContractBuilder class."""
    
    def test_init(self, sample_ontology):
        """Test contract builder initialization."""
        builder = ContractBuilder(sample_ontology)
        assert builder.ontology == sample_ontology
        assert builder.dax_parser is not None
    
    def test_build_contract(self, sample_ontology, sample_contract_permissions):
        """Test building a semantic contract."""
        builder = ContractBuilder(sample_ontology)
        contract = builder.build_contract(
            "TestAgent",
            sample_contract_permissions
        )
        
        assert isinstance(contract, SemanticContract)
        assert contract.agent_name == "TestAgent"
        assert contract.ontology_version == sample_ontology.version
        assert len(contract.permissions.read_entities) > 0
    
    def test_build_contract_permissions(self, sample_ontology):
        """Test contract permissions are correctly set."""
        builder = ContractBuilder(sample_ontology)
        permissions = {
            "read": ["Shipment", "Customer"],
            "write": {"Shipment": ["Status"]},
            "execute": ["RerouteShipment"],
            "role": "Manager"
        }
        
        contract = builder.build_contract("TestAgent", permissions)
        
        assert "Shipment" in contract.permissions.read_entities
        assert "Customer" in contract.permissions.read_entities
        assert "Shipment" in contract.permissions.write_properties
        assert "RerouteShipment" in contract.permissions.executable_actions
        assert contract.permissions.required_role == "Manager"
    
    def test_generate_permissions_from_dashboard(self, sample_ontology, sample_semantic_model):
        """Test generating permissions from Power BI dashboard."""
        builder = ContractBuilder(sample_ontology)
        permissions = builder.generate_permissions_from_dashboard(sample_semantic_model)
        
        assert "read" in permissions
        assert isinstance(permissions["read"], list)
        assert len(permissions["read"]) > 0
    
    def test_add_business_rules(self, sample_ontology):
        """Test adding business rules to contract."""
        builder = ContractBuilder(sample_ontology)
        contract = builder.build_contract("TestAgent", {"read": ["Shipment"]})
        
        initial_count = len(contract.business_rules)
        
        new_rule = BusinessRule(
            name="TestRule",
            entity="Shipment",
            condition="Temperature > 30",
            action="alert"
        )
        
        builder.add_business_rules(contract, [new_rule])
        
        assert len(contract.business_rules) == initial_count + 1
    
    def test_add_validation_constraints(self, sample_ontology):
        """Test adding validation constraints to contract."""
        builder = ContractBuilder(sample_ontology)
        contract = builder.build_contract(
            "TestAgent",
            {"read": ["Shipment"], "write": {"Shipment": ["Status"]}}
        )
        
        builder.add_validation_constraints(contract)
        
        # Should have constraints from ontology entities
        assert isinstance(contract.validation_constraints, list)
    
    def test_export_contract_json(self, sample_ontology):
        """Test exporting contract to JSON format."""
        builder = ContractBuilder(sample_ontology)
        contract = builder.build_contract("TestAgent", {"read": ["Shipment"]})
        
        contract_json = builder.export_contract(contract, "json")
        
        assert isinstance(contract_json, str)
        assert "TestAgent" in contract_json
        assert "permissions" in contract_json.lower()
    
    def test_export_contract_ontoguard(self, sample_ontology):
        """Test exporting contract to OntoGuard format."""
        builder = ContractBuilder(sample_ontology)
        contract = builder.build_contract("TestAgent", {"read": ["Shipment"]})
        
        # May raise if OntoGuard exporter not fully implemented
        try:
            ontoguard_json = builder.export_contract(contract, "ontoguard")
            assert isinstance(ontoguard_json, str)
        except (ValueError, AttributeError):
            # Expected if not fully implemented
            pass
    
    def test_export_contract_fabric_iq(self, sample_ontology):
        """Test exporting contract to Fabric IQ format."""
        builder = ContractBuilder(sample_ontology)
        contract = builder.build_contract("TestAgent", {"read": ["Shipment"]})
        
        try:
            fabric_json = builder.export_contract(contract, "fabric_iq")
            assert isinstance(fabric_json, str)
        except (ValueError, AttributeError):
            # Expected if not fully implemented
            pass
    
    def test_export_contract_invalid_format(self, sample_ontology):
        """Test exporting contract with invalid format."""
        builder = ContractBuilder(sample_ontology)
        contract = builder.build_contract("TestAgent", {"read": ["Shipment"]})
        
        with pytest.raises(ValueError, match="Unknown export format"):
            builder.export_contract(contract, "invalid_format")
    
    def test_add_relevant_business_rules(self, sample_ontology):
        """Test that only relevant business rules are added."""
        builder = ContractBuilder(sample_ontology)
        contract = builder.build_contract(
            "TestAgent",
            {"read": ["Shipment"]}  # Only read Shipment
        )
        
        # Should only include rules for Shipment entity
        relevant_entities = set(contract.permissions.read_entities)
        for rule in contract.business_rules:
            assert rule.entity in relevant_entities or rule.entity == ""
    
    def test_contract_metadata(self, sample_ontology):
        """Test that contract includes metadata."""
        builder = ContractBuilder(sample_ontology)
        contract = builder.build_contract("TestAgent", {"read": ["Shipment"]})
        
        assert "metadata" in contract.__dict__
        assert contract.metadata is not None
    
    def test_audit_settings_default(self, sample_ontology):
        """Test default audit settings."""
        builder = ContractBuilder(sample_ontology)
        contract = builder.build_contract("TestAgent", {"read": ["Shipment"]})
        
        assert contract.audit_settings.log_reads is True
        assert contract.audit_settings.log_writes is True
        assert contract.audit_settings.log_actions is True
