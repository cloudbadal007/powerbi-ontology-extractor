# Getting Started

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/powerbi-ontology-extractor.git
cd powerbi-ontology-extractor

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Verify Installation

```bash
pbi-ontology --help
```

## Quick Start (5 minutes)

### Step 1: Extract Ontology from Power BI

```python
from powerbi_ontology import PowerBIExtractor

# Extract from .pbix file
extractor = PowerBIExtractor("your_dashboard.pbix")
semantic_model = extractor.extract()

print(f"Found {len(semantic_model.entities)} entities")
print(f"Found {len(semantic_model.relationships)} relationships")
```

### Step 2: Generate Ontology

```python
from powerbi_ontology import OntologyGenerator

# Generate formal ontology
generator = OntologyGenerator(semantic_model)
ontology = generator.generate()

print(f"Ontology: {ontology.name}")
print(f"Entities: {len(ontology.entities)}")
print(f"Business Rules: {len(ontology.business_rules)}")
```

### Step 3: Export

```python
# Export to Fabric IQ
from powerbi_ontology.export import FabricIQExporter

exporter = FabricIQExporter(ontology)
fabric_json = exporter.export()

import json
with open("ontology_fabric_iq.json", "w") as f:
    json.dump(fabric_json, f, indent=2)
```

## Command Line Usage

### Extract Ontology

```bash
pbi-ontology extract Supply_Chain.pbix --output supply_chain_ontology.json
```

### Analyze Multiple Dashboards

```bash
pbi-ontology analyze *.pbix --report semantic_debt.html
```

### Export to Different Formats

```bash
pbi-ontology export ontology.json --format fabric-iq --output fabric_iq.json
pbi-ontology export ontology.json --format ontoguard --output ontoguard.json
```

## Next Steps

- Read [Power BI Semantic Models](power_bi_semantic_models.md) to understand .pbix structure
- Check [Ontology Format](ontology_format.md) for ontology structure details
- See [Use Cases](use_cases.md) for real-world scenarios
- Explore [examples/](../examples/) for complete workflows
