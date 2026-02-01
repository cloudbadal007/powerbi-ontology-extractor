"""
Example: Generate Customer Ontology

This example focuses on extracting customer-related ontologies from Power BI.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from powerbi_ontology import PowerBIExtractor, OntologyGenerator
from powerbi_ontology.export import FabricIQExporter, OntoGuardExporter


def main():
    """Generate customer ontology example."""
    print("Customer Ontology Extraction Example")
    print("=" * 80)
    
    pbix_file = "sample_pbix/Customer_Risk_Analysis.pbix"
    
    if not Path(pbix_file).exists():
        print(f"Note: {pbix_file} not found. This is a demonstration.")
        return
    
    # Extract
    extractor = PowerBIExtractor(pbix_file)
    semantic_model = extractor.extract()
    
    # Generate ontology
    generator = OntologyGenerator(semantic_model)
    ontology = generator.generate()
    
    print(f"Generated ontology: {ontology.name}")
    print(f"Entities: {len(ontology.entities)}")
    print(f"Business Rules: {len(ontology.business_rules)}")
    
    # Export
    fabric_exporter = FabricIQExporter(ontology)
    fabric_json = fabric_exporter.export()
    
    print("✓ Exported to Fabric IQ format")


if __name__ == "__main__":
    main()
