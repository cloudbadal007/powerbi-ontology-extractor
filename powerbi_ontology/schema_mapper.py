"""
Schema Mapper

Maps logical ontology entities to physical data sources and detects schema drift.
This prevents the $4.6M mistake by validating schema bindings.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from powerbi_ontology.ontology_generator import Ontology, OntologyEntity

logger = logging.getLogger(__name__)


@dataclass
class SchemaBinding:
    """Maps logical entity to physical data source."""
    entity: str
    physical_source: str  # e.g., "SQL.dbo.customers"
    property_mappings: Dict[str, str] = field(default_factory=dict)  # logical -> physical
    source_type: str = "sql"  # "sql", "azure_sql", "fabric", etc.


@dataclass
class ValidationResult:
    """Result of schema binding validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    message: str = ""


@dataclass
class DriftReport:
    """Report of schema drift detection."""
    entity: str
    missing_columns: List[str] = field(default_factory=list)
    new_columns: List[str] = field(default_factory=list)
    type_changes: Dict[str, str] = field(default_factory=dict)  # column -> old_type -> new_type
    renamed_columns: Dict[str, str] = field(default_factory=dict)  # old_name -> new_name
    severity: str = "INFO"  # "INFO", "WARNING", "CRITICAL"
    message: str = ""


@dataclass
class Fix:
    """Suggested fix for schema drift."""
    type: str  # "update_mapping", "add_column", "remove_column"
    description: str
    action: str  # SQL or mapping update
    entity: str = ""
    property: str = ""


