"""
Tests for PBIXReader utility.
"""

import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from powerbi_ontology.utils.pbix_reader import PBIXReader


class TestPBIXReader:
    """Test PBIXReader class."""
    
    def test_init_with_valid_file(self, sample_pbix_path):
        """Test initialization with valid .pbix file."""
        reader = PBIXReader(str(sample_pbix_path))
        assert reader.pbix_path == Path(sample_pbix_path)
    
    def test_init_with_missing_file(self):
        """Test initialization with non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            PBIXReader("nonexistent.pbix")
    
    def test_extract_to_temp(self, sample_pbix_path):
        """Test extraction to temporary directory."""
        reader = PBIXReader(str(sample_pbix_path))
        temp_dir = reader.extract_to_temp()
        
        assert temp_dir.exists()
        assert temp_dir.is_dir()
        assert (temp_dir / "DataModel" / "model.bim").exists()
    
    def test_extract_to_temp_corrupted_file(self, corrupted_pbix_path):
        """Test extraction with corrupted ZIP file."""
        reader = PBIXReader(str(corrupted_pbix_path))
        with pytest.raises(ValueError, match="Invalid .pbix file format"):
            reader.extract_to_temp()
    
    def test_read_model(self, sample_pbix_path):
        """Test reading model.bim file."""
        reader = PBIXReader(str(sample_pbix_path))
        model = reader.read_model()
        
        assert isinstance(model, dict)
        assert "name" in model
        assert "tables" in model
        assert model["name"] == "Test Model"
    
    def test_read_model_missing_file(self, missing_model_pbix_path):
        """Test reading model when model.bim is missing."""
        reader = PBIXReader(str(missing_model_pbix_path))
        with pytest.raises(FileNotFoundError, match="model.bim not found"):
            reader.read_model()
    
    def test_get_tables(self, sample_pbix_path):
        """Test extracting tables from model."""
        reader = PBIXReader(str(sample_pbix_path))
        tables = reader.get_tables()
        
        assert len(tables) == 2
        assert tables[0]["name"] == "Shipment"
        assert tables[1]["name"] == "Customer"
        assert "columns" in tables[0]
    
    def test_get_relationships(self, sample_pbix_path):
        """Test extracting relationships from model."""
        reader = PBIXReader(str(sample_pbix_path))
        relationships = reader.get_relationships()
        
        assert len(relationships) == 1
        assert relationships[0]["fromTable"] == "Shipment"
        assert relationships[0]["toTable"] == "Customer"
    
    def test_get_measures(self, sample_pbix_path):
        """Test extracting measures from model."""
        reader = PBIXReader(str(sample_pbix_path))
        measures = reader.get_measures()
        
        assert len(measures) == 1
        assert measures[0]["name"] == "High Risk Shipments"
        assert "expression" in measures[0]
        assert "Temperature" in measures[0]["expression"]
    
    def test_read_report(self, sample_pbix_path):
        """Test reading report.json (optional)."""
        reader = PBIXReader(str(sample_pbix_path))
        report = reader.read_report()
        
        # Report may or may not exist
        assert report is None or isinstance(report, dict)
    
    def test_context_manager(self, sample_pbix_path):
        """Test using PBIXReader as context manager."""
        with PBIXReader(str(sample_pbix_path)) as reader:
            model = reader.read_model()
            assert model is not None
        
        # Cleanup should have been called
        assert reader.temp_dir is None or not reader.temp_dir.exists()
    
    def test_cleanup(self, sample_pbix_path):
        """Test cleanup of temporary directory."""
        reader = PBIXReader(str(sample_pbix_path))
        temp_dir = reader.extract_to_temp()
        assert temp_dir.exists()
        
        reader.cleanup()
        assert reader.temp_dir is None
    
    def test_read_model_different_schema_versions(self, temp_dir):
        """Test reading models with different Power BI schema versions."""
        # Test version 1.0 format
        pbix_v1 = temp_dir / "model_v1.pbix"
        with zipfile.ZipFile(pbix_v1, 'w') as zip_file:
            model_data = {
                "model": {
                    "name": "Test Model V1",
                    "tables": []
                }
            }
            zip_file.writestr("DataModel/model.bim", json.dumps(model_data))
        
        reader = PBIXReader(str(pbix_v1))
        model = reader.read_model()
        assert model["model"]["name"] == "Test Model V1"
    
    def test_get_tables_empty_model(self, temp_dir):
        """Test getting tables from empty model."""
        pbix_empty = temp_dir / "empty.pbix"
        with zipfile.ZipFile(pbix_empty, 'w') as zip_file:
            model_data = {"name": "Empty Model", "tables": []}
            zip_file.writestr("DataModel/model.bim", json.dumps(model_data))
        
        reader = PBIXReader(str(pbix_empty))
        tables = reader.get_tables()
        assert len(tables) == 0
    
    def test_get_measures_from_multiple_tables(self, temp_dir):
        """Test extracting measures from multiple tables."""
        pbix_multi = temp_dir / "multi_table.pbix"
        with zipfile.ZipFile(pbix_multi, 'w') as zip_file:
            model_data = {
                "name": "Multi Table Model",
                "tables": [
                    {
                        "name": "Table1",
                        "measures": [
                            {"name": "Measure1", "expression": "SUM(Table1[Value])"}
                        ]
                    },
                    {
                        "name": "Table2",
                        "measures": [
                            {"name": "Measure2", "expression": "COUNT(Table2[ID])"}
                        ]
                    }
                ]
            }
            zip_file.writestr("DataModel/model.bim", json.dumps(model_data))
        
        reader = PBIXReader(str(pbix_multi))
        measures = reader.get_measures()
        assert len(measures) == 2
        assert measures[0]["name"] == "Measure1"
        assert measures[1]["name"] == "Measure2"
    
    def test_invalid_json_in_model_bim(self, temp_dir):
        """Test handling invalid JSON in model.bim."""
        pbix_invalid = temp_dir / "invalid_json.pbix"
        with zipfile.ZipFile(pbix_invalid, 'w') as zip_file:
            zip_file.writestr("DataModel/model.bim", "Not valid JSON {")
        
        reader = PBIXReader(str(pbix_invalid))
        with pytest.raises(ValueError, match="Invalid JSON"):
            reader.read_model()

    def test_read_model_from_tmdl_project_directory(self, temp_dir):
        """Test reading semantic model from PBIP/TMDL project directory."""
        project_dir = temp_dir / "ANZ Inventory Report"
        tables_dir = project_dir / "definition" / "tables"
        tables_dir.mkdir(parents=True)

        (tables_dir / "Shipment.tmdl").write_text(
            """
