# API Reference

Complete API documentation for PowerBI Ontology Extractor.

## Core Classes

### PowerBIExtractor

Main class for extracting semantic models from Power BI .pbix files.

```python
from powerbi_ontology import PowerBIExtractor

extractor = PowerBIExtractor(pbix_path: str)
```

#### Methods

##### `extract() -> SemanticModel`

Extract complete semantic model from .pbix file.

**Returns**: `SemanticModel` with all extracted information

**Example**:
```python
extractor = PowerBIExtractor("dashboard.pbix")
semantic_model = extractor.extract()
```

##### `extract_entities() -> List[Entity]`

Extract entities (tables) from Power BI model.

**Returns**: List of `Entity` objects

##### `extract_relationships() -> List[Relationship]`

Extract relationships between entities.

**Returns**: List of `Relationship` objects

##### `extract_measures() -> List[Measure]`

Extract DAX measures from all tables.

**Returns**: List of `Measure` objects

---

### SemanticModel

Represents a complete semantic model extracted from Power BI.

```python
@dataclass
class SemanticModel:
    name: str
    entities: List[Entity]
    relationships: List[Relationship]
    measures: List[Measure]
    hierarchies: List[Hierarchy]
    security_rules: List[SecurityRule]
    metadata: Dict
    source_file: str
```

#### Methods

##### `to_ontology() -> Ontology`

Convert semantic model to formal ontology.

**Returns**: `Ontology` object

**Example**:
```python
ontology = semantic_model.to_ontology()
```

---

### OntologyGenerator

Generates formal ontologies from Power BI semantic models.

```python
from powerbi_ontology import OntologyGenerator

generator = OntologyGenerator(semantic_model: SemanticModel)
```

#### Methods

##### `generate() -> Ontology`

Generate complete ontology from semantic model.

**Returns**: `Ontology` object

**Example**:
```python
generator = OntologyGenerator(semantic_model)
ontology = generator.generate()
```

##### `map_entity(entity: Entity) -> OntologyEntity`

Map Power BI entity to ontology entity.

**Parameters**:
- `entity`: Power BI `Entity` object

**Returns**: `OntologyEntity`

##### `map_relationship(rel: Relationship) -> OntologyRelationship`

Map Power BI relationship to ontology relationship.

**Parameters**:
- `rel`: Power BI `Relationship` object

**Returns**: `OntologyRelationship`

##### `suggest_enhancements() -> List[Enhancement]`

Suggest enhancements to the ontology.

**Returns**: List of `Enhancement` suggestions

---

### DAXParser

Parses DAX formulas to extract business rules.

```python
from powerbi_ontology.dax_parser import DAXParser

parser = DAXParser()
```

#### Methods

##### `parse_measure(measure_name: str, dax_formula: str) -> ParsedRule`

Parse a DAX measure to extract business rules.

**Parameters**:
- `measure_name`: Name of the measure
- `dax_formula`: DAX formula string

**Returns**: `ParsedRule` with extracted information

**Example**:
```python
parser = DAXParser()
parsed = parser.parse_measure(
    "High Risk Customers",
    "CALCULATE(COUNT(...), RiskScore > 80)"
)
```

##### `extract_business_logic(measure_name: str, dax_formula: str) -> List[BusinessRule]`

Extract business logic from DAX formula.

**Returns**: List of `BusinessRule` objects

##### `identify_dependencies(dax_formula: str) -> List[str]`

Identify table/column dependencies from DAX.

**Returns**: List of dependencies in format "Table.Column"

##### `classify_measure_type(dax_formula: str) -> str`

Classify the type of DAX measure.

**Returns**: One of: "AGGREGATION", "CALCULATION", "CONDITIONAL", "FILTER", "TIME_INTELLIGENCE"

---

### SchemaMapper

Maps logical ontologies to physical data sources and detects schema drift.

```python
from powerbi_ontology import SchemaMapper

mapper = SchemaMapper(ontology: Ontology, data_source: Optional[str] = None)
```

#### Methods

##### `create_binding(entity_name: str, physical_table: str, property_mappings: Optional[Dict[str, str]] = None) -> SchemaBinding`

Create a schema binding between logical entity and physical table.

**Parameters**:
- `entity_name`: Name of the ontology entity
- `physical_table`: Physical table name (e.g., "dbo.customers")
- `property_mappings`: Optional explicit property mappings

**Returns**: `SchemaBinding` object

**Example**:
```python
mapper = SchemaMapper(ontology, "azure_sql")
binding = mapper.create_binding("Shipment", "dbo.shipments")
```

##### `validate_binding(binding: SchemaBinding) -> ValidationResult`

Validate a schema binding.

**Returns**: `ValidationResult` with validation status

##### `detect_drift(binding: SchemaBinding, current_schema: Dict[str, any]) -> DriftReport`

Detect schema drift between binding and current schema.

**Parameters**:
- `binding`: `SchemaBinding` to check
- `current_schema`: Current physical schema (dict of column_name -> type)

**Returns**: `DriftReport` with detected drift

**Example**:
```python
current_schema = {"shipment_id": "GUID", "temperature": "Decimal"}
drift = mapper.detect_drift(binding, current_schema)
if drift.severity == "CRITICAL":
    print(f"DRIFT DETECTED: {drift.message}")
```

