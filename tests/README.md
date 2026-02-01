# Test Suite for PowerBI Ontology Extractor

## Overview

Comprehensive pytest test suite with >85% code coverage.

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=powerbi_ontology --cov-report=html --cov-report=term
```

### Run specific test file
```bash
pytest tests/test_schema_mapper.py -v
```

### Run critical tests (e.g., $4.6M prevention)
```bash
pytest -m critical
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_pbix_reader.py      # PBIX file reading tests
├── test_extractor.py        # Semantic model extraction tests
├── test_dax_parser.py       # DAX parsing and business rule extraction
├── test_ontology_generator.py  # Ontology generation tests
├── test_schema_mapper.py    # Schema drift detection (CRITICAL!)
├── test_contract_builder.py # Semantic contract tests
├── test_analyzers.py        # Conflict detection and semantic debt
├── test_exports/            # Export format tests
│   ├── test_fabric_iq_export.py
│   ├── test_ontoguard_export.py
│   ├── test_json_schema_export.py
│   └── test_owl_export.py
├── test_cli.py              # CLI command tests
├── test_integration.py      # End-to-end workflow tests
└── fixtures/                # Test data and fixtures
    ├── sample_model.json
    ├── sample_ontology.json
    └── test_data.py
```

## Key Test Scenarios

### 1. Schema Drift Detection (The $4.6M Prevention Test)

Located in `test_schema_mapper.py`:

```python
def test_schema_drift_detection_prevents_4_6m_mistake():
    """
    Test that schema drift is detected when column is renamed.
    This is the $4.6M logistics disaster prevention test!
    """
    # Tests the critical scenario where warehouse_location is renamed to facility_id
    # and the system detects it before AI agents break
```

### 2. DAX Business Rule Extraction

Located in `test_dax_parser.py`:

```python
def test_parse_business_rule_from_dax():
    """Test extracting business rule from DAX CALCULATE."""
    # Tests parsing DAX formulas into structured business rules
```

### 3. 70% Auto-Generation

Located in `test_ontology_generator.py`:

```python
def test_70_percent_auto_generation():
    """Test that 70% of ontology is auto-generated from Power BI."""
    # Verifies automatic extraction and generation
```

## Coverage Requirements

- **Overall**: >85% coverage
- **Schema Drift Detection**: 100% coverage (CRITICAL)
- **Business Rule Extraction**: 100% coverage
- **Error Handling**: All error paths tested
- **Edge Cases**: Comprehensive edge case coverage

## Fixtures

Key fixtures in `conftest.py`:

- `sample_pbix_path`: Sample .pbix file for testing
- `sample_semantic_model`: Power BI semantic model
- `sample_ontology`: Generated ontology
- `mock_database_schema`: Database schema for drift testing
- `drifted_database_schema`: Schema with drift (renamed columns)
- `multiple_semantic_models`: Multiple models for conflict detection

## Running Specific Test Categories

```bash
# Run only unit tests
pytest tests/test_*.py -k "not integration"

# Run only integration tests
pytest tests/test_integration.py

# Run tests for specific module
pytest tests/test_schema_mapper.py

# Run with verbose output
pytest -v

# Run with coverage and fail if below threshold
pytest --cov=powerbi_ontology --cov-fail-under=85
```

## Continuous Integration

Tests are configured to run in CI/CD with:
- Python 3.9, 3.10, 3.11, 3.12
- Coverage reporting
- Code quality checks

See `.github/workflows/tests.yml` for CI configuration.