table Shipment
    column ShipmentID
        dataType: string
    column Temperature
        dataType: double
    measure High Risk Shipments = CALCULATE(COUNT(Shipment[ShipmentID]), Shipment[Temperature] > 25)
""".strip(),
            encoding="utf-8",
        )
        (tables_dir / "Customer.tmdl").write_text(
            """
table Customer
    column CustomerID
        dataType: string
""".strip(),
            encoding="utf-8",
        )
        (project_dir / "definition" / "relationships.tmdl").write_text(
            """
relationship ShipmentCustomer
    fromColumn: Shipment[CustomerID]
    toColumn: Customer[CustomerID]
""".strip(),
            encoding="utf-8",
        )

        reader = PBIXReader(str(project_dir))
        model = reader.read_model()

        assert model["name"] == "ANZ Inventory Report"
        assert len(model["tables"]) == 2
        assert any(t["name"] == "Shipment" for t in model["tables"])
        assert len(model["relationships"]) == 1

    def test_read_model_from_pbip_file(self, temp_dir):
        """Test reading semantic model when path points to .pbip descriptor file."""
        project_dir = temp_dir / "InventoryProject"
        tables_dir = project_dir / "definition" / "tables"
        tables_dir.mkdir(parents=True)

        (project_dir / "InventoryProject.pbip").write_text("{}", encoding="utf-8")
        (tables_dir / "Product.tmdl").write_text(
            """
table Product
    column ProductID
        dataType: string
""".strip(),
            encoding="utf-8",
        )

        reader = PBIXReader(str(project_dir / "InventoryProject.pbip"))
        model = reader.read_model()

        assert model["name"] == "InventoryProject"
        assert len(model["tables"]) == 1
        assert model["tables"][0]["name"] == "Product"
