"""
Ontology Generator

Converts Power BI semantic models to formal ontologies.
Implements the "70% auto-generated" concept from the article.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from powerbi_ontology.dax_parser import DAXParser
from powerbi_ontology.extractor import SemanticModel, Entity, Relationship, Measure

logger = logging.getLogger(__name__)


@dataclass
class Constraint:
    """Represents a constraint on a property."""
    type: str  # "range", "regex", "enum", "reference"
    value: any
    message: str = ""


@dataclass
class OntologyProperty:
    """Represents a property in an ontology entity."""
    name: str
    data_type: str
    required: bool = False
    unique: bool = False
    constraints: List[Constraint] = field(default_factory=list)
    description: str = ""
    source_column: str = ""


@dataclass
class OntologyEntity:
    """Represents an entity in the ontology."""
    name: str
    description: str = ""
    properties: List[OntologyProperty] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)
    source_table: str = ""
    entity_type: str = "standard"  # "dimension", "fact", "bridge", "date"


@dataclass
class OntologyRelationship:
    """Represents a relationship in the ontology."""
    from_entity: str
    from_property: str
    to_entity: str
    to_property: str
    relationship_type: str  # "has", "belongs_to", "contains", etc.
    cardinality: str
    description: str = ""
    source_relationship: str = ""


@dataclass
class BusinessRule:
    """Represents a business rule in the ontology."""
    name: str
    entity: str
    condition: str
    action: str = ""
    classification: str = ""
    description: str = ""
    priority: int = 1
    source_measure: str = ""


@dataclass
class Pattern:
    """Represents a detected pattern in the semantic model."""
    pattern_type: str  # "date_table", "dimension", "fact", "bridge"
    entity_name: str
    confidence: float
    description: str = ""


@dataclass
class Enhancement:
    """Represents a suggested enhancement to the ontology."""
    type: str  # "missing_rule", "validation_constraint", "semantic_relationship"
    description: str
    entity: str = ""
    property: str = ""
    suggested_value: any = None


@dataclass
class Ontology:
    """Formal ontology generated from Power BI semantic model."""
    name: str
    version: str = "1.0.0"
    source: str = ""
    entities: List[OntologyEntity] = field(default_factory=list)
    relationships: List[OntologyRelationship] = field(default_factory=list)
    business_rules: List[BusinessRule] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def add_business_rule(self, rule: BusinessRule):
        """Add a business rule to the ontology."""
        self.business_rules.append(rule)
    
    def export_fabric_iq(self, filepath: str):
        """Export to Fabric IQ format."""
        from powerbi_ontology.export.fabric_iq import FabricIQExporter
        exporter = FabricIQExporter(self)
        fabric_json = exporter.export()
        import json
        with open(filepath, 'w') as f:
            json.dump(fabric_json, f, indent=2)


class OntologyGenerator:
    """
    Generates formal ontologies from Power BI semantic models.
    
    This implements the "70% auto-generated" strategy:
    - Automatically extracts entities, relationships, and business rules
    - Business analyst reviews and adds the missing 30%
    """

    def __init__(self, semantic_model: SemanticModel):
        """
        Initialize ontology generator.
        
        Args:
            semantic_model: Extracted semantic model from Power BI
        """
        self.semantic_model = semantic_model
        self.dax_parser = DAXParser()

    def generate(self) -> Ontology:
        """
        Generate complete ontology from semantic model.
        
        Returns:
            Ontology object
        """
        logger.info(f"Generating ontology from semantic model: {self.semantic_model.name}")
        
        ontology = Ontology(
            name=f"{self.semantic_model.name}_Ontology",
            version="1.0.0",
            source=f"Power BI: {self.semantic_model.source_file}",
            metadata={
                "generation_date": str(__import__("datetime").datetime.now().isoformat()),
                "source_model": self.semantic_model.name
            }
        )
        
        # Map entities
        ontology.entities = [self.map_entity(entity) for entity in self.semantic_model.entities]
        
        # Map relationships
        ontology.relationships = [
            self.map_relationship(rel) for rel in self.semantic_model.relationships
        ]
        
        # Map measures to business rules
        for measure in self.semantic_model.measures:
            parsed = self.dax_parser.parse_measure(measure.name, measure.dax_formula)
            for rule in parsed.business_rules:
                ontology.business_rules.append(
                    self.map_measure_to_rule(measure, rule)
                )
        
        # Detect patterns
        patterns = self.detect_patterns()
        logger.info(f"Detected {len(patterns)} patterns")
        
        # Apply pattern-based enhancements
        self._apply_patterns(ontology, patterns)
        
        return ontology

    def map_entity(self, entity: Entity) -> OntologyEntity:
        """
        Map Power BI entity to ontology entity.
        
        Args:
            entity: Power BI entity
            
        Returns:
            OntologyEntity
        """
        properties = []
        for prop in entity.properties:
            ontology_prop = OntologyProperty(
                name=prop.name,
                data_type=prop.data_type,
                required=prop.required,
                unique=prop.unique,
                description=prop.description,
                source_column=prop.source_column
            )
            properties.append(ontology_prop)
        
        return OntologyEntity(
            name=entity.name,
            description=entity.description,
            properties=properties,
            source_table=entity.source_table,
            entity_type=self._classify_entity_type(entity)
        )

    def map_relationship(self, rel: Relationship) -> OntologyRelationship:
        """
        Map Power BI relationship to ontology relationship.
        
        Args:
            rel: Power BI relationship
            
        Returns:
            OntologyRelationship
        """
        # Determine semantic relationship type
        relationship_type = self._determine_relationship_type(rel)
        
        return OntologyRelationship(
            from_entity=rel.from_entity,
            from_property=rel.from_property,
            to_entity=rel.to_entity,
            to_property=rel.to_property,
            relationship_type=relationship_type,
            cardinality=rel.cardinality,
            description=f"Relationship from {rel.from_entity} to {rel.to_entity}",
            source_relationship=rel.name
        )

    def map_measure_to_rule(self, measure: Measure, parsed_rule) -> BusinessRule:
        """
        Map DAX measure to business rule.
        
        Args:
            measure: Power BI measure
            parsed_rule: Parsed business rule from DAX
            
        Returns:
            BusinessRule
        """
        return BusinessRule(
            name=parsed_rule.name,
            entity=parsed_rule.entity or measure.table,
            condition=parsed_rule.condition,
            action=parsed_rule.action,
            classification=parsed_rule.classification,
            description=parsed_rule.description or measure.description,
            priority=parsed_rule.priority,
            source_measure=measure.name
        )

    def detect_patterns(self) -> List[Pattern]:
        """
        Detect common patterns in the semantic model.
        
        Returns:
            List of detected patterns
        """
        patterns = []
        
        for entity in self.semantic_model.entities:
            entity_name_lower = entity.name.lower()
            
            # Date table pattern
            if any(keyword in entity_name_lower for keyword in ['date', 'calendar', 'time']):
                # Check for date-like columns
                date_columns = ['year', 'month', 'day', 'quarter', 'week']
                has_date_columns = any(
                    any(dc in prop.name.lower() for dc in date_columns)
                    for prop in entity.properties
                )
                if has_date_columns:
                    patterns.append(Pattern(
                        pattern_type="date_table",
                        entity_name=entity.name,
                        confidence=0.9,
                        description="Date/Calendar table detected"
                    ))
            
            # Dimension table pattern (small, many relationships)
            relationship_count = sum(
                1 for rel in self.semantic_model.relationships
                if rel.from_entity == entity.name or rel.to_entity == entity.name
            )
            if relationship_count >= 3 and len(entity.properties) < 20:
                patterns.append(Pattern(
                    pattern_type="dimension",
                    entity_name=entity.name,
                    confidence=0.7,
                    description="Dimension table pattern detected"
                ))
            
            # Fact table pattern (large, few relationships, has measures)
            measure_count = sum(
                1 for measure in self.semantic_model.measures
                if measure.table == entity.name
            )
            if measure_count > 0 and relationship_count <= 3:
                patterns.append(Pattern(
                    pattern_type="fact",
                    entity_name=entity.name,
                    confidence=0.8,
                    description="Fact table pattern detected"
                ))
        
        return patterns

    def suggest_enhancements(self) -> List[Enhancement]:
        """
        Suggest enhancements to the ontology.
        
        Returns:
            List of Enhancement suggestions
        """
        enhancements = []
        
        for entity in self.semantic_model.entities:
            for prop in entity.properties:
                prop_name_lower = prop.name.lower()
                
                # Email validation
                if 'email' in prop_name_lower and prop.data_type == "String":
                    enhancements.append(Enhancement(
                        type="validation_constraint",
                        description=f"Add email format validation to {entity.name}.{prop.name}",
                        entity=entity.name,
                        property=prop.name,
                        suggested_value={"type": "regex", "pattern": r"^[^\s@]+@[^\s@]+\.[^\s@]+$"}
                    ))
                
                # URL validation
                if 'url' in prop_name_lower or 'website' in prop_name_lower:
                    enhancements.append(Enhancement(
                        type="validation_constraint",
                        description=f"Add URL format validation to {entity.name}.{prop.name}",
                        entity=entity.name,
                        property=prop.name,
                        suggested_value={"type": "regex", "pattern": r"^https?://"}
                    ))
                
                # Range constraints for numeric fields
                if prop.data_type in ["Integer", "Decimal"]:
                    if 'age' in prop_name_lower:
                        enhancements.append(Enhancement(
                            type="validation_constraint",
                            description=f"Add age range constraint (0-150) to {entity.name}.{prop.name}",
                            entity=entity.name,
                            property=prop.name,
                            suggested_value={"type": "range", "min": 0, "max": 150}
                        ))
                    elif 'score' in prop_name_lower or 'rating' in prop_name_lower:
                        enhancements.append(Enhancement(
                            type="validation_constraint",
                            description=f"Add score range constraint (0-100) to {entity.name}.{prop.name}",
                            entity=entity.name,
                            property=prop.name,
                            suggested_value={"type": "range", "min": 0, "max": 100}
                        ))
        
        return enhancements

    def _classify_entity_type(self, entity: Entity) -> str:
        """Classify entity type based on characteristics."""
        # This is a simplified classification
        # Full classification uses pattern detection
        if any(keyword in entity.name.lower() for keyword in ['date', 'calendar', 'time']):
            return "date"
        return "standard"

    def _determine_relationship_type(self, rel: Relationship) -> str:
        """Determine semantic relationship type from Power BI relationship."""
        # Heuristic mapping based on entity names
        from_lower = rel.from_entity.lower()
        to_lower = rel.to_entity.lower()
        
        # Common patterns
        if 'customer' in from_lower and 'order' in to_lower:
            return "has"
        elif 'order' in from_lower and 'customer' in to_lower:
            return "belongs_to"
        elif 'product' in from_lower and 'order' in to_lower:
            return "contained_in"
        elif 'shipment' in from_lower and 'customer' in to_lower:
            return "belongs_to"
        else:
            # Default based on cardinality
            if rel.cardinality == "one-to-many":
                return "has"
            elif rel.cardinality == "many-to-one":
                return "belongs_to"
            else:
                return "related_to"

    def _apply_patterns(self, ontology: Ontology, patterns: List[Pattern]):
        """Apply detected patterns to enhance ontology."""
        for pattern in patterns:
            # Find corresponding entity
            entity = next((e for e in ontology.entities if e.name == pattern.entity_name), None)
            if entity:
                entity.entity_type = pattern.pattern_type
