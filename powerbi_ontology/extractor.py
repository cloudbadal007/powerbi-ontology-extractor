"""
Power BI Semantic Model Extractor

Extracts semantic intelligence from Power BI .pbix files.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from powerbi_ontology.utils.pbix_reader import PBIXReader

logger = logging.getLogger(__name__)


@dataclass
class Property:
    """Represents a property/column in an entity."""
    name: str
    data_type: str  # String, Integer, Decimal, Date, Boolean, etc.
    required: bool = False
    unique: bool = False
    description: str = ""
    source_column: str = ""


@dataclass
class Entity:
    """Represents an entity (table) in the semantic model."""
    name: str
    description: str = ""
    properties: List[Property] = field(default_factory=list)
    source_table: str = ""
    primary_key: Optional[str] = None


@dataclass
class Relationship:
    """Represents a relationship between entities."""
    from_entity: str
    from_property: str
    to_entity: str
    to_property: str
    cardinality: str  # "one-to-many", "many-to-one", "one-to-one", "many-to-many"
    cross_filter_direction: str = "single"  # "single", "both"
    is_active: bool = True
    name: str = ""


@dataclass
class Measure:
    """Represents a DAX measure."""
    name: str
    dax_formula: str
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    folder: str = ""
    table: str = ""


@dataclass
class Hierarchy:
    """Represents a hierarchy (date or custom)."""
    name: str
    table: str
    levels: List[str] = field(default_factory=list)
    hierarchy_type: str = "custom"  # "date" or "custom"


@dataclass
class SecurityRule:
    """Represents a row-level security (RLS) rule."""
    role: str
    table: str
    dax_filter: str
    description: str = ""


@dataclass
class SemanticModel:
    """Complete semantic model extracted from Power BI."""
    name: str
    entities: List[Entity] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    measures: List[Measure] = field(default_factory=list)
    hierarchies: List[Hierarchy] = field(default_factory=list)
    security_rules: List[SecurityRule] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    source_file: str = ""

    def to_ontology(self):
        """Convert to ontology format (delegates to OntologyGenerator)."""
        from powerbi_ontology.ontology_generator import OntologyGenerator
        generator = OntologyGenerator(self)
        return generator.generate()


class PowerBIExtractor:
    """
    Core class for extracting semantic intelligence from Power BI .pbix files.
    """

    def __init__(self, pbix_path: str):
        """
        Initialize extractor.
        
        Args:
            pbix_path: Path to the .pbix file
        """
        self.pbix_path = pbix_path
        self.reader: Optional[PBIXReader] = None

    def extract(self) -> SemanticModel:
        """
        Extract complete semantic model from .pbix file.
        
        Returns:
            SemanticModel with all extracted information
        """
        logger.info(f"Extracting semantic model from {self.pbix_path}")
        
        self.reader = PBIXReader(self.pbix_path)
        self.reader.extract_to_temp()
        
        model_data = self.reader.read_model()
        
        # Extract model name
        model_name = model_data.get("name", "Unknown")
        if isinstance(model_data, dict) and "model" in model_data:
            model_name = model_data["model"].get("name", model_name)
        
        semantic_model = SemanticModel(
            name=model_name,
            source_file=self.pbix_path,
            metadata={"extraction_date": str(__import__("datetime").datetime.now().isoformat())}
        )
        
        # Extract all components
        semantic_model.entities = self.extract_entities()
        semantic_model.relationships = self.extract_relationships()
        semantic_model.measures = self.extract_measures()
        semantic_model.hierarchies = self.extract_hierarchies()
        semantic_model.security_rules = self.extract_security_rules()
        
        logger.info(
            f"Extracted: {len(semantic_model.entities)} entities, "
            f"{len(semantic_model.relationships)} relationships, "
            f"{len(semantic_model.measures)} measures"
        )
        
        return semantic_model

    def extract_entities(self) -> List[Entity]:
        """
        Extract entities (tables) from Power BI model.
        
        Returns:
            List of Entity objects
        """
        tables = self.reader.get_tables()
        entities = []
        
        for table in tables:
            table_name = str(table.get("name", "Unknown") or "Unknown")
            description = str(table.get("description", "") or "")
            
            # Extract columns as properties
            properties = []
            columns = table.get("columns", [])
            
            for col in columns:
                prop = Property(
                    name=str(col.get("name", "") or ""),
                    data_type=self._map_data_type(str(col.get("dataType", "string") or "string")),
                    required=col.get("isNullable", True) is False,
                    unique=col.get("isUnique", False) or col.get("isKey", False),
                    description=str(col.get("description", "") or ""),
                    source_column=str(col.get("name", "") or "")
                )
                properties.append(prop)
            
            # Identify primary key
            primary_key = None
            for col in columns:
                if col.get("isKey", False) or col.get("isUnique", False):
                    primary_key = col.get("name")
                    break
            
            entity = Entity(
                name=table_name,
                description=description,
                properties=properties,
                source_table=table_name,
                primary_key=primary_key
            )
            entities.append(entity)
        
        return entities

    def extract_relationships(self) -> List[Relationship]:
        """
        Extract relationships between entities.
        
        Returns:
            List of Relationship objects
        """
        relationships_data = self.reader.get_relationships()
        relationships = []
        
        for rel in relationships_data:
            from_table = str(rel.get("fromTable", "") or "")
            from_column = str(rel.get("fromColumn", "") or "")
            to_table = str(rel.get("toTable", "") or "")
            to_column = str(rel.get("toColumn", "") or "")
            
            # Determine cardinality
            cardinality = "many-to-one"  # Default
            if rel.get("fromCardinality") == "one" and rel.get("toCardinality") == "many":
                cardinality = "one-to-many"
            elif rel.get("fromCardinality") == "one" and rel.get("toCardinality") == "one":
                cardinality = "one-to-one"
            elif rel.get("fromCardinality") == "many" and rel.get("toCardinality") == "many":
                cardinality = "many-to-many"
            
            cross_filter = rel.get("crossFilteringBehavior", "singleDirection")
            if cross_filter == "bothDirections":
                cross_filter_direction = "both"
            else:
                cross_filter_direction = "single"
            
            relationship = Relationship(
                from_entity=from_table,
                from_property=from_column,
                to_entity=to_table,
                to_property=to_column,
                cardinality=cardinality,
                cross_filter_direction=cross_filter_direction,
                is_active=rel.get("isActive", True),
                name=rel.get("name", f"{from_table}_{to_table}")
            )
            relationships.append(relationship)
        
        return relationships

    def extract_measures(self) -> List[Measure]:
        """
        Extract DAX measures from all tables.
        
        Returns:
            List of Measure objects
        """
        measures_data = self.reader.get_measures()
        measures = []
        
        for measure_data in measures_data:
            measure = Measure(
                name=str(measure_data.get("name", "") or ""),
                dax_formula=str(measure_data.get("expression", "") or ""),
                description=str(measure_data.get("description", "") or ""),
                folder=str(measure_data.get("displayFolder", "") or ""),
                table=str(measure_data.get("table", "") or "")
            )
            
            # Extract dependencies (basic - can be enhanced)
            measure.dependencies = self._extract_measure_dependencies(measure.dax_formula)
            
            measures.append(measure)
        
        return measures

    def extract_hierarchies(self) -> List[Hierarchy]:
        """
        Extract hierarchies (date and custom).
        
        Returns:
            List of Hierarchy objects
        """
        tables = self.reader.get_tables()
        hierarchies = []
        
        for table in tables:
            table_name = str(table.get("name", "") or "")
            
            # Extract hierarchies from table
            table_hierarchies = table.get("hierarchies", [])
            for hier in table_hierarchies:
                hierarchy = Hierarchy(
                    name=str(hier.get("name", "") or ""),
                    table=table_name,
                    levels=[str(level.get("name", "") or "") for level in hier.get("levels", [])],
                    hierarchy_type="date" if "date" in str(table_name or "").lower() else "custom"
                )
                hierarchies.append(hierarchy)
        
        return hierarchies

    def extract_security_rules(self) -> List[SecurityRule]:
        """
        Extract row-level security (RLS) rules.
        
        Returns:
            List of SecurityRule objects
        """
        model_data = self.reader.read_model()
        security_rules = []
        
        # Handle different schema versions
        roles = []
        if isinstance(model_data, dict):
            if "model" in model_data:
                model_data = model_data["model"]
            roles = model_data.get("roles", [])
        
        for role in roles:
            role_name = str(role.get("name", "") or "")
            table_permissions = role.get("tablePermissions", [])
            
            for perm in table_permissions:
                table_name = str(perm.get("name", "") or "")
                filter_expression = str(perm.get("filterExpression", "") or "")
                
                if filter_expression:
                    rule = SecurityRule(
                        role=role_name,
                        table=table_name,
                        dax_filter=filter_expression,
                        description=f"RLS rule for {table_name} in role {role_name}"
                    )
                    security_rules.append(rule)
        
        return security_rules

    def _map_data_type(self, pbix_type: str) -> str:
        """Map Power BI data type to ontology data type."""
        type_mapping = {
            "string": "String",
            "int64": "Integer",
            "double": "Decimal",
            "dateTime": "Date",
            "boolean": "Boolean",
            "decimal": "Decimal",
        }
        return type_mapping.get(str(pbix_type or "string").lower(), "String")

    def _extract_measure_dependencies(self, dax_formula: str) -> List[str]:
        """
        Extract table/column dependencies from DAX formula (basic implementation).
        
        This is a simplified version - full parsing is done in dax_parser.py
        """
        dependencies = []
        # Simple regex-based extraction (enhanced in dax_parser)
        import re
        # Match table[column] patterns
        pattern = r'(\w+)\[(\w+)\]'
        matches = re.findall(pattern, dax_formula)
        for table, column in matches:
            dependencies.append(f"{table}.{column}")
        return list(set(dependencies))

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        if self.reader:
            self.reader.cleanup()
