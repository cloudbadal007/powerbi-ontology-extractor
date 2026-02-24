"""
OWL/RDF Exporter

Exports ontologies to OWL/RDF format for semantic web standards.
"""

import logging
from typing import Optional
from urllib.parse import quote

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

from powerbi_ontology.ontology_generator import Ontology, OntologyEntity, OntologyRelationship

logger = logging.getLogger(__name__)


class OWLExporter:
    """
    Exports ontologies to OWL/RDF format.
    
    Uses RDFLib to generate standard OWL/RDF files compatible with
    triple stores and other semantic web tools.
    """

    def __init__(self, ontology: Ontology):
        """
        Initialize OWL exporter.
        
        Args:
            ontology: Ontology to export
        """
        self.ontology = ontology
        self.graph = Graph()
        
        # Create namespace for this ontology
        safe_name = quote(ontology.name, safe="")
        self.base_uri = f"http://example.com/ontologies/{safe_name}#"
        self.ont = Namespace(self.base_uri)

    def export(self, format: str = "xml") -> str:
        """
        Export ontology to OWL/RDF format.
        
        Args:
            format: Output format ("xml", "turtle", "json-ld", "n3")
            
        Returns:
            OWL/RDF string
        """
        logger.info(f"Exporting ontology '{self.ontology.name}' to OWL format ({format})")
        
        # Add ontology metadata
        ontology_uri = URIRef(self.base_uri)
        self.graph.add((ontology_uri, RDF.type, OWL.Ontology))
        self.graph.add((ontology_uri, RDFS.label, Literal(self.ontology.name)))
        self.graph.add((ontology_uri, RDFS.comment, Literal(f"Ontology from {self.ontology.source}")))
        
        # Add entities (classes)
        for entity in self.ontology.entities:
            self._add_entity(entity)
        
        # Add relationships (object properties)
        for rel in self.ontology.relationships:
            self._add_relationship(rel)
        
        # Serialize to requested format
        return self.graph.serialize(format=format)

    def _add_entity(self, entity: OntologyEntity):
        """Add entity as OWL class with properties."""
        entity_uri = URIRef(self.base_uri + entity.name)
        
        # Entity is a class
        self.graph.add((entity_uri, RDF.type, OWL.Class))
        self.graph.add((entity_uri, RDFS.label, Literal(entity.name)))
        if entity.description:
            self.graph.add((entity_uri, RDFS.comment, Literal(entity.description)))
        
        # Add properties (datatype properties)
        for prop in entity.properties:
            prop_uri = URIRef(self.base_uri + f"{entity.name}_{prop.name}")
            self.graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.graph.add((prop_uri, RDFS.label, Literal(prop.name)))
            self.graph.add((prop_uri, RDFS.domain, entity_uri))
            
            # Map data type to XSD
            xsd_type = self._map_to_xsd(prop.data_type)
            self.graph.add((prop_uri, RDFS.range, xsd_type))
            
            if prop.description:
                self.graph.add((prop_uri, RDFS.comment, Literal(prop.description)))

    def _add_relationship(self, rel: OntologyRelationship):
        """Add relationship as OWL object property."""
        rel_uri = URIRef(self.base_uri + rel.relationship_type)
        from_uri = URIRef(self.base_uri + rel.from_entity)
        to_uri = URIRef(self.base_uri + rel.to_entity)
        
        # Relationship is an object property
        self.graph.add((rel_uri, RDF.type, OWL.ObjectProperty))
        self.graph.add((rel_uri, RDFS.label, Literal(rel.relationship_type)))
        self.graph.add((rel_uri, RDFS.domain, from_uri))
        self.graph.add((rel_uri, RDFS.range, to_uri))
        
        if rel.description:
            self.graph.add((rel_uri, RDFS.comment, Literal(rel.description)))
        
        # Add cardinality restrictions if applicable
        if rel.cardinality == "one-to-many":
            # From side: exactly one
            self.graph.add((from_uri, OWL.onProperty, rel_uri))
            # To side: many (no restriction)

    def _map_to_xsd(self, data_type: str) -> URIRef:
        """Map ontology data type to XSD type."""
        type_mapping = {
            "String": XSD.string,
            "Integer": XSD.integer,
            "Decimal": XSD.decimal,
            "Date": XSD.dateTime,
            "Boolean": XSD.boolean
        }
        return type_mapping.get(data_type, XSD.string)

    def save(self, filepath: str, format: str = "xml"):
        """
        Save OWL export to file.
        
        Args:
            filepath: Path to save file
            format: Output format
        """
        output = self.export(format=format)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(output)
        logger.info(f"Saved OWL export to {filepath}")