class SchemaMapper:
    """
    Maps ontology entities to physical data sources and detects schema drift.
    
    This is the CRITICAL piece that prevents the $4.6M mistake by detecting
    when columns are renamed or deleted before AI agents use them.
    """

    def __init__(self, ontology: Ontology, data_source: Optional[str] = None):
        """
        Initialize schema mapper.
        
        Args:
            ontology: The ontology to map
            data_source: Optional default data source
        """
        self.ontology = ontology
        self.data_source = data_source
        self.bindings: Dict[str, SchemaBinding] = {}

    def create_binding(
        self,
        entity_name: str,
        physical_table: str,
        property_mappings: Optional[Dict[str, str]] = None
    ) -> SchemaBinding:
        """
        Create a schema binding between logical entity and physical table.
        
        Args:
            entity_name: Name of the ontology entity
            physical_table: Physical table name (e.g., "dbo.customers")
            property_mappings: Optional explicit property mappings
            
        Returns:
            SchemaBinding object
        """
        entity = next((e for e in self.ontology.entities if e.name == entity_name), None)
        if not entity:
            raise ValueError(f"Entity not found: {entity_name}")
        
        # Auto-generate mappings if not provided
        if not property_mappings:
            property_mappings = {}
            for prop in entity.properties:
                # Default: use property name as column name (snake_case conversion)
                physical_name = self._to_snake_case(prop.name)
                property_mappings[prop.name] = physical_name
        
        binding = SchemaBinding(
            entity=entity_name,
            physical_source=physical_table,
            property_mappings=property_mappings,
            source_type=self._detect_source_type(physical_table)
        )
        
        self.bindings[entity_name] = binding
        logger.info(f"Created binding: {entity_name} -> {physical_table}")
        
        return binding

    def validate_binding(self, binding: SchemaBinding) -> ValidationResult:
        """
        Validate a schema binding.
        
        Args:
            binding: SchemaBinding to validate
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Check if entity exists in ontology
        entity = next((e for e in self.ontology.entities if e.name == binding.entity), None)
        if not entity:
            errors.append(f"Entity '{binding.entity}' not found in ontology")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                message=f"Entity '{binding.entity}' not found"
            )
        
        # Check if all mapped properties exist in entity
        for logical_prop, physical_col in binding.property_mappings.items():
            prop_exists = any(p.name == logical_prop for p in entity.properties)
            if not prop_exists:
                warnings.append(
                    f"Property '{logical_prop}' mapped but not found in entity '{binding.entity}'"
                )
        
        # Note: Full validation would require connection to actual data source
        # This is a basic validation - full implementation would query the database
        
        is_valid = len(errors) == 0
        message = "Binding is valid" if is_valid else f"Found {len(errors)} errors"
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            message=message
        )

    def detect_drift(
        self,
        binding: SchemaBinding,
        current_schema: Dict[str, any]
    ) -> DriftReport:
        """
        Detect schema drift between binding and current schema.
        
        This is the function that PREVENTS THE $4.6M MISTAKE!
        
        Args:
            binding: SchemaBinding to check
            current_schema: Current physical schema (dict of column_name -> type)
            
        Returns:
            DriftReport
        """
        missing_columns = []
        new_columns = []
        type_changes = {}
        renamed_columns = {}
        
        # Get expected columns from binding
        expected_columns = set(binding.property_mappings.values())
        actual_columns = set(current_schema.keys())
        
        # Find missing columns (THE $4.6M PROBLEM!)
        missing_columns = list(expected_columns - actual_columns)
        
        # Find new columns
        new_columns = list(actual_columns - expected_columns)
        
        # Check for type changes
        for logical_prop, physical_col in binding.property_mappings.items():
            if physical_col in current_schema:
                # Get expected type from ontology
                entity = next((e for e in self.ontology.entities if e.name == binding.entity), None)
                if entity:
                    prop = next((p for p in entity.properties if p.name == logical_prop), None)
                    if prop:
                        expected_type = prop.data_type
                        actual_type = current_schema[physical_col]
                        if expected_type != actual_type:
                            type_changes[physical_col] = f"{expected_type} -> {actual_type}"
        
        # Heuristic: If column is missing but similar name exists, might be renamed
        if missing_columns and new_columns:
            for missing in missing_columns:
                for new_col in new_columns:
                    if self._similar_names(missing, new_col):
                        renamed_columns[missing] = new_col
                        # Remove from missing/new if we found a match
                        if missing in missing_columns:
                            missing_columns.remove(missing)
                        if new_col in new_columns:
                            new_columns.remove(new_col)
        
        # Determine severity
        severity = "INFO"
        if missing_columns:
            severity = "CRITICAL"  # This is the $4.6M mistake scenario!
        elif type_changes:
            severity = "WARNING"
        elif renamed_columns:
            severity = "WARNING"
        
        # Build message
        message_parts = []
        if missing_columns:
            message_parts.append(
                f"CRITICAL: Missing columns: {', '.join(missing_columns)}. "
                f"This could cause the $4.6M mistake!"
            )
        if renamed_columns:
            message_parts.append(
                f"Columns may have been renamed: {', '.join(f'{k} -> {v}' for k, v in renamed_columns.items())}"
            )
        if type_changes:
            message_parts.append(f"Type changes detected: {', '.join(f'{k}: {v}' for k, v in type_changes.items())}")
        if new_columns:
            message_parts.append(f"New columns found: {', '.join(new_columns)}")
        
        message = " | ".join(message_parts) if message_parts else "No drift detected"
        
        return DriftReport(
            entity=binding.entity,
            missing_columns=missing_columns,
            new_columns=new_columns,
            type_changes=type_changes,
            renamed_columns=renamed_columns,
            severity=severity,
            message=message
        )

    def suggest_fix(self, drift_report: DriftReport) -> List[Fix]:
        """
        Suggest fixes for detected drift.
        
        Args:
            drift_report: DriftReport with detected issues
            
        Returns:
            List of Fix suggestions
        """
        fixes = []
        binding = self.bindings.get(drift_report.entity)
        
        if not binding:
            return fixes
        
        # Fix for renamed columns
        for old_name, new_name in drift_report.renamed_columns.items():
            fixes.append(Fix(
                type="update_mapping",
                description=f"Update mapping: {old_name} -> {new_name}",
                action=f"Update binding.property_mappings['{old_name}'] = '{new_name}'",
                entity=drift_report.entity,
                property=old_name
            ))
        
        # Fix for missing columns
        for missing_col in drift_report.missing_columns:
            fixes.append(Fix(
                type="update_mapping",
                description=f"Column '{missing_col}' not found. Check if renamed or deleted.",
                action=f"Verify column exists: SELECT * FROM {binding.physical_source} WHERE 1=0",
                entity=drift_report.entity,
                property=missing_col
            ))
        
        # Fix for new columns
        for new_col in drift_report.new_columns:
            fixes.append(Fix(
                type="add_column",
                description=f"New column '{new_col}' found. Consider adding to ontology.",
                action=f"Review and potentially add '{new_col}' to entity '{drift_report.entity}'",
                entity=drift_report.entity,
                property=new_col
            ))
        
        return fixes

    def generate_binding_yaml(self, ontology: Ontology) -> str:
        """
        Generate YAML configuration for schema bindings.
        
        Args:
            ontology: The ontology
            
        Returns:
            YAML string
        """
        try:
            import yaml
        except ImportError:
            logger.warning("PyYAML not installed. Cannot generate YAML.")
            return ""
        
        yaml_data = {
            "ontology": {
                "name": ontology.name,
                "version": ontology.version
            },
            "entities": {}
        }
        
        for entity_name, binding in self.bindings.items():
            yaml_data["entities"][entity_name] = {
                "source": binding.physical_source,
                "source_type": binding.source_type,
                "mappings": binding.property_mappings
            }
        
        return yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)

    def _to_snake_case(self, name: str) -> str:
        """Convert property name to snake_case."""
        import re
        # Insert underscore before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _detect_source_type(self, physical_table: str) -> str:
        """Detect source type from table name."""
        if "azure" in physical_table.lower() or "sql" in physical_table.lower():
            return "azure_sql"
        elif "fabric" in physical_table.lower() or "onelake" in physical_table.lower():
            return "fabric"
        else:
            return "sql"

    def _similar_names(self, name1: str, name2: str) -> bool:
        """Check if two names are similar (heuristic for rename detection)."""
        name1_lower = name1.lower().replace("_", "").replace("-", "")
        name2_lower = name2.lower().replace("_", "").replace("-", "")
        
        # Check if one contains the other
        if name1_lower in name2_lower or name2_lower in name1_lower:
            return True
        
        # Check Levenshtein distance (simplified)
        if abs(len(name1_lower) - len(name2_lower)) <= 3:
            # Simple similarity check
            common_chars = sum(1 for c in name1_lower if c in name2_lower)
            similarity = common_chars / max(len(name1_lower), len(name2_lower))
            return similarity > 0.7
        
        return False
