"""
Example: Extract Supply Chain Dashboard

This example demonstrates the complete workflow:
1. Extract from .pbix file
2. Analyze semantic model
3. Generate ontology
4. Add business analyst enhancements (the missing 30%)
5. Create schema bindings
6. Generate semantic contracts
7. Export to Fabric IQ and OntoGuard
8. Visualize

This references the supply chain scenario from "The Power BI Paradox" article.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from powerbi_ontology import PowerBIExtractor, OntologyGenerator, ContractBuilder, SchemaMapper
from powerbi_ontology.export import FabricIQExporter, OntoGuardExporter
from powerbi_ontology.ontology_generator import BusinessRule
from powerbi_ontology.utils.visualizer import OntologyVisualizer


def main():
    """Main example workflow."""
    print("=" * 80)
    print("PowerBI Ontology Extractor - Supply Chain Example")
    print("=" * 80)
    print()
    
    # Step 1: Extract from Power BI (the 70% auto-generation)
    print("Step 1: Extracting semantic model from Power BI...")
    pbix_file = "sample_pbix/Supply_Chain_Operations.pbix"
    
    # Check if file exists (or use a placeholder)
    if not Path(pbix_file).exists():
        print(f"  ⚠️  Note: {pbix_file} not found. This is a demonstration.")
        print("  In production, this would extract from an actual .pbix file.")
        print()
        return
    
    extractor = PowerBIExtractor(pbix_file)
    semantic_model = extractor.extract()
    
    print(f"  ✓ Extracted: {len(semantic_model.entities)} entities")
    print(f"  ✓ Extracted: {len(semantic_model.relationships)} relationships")
    print(f"  ✓ Extracted: {len(semantic_model.measures)} DAX measures")
    print()
    
    # Step 2: Generate ontology
    print("Step 2: Generating ontology...")
    generator = OntologyGenerator(semantic_model)
    ontology = generator.generate()
    
    print(f"  ✓ Generated ontology: {ontology.name}")
    print(f"  ✓ Entities: {len(ontology.entities)}")
    print(f"  ✓ Relationships: {len(ontology.relationships)}")
    print(f"  ✓ Business Rules: {len(ontology.business_rules)}")
    print()
    
    # Step 3: Review AI suggestions (business analyst review)
    print("Step 3: Reviewing AI suggestions...")
    suggestions = generator.suggest_enhancements()
    print(f"  ✓ AI suggests {len(suggestions)} enhancements")
    for suggestion in suggestions[:3]:  # Show first 3
        print(f"    • {suggestion.description}")
    print()
    
    # Step 4: Add business analyst input (the missing 30%)
    print("Step 4: Adding business analyst enhancements...")
    # Business analyst reviews and adds:
    ontology.add_business_rule(BusinessRule(
        name="RerouteApproval",
        entity="Shipment",
        condition="Shipment.RiskScore > 80",
        action="RerouteShipment",
        description="High-risk shipments require manager approval for rerouting",
        priority=1
    ))
    print("  ✓ Added business rule: RerouteApproval")
    print()
    
    # Step 5: Create schema bindings (PREVENT THE $4.6M MISTAKE!)
    print("Step 5: Creating schema bindings...")
    mapper = SchemaMapper(ontology, data_source="azure_sql")
    binding = mapper.create_binding("Shipment", "dbo.shipments")
    
    # Simulate current schema (in production, this would come from database)
    current_schema = {
        "shipment_id": "GUID",
        "customer_id": "GUID",
        "warehouse_location": "String",  # This is the critical column!
        "temperature": "Decimal",
        "status": "String"
    }
    
    # Validate schema
    result = mapper.validate_binding(binding)
    if not result.is_valid:
        print(f"  ⚠️  Validation errors: {result.errors}")
    
    # Detect drift
    drift = mapper.detect_drift(binding, current_schema)
    if drift.severity == "CRITICAL":
        print(f"  🚨 CRITICAL DRIFT DETECTED: {drift.message}")
        print(f"     This would have caused the $4.6M mistake!")
        fixes = mapper.suggest_fix(drift)
        for fix in fixes:
            print(f"     Suggested fix: {fix.description}")
    else:
        print(f"  ✓ Schema binding validated. No critical drift detected.")
    print()
    
    # Step 6: Create semantic contracts for AI agents
    print("Step 6: Creating semantic contracts for AI agents...")
    contract_builder = ContractBuilder(ontology)
    contract = contract_builder.build_contract(
        agent_name="SupplyChainMonitor",
        permissions={
            "read": ["Shipment", "Customer", "Warehouse"],
            "write": {"Shipment": ["Status"]},
            "execute": ["RerouteShipment", "NotifyCustomer"],
            "role": "Operations_Manager"
        }
    )
    print(f"  ✓ Created contract for: {contract.agent_name}")
    print(f"  ✓ Read permissions: {len(contract.permissions.read_entities)} entities")
    print(f"  ✓ Business rules: {len(contract.business_rules)}")
    print()
    
    # Step 7: Export to Fabric IQ and OntoGuard
    print("Step 7: Exporting to Fabric IQ and OntoGuard...")
    
    # Export to Fabric IQ
    fabric_exporter = FabricIQExporter(ontology)
    fabric_json = fabric_exporter.export()
    fabric_output = "output/supply_chain_fabric_iq.json"
    Path("output").mkdir(exist_ok=True)
    with open(fabric_output, 'w') as f:
        json.dump(fabric_json, f, indent=2)
    print(f"  ✓ Exported to Fabric IQ: {fabric_output}")
    
    # Export to OntoGuard
    ontoguard_exporter = OntoGuardExporter(ontology)
    ontoguard_json = ontoguard_exporter.export()
    ontoguard_output = "output/supply_chain_ontoguard.json"
    with open(ontoguard_output, 'w') as f:
        json.dump(ontoguard_json, f, indent=2)
    print(f"  ✓ Exported to OntoGuard: {ontoguard_output}")
    print()
    
    # Step 8: Visualize
    print("Step 8: Generating visualizations...")
    visualizer = OntologyVisualizer(ontology)
    
    # Save ER diagram
    diagram_output = "output/supply_chain_diagram.png"
    visualizer.save_as_image(diagram_output)
    print(f"  ✓ Saved ER diagram: {diagram_output}")
    
    # Save interactive graph
    interactive_output = "output/supply_chain_interactive.html"
    visualizer.save_interactive_html(interactive_output)
    print(f"  ✓ Saved interactive graph: {interactive_output}")
    
    # Export mermaid for README
    mermaid_code = visualizer.export_mermaid_diagram()
    mermaid_output = "output/supply_chain_mermaid.md"
    with open(mermaid_output, 'w') as f:
        f.write("```mermaid\n")
        f.write(mermaid_code)
        f.write("\n```\n")
    print(f"  ✓ Saved Mermaid diagram: {mermaid_output}")
    print()
    
    print("=" * 80)
    print("✅ Complete! From Power BI dashboard to AI-ready ontology in minutes!")
    print("   This unlocked the hidden semantic intelligence in your Power BI model.")
    print("=" * 80)


if __name__ == "__main__":
    main()
