"""
Contract Builder

Builds semantic contracts for AI agents from ontologies.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from powerbi_ontology.ontology_generator import Ontology, BusinessRule, Constraint
from powerbi_ontology.dax_parser import DAXParser
from powerbi_ontology.extractor import SemanticModel, Measure

logger = logging.getLogger(__name__)


@dataclass
class ContractPermissions:
    """Permissions for an AI agent contract."""
    read_entities: List[str] = field(default_factory=list)
    write_properties: Dict[str, List[str]] = field(default_factory=dict)  # entity -> properties
    executable_actions: List[str] = field(default_factory=list)
    required_role: str = ""
    context_filters: Dict[str, str] = field(default_factory=dict)  # entity -> filter condition


@dataclass
class AuditConfig:
    """Audit configuration for contract."""
    log_reads: bool = True
    log_writes: bool = True
    log_actions: bool = True
    alert_on_violation: bool = True


@dataclass
class SemanticContract:
    """Semantic contract for an AI agent."""
    agent_name: str
    ontology_version: str
    permissions: ContractPermissions
    business_rules: List[BusinessRule] = field(default_factory=list)
    validation_constraints: List[Constraint] = field(default_factory=list)
    audit_settings: AuditConfig = field(default_factory=AuditConfig)
    metadata: Dict = field(default_factory=dict)


class ContractBuilder:
    """
    Builds semantic contracts for AI agents from ontologies.
    
    AI agents need semantic contracts that define:
    - What entities they can read
    - What properties they can write
    - What actions they can execute
    - What business rules govern their behavior
    """

    def __init__(self, ontology: Ontology):
        """
        Initialize contract builder.
        
        Args:
            ontology: The ontology to build contracts from
        """
        self.ontology = ontology
        self.dax_parser = DAXParser()

    def build_contract(
        self,
        agent_name: str,
        permissions: Dict[str, any]
    ) -> SemanticContract:
        """
        Build a semantic contract for an AI agent.
        
        Args:
            agent_name: Name of the AI agent
            permissions: Dictionary with read, write, execute, role keys
            
        Returns:
            SemanticContract
        """
        logger.info(f"Building contract for agent: {agent_name}")
        
        contract_permissions = ContractPermissions(
            read_entities=permissions.get("read", []),
            write_properties=permissions.get("write", {}),
            executable_actions=permissions.get("execute", []),
            required_role=permissions.get("role", ""),
            context_filters=permissions.get("filters", {})
        )
        
        contract = SemanticContract(
            agent_name=agent_name,
            ontology_version=self.ontology.version,
            permissions=contract_permissions,
            metadata={
                "created_date": str(__import__("datetime").datetime.now().isoformat()),
                "ontology_source": self.ontology.source
            }
        )
        
        # Add relevant business rules
        self._add_relevant_business_rules(contract)
        
        # Add validation constraints
        self.add_validation_constraints(contract)
        
        return contract

    def generate_permissions_from_dashboard(
        self,
        semantic_model: SemanticModel
    ) -> Dict[str, any]:
        """
        Generate suggested permissions from a Power BI dashboard.
        
        Analyzes what entities the dashboard uses and suggests appropriate permissions.
        
        Args:
            semantic_model: Semantic model from Power BI dashboard
            
        Returns:
            Dictionary with suggested permissions
        """
        # Get all entities used in the dashboard
        entities_used = set()
        for entity in semantic_model.entities:
            entities_used.add(entity.name)
        
        # Get entities from relationships
        for rel in semantic_model.relationships:
            entities_used.add(rel.from_entity)
            entities_used.add(rel.to_entity)
        
        # Get entities from measures
        for measure in semantic_model.measures:
            parsed = self.dax_parser.parse_measure(measure.name, measure.dax_formula)
            for dep in parsed.dependencies:
                if '.' in dep:
                    entity = dep.split('.')[0]
                    entities_used.add(entity)
        
        return {
            "read": list(entities_used),
            "write": {},  # Dashboard typically doesn't write
            "execute": [],  # Dashboard typically doesn't execute actions
            "role": "Viewer"  # Default role
        }

    def add_business_rules(
        self,
        contract: SemanticContract,
        rules: List[BusinessRule]
    ):
        """
        Add business rules to contract.
        
        Args:
            contract: SemanticContract to add rules to
            rules: List of BusinessRule objects
        """
        contract.business_rules.extend(rules)
        logger.info(f"Added {len(rules)} business rules to contract")

    def add_validation_constraints(self, contract: SemanticContract):
        """
        Add validation constraints from ontology to contract.
        
        Args:
            contract: SemanticContract to add constraints to
        """
        # Get entities that agent can read/write
        relevant_entities = set(contract.permissions.read_entities)
        relevant_entities.update(contract.permissions.write_properties.keys())
        
        constraints = []
        for entity_name in relevant_entities:
            entity = next(
                (e for e in self.ontology.entities if e.name == entity_name),
                None
            )
            if entity:
                # Add constraints from entity properties
                for prop in entity.properties:
                    constraints.extend(prop.constraints)
                # Add constraints from entity
                constraints.extend(entity.constraints)
        
        contract.validation_constraints = constraints
        logger.info(f"Added {len(constraints)} validation constraints to contract")

    def export_contract(self, contract: SemanticContract, format: str = "json") -> str:
        """
        Export contract to different formats.
        
        Args:
            contract: SemanticContract to export
            format: Export format ("json", "ontoguard", "fabric_iq")
            
        Returns:
            Exported contract as string
        """
        if format == "json":
            import json
            return json.dumps(self._contract_to_dict(contract), indent=2)
        elif format == "ontoguard":
            from powerbi_ontology.export.ontoguard import OntoGuardExporter
            # Convert contract to ontology-like structure for export
            return OntoGuardExporter(self.ontology).export_contract(contract)
        elif format == "fabric_iq":
            from powerbi_ontology.export.fabric_iq import FabricIQExporter
            return FabricIQExporter(self.ontology).export_contract(contract)
        else:
            raise ValueError(f"Unknown export format: {format}")

    def _add_relevant_business_rules(self, contract: SemanticContract):
        """Add business rules relevant to the agent's permissions."""
        relevant_entities = set(contract.permissions.read_entities)
        relevant_entities.update(contract.permissions.write_properties.keys())
        
        relevant_rules = [
            rule for rule in self.ontology.business_rules
            if rule.entity in relevant_entities
        ]
        
        contract.business_rules = relevant_rules
        logger.info(f"Added {len(relevant_rules)} relevant business rules")

    def _contract_to_dict(self, contract: SemanticContract) -> Dict:
        """Convert contract to dictionary for JSON export."""
        return {
            "agent_name": contract.agent_name,
            "ontology_version": contract.ontology_version,
            "permissions": {
                "read_entities": contract.permissions.read_entities,
                "write_properties": contract.permissions.write_properties,
                "executable_actions": contract.permissions.executable_actions,
                "required_role": contract.permissions.required_role,
                "context_filters": contract.permissions.context_filters
            },
            "business_rules": [
                {
                    "name": rule.name,
                    "entity": rule.entity,
                    "condition": rule.condition,
                    "action": rule.action,
                    "description": rule.description
                }
                for rule in contract.business_rules
            ],
            "validation_constraints": [
                {
                    "type": constraint.type,
                    "value": str(constraint.value),
                    "message": constraint.message
                }
                for constraint in contract.validation_constraints
            ],
            "audit_settings": {
                "log_reads": contract.audit_settings.log_reads,
                "log_writes": contract.audit_settings.log_writes,
                "log_actions": contract.audit_settings.log_actions,
                "alert_on_violation": contract.audit_settings.alert_on_violation
            },
            "metadata": contract.metadata
        }