##### `suggest_fix(drift_report: DriftReport) -> List[Fix]`

Suggest fixes for detected drift.

**Returns**: List of `Fix` suggestions

---

### ContractBuilder

Builds semantic contracts for AI agents.

```python
from powerbi_ontology import ContractBuilder

builder = ContractBuilder(ontology: Ontology)
```

#### Methods

##### `build_contract(agent_name: str, permissions: Dict[str, any]) -> SemanticContract`

Build a semantic contract for an AI agent.

**Parameters**:
- `agent_name`: Name of the AI agent
- `permissions`: Dictionary with read, write, execute, role keys

**Returns**: `SemanticContract`

**Example**:
```python
contract = builder.build_contract(
    "SupplyChainMonitor",
    {
        "read": ["Shipment", "Customer"],
        "write": {"Shipment": ["Status"]},
        "execute": ["RerouteShipment"],
        "role": "Operations_Manager"
    }
)
```

##### `export_contract(contract: SemanticContract, format: str = "json") -> str`

Export contract to different formats.

**Parameters**:
- `contract`: `SemanticContract` to export
- `format`: Export format ("json", "ontoguard", "fabric_iq")

**Returns**: Exported contract as string

---

### SemanticAnalyzer

Analyzes multiple Power BI semantic models for conflicts and semantic debt.

```python
from powerbi_ontology import SemanticAnalyzer

analyzer = SemanticAnalyzer(semantic_models: List[SemanticModel])
```

#### Methods

##### `detect_conflicts() -> List[Conflict]`

Detect conflicting definitions across dashboards.

**Returns**: List of `Conflict` objects

##### `identify_duplicate_logic() -> List[Duplication]`

Identify duplicated DAX measures across dashboards.

**Returns**: List of `Duplication` objects

##### `calculate_semantic_debt() -> SemanticDebtReport`

Calculate semantic debt from conflicts.

**Returns**: `SemanticDebtReport` with cost calculations

**Example**:
```python
debt_report = analyzer.calculate_semantic_debt()
print(f"Total semantic debt: ${debt_report.total_cost:,.0f}")
```

##### `suggest_canonical_definitions() -> List[CanonicalEntity]`

Suggest canonical definitions for entities/concepts.

**Returns**: List of `CanonicalEntity` suggestions

---

## Export Modules

### FabricIQExporter

Exports ontologies to Microsoft Fabric IQ format.

```python
from powerbi_ontology.export import FabricIQExporter

exporter = FabricIQExporter(ontology: Ontology)
fabric_json = exporter.export()
```

### OntoGuardExporter

Exports ontologies to OntoGuard format.

```python
from powerbi_ontology.export import OntoGuardExporter

exporter = OntoGuardExporter(ontology: Ontology)
ontoguard_json = exporter.export()
```

### JSONSchemaExporter

Exports ontologies to JSON Schema format.

```python
from powerbi_ontology.export import JSONSchemaExporter

exporter = JSONSchemaExporter(ontology: Ontology)
schema = exporter.export()
```

### OWLExporter

Exports ontologies to OWL/RDF format.

```python
from powerbi_ontology.export import OWLExporter

exporter = OWLExporter(ontology: Ontology)
owl_xml = exporter.export(format="xml")
```

---

## Data Classes

### Entity

Represents an entity (table) in the semantic model.

```python
@dataclass
class Entity:
    name: str
    description: str
    properties: List[Property]
    source_table: str
    primary_key: Optional[str]
```

### Property

Represents a property/column in an entity.

```python
@dataclass
class Property:
    name: str
    data_type: str
    required: bool
    unique: bool
    description: str
    source_column: str
```

### Relationship

Represents a relationship between entities.

```python
@dataclass
class Relationship:
    from_entity: str
    from_property: str
    to_entity: str
    to_property: str
    cardinality: str
    cross_filter_direction: str
    is_active: bool
    name: str
```

### Measure

Represents a DAX measure.

```python
@dataclass
class Measure:
    name: str
    dax_formula: str
    description: str
    dependencies: List[str]
    folder: str
    table: str
```

---

## Utilities

### PBIXReader

Reads Power BI .pbix files (ZIP archives).

```python
from powerbi_ontology.utils import PBIXReader

with PBIXReader("dashboard.pbix") as reader:
    model = reader.read_model()
    tables = reader.get_tables()
```

### OntologyVisualizer

Creates visualizations of ontologies.

```python
from powerbi_ontology.utils import OntologyVisualizer

visualizer = OntologyVisualizer(ontology)
visualizer.save_as_image("diagram.png")
visualizer.save_interactive_html("graph.html")
```

---

## Error Handling

### Common Exceptions

#### `FileNotFoundError`
Raised when .pbix file doesn't exist.

#### `ValueError`
Raised for invalid .pbix format or JSON parsing errors.

#### `RuntimeError`
Raised for extraction failures.

---

## Type Hints

All functions include type hints for better IDE support and type checking.

**Example**:
```python
def extract_entities(self) -> List[Entity]:
    """Extract entities from model."""
    ...
```

---

## Logging

The package uses Python's logging module. Configure logging to see debug information:

```python
import logging

logging.basicConfig(level=logging.INFO)
```

---

For more examples, see the [Examples](../examples/) directory.
