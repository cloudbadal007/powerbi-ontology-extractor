# Examples

This directory contains example scripts demonstrating how to use PowerBI Ontology Extractor.

## Examples

### 1. `extract_supply_chain_dashboard.py`

Complete workflow example showing:
- Extracting from .pbix file
- Generating ontology
- Adding business analyst enhancements
- Creating schema bindings (prevents $4.6M mistake!)
- Generating semantic contracts
- Exporting to Fabric IQ and OntoGuard
- Visualizing the ontology

**Run:**
```bash
python examples/extract_supply_chain_dashboard.py
```

### 2. `detect_semantic_conflicts.py`

Multi-dashboard analysis example showing:
- Loading multiple .pbix files
- Detecting semantic conflicts
- Calculating semantic debt
- Suggesting canonical definitions
- Generating consolidation report

**Run:**
```bash
python examples/detect_semantic_conflicts.py
```

### 3. `generate_customer_ontology.py`

Example focused on customer data ontology extraction.

**Run:**
```bash
python examples/generate_customer_ontology.py
```

## Sample Data

The `sample_pbix/` directory should contain sample Power BI .pbix files for testing. In production, use your actual Power BI files.

**Note:** .pbix files are not included in the repository due to size and privacy concerns. You can use your own Power BI files for testing.

## Output

Example outputs are saved to the `output/` directory:
- `supply_chain_fabric_iq.json` - Fabric IQ format export
- `supply_chain_ontoguard.json` - OntoGuard format export
- `supply_chain_diagram.png` - Entity-relationship diagram
- `supply_chain_interactive.html` - Interactive visualization
- `semantic_analysis.html` - Conflict analysis report
