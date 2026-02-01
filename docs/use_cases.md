# Use Cases

Real-world scenarios and use cases for PowerBI Ontology Extractor.

## 1. Supply Chain Optimization

### Problem
A logistics company has 50+ Power BI dashboards tracking shipments, but AI agents can't access the business logic embedded in DAX measures.

### Solution
Extract ontologies from supply chain dashboards and deploy AI agents for real-time monitoring.

### Implementation

```python
# Extract from supply chain dashboard
extractor = PowerBIExtractor("Supply_Chain_Operations.pbix")
semantic_model = extractor.extract()

# Generate ontology
ontology = OntologyGenerator(semantic_model).generate()

# Business rules automatically extracted:
# - "High Risk" = Temperature > 25 OR Vibration > 5
# - "At-Risk Customer" = RiskScore > 80 AND has delayed shipments

# Create schema bindings (PREVENT THE $4.6M MISTAKE!)
mapper = SchemaMapper(ontology, "azure_sql")
binding = mapper.create_binding("Shipment", "dbo.shipments")

# Validate before deploying agents
drift = mapper.detect_drift(binding, current_schema)
if drift.severity == "CRITICAL":
    # Agent stops here - prevents disaster!
    raise SchemaDriftError("Critical schema drift detected")

# Export for AI agents
fabric_exporter = FabricIQExporter(ontology)
fabric_json = fabric_exporter.export()

# Deploy AI agents with semantic contracts
deploy_supply_chain_agents(ontology)
```

### Results
- ✅ Real-time shipment monitoring
- ✅ Automatic risk detection
- ✅ Schema drift prevention ($4.6M mistake avoided!)
- ✅ Unified ontology across 50+ dashboards

---

## 2. Customer Risk Management

### Problem
Multiple departments define "High Risk Customer" differently across 20 Power BI dashboards, causing inconsistent risk assessments.

### Solution
Extract all customer risk definitions, detect conflicts, and create a unified ontology.

### Implementation

```python
# Load all customer risk dashboards
dashboards = [
    "Finance_Customer_Risk.pbix",
    "Sales_Customer_Risk.pbix",
    "Operations_Customer_Risk.pbix"
]

semantic_models = []
for dashboard in dashboards:
    extractor = PowerBIExtractor(dashboard)
    semantic_models.append(extractor.extract())

# Analyze for conflicts
analyzer = SemanticAnalyzer(semantic_models)
conflicts = analyzer.detect_conflicts()

# Found conflicts:
# - Finance: HighRiskCustomer = RiskScore > 80
# - Sales: HighRiskCustomer = ChurnProbability > 0.7
# - Operations: HighRiskCustomer = PaymentDelay > 30 days

# Calculate semantic debt
debt_report = analyzer.calculate_semantic_debt()
# Result: $600K in semantic debt (12 conflicts × $50K)

# Suggest canonical definition
canonical_defs = analyzer.suggest_canonical_definitions()
# Suggests: Most common definition as canonical

# Generate unified ontology
unified_ontology = create_unified_ontology(semantic_models, canonical_defs)

# Deploy to AI agents
deploy_risk_management_agents(unified_ontology)
```

### Results
- ✅ Unified risk definition
- ✅ $600K semantic debt identified
- ✅ Consistent risk assessment across departments
- ✅ AI agents use canonical definition

---

## 3. Financial Reconciliation

### Problem
Financial dashboards have conflicting definitions of "Revenue" and "Profit" across different business units.

### Solution
Extract financial ontologies, detect conflicts, and consolidate into a single source of truth.

### Implementation

```python
# Extract from all financial dashboards
financial_dashboards = glob.glob("Finance/*.pbix")
models = [PowerBIExtractor(d).extract() for d in financial_dashboards]

# Analyze conflicts
analyzer = SemanticAnalyzer(models)
conflicts = analyzer.detect_conflicts()

# Generate consolidation report
analyzer.generate_consolidation_report("financial_reconciliation.html")

# Create unified financial ontology
unified = create_unified_ontology(models)

# Export for reconciliation agents
export_to_reconciliation_system(unified)
```

### Results
- ✅ Single source of truth for financial metrics
- ✅ Automated reconciliation
- ✅ Conflict resolution
- ✅ Compliance reporting

---

## 4. Cross-Department Consolidation

### Problem
Enterprise has 200+ Power BI dashboards with duplicate logic and conflicting definitions.

### Solution
Analyze all dashboards, identify duplicates, and suggest consolidation opportunities.

### Implementation

```python
# Batch process all dashboards
all_dashboards = find_all_pbix_files("Enterprise/")

# Extract all models
all_models = []
for pbix in all_dashboards:
    try:
        model = PowerBIExtractor(pbix).extract()
        all_models.append(model)
    except Exception as e:
        log_error(pbix, e)

# Comprehensive analysis
analyzer = SemanticAnalyzer(all_models)

# Detect conflicts
conflicts = analyzer.detect_conflicts()
print(f"Found {len(conflicts)} conflicts")

# Identify duplicates
duplications = analyzer.identify_duplicate_logic()
print(f"Found {len(duplications)} duplicate measures")

# Calculate total semantic debt
debt = analyzer.calculate_semantic_debt()
print(f"Total semantic debt: ${debt.total_cost:,.0f}")

# Generate consolidation plan
plan = generate_consolidation_plan(conflicts, duplications)
```

### Results
- ✅ Identified $2M+ in semantic debt
- ✅ Found 50+ duplicate measures
- ✅ Consolidation roadmap created
- ✅ Cost savings identified

---

## 5. AI Agent Deployment

### Problem
Need to deploy AI agents that understand Power BI business logic without manual configuration.

