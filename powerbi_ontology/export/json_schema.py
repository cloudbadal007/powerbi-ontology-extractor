"""
JSON Schema Exporter

Exports ontologies to JSON Schema format (draft-07).
"""

import logging
from typing import Dict

from powerbi_ontology.ontology_generator import Ontology, OntologyEntity

logger = logging.getLogger(__name__)


class JSONSchemaExporter:
    """
    Exports ontologies to JSON Schema format.
    
    Uses JSON Schema draft-07 standard for maximum compatibility.
    """

    def __init__(self, ontology: Ontology):
        """
        Initialize JSON Schema exporter.
        
        Args:
            ontology: Ontology to export
        """
        self.ontology = ontology

    def export(self) -> Dict:
        """
        Export ontology to JSON Schema format.
        
        Returns:
            Dictionary in JSON Schema format
        """
        logger.info(f"Exporting ontology '{self.ontology.name}' to JSON Schema format")
        
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": f"https://example.com/ontologies/{self.ontology.name}.schema.json",
            "title": self.ontology.name,
            "description": f"Ontology extracted from {self.ontology.source}",
            "version": self.ontology.version,
            "definitions": {}
        }
        
        # Add entity definitions
        for entity in self.ontology.entities:
            schema["definitions"][entity.name] = self._entity_to_json_schema(entity)
        
        # Add root schema with all entities
        schema["properties"] = {
            entity.name: {"$ref": f"#/definitions/{entity.name}"}
            for entity in self.ontology.entities
        }
        
        return schema

    def _entity_to_json_schema(self, entity: OntologyEntity) -> Dict:
        """Convert entity to JSON Schema."""
        properties = {}
        required = []
        
        for prop in entity.properties:
            prop_schema = {
                "type": self._map_type_to_json_schema(prop.data_type),
                "description": prop.description
            }
            
            # Add constraints
            for constraint in prop.constraints:
                if constraint.type == "range":
                    if isinstance(constraint.value, dict):
                        if "min" in constraint.value:
                            prop_schema["minimum"] = constraint.value["min"]
                        if "max" in constraint.value:
                            prop_schema["maximum"] = constraint.value["max"]
                elif constraint.type == "enum":
                    prop_schema["enum"] = constraint.value
                elif constraint.type == "regex":
                    prop_schema["pattern"] = constraint.value
            
            properties[prop.name] = prop_schema
            
            if prop.required:
                required.append(prop.name)
        
        schema = {
            "type": "object",
            "description": entity.description,
            "properties": properties
        }
        
        if required:
            schema["required"] = required
        
        return schema

    def _map_type_to_json_schema(self, data_type: str) -> str:
        """Map ontology data type to JSON Schema type."""
        type_mapping = {
            "String": "string",
            "Integer": "integer",
            "Decimal": "number",
            "Date": "string",  # JSON Schema uses string for dates
            "Boolean": "boolean"
        }
        return type_mapping.get(data_type, "string")
