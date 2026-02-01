"""
Pytest fixtures for PowerBI Ontology Extractor tests.
"""

import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from powerbi_ontology.extractor import SemanticModel, Entity, Property, Relationship, Measure
from powerbi_ontology.ontology_generator import Ontology, OntologyEntity, OntologyProperty, OntologyRelationship, BusinessRule


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_pbix_path(temp_dir):
    """Create a sample .pbix file (ZIP archive) for testing."""
    pbix_path = temp_dir / "sample_model.pbix"
    
    # Create a ZIP file with model.bim structure
    with zipfile.ZipFile(pbix_path, 'w') as zip_file:
        # Create model.bim JSON
        model_data = {
            "name": "Test Model",
            "tables": [
                {
                    "name": "Shipment",
                    "description": "Shipment entity",
                    "columns": [
                        {
                            "name": "ShipmentID",
                            "dataType": "string",
                            "isKey": True,
                            "isNullable": False,
                            "description": "Primary key"
                        },
                        {
                            "name": "Temperature",
                            "dataType": "double",
                            "isNullable": True,
                            "description": "Temperature reading"
                        },
                        {
                            "name": "Status",
                            "dataType": "string",
                            "isNullable": False,
                            "description": "Shipment status"
                        }
                    ],
                    "measures": [
                        {
                            "name": "High Risk Shipments",
                            "expression": "CALCULATE(COUNT(Shipment[ShipmentID]), Shipment[Temperature] > 25)",
                            "description": "Count of high-risk shipments"
                        }
                    ]
                },
                {
                    "name": "Customer",
                    "columns": [
                        {
                            "name": "CustomerID",
                            "dataType": "string",
                            "isKey": True,
                            "isNullable": False
                        },
                        {
                            "name": "RiskScore",
                            "dataType": "double",
                            "isNullable": True
                        }
                    ],
                    "measures": []
                }
            ],
            "relationships": [
                {
                    "name": "Shipment_Customer",
                    "fromTable": "Shipment",
                    "fromColumn": "CustomerID",
                    "toTable": "Customer",
                    "toColumn": "CustomerID",
                    "fromCardinality": "many",
                    "toCardinality": "one",
                    "crossFilteringBehavior": "singleDirection",
                    "isActive": True
                }
            ],
            "roles": []
        }
        
        # Write model.bim to ZIP
        zip_file.writestr("DataModel/model.bim", json.dumps(model_data, indent=2))
    
    return pbix_path


@pytest.fixture
def corrupted_pbix_path(temp_dir):
    """Create a corrupted .pbix file for testing error handling."""
    pbix_path = temp_dir / "corrupted.pbix"
    pbix_path.write_bytes(b"Not a valid ZIP file")
    return pbix_path


@pytest.fixture
def missing_model_pbix_path(temp_dir):
    """Create a .pbix file without model.bim for testing."""
    pbix_path = temp_dir / "missing_model.pbix"
    with zipfile.ZipFile(pbix_path, 'w') as zip_file:
        zip_file.writestr("Report/report.json", '{"name": "Test Report"}')
    return pbix_path


@pytest.fixture
def sample_semantic_model():
    """Sample Power BI semantic model for testing."""
    return SemanticModel(
        name="Test Model",
        source_file="test.pbix",
        entities=[
            Entity(
                name="Shipment",
                description="Shipment entity",
                properties=[
                    Property(
                        name="ShipmentID",
                        data_type="String",
                        required=True,
                        unique=True,
                        description="Primary key"
                    ),
                    Property(
                        name="Temperature",
                        data_type="Decimal",
                        required=False,
                        unique=False,
                        description="Temperature reading"
                    )
                ],
                source_table="Shipment",
                primary_key="ShipmentID"
            ),
            Entity(
                name="Customer",
                description="Customer entity",
                properties=[
                    Property(
                        name="CustomerID",
                        data_type="String",
                        required=True,
                        unique=True
                    ),
                    Property(
                        name="RiskScore",
                        data_type="Decimal",
                        required=False
                    )
                ],
                source_table="Customer",
                primary_key="CustomerID"
            )
        ],
        relationships=[
            Relationship(
                from_entity="Shipment",
                from_property="CustomerID",
                to_entity="Customer",
                to_property="CustomerID",
                cardinality="many-to-one",
                cross_filter_direction="single",
                is_active=True,
                name="Shipment_Customer"
            )
        ],
        measures=[
            Measure(
                name="High Risk Shipments",
                dax_formula="CALCULATE(COUNT(Shipment[ShipmentID]), Shipment[Temperature] > 25)",
                description="Count of high-risk shipments",
                table="Shipment",
                dependencies=["Shipment.ShipmentID", "Shipment.Temperature"]
            )
        ],
        hierarchies=[],
        security_rules=[],
        metadata={}
    )


