"""
Ontology Visualizer

Creates visualizations of ontologies using networkx, matplotlib, and plotly.
"""

import logging
from typing import Optional

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go
    import plotly.express as px
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("Visualization libraries not installed. Install with: pip install networkx matplotlib plotly")

from powerbi_ontology.ontology_generator import Ontology, OntologyEntity, OntologyRelationship

logger = logging.getLogger(__name__)


class OntologyVisualizer:
    """
    Visualizes ontologies as entity-relationship diagrams and interactive graphs.
    """

    def __init__(self, ontology: Ontology):
        """
        Initialize visualizer.
        
        Args:
            ontology: Ontology to visualize
        """
        self.ontology = ontology
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build networkx graph from ontology."""
        try:
            import networkx as nx
        except ImportError:
            logger.error("networkx not installed. Cannot build graph.")
            return None
        
        G = nx.DiGraph()
        
        # Add entities as nodes
        for entity in self.ontology.entities:
            G.add_node(
                entity.name,
                node_type=entity.entity_type,
                description=entity.description,
                property_count=len(entity.properties)
            )
        
        # Add relationships as edges
        for rel in self.ontology.relationships:
            G.add_edge(
                rel.from_entity,
                rel.to_entity,
                relationship_type=rel.relationship_type,
                cardinality=rel.cardinality,
                label=rel.relationship_type
            )
        
        return G

    def plot_entity_relationship_diagram(self) -> Optional[object]:
        """
        Create entity-relationship diagram using matplotlib.
        
        Returns:
            matplotlib Figure object
        """
        if not self.graph:
            logger.error("Graph not built. Cannot create diagram.")
            return None
        
        try:
            import matplotlib.pyplot as plt
            import networkx as nx
        except ImportError:
            logger.error("matplotlib or networkx not installed.")
            return None
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Layout
        pos = nx.spring_layout(self.graph, k=2, iterations=50)
        
        # Color nodes by entity type
        node_colors = []
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get('node_type', 'standard')
            if node_type == 'dimension':
                node_colors.append('#90EE90')  # Light green
            elif node_type == 'fact':
                node_colors.append('#87CEEB')  # Sky blue
            elif node_type == 'date':
                node_colors.append('#FFB6C1')  # Light pink
            else:
                node_colors.append('#D3D3D3')  # Light gray
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph, pos,
            node_color=node_colors,
            node_size=2000,
            alpha=0.9,
            ax=ax
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            self.graph, pos,
            edge_color='gray',
            arrows=True,
            arrowsize=20,
            alpha=0.6,
            ax=ax
        )
        
        # Draw labels
        nx.draw_networkx_labels(
            self.graph, pos,
            font_size=10,
            font_weight='bold',
            ax=ax
        )
        
        # Draw edge labels
        edge_labels = {
            (u, v): self.graph.edges[u, v].get('label', '')
            for u, v in self.graph.edges()
        }
        nx.draw_networkx_edge_labels(
            self.graph, pos,
            edge_labels=edge_labels,
            font_size=8,
            ax=ax
        )
        
        ax.set_title(f"Entity-Relationship Diagram: {self.ontology.name}", fontsize=16, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        return fig

    def generate_interactive_graph(self) -> Optional[object]:
        """
        Generate interactive graph using plotly.
        
        Returns:
            plotly Figure object
        """
        if not self.graph:
            logger.error("Graph not built. Cannot create interactive graph.")
            return None
        
        try:
            import plotly.graph_objects as go
            import networkx as nx
        except ImportError:
            logger.error("plotly or networkx not installed.")
            return None
        
        # Get positions
        pos = nx.spring_layout(self.graph, k=2, iterations=50)
        
        # Prepare edge traces
        edge_x = []
        edge_y = []
        edge_info = []
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_info.append(self.graph.edges[edge].get('relationship_type', ''))
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Prepare node traces
        node_x = []
        node_y = []
        node_text = []
        node_info = []
        node_colors = []
        
        for node in self.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            node_data = self.graph.nodes[node]
            node_type = node_data.get('node_type', 'standard')
            prop_count = node_data.get('property_count', 0)
            
            node_text.append(f"{node}<br>{node_type}<br>{prop_count} properties")
            node_info.append(f"Type: {node_type}<br>Properties: {prop_count}")
            
            # Color by type
            if node_type == 'dimension':
                node_colors.append('#90EE90')
            elif node_type == 'fact':
                node_colors.append('#87CEEB')
            elif node_type == 'date':
                node_colors.append('#FFB6C1')
            else:
                node_colors.append('#D3D3D3')
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[node for node in self.graph.nodes()],
            textposition="middle center",
            hovertext=node_info,
            marker=dict(
                size=30,
                color=node_colors,
                line=dict(width=2, color='black')
            )
        )
        
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=f"Interactive Ontology Graph: {self.ontology.name}",
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[
                    dict(
                        text="Hover over nodes for details",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002,
                        xanchor="left", yanchor="bottom",
                        font=dict(color="#888", size=12)
                    )
                ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
        
        return fig

    def export_mermaid_diagram(self) -> str:
        """
        Export ontology as Mermaid diagram code.
        
        Returns:
            Mermaid diagram code string
        """
        mermaid = ["erDiagram"]
        
        # Add entities
        for entity in self.ontology.entities:
            entity_name = entity.name.upper()
            mermaid.append(f"    {entity_name} {{")
            
            # Add key properties
            for prop in entity.properties[:5]:  # Limit to 5 for readability
                prop_type = prop.data_type.lower()
                prop_name = prop.name
                if prop.unique:
                    prop_name += " PK"
                mermaid.append(f"        {prop_type} {prop_name}")
            
            if len(entity.properties) > 5:
                mermaid.append(f"        ... {len(entity.properties) - 5} more properties")
            
            mermaid.append("    }")
        
        # Add relationships
        for rel in self.ontology.relationships:
            from_entity = rel.from_entity.upper()
            to_entity = rel.to_entity.upper()
            rel_type = rel.relationship_type.replace("_", " ")
            
            # Mermaid cardinality notation
            if rel.cardinality == "one-to-many":
                cardinality = "||--o{"
            elif rel.cardinality == "many-to-one":
                cardinality = "}o--||"
            elif rel.cardinality == "one-to-one":
                cardinality = "||--||"
            else:
                cardinality = "}o--o{"
            
            mermaid.append(f"    {from_entity} {cardinality} {to_entity} : \"{rel_type}\"")
        
        return "\n".join(mermaid)

    def save_as_image(self, filename: str, format: str = "png"):
        """
        Save visualization as image.
        
        Args:
            filename: Output filename
            format: Image format ("png", "svg", "pdf")
        """
        fig = self.plot_entity_relationship_diagram()
        if fig:
            fig.savefig(filename, format=format, dpi=300, bbox_inches='tight')
            logger.info(f"Saved diagram to {filename}")
        else:
            logger.error("Could not create diagram")

    def save_interactive_html(self, filename: str):
        """
        Save interactive graph as HTML.
        
        Args:
            filename: Output HTML filename
        """
        fig = self.generate_interactive_graph()
        if fig:
            fig.write_html(filename)
            logger.info(f"Saved interactive graph to {filename}")
        else:
            logger.error("Could not create interactive graph")
