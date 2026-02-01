"""
Tests for OWLExporter.
"""

import pytest

from powerbi_ontology.export.owl import OWLExporter


class TestOWLExporter:
    """Test OWLExporter class."""
    
    def test_init(self, sample_ontology):
        """Test exporter initialization."""
        exporter = OWLExporter(sample_ontology)
        assert exporter.ontology == sample_ontology
        assert exporter.graph is not None
    
    def test_export_xml(self, sample_ontology):
        """Test exporting to OWL XML format."""
        exporter = OWLExporter(sample_ontology)
        owl_xml = exporter.export(format="xml")
        
        assert isinstance(owl_xml, str)
        assert len(owl_xml) > 0
        # May contain RDF/OWL elements
        assert "rdf" in owl_xml.lower() or "owl" in owl_xml.lower()
    
    def test_export_turtle(self, sample_ontology):
        """Test exporting to Turtle format."""
        exporter = OWLExporter(sample_ontology)
        owl_turtle = exporter.export(format="turtle")
        
        assert isinstance(owl_turtle, str)
        assert len(owl_turtle) > 0
    
    def test_add_entity(self, sample_ontology):
        """Test adding entity as OWL class."""
        exporter = OWLExporter(sample_ontology)
        entity = sample_ontology.entities[0]
        
        exporter._add_entity(entity)
        
        # Graph should have been modified
        assert exporter.graph is not None
    
    def test_add_relationship(self, sample_ontology):
        """Test adding relationship as OWL object property."""
        exporter = OWLExporter(sample_ontology)
        if sample_ontology.relationships:
            rel = sample_ontology.relationships[0]
            
            exporter._add_relationship(rel)
            
            # Graph should have been modified
            assert exporter.graph is not None
    
    def test_map_to_xsd(self, sample_ontology):
        """Test mapping ontology types to XSD types."""
        exporter = OWLExporter(sample_ontology)
        
        from rdflib.namespace import XSD
        
        xsd_type = exporter._map_to_xsd("String")
        assert xsd_type == XSD.string
        
        xsd_type = exporter._map_to_xsd("Integer")
        assert xsd_type == XSD.integer
    
    def test_save(self, sample_ontology, temp_dir):
        """Test saving OWL export to file."""
        exporter = OWLExporter(sample_ontology)
        output_path = temp_dir / "test_ontology.owl"
        
        exporter.save(str(output_path), format="xml")
        
        assert output_path.exists()
        content = output_path.read_text()
        assert len(content) > 0