### Solution
Extract ontologies, create semantic contracts, and deploy agents with automatic understanding.

### Implementation

```python
# Extract ontology
extractor = PowerBIExtractor("Customer_Dashboard.pbix")
ontology = extractor.extract().to_ontology()

# Create semantic contract for AI agent
contract_builder = ContractBuilder(ontology)
contract = contract_builder.build_contract(
    agent_name="CustomerServiceAgent",
    permissions={
        "read": ["Customer", "Order", "SupportTicket"],
        "write": {"SupportTicket": ["Status", "Resolution"]},
        "execute": ["EscalateTicket", "NotifyCustomer"],
        "role": "Customer_Service"
    }
)

# Add business rules from Power BI
for rule in ontology.business_rules:
    if "Customer" in rule.entity:
        contract.add_business_rule(rule)

# Export contract
contract_json = contract_builder.export_contract(contract, "ontoguard")

# Deploy agent with contract
deploy_ai_agent("CustomerServiceAgent", contract_json, ontology)
```

### Results
- ✅ Agents understand Power BI business logic automatically
- ✅ Semantic contracts enforce permissions
- ✅ Business rules applied automatically
- ✅ No manual configuration needed

---

## 6. Schema Drift Prevention

### Problem
Data team renames columns, causing AI agents to break (the $4.6M mistake scenario).

### Solution
Use schema drift detection to catch changes before agents break.

### Implementation

```python
# Create schema binding
mapper = SchemaMapper(ontology, "azure_sql")
binding = mapper.create_binding("Warehouse", "warehouses")
binding.property_mappings["Location"] = "warehouse_location"

# Data team renames column: warehouse_location → facility_id
# This would cause the $4.6M mistake!

# Before agent execution, validate schema
current_schema = get_current_database_schema("warehouses")
drift = mapper.detect_drift(binding, current_schema)

if drift.severity == "CRITICAL":
    # Agent stops execution - prevents disaster!
    raise SchemaDriftDetectedError(
        f"CRITICAL: Column 'warehouse_location' not found. "
        f"Was it renamed to 'facility_id'?"
    )
    
    # Get suggested fixes
    fixes = mapper.suggest_fix(drift)
    # Suggests: "Map Location to facility_id"
    
    # Update binding
    binding.property_mappings["Location"] = "facility_id"
    
    # Retry validation
    drift = mapper.detect_drift(binding, current_schema)
    assert drift.severity != "CRITICAL"
```

### Results
- ✅ Prevents $4.6M mistake scenario
- ✅ Catches schema changes before agents break
- ✅ Suggests fixes automatically
- ✅ Zero-downtime schema updates

---

## 7. Multi-Format Export

### Problem
Need to use ontologies with different tools (Fabric IQ, OntoGuard, semantic web tools).

### Solution
Export to multiple formats from a single Power BI source.

### Implementation

```python
# Generate ontology once
ontology = extract_and_generate("dashboard.pbix")

# Export to all formats
formats = {
    "fabric_iq": FabricIQExporter(ontology).export(),
    "ontoguard": OntoGuardExporter(ontology).export(),
    "json_schema": JSONSchemaExporter(ontology).export(),
    "owl": OWLExporter(ontology).export(format="xml")
}

# Use with different tools
deploy_to_fabric(formats["fabric_iq"])
deploy_to_ontoguard(formats["ontoguard"])
load_to_triple_store(formats["owl"])
validate_with_json_schema(formats["json_schema"])
```

### Results
- ✅ Single source, multiple formats
- ✅ Works with all tools
- ✅ No format conversion needed
- ✅ Consistent ontology across tools

---

## 8. Real-Time Ontology Updates

### Problem
Power BI dashboards are updated frequently, need to keep ontologies in sync.

### Solution
Automated extraction and validation pipeline.

### Implementation

```python
# Scheduled job: Extract and validate daily
def daily_ontology_update():
    # Extract from latest Power BI
    ontology = extract_and_generate("dashboard.pbix")
    
    # Validate schema bindings
    mapper = SchemaMapper(ontology, "azure_sql")
    for entity in ontology.entities:
        binding = mapper.create_binding(entity.name, get_table_name(entity))
        drift = mapper.detect_drift(binding, get_current_schema())
        
        if drift.severity == "CRITICAL":
            send_alert("Schema drift detected!", drift)
        else:
            # Update ontology
            update_ontology_in_fabric(ontology)
            notify_agents("Ontology updated")
```

### Results
- ✅ Always up-to-date ontologies
- ✅ Automatic drift detection
- ✅ Proactive alerts
- ✅ Zero manual intervention

---

## Success Metrics

### Before Using This Tool
- ❌ 20+ conflicting definitions of "Customer"
- ❌ $600K+ in semantic debt
- ❌ AI agents break when schemas change
- ❌ Manual ontology creation (weeks per ontology)
- ❌ No visibility into semantic conflicts

### After Using This Tool
- ✅ Unified definitions across all dashboards
- ✅ Semantic debt identified and quantified
- ✅ Schema drift detected before agents break
- ✅ Automatic ontology generation (minutes)
- ✅ Complete visibility into semantic landscape

---

## Getting Started

Choose a use case that matches your needs:

1. **Single Dashboard**: Start with [Getting Started Guide](getting_started.md)
2. **Multiple Dashboards**: See [Conflict Detection Example](../examples/detect_semantic_conflicts.py)
3. **AI Agent Deployment**: See [Contract Builder API](api_reference.md#contractbuilder)
4. **Fabric Integration**: See [Fabric IQ Integration Guide](fabric_iq_integration.md)

---

**Ready to unlock the semantic intelligence in your Power BI dashboards?** 🚀
