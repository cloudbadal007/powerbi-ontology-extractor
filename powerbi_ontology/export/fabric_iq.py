"""
Microsoft Fabric IQ Exporter

Exports ontologies to Microsoft Fabric IQ format.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from powerbi_ontology.ontology_generator import Ontology, OntologyEntity, OntologyRelationship, BusinessRule

logger = logging.getLogger(__name__)


class FabricIQExporter:
    """
    Exports ontologies to Microsoft Fabric IQ format.
    
    Fabric IQ uses a specific JSON schema for ontologies.
    """

    def __init__(self, ontology: Ontology):
        """
        Initialize Fabric IQ exporter.
        
        Args:
            ontology: Ontology to export
        """
        self.ontology = ontology

    def export(self) -> Dict:
        """
        Export ontology to Fabric IQ JSON format.
        
        Returns:
            Dictionary in Fabric IQ format
        """
        logger.info(f"Exporting ontology '{self.ontology.name}' to Fabric IQ format")
        
        fabric_iq = {
            "ontologyItem": f"{self.ontology.name}_v{self.ontology.version}",
            "version": self.ontology.version,
            "source": self.ontology.source,
            "extractedDate": datetime.now().isoformat() + "Z",
            "entities": [self.format_entity(entity) for entity in self.ontology.entities],
            "relationships": [
                self.format_relationship(rel) for rel in self.ontology.relationships
            ],
            "businessRules": [
                self.format_business_rule(rule) for rule in self.ontology.business_rules
            ],
            "dataBindings": self._generate_data_bindings(),
            "metadata": self.ontology.metadata
        }
        
        # Validate export
        if self.validate_export(fabric_iq):
            logger.info("Fabric IQ export validated successfully")
        else:
            logger.warning("Fabric IQ export validation failed")
        
        return fabric_iq

    def format_entity(self, entity: OntologyEntity) -> Dict:
        """
        Format entity for Fabric IQ.
        
        Args:
            entity: OntologyEntity to format
            
        Returns:
            Dictionary in Fabric IQ entity format
        """
        return {
            "name": entity.name,
            "description": entity.description,
            "entityType": entity.entity_type,
            "properties": [
                {
                    "name": prop.name,
                    "type": prop.data_type,
                    "required": prop.required,
                    "unique": prop.unique,
                    "description": prop.description,
                    "constraints": [
                        {
                            "type": constraint.type,
                            "value": constraint.value,
                            "message": constraint.message
                        }
                        for constraint in prop.constraints
                    ]
                }
                for prop in entity.properties
            ],
            "relationships": [
                {
                    "type": rel.relationship_type,
                    "target": rel.to_entity,
                    "cardinality": rel.cardinality
                }
                for rel in self.ontology.relationships
                if rel.from_entity == entity.name
            ],
            "source": entity.source_table
        }

    def format_relationship(self, rel: OntologyRelationship) -> Dict:
        """
        Format relationship for Fabric IQ.
        
        Args:
            rel: OntologyRelationship to format
            
        Returns:
            Dictionary in Fabric IQ relationship format
        """
        return {
            "from": rel.from_entity,
            "fromProperty": rel.from_property,
            "to": rel.to_entity,
            "toProperty": rel.to_property,
            "type": rel.relationship_type,
            "cardinality": rel.cardinality,
            "description": rel.description
        }

    def format_business_rule(self, rule: BusinessRule) -> Dict:
        """
        Format business rule for Fabric IQ.
        
        Args:
            rule: BusinessRule to format
            
        Returns:
            Dictionary in Fabric IQ business rule format
        """
        return {
            "name": rule.name,
            "source": f"DAX: {rule.source_measure}" if rule.source_measure else "Manual",
            "entity": rule.entity,
            "condition": rule.condition,
            "action": rule.action,
            "classification": rule.classification,
            "triggers": self._extract_triggers(rule),
            "description": rule.description,
            "priority": rule.priority
        }

    def generate_semantic_bindings(self, schema_mappings: Dict) -> Dict:
        """
        Generate semantic bindings for OneLake.
        
        Args:
            schema_mappings: Dictionary of entity -> physical source mappings
            
        Returns:
            Dictionary of data bindings
        """
        bindings = {}
        for entity_name, physical_source in schema_mappings.items():
            entity = next(
                (e for e in self.ontology.entities if e.name == entity_name),
                None
            )
            if entity:
                bindings[entity_name] = {
                    "source": physical_source,
                    "mapping": {
                        prop.name: prop.name  # Default mapping
                        for prop in entity.properties
                    }
                }
        return bindings

    def validate_export(self, fabric_iq_json: Dict) -> bool:
        """
        Validate Fabric IQ export against schema.
        
        Args:
            fabric_iq_json: Fabric IQ JSON to validate
            
        Returns:
            True if valid
        """
        required_fields = ["ontologyItem", "version", "source", "entities"]
        for field in required_fields:
            if field not in fabric_iq_json:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate entities
        if not isinstance(fabric_iq_json["entities"], list):
            logger.error("Entities must be a list")
            return False
        
        for entity in fabric_iq_json["entities"]:
            if "name" not in entity:
                logger.error("Entity missing 'name' field")
                return False
        
        return True

    def export_contract(self, contract) -> str:
        """Export semantic contract to Fabric IQ format."""
        import json
        # Convert contract to Fabric IQ format
        contract_json = {
            "agentContract": contract.agent_name,
            "ontologyVersion": contract.ontology_version,
            "permissions": {
                "readEntities": contract.permissions.read_entities,
                "writeProperties": contract.permissions.write_properties,
                "executableActions": contract.permissions.executable_actions
            },
            "businessRules": [
                {
                    "name": rule.name,
                    "condition": rule.condition,
                    "action": rule.action
                }
                for rule in contract.business_rules
            ]
        }
        return json.dumps(contract_json, indent=2)

    def _generate_data_bindings(self) -> Dict:
        """Generate data bindings from ontology metadata."""
        # This would typically come from SchemaMapper
        # For now, return empty dict
        return {}

    def _extract_triggers(self, rule: BusinessRule) -> List[str]:
        """Extract trigger actions from business rule."""
        triggers = []
        if "notify" in rule.action.lower() or "alert" in rule.action.lower():
            triggers.append("NotifyOperations")
        if "log" in rule.action.lower() or "record" in rule.action.lower():
            triggers.append("LogIncident")
        if "classify" in rule.action.lower():
            triggers.append("UpdateClassification")
        return triggers
