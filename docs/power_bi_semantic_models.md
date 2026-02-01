# Power BI Semantic Models

## What are Semantic Models?

Power BI semantic models are the data models behind Power BI reports. They contain:

- **Tables** - Entities with columns and data types
- **Relationships** - Foreign key relationships between tables
- **Measures** - DAX formulas that encode business logic
- **Hierarchies** - Date tables and organizational hierarchies
- **Security Rules** - Row-level security (RLS) definitions

## Understanding .pbix Files

Power BI `.pbix` files are actually **ZIP archives** containing:

```
.pbix file (ZIP archive)
├── DataModel/
│   └── model.bim          # Semantic model in JSON format
├── Report/
│   └── report.json        # Visualizations and layouts
├── DiagramLayout/
│   └── layout.json        # Diagram layout
└── [DataMashup]/          # Power Query M code
```

### model.bim Structure

The `model.bim` file contains the semantic model in JSON format:

```json
{
  "name": "Supply Chain Model",
  "tables": [
    {
      "name": "Shipment",
      "columns": [
        {
          "name": "ShipmentID",
          "dataType": "string",
          "isKey": true
        },
        {
          "name": "Temperature",
          "dataType": "double"
        }
      ],
      "measures": [
        {
          "name": "High Risk Shipments",
          "expression": "CALCULATE(COUNT(...), Temperature > 25)"
        }
      ]
    }
  ],
  "relationships": [
    {
      "fromTable": "Shipment",
      "fromColumn": "CustomerID",
      "toTable": "Customer",
      "toColumn": "CustomerID",
      "cardinality": "manyToOne"
    }
  ]
}
```

## DAX Measures and Business Logic

DAX measures contain business logic that should be extracted as business rules:

### Example 1: Simple Aggregation
```dax
Total Revenue = SUM(Orders[OrderValue])
```
**Extracted as:** Aggregation measure

### Example 2: Conditional Logic (Business Rule)
```dax
High Risk Customers = 
    CALCULATE(
        DISTINCTCOUNT(Customers[CustomerID]),
        Customers[RiskScore] > 80
    )
```
**Extracted as:** Business Rule
- Condition: `RiskScore > 80`
- Classification: `HighRisk`
- Action: `classify_as_high_risk`

### Example 3: Complex Business Rule
```dax
Shipment Risk Level = 
    SWITCH(
        TRUE(),
        Shipments[Temperature] > 25, "High",
        Shipments[Vibration] > 5, "High",
        Shipments[Status] = "Delayed", "Medium",
        "Low"
    )
```
**Extracted as:** Multiple Business Rules
- Rule 1: `Temperature > 25` → `High`
- Rule 2: `Vibration > 5` → `High`
- Rule 3: `Status = "Delayed"` → `Medium`
- Default: `Low`

## Accessing .pbix Files

### From Power BI Desktop

1. Open Power BI Desktop
2. File → Save As → Save as `.pbix` file
3. Use the saved file with this tool

### From Power BI Service

1. Download the `.pbix` file from Power BI Service
2. Use the downloaded file with this tool

### Programmatic Access

Use Power BI REST API to download `.pbix` files programmatically.

## Semantic Model Versions

Power BI has different schema versions. This tool handles:
- Version 1.0 (older models)
- Version 2.0+ (current models)
- Different JSON structures

The tool automatically detects and handles version differences.

## Key Information Extracted

1. **Entities (Tables)**
   - Name, description
   - Columns (properties)
   - Data types
   - Primary keys

2. **Relationships**
   - From/to entities
   - Cardinality
   - Cross-filter direction
   - Active/inactive status

3. **Measures (DAX)**
   - Formula
   - Dependencies
   - Business logic (extracted as rules)

4. **Hierarchies**
   - Date hierarchies
   - Custom hierarchies

5. **Security Rules (RLS)**
   - Role-based filters
   - DAX filter expressions

## Limitations

- Some Power BI features may not be fully extractable
- Complex DAX formulas may require manual review
- Visualizations are not extracted (only semantic model)
- Power Query M code is not parsed (only referenced)
