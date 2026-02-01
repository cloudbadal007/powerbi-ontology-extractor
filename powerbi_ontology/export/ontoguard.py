"""
OntoGuard Exporter

Exports ontologies to OntoGuard format for validation and drift detection.
"""

import logging
from typing import Dict, List

from powerbi_ontology.ontology_generator import Ontology, OntologyEntity, BusinessRule, Constraint

logger = logging.getLogger(__name__)


class OntoGuardExporter:
    """
    Exports ontologies to OntoGuard format.
    
    This integrates with ontoguard-ai project for:
    - Validation firewall
    - Schema drift detection
    - Business rule enforcement
    """

    def __init__(self, ontology: Ontology):
        """
        Initialize OntoGuard exporter.
        
        Args:
            ontology: Ontology to export
        """
        self.ontology = ontology

    def export(self) -> Dict:
        """
        Export ontology to OntoGuard format.
        
        Returns:
            Dictionary in OntoGuard format
        """
        logger.info(f"Exporting ontology '{self.ontology.name}' to OntoGuard format")
        
        ontoguard = {
            "ontology": {
                "name": self.ontology.name,
                "version": self.ontology.version,
                "source": self.ontology.source
            },
            "validationRules": self.generate_validation_rules(),
            "schemaBindings": self.generate_schema_bindings(),
            "firewallRules": self.generate_firewall_config(),
            "businessRules": [
                {
                    "name": rule.name,
                    "entity": rule.entity,
                    "condition": rule.condition,
                    "action": rule.action,
                    "description": rule.description
                }
                for rule in self.ontology.business_rules
            ]
        }
        
        return ontoguard

    def generate_validation_rules(self) -> List[Dict]:
        """
        Generate validation rules from ontology constraints.
        
        Returns:
            List of validation rule dictionaries
        """
        validation_rules = []
        
        for entity in self.ontology.entities:
            for prop in entity.properties:
                for constraint in prop.constraints:
                    rule = {
                        "rule": f"{entity.name}_{prop.name}_{constraint.type}",
                        "entity": entity.name,
                        "property": prop.name,
                        "validation": {
                            "type": constraint.type,
                            "value": constraint.value,
                            "error": constraint.message or f"Validation failed for {entity.name}.{prop.name}"
                        }
                    }
                    
                    # Format based on constraint type
                    if constraint.type == "range":
                        if isinstance(constraint.value, dict):
                            rule["validation"]["min"] = constraint.value.get("min")
                            rule["validation"]["max"] = constraint.value.get("max")
                    elif constraint.type == "enum":
                        rule["validation"]["values"] = constraint.value
                    elif constraint.type == "regex":
                        rule["validation"]["pattern"] = constraint.value
                    
                    validation_rules.append(rule)
        
        return validation_rules

    def generate_schema_bindings(self) -> Dict:
        """
        Generate schema binding definitions.
        
        This is CRITICAL for preventing the $4.6M mistake!
        
        Returns:
            Dictionary of schema bindings
        """
        bindings = {}
        
        for entity in self.ontology.entities:
            # Get expected columns from entity properties
            expected_columns = [prop.source_column or prop.name for prop in entity.properties]
            
            bindings[entity.name] = {
                "expectedColumns": expected_columns,
                "source": entity.source_table or f"sql_db.dbo.{entity.name.lower()}",
                "primaryKey": next(
                    (prop.name for prop in entity.properties if prop.unique),
                    None
                )
            }
        
        return bindings

    def generate_firewall_config(self) -> List[Dict]:
        """
        Generate OntoGuard firewall configuration.
        
        Returns:
            List of firewall rule dictionaries
        """
        firewall_rules = []
        
        # Generate rules from business rules
        for rule in self.ontology.business_rules:
            if "risk" in rule.name.lower() or "alert" in rule.name.lower():
                firewall_rule = {
                    "name": f"prevent_invalid_{rule.name.lower()}",
                    "trigger": f"action.{rule.action}",
                    "checks": [
                        f"{rule.entity}_exists",
                        f"{rule.condition}_valid"
                    ],
                    "onFailure": "block",
                    "description": f"Prevent invalid {rule.name} based on {rule.condition}"
                }
                firewall_rules.append(firewall_rule)
        
        return firewall_rules

    def export_contract(self, contract) -> str:
        """Export semantic contract to OntoGuard format."""
        import json
        contract_json = {
            "agentContract": contract.agent_name,
            "ontologyVersion": contract.ontology_version,
            "validationRules": [
                {
                    "entity": rule.get("entity", ""),
                    "property": rule.get("property", ""),
                    "validation": rule.get("validation", {})
                }
                for rule in self.generate_validation_rules()
                if rule.get("entity") in contract.permissions.read_entities
            ],
            "permissions": {
                "readEntities": contract.permissions.read_entities,
                "writeProperties": contract.permissions.write_properties,
                "executableActions": contract.permissions.executable_actions
            },
            "firewallRules": self.generate_firewall_config()
        }
        return json.dumps(contract_json, indent=2)
