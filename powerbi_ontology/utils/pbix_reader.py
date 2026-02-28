"""
PBIX Reader Utility

Reads Power BI .pbix files (which are ZIP archives) and extracts semantic model data.
"""

import json
import logging
import re
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

        # PBIP support:
        # - directory path (project root)
        # - .pbip file path (project descriptor file)
        self.project_root: Optional[Path] = None
        if self.pbix_path.is_dir():
            self.project_root = self.pbix_path
        elif self.pbix_path.suffix.lower() == ".pbip":
            self.project_root = self.pbix_path.parent
        
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

        # PBIP/TMDL projects are already directories, no zip extraction required.
        if self.project_root:
            self.temp_dir = self.project_root
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

        if self.project_root:
            self._model_data = self._read_tmdl_model(self.project_root)
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

    def _read_tmdl_model(self, project_root: Path) -> Dict:
        """
        Read semantic model from PBIP/TMDL project.

        This is a lightweight parser that extracts tables, columns, measures and
        relationships from .tmdl files so downstream extraction can reuse the same
        model JSON shape as model.bim.
        """
        tmdl_files = list(project_root.rglob("*.tmdl"))
        if not tmdl_files:
            raise FileNotFoundError(
                f"model.bim/TMDL model files not found in project: {self.pbix_path}"
            )

        tables_by_name: Dict[str, Dict] = {}
        relationships: List[Dict] = []

        for tmdl_file in tmdl_files:
            try:
                content = tmdl_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = tmdl_file.read_text(encoding="utf-16", errors="ignore")

            self._extract_tables_from_tmdl(content, tmdl_file, tables_by_name)
            rels = self._extract_relationships_from_tmdl(content)
            relationships.extend(rels)

        model_name = project_root.name
        return {
            "name": model_name,
            "tables": list(tables_by_name.values()),
            "relationships": relationships,
            "roles": [],
        }

    def _extract_tables_from_tmdl(self, content: str, tmdl_file: Path, tables_by_name: Dict[str, Dict]) -> None:
        """Extract table/column/measure info from a TMDL file."""
        table_names = []

        for match in re.finditer(r"(?im)^\s*table\s+(.+?)\s*$", content):
            table_names.append(self._clean_identifier(match.group(1)))

        if not table_names and tmdl_file.parent.name.lower() in {"tables", "table"}:
            table_names.append(self._clean_identifier(tmdl_file.stem))

        if not table_names:
            return

        columns = []
        for col_match in re.finditer(r"(?im)^\s*column\s+(.+?)\s*$", content):
            col_name = self._clean_identifier(col_match.group(1))
            if not col_name:
                continue
            data_type = "string"
            window = content[col_match.end(): col_match.end() + 240]
            type_match = re.search(r"(?im)\bdataType\s*:\s*([A-Za-z0-9_]+)", window)
            if type_match:
                data_type = type_match.group(1)
            columns.append({"name": col_name, "dataType": data_type})

        measures = []
        for msr_match in re.finditer(r"(?im)^\s*measure\s+(.+?)\s*=\s*(.+)$", content):
            measure_name = self._clean_identifier(msr_match.group(1))
            expression = msr_match.group(2).strip()
            if measure_name:
                measures.append({"name": measure_name, "expression": expression})

        for table_name in table_names:
            table = tables_by_name.setdefault(
                table_name,
                {"name": table_name, "columns": [], "measures": [], "hierarchies": []},
            )

            existing_cols = {c.get("name") for c in table["columns"]}
            for col in columns:
                if col["name"] not in existing_cols:
                    table["columns"].append(col)

            existing_measures = {m.get("name") for m in table["measures"]}
            for msr in measures:
                if msr["name"] not in existing_measures:
                    table["measures"].append(msr)

    def _extract_relationships_from_tmdl(self, content: str) -> List[Dict]:
        """Extract relationship metadata from TMDL file content."""
        rels: List[Dict] = []

        # Pattern: fromColumn: 'Table'[Column] ... toColumn: 'Table'[Column]
        pattern = (
            r"(?is)fromColumn\s*:\s*['\"]?([A-Za-z0-9_ ]+)['\"]?\[([A-Za-z0-9_ ]+)\]"
            r".*?toColumn\s*:\s*['\"]?([A-Za-z0-9_ ]+)['\"]?\[([A-Za-z0-9_ ]+)\]"
        )
        for match in re.finditer(pattern, content):
            from_table = self._clean_identifier(match.group(1))
            from_col = self._clean_identifier(match.group(2))
            to_table = self._clean_identifier(match.group(3))
            to_col = self._clean_identifier(match.group(4))
            rels.append(
                {
                    "fromTable": from_table,
                    "fromColumn": from_col,
                    "toTable": to_table,
                    "toColumn": to_col,
                    "fromCardinality": "many",
                    "toCardinality": "one",
                    "crossFilteringBehavior": "singleDirection",
                    "isActive": True,
                    "name": f"{from_table}_{to_table}",
                }
            )

        return rels

    def _clean_identifier(self, value: str) -> str:
        """Normalize TMDL identifiers by removing quotes and wrappers."""
        cleaned = value.strip()
        # remove trailing metadata blocks if any
        cleaned = cleaned.split("{", 1)[0].strip()
        # strip quotes
        if (cleaned.startswith('"') and cleaned.endswith('"')) or (
            cleaned.startswith("'") and cleaned.endswith("'")
        ):
            cleaned = cleaned[1:-1].strip()
        return cleaned

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
        # For PBIP project mode, temp_dir points at user's directory and must not be removed.
        if self.project_root:
            self.temp_dir = None
            return

        if self.temp_dir and self.temp_dir.exists():
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")
            finally:
                self.temp_dir = None
