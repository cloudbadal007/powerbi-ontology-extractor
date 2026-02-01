# Fabric IQ Integration Guide

This guide explains how to export ontologies to Microsoft Fabric IQ format and integrate with Microsoft Fabric.

## Overview

Microsoft Fabric IQ is Microsoft's semantic layer for Fabric. This tool exports Power BI ontologies to Fabric IQ format for deployment in Microsoft Fabric workspaces.

## Exporting to Fabric IQ

### Basic Export

```python
from powerbi_ontology import PowerBIExtractor, OntologyGenerator
from powerbi_ontology.export import FabricIQExporter
import json

# Extract and generate ontology
extractor = PowerBIExtractor("dashboard.pbix")
semantic_model = extractor.extract()
generator = OntologyGenerator(semantic_model)
ontology = generator.generate()

# Export to Fabric IQ
fabric_exporter = FabricIQExporter(ontology)
fabric_json = fabric_exporter.export()

# Save to file
with open("ontology_fabric_iq.json", "w") as f:
    json.dump(fabric_json, f, indent=2)
```

### Fabric IQ Format

The exported JSON follows Fabric IQ schema:

```json
{
  "ontologyItem": "SupplyChain_Ontology_v1",
  "version": "1.0.0",
  "source": "Power BI: Supply_Chain_Operations.pbix",
  "extractedDate": "2025-01-31T10:00:00Z",
  "entities": [
    {
      "name": "Shipment",
      "description": "Shipment entity",
      "entityType": "standard",
      "properties": [
        {
          "name": "ShipmentID",
          "type": "GUID",
          "required": true,
          "unique": true
        }
      ],
      "relationships": [
        {
          "type": "belongs_to",
          "target": "Customer",
          "cardinality": "many-to-one"
        }
      ]
    }
  ],
  "businessRules": [
    {
      "name": "HighRiskShipmentDetection",
      "source": "DAX: High Risk Shipments",
      "condition": "Temperature > 25",
      "action": "classify_as_high_risk",
      "triggers": ["NotifyOperations"]
    }
  ],
  "dataBindings": {
    "Shipment": {
      "source": "OneLake.supply_chain_db.shipments",
      "mapping": {
        "ShipmentID": "shipment_id",
        "Temperature": "iot_temperature"
      }
    }
  }
}
```

## Deploying to Microsoft Fabric

### Step 1: Export Ontology

Export your Power BI ontology to Fabric IQ format (see above).

### Step 2: Create Ontology Item in Fabric

1. Open Microsoft Fabric workspace
2. Navigate to **Semantic Models** or **Ontology Items**
3. Click **New** → **Ontology Item**
4. Upload the exported JSON file
5. Configure data bindings to OneLake tables

### Step 3: Configure Data Bindings

Map logical entities to physical OneLake tables:

```json
{
  "dataBindings": {
    "Shipment": {
      "source": "OneLake.workspace.database.shipments",
      "mapping": {
        "ShipmentID": "shipment_id",
        "Temperature": "temperature_reading"
      }
    }
  }
}
```

### Step 4: Validate Schema

Before deploying, validate schema bindings:

```python
from powerbi_ontology import SchemaMapper

mapper = SchemaMapper(ontology, "fabric")
binding = mapper.create_binding("Shipment", "OneLake.workspace.database.shipments")

# Validate against actual OneLake schema
current_schema = get_fabric_schema("OneLake.workspace.database.shipments")
result = mapper.validate_binding(binding)
drift = mapper.detect_drift(binding, current_schema)

if drift.severity == "CRITICAL":
    print("Schema drift detected! Fix before deploying.")
```

## Using with Fabric Semantic Models

### Create Semantic Model from Ontology

1. Import ontology into Fabric
2. Fabric creates a semantic model based on the ontology
3. Use the semantic model in Power BI reports
4. Connect AI agents to the semantic model

### AI Agent Integration

Fabric IQ ontologies can be used by AI agents:

```python
# Agent reads from Fabric semantic model
from fabric_sdk import FabricClient

client = FabricClient()
semantic_model = client.get_semantic_model("SupplyChain_Ontology")

# Agent uses ontology for understanding
agent.understand_entities(semantic_model.entities)
agent.apply_business_rules(semantic_model.business_rules)
```

## Best Practices

### 1. Naming Conventions

- Use descriptive ontology item names
- Include version in name (e.g., "SupplyChain_v1")
- Follow Fabric naming guidelines

### 2. Data Bindings

- Map all entities to OneLake tables
- Use consistent naming between logical and physical
- Validate bindings before deployment

### 3. Business Rules

- Extract all business rules from DAX
- Document rule logic
- Test rules in staging before production

### 4. Versioning

- Version ontologies using Semantic Versioning
- Document changes between versions
- Maintain backward compatibility when possible

### 5. Schema Validation

- Always validate schema bindings
- Use schema drift detection
- Monitor for schema changes

## Troubleshooting

### Issue: Ontology Import Fails

**Solution**:
- Validate JSON format
- Check Fabric IQ schema compliance
- Verify all required fields are present

### Issue: Data Binding Errors

**Solution**:
- Verify OneLake table exists
- Check column name mappings
- Validate data types match

### Issue: Business Rules Not Applied

**Solution**:
- Verify rule format
- Check entity names match
- Test rules individually

## Example: Complete Workflow

```python
# 1. Extract from Power BI
extractor = PowerBIExtractor("Supply_Chain.pbix")
semantic_model = extractor.extract()

# 2. Generate ontology
generator = OntologyGenerator(semantic_model)
ontology = generator.generate()

# 3. Add business analyst enhancements
ontology.add_business_rule(BusinessRule(...))

# 4. Create schema bindings
mapper = SchemaMapper(ontology, "fabric")
binding = mapper.create_binding(
    "Shipment",
    "OneLake.supply_chain.shipments"
)

# 5. Validate schema
current_schema = get_fabric_schema("OneLake.supply_chain.shipments")
drift = mapper.detect_drift(binding, current_schema)
if drift.severity == "CRITICAL":
    raise ValueError("Schema drift detected!")

# 6. Export to Fabric IQ
fabric_exporter = FabricIQExporter(ontology)
fabric_json = fabric_exporter.export()

# 7. Deploy to Fabric
deploy_to_fabric(fabric_json, workspace="SupplyChain")
```

## Resources

- [Microsoft Fabric Documentation](https://learn.microsoft.com/fabric/)
- [Fabric IQ Overview](https://learn.microsoft.com/fabric/semantic-models/)
- [OneLake Documentation](https://learn.microsoft.com/fabric/onelake/)

## Related

- [API Reference](api_reference.md) - Export API details
- [Ontology Format](ontology_format.md) - Ontology structure
- [Use Cases](use_cases.md) - Real-world examples

---

**Ready to deploy your Power BI ontologies to Microsoft Fabric!** 🚀
