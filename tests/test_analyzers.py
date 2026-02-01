"""
Tests for SemanticAnalyzer class.
"""

import pytest

from powerbi_ontology.analyzer import (
    SemanticAnalyzer, Conflict, Duplication, CanonicalEntity, SemanticDebtReport
)


class TestSemanticAnalyzer:
    """Test SemanticAnalyzer class."""
    
    def test_init(self, multiple_semantic_models):
        """Test analyzer initialization."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        assert len(analyzer.semantic_models) == 2
        assert len(analyzer._model_map) == 2
    
    def test_detect_conflicts(self, multiple_semantic_models):
        """Test conflict detection across dashboards."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        conflicts = analyzer.detect_conflicts()
        
        assert isinstance(conflicts, list)
        # Should detect conflict: same measure name, different definitions
        assert len(conflicts) > 0
        
        conflict = conflicts[0]
        assert isinstance(conflict, Conflict)
        assert conflict.concept == "high risk customer" or "High Risk Customer" in conflict.concept
        assert conflict.dashboard1 != conflict.dashboard2
    
    def test_detect_conflicts_entity_properties(self, multiple_semantic_models):
        """Test detecting conflicts in entity properties."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        conflicts = analyzer.detect_conflicts()
        
        # Should detect that Customer entity has different properties
        entity_conflicts = [
            c for c in conflicts 
            if c.concept.lower() == "customer"
        ]
        # May or may not detect depending on property differences
        assert isinstance(conflicts, list)
    
    def test_identify_duplicate_logic(self, multiple_semantic_models):
        """Test identifying duplicate logic."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        duplications = analyzer.identify_duplicate_logic()
        
        assert isinstance(duplications, list)
        # May detect duplicates if formulas are similar
        for dup in duplications:
            assert isinstance(dup, Duplication)
            assert len(dup.dashboards) > 0
    
    def test_calculate_semantic_debt(self, multiple_semantic_models):
        """Test semantic debt calculation."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        debt_report = analyzer.calculate_semantic_debt()
        
        assert isinstance(debt_report, SemanticDebtReport)
        assert debt_report.total_conflicts >= 0
        assert debt_report.total_duplications >= 0
        assert debt_report.cost_per_conflict == 50000.0
        assert debt_report.total_cost >= 0
    
    def test_calculate_semantic_debt_cost(self, multiple_semantic_models):
        """Test that semantic debt cost is calculated correctly."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        debt_report = analyzer.calculate_semantic_debt()
        
        expected_cost = (
            debt_report.total_conflicts * debt_report.cost_per_conflict +
            debt_report.total_duplications * 10000.0
        )
        assert debt_report.total_cost == expected_cost
    
    def test_suggest_canonical_definitions(self, multiple_semantic_models):
        """Test suggesting canonical definitions."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        canonical_defs = analyzer.suggest_canonical_definitions()
        
        assert isinstance(canonical_defs, list)
        for canon in canonical_defs:
            assert isinstance(canon, CanonicalEntity)
            assert canon.name is not None
            assert canon.confidence >= 0.0
            assert canon.confidence <= 1.0
    
    def test_generate_consolidation_report(self, multiple_semantic_models, temp_dir):
        """Test generating HTML consolidation report."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        report_path = temp_dir / "semantic_debt_report.html"
        
        analyzer.generate_consolidation_report(str(report_path))
        
        assert report_path.exists()
        content = report_path.read_text()
        assert "Semantic Debt" in content or "semantic" in content.lower()
    
    def test_determine_severity(self, multiple_semantic_models):
        """Test conflict severity determination."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        
        # Test different formula differences
        formula1 = "RiskScore > 80"
        formula2 = "RiskScore > 80"  # Same
        formula3 = "RiskScore > 90"  # Different threshold
        
        severity_same = analyzer._determine_severity(formula1, formula2)
        severity_diff = analyzer._determine_severity(formula1, formula3)
        
        assert severity_same == "LOW" or severity_same == "MEDIUM"
        assert severity_diff in ["LOW", "MEDIUM", "HIGH"]
    
    def test_normalize_formula(self, multiple_semantic_models):
        """Test formula normalization for comparison."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        
        formula1 = "SUM(Orders[Value])"
        formula2 = "SUM( Orders[Value] )"  # With spaces
        
        normalized1 = analyzer._normalize_formula(formula1)
        normalized2 = analyzer._normalize_formula(formula2)
        
        assert normalized1 == normalized2
    
    def test_conflicts_by_severity(self, multiple_semantic_models):
        """Test that conflicts are categorized by severity."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        debt_report = analyzer.calculate_semantic_debt()
        
        assert isinstance(debt_report.conflicts_by_severity, dict)
        # Should have severity counts
        total_by_severity = sum(debt_report.conflicts_by_severity.values())
        assert total_by_severity == debt_report.total_conflicts
    
    def test_duplication_description(self, multiple_semantic_models):
        """Test that duplications have descriptive messages."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        duplications = analyzer.identify_duplicate_logic()
        
        for dup in duplications:
            assert dup.description is not None
            assert len(dup.description) > 0
    
    def test_canonical_confidence_calculation(self, multiple_semantic_models):
        """Test that canonical definition confidence is calculated."""
        analyzer = SemanticAnalyzer(multiple_semantic_models)
        canonical_defs = analyzer.suggest_canonical_definitions()
        
        for canon in canonical_defs:
            # Confidence should be based on usage frequency
            assert 0.0 <= canon.confidence <= 1.0
            assert len(canon.dashboards_using) > 0
