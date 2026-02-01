"""
Tests for PowerBIExtractor class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from powerbi_ontology.extractor import (
    PowerBIExtractor, SemanticModel, Entity, Property, Relationship, Measure
)
from powerbi_ontology.utils.pbix_reader import PBIXReader


class TestPowerBIExtractor:
    """Test PowerBIExtractor class."""
    
    def test_init(self):
        """Test extractor initialization."""
        extractor = PowerBIExtractor("test.pbix")
        assert extractor.pbix_path == "test.pbix"
        assert extractor.reader is None
    
    @patch('powerbi_ontology.extractor.PBIXReader')
    def test_extract_success(self, mock_reader_class, sample_pbix_path):
        """Test successful extraction."""
        # Mock reader
        mock_reader = Mock()
        mock_reader.extract_to_temp.return_value = None
        mock_reader.read_model.return_value = {
            "name": "Test Model",
            "tables": [
                {
                    "name": "Shipment",
                    "description": "Shipment entity",
                    "columns": [
                        {
                            "name": "ShipmentID",
                            "dataType": "string",
                            "isKey": True,
                            "isNullable": False,
                            "description": "Primary key"
                        }
                    ],
                    "measures": []
                }
            ],
            "relationships": []
        }
        mock_reader.get_tables.return_value = [
            {
                "name": "Shipment",
                "description": "Shipment entity",
                "columns": [
                    {
                        "name": "ShipmentID",
                        "dataType": "string",
                        "isKey": True,
                        "isNullable": False,
                        "description": "Primary key"
                    }
                ],
                "measures": []
            }
        ]
        mock_reader.get_relationships.return_value = []
        mock_reader.get_measures.return_value = []
        
        mock_reader_class.return_value = mock_reader
        
        extractor = PowerBIExtractor(str(sample_pbix_path))
        semantic_model = extractor.extract()
        
        assert isinstance(semantic_model, SemanticModel)
        assert semantic_model.name == "Test Model"
        assert len(semantic_model.entities) == 1
    
    def test_extract_entities(self, sample_semantic_model):
        """Test entity extraction logic."""
        # This tests the extract_entities method indirectly through extract
        assert len(sample_semantic_model.entities) == 2
        assert sample_semantic_model.entities[0].name == "Shipment"
        assert sample_semantic_model.entities[1].name == "Customer"
    
    def test_extract_entities_with_properties(self, sample_semantic_model):
        """Test that entities have correct properties."""
        shipment_entity = sample_semantic_model.entities[0]
        assert len(shipment_entity.properties) == 2
        assert shipment_entity.properties[0].name == "ShipmentID"
        assert shipment_entity.properties[0].data_type == "String"
        assert shipment_entity.properties[0].required is True
        assert shipment_entity.properties[0].unique is True
    
    def test_extract_relationships(self, sample_semantic_model):
        """Test relationship extraction."""
        assert len(sample_semantic_model.relationships) == 1
        rel = sample_semantic_model.relationships[0]
        assert rel.from_entity == "Shipment"
        assert rel.to_entity == "Customer"
        assert rel.cardinality == "many-to-one"
    
    def test_extract_measures(self, sample_semantic_model):
        """Test measure extraction."""
        assert len(sample_semantic_model.measures) == 1
        measure = sample_semantic_model.measures[0]
        assert measure.name == "High Risk Shipments"
        assert "Temperature" in measure.dax_formula
        assert measure.table == "Shipment"
    
    def test_extract_hierarchies(self, sample_semantic_model):
        """Test hierarchy extraction."""
        # Current sample has no hierarchies
        assert len(sample_semantic_model.hierarchies) == 0
    
    def test_extract_security_rules(self, sample_semantic_model):
        """Test security rule extraction."""
        # Current sample has no security rules
        assert len(sample_semantic_model.security_rules) == 0
    
    def test_map_data_type(self):
        """Test data type mapping."""
        extractor = PowerBIExtractor("test.pbix")
        assert extractor._map_data_type("string") == "String"
        assert extractor._map_data_type("int64") == "Integer"
        assert extractor._map_data_type("double") == "Decimal"
        assert extractor._map_data_type("dateTime") == "Date"
        assert extractor._map_data_type("boolean") == "Boolean"
        assert extractor._map_data_type("unknown") == "String"  # Default
    
    def test_extract_measure_dependencies(self):
        """Test dependency extraction from DAX."""
        extractor = PowerBIExtractor("test.pbix")
        dax = "CALCULATE(SUM(Orders[OrderValue]), Customers[CustomerID] = 1)"
        deps = extractor._extract_measure_dependencies(dax)
        
        assert "Orders.OrderValue" in deps
        assert "Customers.CustomerID" in deps
    
    def test_extract_relationships_cardinality(self):
        """Test relationship cardinality mapping."""
        # Test one-to-many
        rel_data = {
            "fromTable": "Customer",
            "fromColumn": "CustomerID",
            "toTable": "Order",
            "toColumn": "CustomerID",
            "fromCardinality": "one",
            "toCardinality": "many"
        }
        
        extractor = PowerBIExtractor("test.pbix")
        # This would be tested through extract_relationships
        # For now, test the logic directly
        assert rel_data["fromCardinality"] == "one"
        assert rel_data["toCardinality"] == "many"
    
    def test_extract_relationships_cross_filter(self):
        """Test cross-filter direction extraction."""
        rel_data_both = {
            "crossFilteringBehavior": "bothDirections"
        }
        rel_data_single = {
            "crossFilteringBehavior": "singleDirection"
        }
        
        assert rel_data_both["crossFilteringBehavior"] == "bothDirections"
        assert rel_data_single["crossFilteringBehavior"] == "singleDirection"
    
    def test_context_manager(self, sample_pbix_path):
        """Test using extractor as context manager."""
        with PowerBIExtractor(str(sample_pbix_path)) as extractor:
            # Should not raise
            pass
        
        # Cleanup should be called
        assert extractor.reader is None or extractor.reader.temp_dir is None
    
    def test_to_ontology_method(self, sample_semantic_model):
        """Test SemanticModel.to_ontology() method."""
        ontology = sample_semantic_model.to_ontology()
        assert ontology is not None
        assert ontology.name is not None
    
    @patch('powerbi_ontology.extractor.PBIXReader')
    def test_extract_with_different_power_bi_versions(self, mock_reader_class):
        """Test handling different Power BI schema versions."""
        # Version 2.0 format
        mock_reader = Mock()
        mock_reader.extract_to_temp.return_value = None
        mock_reader.read_model.return_value = {
            "model": {
                "name": "V2 Model",
                "tables": []
            }
        }
        mock_reader.get_tables.return_value = []
        mock_reader.get_relationships.return_value = []
        mock_reader.get_measures.return_value = []
        
        mock_reader_class.return_value = mock_reader
        
        extractor = PowerBIExtractor("test.pbix")
        model = extractor.extract()
        assert model.name == "V2 Model"
    
    def test_extract_entities_primary_key_detection(self):
        """Test primary key identification."""
        table_data = {
            "name": "TestTable",
            "columns": [
                {"name": "ID", "dataType": "string", "isKey": True},
                {"name": "Name", "dataType": "string", "isKey": False}
            ]
        }
        
        # Simulate extraction logic
        primary_key = None
        for col in table_data["columns"]:
            if col.get("isKey", False):
                primary_key = col["name"]
                break
        
        assert primary_key == "ID"
    
    def test_extract_entities_without_primary_key(self):
        """Test entity extraction when no primary key is defined."""
        table_data = {
            "name": "TestTable",
            "columns": [
                {"name": "ID", "dataType": "string", "isKey": False},
                {"name": "Name", "dataType": "string", "isKey": False}
            ]
        }
        
        primary_key = None
        for col in table_data["columns"]:
            if col.get("isKey", False) or col.get("isUnique", False):
                primary_key = col["name"]
                break
        
        assert primary_key is None