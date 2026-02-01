"""
PBIX Reader Utility

Reads Power BI .pbix files (which are ZIP archives) and extracts semantic model data.
"""

import json
import logging
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PBIXReader:
    """
    Reads Power BI .pbix files and extracts semantic model information.
    
    .pbix files are ZIP archives containing:
    - DataModel/model.bim (the semantic model in JSON)
    - Report/report.json (visualizations)
    - DiagramLayout/layout.json
    - [DataMashup] (Power Query M code)
    """

    def __init__(self, pbix_path: str):
        """
        Initialize PBIX reader.
        
        Args:
            pbix_path: Path to the .pbix file
        """
        self.pbix_path = Path(pbix_path)
        if not self.pbix_path.exists():
            raise FileNotFoundError(f"Power BI file not found: {pbix_path}")
        
        self.temp_dir: Optional[Path] = None
        self._model_data: Optional[Dict] = None
        self._report_data: Optional[Dict] = None

    def __enter__(self):
        """Context manager entry."""
        self.extract_to_temp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup temp files."""
        self.cleanup()

    def extract_to_temp(self) -> Path:
        """
        Extract .pbix file to temporary directory.
        
        Returns:
            Path to temporary extraction directory
        """
        if self.temp_dir:
            return self.temp_dir

        try:
            self.temp_dir = Path(tempfile.mkdtemp(prefix="pbix_extract_"))
            
            with zipfile.ZipFile(self.pbix_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            logger.info(f"Extracted .pbix file to {self.temp_dir}")
            return self.temp_dir
        except zipfile.BadZipFile:
            raise ValueError(f"Invalid .pbix file format: {self.pbix_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to extract .pbix file: {e}")

    def read_model(self) -> Dict:
        """
        Read and parse the model.bim file (semantic model).
        
        Returns:
            Parsed JSON model data
        """
        if self._model_data:
            return self._model_data

        if not self.temp_dir:
            self.extract_to_temp()

        # Try different possible paths for model.bim
        possible_paths = [
            self.temp_dir / "DataModel" / "model.bim",
            self.temp_dir / "model.bim",
            self.temp_dir / "DataModelSchema",
        ]

        model_path = None
        for path in possible_paths:
            if path.exists():
                model_path = path
                break

        if not model_path:
            # Try to find any .bim file
            bim_files = list(self.temp_dir.rglob("*.bim"))
            if bim_files:
                model_path = bim_files[0]
            else:
                raise FileNotFoundError(
                    f"model.bim not found in .pbix file: {self.pbix_path}"
                )

        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                self._model_data = json.load(f)
            logger.info(f"Successfully read model.bim from {model_path}")
            return self._model_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in model.bim: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to read model.bim: {e}")

    def read_report(self) -> Optional[Dict]:
        """
        Read and parse the report.json file (optional, for context).
        
        Returns:
            Parsed JSON report data or None if not found
        """
        if self._report_data is not None:
            return self._report_data

        if not self.temp_dir:
            self.extract_to_temp()

        report_path = self.temp_dir / "Report" / "report.json"
        if not report_path.exists():
            logger.warning("report.json not found in .pbix file")
            self._report_data = None
            return None

        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                self._report_data = json.load(f)
            return self._report_data
        except Exception as e:
            logger.warning(f"Failed to read report.json: {e}")
            self._report_data = None
            return None

    def get_tables(self) -> List[Dict]:
        """
        Extract table definitions from model.
        
        Returns:
            List of table definitions
        """
        model = self.read_model()
        
        # Handle different Power BI schema versions
        if isinstance(model, dict):
            if "model" in model:
                model = model["model"]
            if "tables" in model:
                return model["tables"]
            if "model" in model and "tables" in model["model"]:
                return model["model"]["tables"]
        
        return []

    def get_relationships(self) -> List[Dict]:
        """
        Extract relationship definitions from model.
        
        Returns:
            List of relationship definitions
        """
        model = self.read_model()
        
        # Handle different Power BI schema versions
        if isinstance(model, dict):
            if "model" in model:
                model = model["model"]
            if "relationships" in model:
                return model["relationships"]
            if "model" in model and "relationships" in model["model"]:
                return model["model"]["relationships"]
        
        return []

    def get_measures(self) -> List[Dict]:
        """
        Extract DAX measures from all tables.
        
        Returns:
            List of measure definitions
        """
        tables = self.get_tables()
        measures = []
        
        for table in tables:
            if "measures" in table:
                for measure in table["measures"]:
                    measure["table"] = table.get("name", "Unknown")
                    measures.append(measure)
        
        return measures

    def cleanup(self):
        """Remove temporary extraction directory."""
        if self.temp_dir and self.temp_dir.exists():
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")
            finally:
                self.temp_dir = None
