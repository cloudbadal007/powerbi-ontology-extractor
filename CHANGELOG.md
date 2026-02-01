# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Features in development

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements

---

## [0.1.0] - 2025-01-31

### Added

#### Core Functionality
- **PBIX Reader**: Extract semantic models from Power BI .pbix files (ZIP-based format)
- **PowerBI Extractor**: Extract entities, relationships, measures, hierarchies, and security rules
- **DAX Parser**: Parse DAX formulas and convert to structured business rules
  - Support for CALCULATE, IF, SWITCH statements
  - Dependency identification
  - Measure type classification (aggregation, conditional, filter, time intelligence)
- **Ontology Generator**: Convert Power BI semantic models to formal ontologies
  - 70% automatic generation from Power BI models
  - Entity and property mapping
  - Relationship mapping with cardinality
  - Pattern detection (date tables, dimensions, facts)
  - Enhancement suggestions

#### Schema Management
- **Schema Mapper**: Map logical ontologies to physical data sources
- **Schema Drift Detection**: Detect column renames/deletions (prevents $4.6M mistakes!)
  - Critical drift detection
  - Rename detection with heuristic matching
  - Type change detection
  - Fix suggestions
- **Schema Binding Validation**: Validate schema bindings before AI agent execution

#### Analysis & Reporting
- **Semantic Analyzer**: Analyze multiple Power BI dashboards
  - Conflict detection across dashboards
  - Duplicate logic identification
  - Semantic debt calculation ($50K per conflict)
  - Canonical definition suggestions
  - HTML consolidation reports

#### Export Formats
- **Fabric IQ Exporter**: Export ontologies to Microsoft Fabric IQ format
- **OntoGuard Exporter**: Export to OntoGuard format for validation firewalls
- **JSON Schema Exporter**: Export to JSON Schema (draft-07) format
- **OWL Exporter**: Export to OWL/RDF format for semantic web tools

#### AI Agent Integration
- **Contract Builder**: Create semantic contracts for AI agents
  - Permission management (read, write, execute)
  - Business rule integration
  - Validation constraints
  - Audit settings
- **Semantic Contracts**: Define agent capabilities and constraints

#### CLI Tool
- **Command-line interface** with Click framework
  - `extract`: Extract ontology from .pbix file
  - `analyze`: Analyze multiple dashboards for conflicts
  - `export`: Export to different formats
  - `validate`: Validate schema bindings
  - `visualize`: Generate ontology visualizations
  - `batch`: Process multiple files

#### Visualization
- **Entity-Relationship Diagrams**: Generate ER diagrams with matplotlib
- **Interactive Graphs**: Create interactive visualizations with plotly
- **Mermaid Diagrams**: Export to Mermaid format for documentation
- **Multiple Formats**: PNG, SVG, PDF, HTML export

#### Documentation
- **Comprehensive README**: Project overview, quick start, examples
- **Getting Started Guide**: Installation and basic usage
- **Power BI Semantic Models Guide**: Understanding .pbix structure
- **Ontology Format Specification**: Ontology structure and definitions
- **Fabric IQ Integration Guide**: Exporting to Microsoft Fabric
- **Use Cases Documentation**: Real-world scenarios
- **API Reference**: Complete API documentation
- **Contributing Guide**: Guidelines for contributors
- **Examples**: Supply chain, conflict detection, customer ontology examples

#### Testing
- **Comprehensive Test Suite**: 85%+ code coverage
  - Unit tests for all core modules
  - Integration tests for complete workflows
  - Schema drift detection tests (100% coverage)
  - DAX parsing tests
  - Export format validation tests
  - CLI command tests
- **Test Fixtures**: Reusable test data and mocks
- **Pytest Configuration**: Coverage reporting and test markers

#### CI/CD
- **GitHub Actions Workflows**:
  - Multi-platform testing (Linux, Windows, macOS)
  - Multiple Python versions (3.9, 3.10, 3.11, 3.12)
  - Code quality checks (black, flake8, mypy, isort)
  - Coverage reporting with Codecov
  - Automated releases
  - Security scanning (CodeQL, dependency review)

#### Project Infrastructure
- **Issue Templates**: Bug reports, feature requests, questions
- **Pull Request Template**: Comprehensive PR checklist
- **License**: MIT License
- **Setup.py**: Package configuration for PyPI
- **Requirements Files**: Core and development dependencies

### Documentation
- Getting Started guide with 5-minute quick start
- Power BI Semantic Models explained
- Ontology Format specification
- Fabric IQ Integration guide
- Use Cases and examples
- API Reference documentation
- Contributing guidelines
- Code of conduct

### Tests
- Unit tests for all core modules (>200 test cases)
- Integration tests for complete workflows
- Schema drift detection tests (critical $4.6M prevention)
- DAX parsing tests with multiple scenarios
- Export format validation tests
- CLI command tests with Click's CliRunner
- Test fixtures and sample data
- Coverage reporting with pytest-cov

### Security
- Dependency review workflow
- CodeQL security analysis
- Secure handling of .pbix files
- No hardcoded secrets or credentials

---

## [0.0.1] - 2025-01-15

### Added
- Project initialization
- Basic project structure
- Initial README
- License (MIT)
- Basic setup.py configuration
- Initial .gitignore

---

[Unreleased]: https://github.com/cloudbadal007/powerbi-ontology-extractor/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/cloudbadal007/powerbi-ontology-extractor/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/cloudbadal007/powerbi-ontology-extractor/releases/tag/v0.0.1
