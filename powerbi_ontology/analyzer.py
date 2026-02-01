"""
Semantic Model Analyzer

Analyzes multiple Power BI semantic models to detect conflicts and calculate semantic debt.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from powerbi_ontology.extractor import SemanticModel, Measure
from powerbi_ontology.dax_parser import DAXParser

logger = logging.getLogger(__name__)


@dataclass
class Conflict:
    """Represents a semantic conflict between dashboards."""
    concept: str  # e.g., "HighRiskCustomer"
    dashboard1: str
    definition1: str
    dashboard2: str
    definition2: str
    severity: str = "MEDIUM"  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    description: str = ""


@dataclass
class Duplication:
    """Represents duplicated logic across dashboards."""
    measure_name: str
    dashboards: List[str]
    dax_formula: str
    description: str = ""


@dataclass
class CanonicalEntity:
    """Suggested canonical definition for an entity."""
    name: str
    suggested_definition: str
    dashboards_using: List[str]
    alternative_definitions: Dict[str, str] = field(default_factory=dict)
    confidence: float = 0.0


@dataclass
class SemanticDebtReport:
    """Report of semantic debt calculation."""
    total_conflicts: int
    total_duplications: int
    cost_per_conflict: float = 50000.0  # $50K per conflict
    total_cost: float = 0.0
    conflicts_by_severity: Dict[str, int] = field(default_factory=dict)
    message: str = ""


class SemanticAnalyzer:
    """
    Analyzes multiple Power BI semantic models to:
    - Detect semantic conflicts
    - Identify duplicate logic
    - Calculate semantic debt
    - Suggest canonical definitions
    """

    def __init__(self, semantic_models: List[SemanticModel]):
        """
        Initialize analyzer.
        
        Args:
            semantic_models: List of semantic models to analyze
        """
        self.semantic_models = semantic_models
        self.dax_parser = DAXParser()
        self._model_map = {model.source_file: model for model in semantic_models}

    def detect_conflicts(self) -> List[Conflict]:
        """
        Detect conflicting definitions across dashboards.
        
        Example:
        - Dashboard A: HighRiskCustomer = RiskScore > 80
        - Dashboard B: HighRiskCustomer = ChurnProbability > 0.7
        - Conflict: Same concept, different definitions!
        
        Returns:
            List of Conflict objects
        """
        conflicts = []
        
        # Group measures by name (case-insensitive)
        measures_by_name: Dict[str, List[tuple]] = {}  # name -> [(model, measure), ...]
        
        for model in self.semantic_models:
            for measure in model.measures:
                measure_key = measure.name.lower()
                if measure_key not in measures_by_name:
                    measures_by_name[measure_key] = []
                measures_by_name[measure_key].append((model, measure))
        
        # Find conflicts: same measure name, different definitions
        for measure_name, measure_list in measures_by_name.items():
            if len(measure_list) > 1:
                # Compare all pairs
                for i, (model1, measure1) in enumerate(measure_list):
                    for model2, measure2 in measure_list[i+1:]:
                        if measure1.dax_formula != measure2.dax_formula:
                            # Conflict detected!
                            conflict = Conflict(
                                concept=measure_name,
                                dashboard1=model1.source_file,
                                definition1=measure1.dax_formula,
                                dashboard2=model2.source_file,
                                definition2=measure2.dax_formula,
                                severity=self._determine_severity(measure1.dax_formula, measure2.dax_formula),
                                description=f"'{measure_name}' defined differently in {model1.source_file} vs {model2.source_file}"
                            )
                            conflicts.append(conflict)
        
        # Also check for entity definition conflicts
        entities_by_name: Dict[str, List[tuple]] = {}
        for model in self.semantic_models:
            for entity in model.entities:
                entity_key = entity.name.lower()
                if entity_key not in entities_by_name:
                    entities_by_name[entity_key] = []
                entities_by_name[entity_key].append((model, entity))
        
        for entity_name, entity_list in entities_by_name.items():
            if len(entity_list) > 1:
                # Check for property differences
                for i, (model1, entity1) in enumerate(entity_list):
                    for model2, entity2 in entity_list[i+1:]:
                        props1 = {p.name: p.data_type for p in entity1.properties}
                        props2 = {p.name: p.data_type for p in entity2.properties}
                        
                        if props1 != props2:
                            conflict = Conflict(
                                concept=entity_name,
                                dashboard1=model1.source_file,
                                definition1=f"{len(entity1.properties)} properties",
                                dashboard2=model2.source_file,
                                definition2=f"{len(entity2.properties)} properties",
                                severity="MEDIUM",
                                description=f"Entity '{entity_name}' has different properties across dashboards"
                            )
                            conflicts.append(conflict)
        
        logger.info(f"Detected {len(conflicts)} conflicts")
        return conflicts

    def identify_duplicate_logic(self) -> List[Duplication]:
        """
        Identify duplicated DAX measures across dashboards.
        
        Returns:
            List of Duplication objects
        """
        duplications = []
        
        # Group measures by formula (normalized)
        measures_by_formula: Dict[str, List[tuple]] = {}
        
        for model in self.semantic_models:
            for measure in model.measures:
                # Normalize formula (remove whitespace, case-insensitive)
                normalized = self._normalize_formula(measure.dax_formula)
                if normalized not in measures_by_formula:
                    measures_by_formula[normalized] = []
                measures_by_formula[normalized].append((model, measure))
        
        # Find duplications (same formula, different names or dashboards)
        for formula, measure_list in measures_by_formula.items():
            if len(measure_list) > 1:
                dashboards = [model.source_file for model, _ in measure_list]
                measure_names = [measure.name for _, measure in measure_list]
                
                # Check if same name or different names
                if len(set(measure_names)) == 1:
                    # Same name, same formula - true duplication
                    duplication = Duplication(
                        measure_name=measure_names[0],
                        dashboards=dashboards,
                        dax_formula=measure_list[0][1].dax_formula,
                        description=f"Same measure '{measure_names[0]}' duplicated across {len(dashboards)} dashboards"
                    )
                else:
                    # Different names, same formula - opportunity for consolidation
                    duplication = Duplication(
                        measure_name=f"{measure_names[0]} (and {len(measure_names)-1} others)",
                        dashboards=dashboards,
                        dax_formula=measure_list[0][1].dax_formula,
                        description=f"Same logic with different names: {', '.join(measure_names)}"
                    )
                duplications.append(duplication)
        
        logger.info(f"Identified {len(duplications)} duplications")
        return duplications

    def calculate_semantic_debt(self) -> SemanticDebtReport:
        """
        Calculate semantic debt from conflicts.
        
        From article: $50K per conflict to reconcile.
        
        Returns:
            SemanticDebtReport
        """
        conflicts = self.detect_conflicts()
        duplications = self.identify_duplicate_logic()
        
        # Count by severity
        conflicts_by_severity = {}
        for conflict in conflicts:
            severity = conflict.severity
            conflicts_by_severity[severity] = conflicts_by_severity.get(severity, 0) + 1
        
        # Calculate cost
        cost_per_conflict = 50000.0  # $50K per conflict
        total_cost = len(conflicts) * cost_per_conflict
        
        # Add cost for duplications (lower cost, but still significant)
        duplication_cost = len(duplications) * 10000.0  # $10K per duplication
        total_cost += duplication_cost
        
        report = SemanticDebtReport(
            total_conflicts=len(conflicts),
            total_duplications=len(duplications),
            cost_per_conflict=cost_per_conflict,
            total_cost=total_cost,
            conflicts_by_severity=conflicts_by_severity,
            message=f"Total semantic debt: ${total_cost:,.0f} ({len(conflicts)} conflicts × ${cost_per_conflict:,.0f} + {len(duplications)} duplications × $10,000)"
        )
        
        logger.info(f"Semantic debt calculated: ${total_cost:,.0f}")
        return report

    def suggest_canonical_definitions(self) -> List[CanonicalEntity]:
        """
        Suggest canonical definitions for entities/concepts.
        
        Returns:
            List of CanonicalEntity suggestions
        """
        canonical_entities = []
        
        # Group measures by name
        measures_by_name: Dict[str, List[tuple]] = {}
        for model in self.semantic_models:
            for measure in model.measures:
                key = measure.name.lower()
                if key not in measures_by_name:
                    measures_by_name[key] = []
                measures_by_name[key].append((model, measure))
        
        # For each measure with multiple definitions, suggest canonical
        for measure_name, measure_list in measures_by_name.items():
            if len(measure_list) > 1:
                # Find most common definition
                formula_counts: Dict[str, int] = {}
                for model, measure in measure_list:
                    normalized = self._normalize_formula(measure.dax_formula)
                    formula_counts[normalized] = formula_counts.get(normalized, 0) + 1
                
                # Most common is the suggested canonical
                most_common_formula = max(formula_counts.items(), key=lambda x: x[1])
                suggested_def = most_common_formula[0]
                confidence = most_common_formula[1] / len(measure_list)
                
                # Get dashboards using this definition
                dashboards_using = [
                    model.source_file for model, measure in measure_list
                    if self._normalize_formula(measure.dax_formula) == suggested_def
                ]
                
                # Get alternative definitions
                alternative_defs = {}
                for model, measure in measure_list:
                    normalized = self._normalize_formula(measure.dax_formula)
                    if normalized != suggested_def:
                        alternative_defs[model.source_file] = measure.dax_formula
                
                canonical = CanonicalEntity(
                    name=measure_name,
                    suggested_definition=suggested_def,
                    dashboards_using=dashboards_using,
                    alternative_definitions=alternative_defs,
                    confidence=confidence
                )
                canonical_entities.append(canonical)
        
        logger.info(f"Suggested {len(canonical_entities)} canonical definitions")
        return canonical_entities

    def generate_consolidation_report(self, output_path: str):
        """
        Generate HTML/PDF report showing analysis results.
        
        Args:
            output_path: Path to save report
        """
        conflicts = self.detect_conflicts()
        duplications = self.identify_duplicate_logic()
        debt_report = self.calculate_semantic_debt()
        canonical_defs = self.suggest_canonical_definitions()
        
        # Generate HTML report
        html = self._generate_html_report(
            conflicts, duplications, debt_report, canonical_defs
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"Generated consolidation report: {output_path}")

    def _determine_severity(self, formula1: str, formula2: str) -> str:
        """Determine conflict severity based on formula differences."""
        # Simple heuristic
        if formula1.lower() == formula2.lower():
            return "LOW"
        
        # Check if they're similar (threshold-based)
        if ">" in formula1 and ">" in formula2:
            # Extract thresholds
            import re
            thresholds1 = re.findall(r'[><=]+\s*(\d+)', formula1)
            thresholds2 = re.findall(r'[><=]+\s*(\d+)', formula2)
            if thresholds1 and thresholds2:
                if abs(int(thresholds1[0]) - int(thresholds2[0])) > 20:
                    return "HIGH"
        
        return "MEDIUM"

    def _normalize_formula(self, formula: str) -> str:
        """Normalize DAX formula for comparison."""
        # Remove whitespace, convert to lowercase
        normalized = formula.replace(" ", "").replace("\n", "").replace("\t", "").lower()
        return normalized

    def _generate_html_report(
        self,
        conflicts: List[Conflict],
        duplications: List[Duplication],
        debt_report: SemanticDebtReport,
        canonical_defs: List[CanonicalEntity]
    ) -> str:
        """Generate HTML report."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Semantic Debt Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; margin-top: 30px; }}
        .conflict {{ border-left: 4px solid #f44336; padding: 10px; margin: 10px 0; background: #ffebee; }}
        .duplication {{ border-left: 4px solid #ff9800; padding: 10px; margin: 10px 0; background: #fff3e0; }}
        .debt {{ border: 2px solid #f44336; padding: 20px; margin: 20px 0; background: #ffebee; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>Semantic Debt Analysis Report</h1>
    
    <div class="debt">
        <h2>Total Semantic Debt</h2>
        <p><strong>${debt_report.total_cost:,.0f}</strong></p>
        <p>{debt_report.message}</p>
        <p>Conflicts: {debt_report.total_conflicts}</p>
        <p>Duplications: {debt_report.total_duplications}</p>
    </div>
    
    <h2>Conflicts Detected ({len(conflicts)})</h2>
    {"".join(f'''
    <div class="conflict">
        <h3>{conflict.concept}</h3>
        <p><strong>Severity:</strong> {conflict.severity}</p>
        <p><strong>{conflict.dashboard1}:</strong> {conflict.definition1}</p>
        <p><strong>{conflict.dashboard2}:</strong> {conflict.definition2}</p>
        <p>{conflict.description}</p>
    </div>
    ''' for conflict in conflicts)}
    
    <h2>Duplications Identified ({len(duplications)})</h2>
    {"".join(f'''
    <div class="duplication">
        <h3>{dup.measure_name}</h3>
        <p><strong>Dashboards:</strong> {', '.join(dup.dashboards)}</p>
        <p><strong>Formula:</strong> <code>{dup.dax_formula}</code></p>
        <p>{dup.description}</p>
    </div>
    ''' for dup in duplications)}
    
    <h2>Canonical Definition Suggestions ({len(canonical_defs)})</h2>
    <table>
        <tr>
            <th>Concept</th>
            <th>Suggested Definition</th>
            <th>Confidence</th>
            <th>Dashboards Using</th>
        </tr>
        {"".join(f'''
        <tr>
            <td>{canon.name}</td>
            <td><code>{canon.suggested_definition[:100]}...</code></td>
            <td>{canon.confidence:.0%}</td>
            <td>{len(canon.dashboards_using)}</td>
        </tr>
        ''' for canon in canonical_defs)}
    </table>
</body>
</html>
        """
        return html
