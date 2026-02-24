"""Utility modules for PowerBI Ontology Extractor.

Avoid eager imports here because `OntologyVisualizer` depends on ontology modules
that can participate in import cycles during package initialization.
"""

__all__ = ["PBIXReader", "OntologyVisualizer"]


def __getattr__(name: str):
    if name == "PBIXReader":
        from powerbi_ontology.utils.pbix_reader import PBIXReader

        return PBIXReader
    if name == "OntologyVisualizer":
        from powerbi_ontology.utils.visualizer import OntologyVisualizer

        return OntologyVisualizer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
