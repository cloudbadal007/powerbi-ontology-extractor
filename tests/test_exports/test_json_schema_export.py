"""
Tests for JSONSchemaExporter.
"""

import pytest

from powerbi_ontology.export.json_schema import JSONSchemaExporter


class TestJSONSchemaExporter:
    """Test JSONSchemaExporter class."""
    
    def test_init(self, sample_ontology):
        """Test exporter initialization."""
        exporter = JSONSchemaExporter(sample_ontology)
        assert exporter.ontology == sample_ontology
    
    def test_export(self, sample_ontology):
        """Test exporting to JSON Schema format."""
        exporter = JSONSchemaExporter(sample_ontology)
        schema = exporter.export()
        
        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert "definitions" in schema
    
    def test_export_has_entity_definitions(self, sample_ontology):
        """Test that entity definitions are included."""
        exporter = JSONSchemaExporter(sample_ontology)
        schema = exporter.export()
        
        assert "definitions" in schema
        assert len(schema["definitions"]) > 0
    
    def test_entity_to_json_schema(self, sample_ontology):
        """Test converting entity to JSON Schema."""
        exporter = JSONSchemaExporter(sample_ontology)
        entity = sample_ontology.entities[0]
        
        entity_schema = exporter._entity_to_json_schema(entity)
        
        assert isinstance(entity_schema, dict)
        assert entity_schema["type"] == "object"
        assert "properties" in entity_schema
    
    def test_map_type_to_json_schema(self, sample_ontology):
        """Test mapping ontology types to JSON Schema types."""
        exporter = JSONSchemaExporter(sample_ontology)
        
        assert exporter._map_type_to_json_schema("String") == "string"
        assert exporter._map_type_to_json_schema("Integer") == "integer"
        assert exporter._map_type_to_json_schema("Decimal") == "number"
        assert exporter._map_type_to_json_schema("Boolean") == "boolean"
        assert exporter._map_type_to_json_schema("Date") == "string"
        assert exporter._map_type_to_json_schema("Unknown") == "string"  # Default
