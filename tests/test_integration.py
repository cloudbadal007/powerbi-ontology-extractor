"""
Integration tests for complete workflows.
"""

import json
import pytest
from pathlib import Path

from powerbi_ontology import PowerBIExtractor, OntologyGenerator, SemanticAnalyzer, ContractBuilder, SchemaMapper
from powerbi_ontology.export import FabricIQExporter, OntoGuardExporter
from powerbi_ontology.schema_mapper import ValidationResult, DriftReport
from powerbi_ontology.ontology_generator import OntologyEntity, OntologyProperty


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_workflow_pbix_to_ontology(self, sample_pbix_path, temp_dir):
        """Test complete workflow: .pbix → ontology → export."""
        # Step 1: Extract
        extractor = PowerBIExtractor(str(sample_pbix_path))
        semantic_model = extractor.extract()
        
        assert semantic_model is not None
        assert len(semantic_model.entities) > 0
        
        # Step 2: Generate ontology
        generator = OntologyGenerator(semantic_model)
        ontology = generator.generate()
        
        assert ontology is not None
        assert len(ontology.entities) > 0
        
        # Step 3: Export
        fabric_exporter = FabricIQExporter(ontology)
        fabric_json = fabric_exporter.export()
        
        assert isinstance(fabric_json, dict)
        assert "entities" in fabric_json

    def test_complete_workflow_pbip_tmdl_to_ontology(self, temp_dir):
        """Test complete workflow for PBIP/TMDL project input."""
        project_dir = temp_dir / "InventoryProject"
        tables_dir = project_dir / "definition" / "tables"
        tables_dir.mkdir(parents=True)

        (project_dir / "InventoryProject.pbip").write_text("{}", encoding="utf-8")
        (tables_dir / "Shipment.tmdl").write_text(
            """
table Shipment
    column ShipmentID
        dataType: string
    column Temperature
        dataType: double
    measure High Risk Shipments = CALCULATE(COUNT(Shipment[ShipmentID]), Shipment[Temperature] > 25)
""".strip(),
            encoding="utf-8",
        )
        (tables_dir / "Customer.tmdl").write_text(
            """
table Customer
    column CustomerID
        dataType: string
""".strip(),
            encoding="utf-8",
        )
        (project_dir / "definition" / "relationships.tmdl").write_text(
            """
relationship ShipmentCustomer
    fromColumn: Shipment[CustomerID]
    toColumn: Customer[CustomerID]
""".strip(),
            encoding="utf-8",
        )

        extractor = PowerBIExtractor(str(project_dir / "InventoryProject.pbip"))
        semantic_model = extractor.extract()

        assert semantic_model is not None
        assert len(semantic_model.entities) == 2
        assert len(semantic_model.relationships) == 1

        ontology = OntologyGenerator(semantic_model).generate()
        assert ontology is not None
        assert len(ontology.entities) == 2
    
    def test_multi_dashboard_analysis(self, multiple_semantic_models):
        """Test analyzing multiple dashboards."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        
        # Detect conflicts
        conflicts = analyzer.detect_conflicts()
        assert isinstance(conflicts, list)
        
        # Calculate debt
        debt_report = analyzer.calculate_semantic_debt()
        assert debt_report.total_cost >= 0
        
        # Suggest canonical definitions
        canonical_defs = analyzer.suggest_canonical_definitions()
        assert isinstance(canonical_defs, list)
    
    def test_semantic_debt_calculation(self, multiple_semantic_models):
        """Test semantic debt calculation across dashboards."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        debt_report = analyzer.calculate_semantic_debt()
        
        # Should calculate cost based on conflicts
        assert debt_report.cost_per_conflict == 50000.0
        assert debt_report.total_cost == (
            debt_report.total_conflicts * debt_report.cost_per_conflict +
            debt_report.total_duplications * 10000.0
        )
    
    def test_end_to_end_agent_deployment(self, sample_ontology, mock_database_schema):
        """Test end-to-end agent deployment scenario."""
        # Step 1: Create schema binding
        mapper = SchemaMapper(sample_ontology, "test_db")
        binding = mapper.create_binding("Shipment", "dbo.shipments")
        
        # Step 2: Validate binding
        result = mapper.validate_binding(binding)
        assert isinstance(result, ValidationResult)
        
        # Step 3: Detect drift
        drift = mapper.detect_drift(binding, mock_database_schema)
        assert isinstance(drift, DriftReport)
        
        # Step 4: Create contract
        contract_builder = ContractBuilder(sample_ontology)
        contract = contract_builder.build_contract(
            "TestAgent",
            {
                "read": ["Shipment"],
                "write": {"Shipment": ["Status"]},
                "execute": ["RerouteShipment"]
            }
        )
        
        assert contract.agent_name == "TestAgent"
        assert len(contract.permissions.read_entities) > 0
        
        # Step 5: Export contracts
        fabric_exporter = FabricIQExporter(sample_ontology)
        fabric_json = fabric_exporter.export()
        
        ontoguard_exporter = OntoGuardExporter(sample_ontology)
        ontoguard_json = ontoguard_exporter.export()
        
        assert isinstance(fabric_json, dict)
        assert isinstance(ontoguard_json, dict)
    
    def test_schema_drift_prevention_workflow(self, sample_ontology):
        """
        Test the critical $4.6M mistake prevention workflow.
        """
        # Create binding expecting warehouse_location
        mapper = SchemaMapper(sample_ontology, "test_db")
        
        # Add Warehouse entity if not present
        if not any(e.name == "Warehouse" for e in sample_ontology.entities):
            warehouse_entity = OntologyEntity(
                name="Warehouse",
                properties=[OntologyProperty(name="Location", data_type="String")]
            )
            sample_ontology.entities.append(warehouse_entity)
        
        binding = mapper.create_binding("Warehouse", "warehouses")
        binding.property_mappings["Location"] = "warehouse_location"
        
        # Simulate schema change (column renamed)
        drifted_schema = {
            "warehouse_id": "GUID",
            "facility_id": "String",  # warehouse_location was renamed!
            "status": "String"
        }
        
        # Detect drift
        drift = mapper.detect_drift(binding, drifted_schema)
        
        # Should detect CRITICAL drift
        assert drift.severity == "CRITICAL"
        assert "warehouse_location" in drift.missing_columns
        
        # Agent should stop execution
        if drift.severity == "CRITICAL":
            # This prevents the $4.6M mistake!
            assert len(drift.missing_columns) > 0
            assert drift.message is not None
    
    def test_ontology_generation_from_real_structure(self, sample_semantic_model):
        """Test ontology generation from realistic semantic model structure."""
        generator = OntologyGenerator(sample_semantic_model)
        ontology = generator.generate()
        
        # Verify 70% auto-generation
        assert len(ontology.entities) == len(sample_semantic_model.entities)
        assert len(ontology.relationships) == len(sample_semantic_model.relationships)
        
        # Business rules should be generated from DAX
        assert isinstance(ontology.business_rules, list)
    
    def test_export_all_formats(self, sample_ontology, temp_dir):
        """Test exporting to all supported formats."""
        # Fabric IQ
        fabric_exporter = FabricIQExporter(sample_ontology)
        fabric_json = fabric_exporter.export()
        assert isinstance(fabric_json, dict)
        
        # OntoGuard
        ontoguard_exporter = OntoGuardExporter(sample_ontology)
        ontoguard_json = ontoguard_exporter.export()
        assert isinstance(ontoguard_json, dict)
        
        # JSON Schema
        from powerbi_ontology.export.json_schema import JSONSchemaExporter
        json_schema_exporter = JSONSchemaExporter(sample_ontology)
        json_schema = json_schema_exporter.export()
        assert isinstance(json_schema, dict)
        
        # OWL
        from powerbi_ontology.export.owl import OWLExporter
        owl_exporter = OWLExporter(sample_ontology)
        owl_xml = owl_exporter.export(format="xml")
        assert isinstance(owl_xml, str)
        assert len(owl_xml) > 0