@pytest.fixture
def sample_ontology(sample_semantic_model):
    """Sample generated ontology for testing."""
    from powerbi_ontology.ontology_generator import OntologyGenerator
    
    generator = OntologyGenerator(sample_semantic_model)
    return generator.generate()


@pytest.fixture
def mock_database_schema():
    """Mock database schema for testing schema drift."""
    return {
        "shipments": {
            "shipment_id": "GUID",
            "customer_id": "GUID",
            "warehouse_location": "String",  # This is the critical column!
            "temperature": "Decimal",
            "status": "String"
        },
        "customers": {
            "customer_id": "GUID",
            "risk_score": "Decimal"
        }
    }


@pytest.fixture
def drifted_database_schema():
    """Database schema with drift (renamed column)."""
    return {
        "shipments": {
            "shipment_id": "GUID",
            "customer_id": "GUID",
            "facility_id": "String",  # 'warehouse_location' was renamed!
            "temperature": "Decimal",
            "status": "String"
        }
    }


@pytest.fixture
def sample_dax_measures():
    """Sample DAX measures for testing."""
    return {
        "simple_sum": "Total Revenue = SUM(Orders[OrderValue])",
        "conditional": """
            High Risk Customers = 
                CALCULATE(
                    DISTINCTCOUNT(Customers[CustomerID]),
                    Customers[RiskScore] > 80
                )
        """,
        "switch": """
            Shipment Risk Level = 
                SWITCH(
                    TRUE(),
                    Shipments[Temperature] > 25, "High",
                    Shipments[Vibration] > 5, "High",
                    Shipments[Status] = "Delayed", "Medium",
                    "Low"
                )
        """,
        "calculate_filter": """
            At Risk Revenue = 
                CALCULATE(
                    SUM(Orders[OrderValue]),
                    Customers[RiskScore] > 80,
                    Orders[Status] = "Pending"
                )
        """,
        "time_intelligence": "YTD Revenue = TOTALYTD(SUM(Orders[OrderValue]), Calendar[Date])"
    }


@pytest.fixture
def sample_contract_permissions():
    """Sample contract permissions for testing."""
    return {
        "read": ["Shipment", "Customer", "Warehouse"],
        "write": {"Shipment": ["Status"]},
        "execute": ["RerouteShipment", "NotifyCustomer"],
        "role": "Operations_Manager",
        "filters": {
            "Shipment": "Status = 'In Transit'"
        }
    }


@pytest.fixture
def multiple_semantic_models():
    """Multiple semantic models for conflict detection testing."""
    return [
        SemanticModel(
            name="Finance Dashboard",
            source_file="Finance.pbix",
            entities=[
                Entity(
                    name="Customer",
                    properties=[
                        Property(name="CustomerID", data_type="String", required=True),
                        Property(name="RiskScore", data_type="Decimal")
                    ]
                )
            ],
            measures=[
                Measure(
                    name="High Risk Customer",
                    dax_formula="CALCULATE(COUNT(Customers[CustomerID]), Customers[RiskScore] > 80)",
                    table="Customer"
                )
            ]
        ),
        SemanticModel(
            name="Sales Dashboard",
            source_file="Sales.pbix",
            entities=[
                Entity(
                    name="Customer",
                    properties=[
                        Property(name="CustomerID", data_type="String", required=True),
                        Property(name="ChurnProbability", data_type="Decimal")
                    ]
                )
            ],
            measures=[
                Measure(
                    name="High Risk Customer",
                    dax_formula="CALCULATE(COUNT(Customers[CustomerID]), Customers[ChurnProbability] > 0.7)",
                    table="Customer"
                )
            ]
        )
    ]


@pytest.fixture
def sample_business_rule():
    """Sample business rule for testing."""
    return BusinessRule(
        name="HighRiskShipmentDetection",
        entity="Shipment",
        condition="Temperature > 25 OR Vibration > 5",
        action="classify_as_high_risk",
        classification="HighRisk",
        description="Detect high-risk shipments",
        priority=1,
        source_measure="High Risk Shipments"
    )
