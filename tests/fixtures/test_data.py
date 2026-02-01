"""
Test data constants for PowerBI Ontology Extractor tests.
"""

# Sample DAX formulas
SIMPLE_DAX_SUM = "Total Revenue = SUM(Orders[OrderValue])"

CONDITIONAL_DAX = """
High Risk Customers = 
    CALCULATE(
        DISTINCTCOUNT(Customers[CustomerID]),
        Customers[RiskScore] > 80
    )
"""

SWITCH_DAX = """
Shipment Risk Level = 
    SWITCH(
        TRUE(),
        Shipments[Temperature] > 25, "High",
        Shipments[Vibration] > 5, "High",
        Shipments[Status] = "Delayed", "Medium",
        "Low"
    )
"""

CALCULATE_FILTER_DAX = """
At Risk Revenue = 
    CALCULATE(
        SUM(Orders[OrderValue]),
        Customers[RiskScore] > 80,
        Orders[Status] = "Pending"
    )
"""

TIME_INTELLIGENCE_DAX = "YTD Revenue = TOTALYTD(SUM(Orders[OrderValue]), Calendar[Date])"

# Expected business rules
EXPECTED_HIGH_RISK_RULE = {
    "condition": "RiskScore > 80",
    "entity": "Customer",
    "classification": "HighRisk"
}

EXPECTED_TEMPERATURE_RULE = {
    "condition": "Temperature > 25",
    "entity": "Shipment",
    "classification": "High"
}

# Schema drift scenarios
SCHEMA_WITH_DRIFT = {
    "warehouses": {
        "warehouse_id": "GUID",
        "facility_id": "String",  # 'warehouse_location' was renamed!
        "status": "String"
    }
}

SCHEMA_WITHOUT_DRIFT = {
    "warehouses": {
        "warehouse_id": "GUID",
        "warehouse_location": "String",  # Expected column exists
        "status": "String"
    }
}
