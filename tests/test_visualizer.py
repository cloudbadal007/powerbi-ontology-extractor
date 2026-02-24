"""
Tests for ontology visualizer utilities.
"""

import pytest

from powerbi_ontology.utils.visualizer import OntologyVisualizer


class TestOntologyVisualizer:
    """Coverage tests for visualizer and utils lazy imports."""

    def test_build_graph_and_mermaid_export(self, sample_ontology):
        visualizer = OntologyVisualizer(sample_ontology)

        assert visualizer.graph is not None
        assert visualizer.graph.number_of_nodes() == len(sample_ontology.entities)
        assert visualizer.graph.number_of_edges() == len(sample_ontology.relationships)

        mermaid = visualizer.export_mermaid_diagram()
        assert "erDiagram" in mermaid
        assert "SHIPMENT" in mermaid
        assert "CUSTOMER" in mermaid

    def test_utils_lazy_imports(self):
        from powerbi_ontology import utils

        assert utils.PBIXReader is not None
        assert utils.OntologyVisualizer is not None

        with pytest.raises(AttributeError):
            _ = utils.DoesNotExist
