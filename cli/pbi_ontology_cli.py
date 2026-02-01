"""
PowerBI Ontology CLI

Command-line interface for PowerBI Ontology Extractor.
"""

import json
import logging
import sys
from pathlib import Path

try:
    import click
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich import print as rprint
except ImportError:
    print("Error: Required packages not installed. Run: pip install click rich")
    sys.exit(1)

from powerbi_ontology import PowerBIExtractor, OntologyGenerator, SemanticAnalyzer
from powerbi_ontology.export import FabricIQExporter, OntoGuardExporter, JSONSchemaExporter, OWLExporter
from powerbi_ontology import SchemaMapper
from powerbi_ontology.utils.visualizer import OntologyVisualizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

console = Console()


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose):
    """PowerBI Ontology Extractor - Extract semantic intelligence from Power BI dashboards."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.argument('pbix_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', '-f', type=click.Choice(['json', 'fabric-iq', 'ontoguard']), default='json', help='Output format')
def extract(pbix_file, output, format):
    """Extract ontology from Power BI .pbix file."""
    console.print(f"[bold green]Extracting ontology from[/bold green] {pbix_file}")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Extracting...", total=None)
        
        try:
            extractor = PowerBIExtractor(pbix_file)
            semantic_model = extractor.extract()
            
            progress.update(task, description="Generating ontology...")
            generator = OntologyGenerator(semantic_model)
            ontology = generator.generate()
            
            # Determine output file
            if not output:
                output = Path(pbix_file).stem + "_ontology.json"
            
            # Export based on format
            if format == 'json':
                ontology_dict = {
                    "name": ontology.name,
                    "version": ontology.version,
                    "source": ontology.source,
                    "entities": [
                        {
                            "name": e.name,
                            "description": e.description,
                            "properties": [
                                {
                                    "name": p.name,
                                    "type": p.data_type,
                                    "required": p.required
                                }
                                for p in e.properties
                            ]
                        }
                        for e in ontology.entities
                    ],
                    "relationships": [
                        {
                            "from": r.from_entity,
                            "to": r.to_entity,
                            "type": r.relationship_type,
                            "cardinality": r.cardinality
                        }
                        for r in ontology.relationships
                    ],
                    "businessRules": [
                        {
                            "name": r.name,
                            "entity": r.entity,
                            "condition": r.condition,
                            "action": r.action
                        }
                        for r in ontology.business_rules
                    ]
                }
                with open(output, 'w') as f:
                    json.dump(ontology_dict, f, indent=2)
            elif format == 'fabric-iq':
                exporter = FabricIQExporter(ontology)
                fabric_json = exporter.export()
                with open(output, 'w') as f:
                    json.dump(fabric_json, f, indent=2)
            elif format == 'ontoguard':
                exporter = OntoGuardExporter(ontology)
                ontoguard_json = exporter.export()
                with open(output, 'w') as f:
                    json.dump(ontoguard_json, f, indent=2)
            
            progress.update(task, completed=True)
            console.print(f"[bold green]✓[/bold green] Ontology extracted to {output}")
            console.print(f"  Entities: {len(ontology.entities)}")
            console.print(f"  Relationships: {len(ontology.relationships)}")
            console.print(f"  Business Rules: {len(ontology.business_rules)}")
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            logging.exception("Extraction failed")
            sys.exit(1)


@cli.command()
@click.argument('pbix_files', nargs=-1, type=click.Path(exists=True))
@click.option('--report', '-r', type=click.Path(), help='Output report file (HTML)')
@click.option('--output-dir', '-d', type=click.Path(), help='Output directory for individual ontologies')
def analyze(pbix_files, report, output_dir):
    """Analyze multiple Power BI files for conflicts and semantic debt."""
    if not pbix_files:
        console.print("[bold red]Error:[/bold red] No .pbix files provided")
        sys.exit(1)
    
    console.print(f"[bold green]Analyzing[/bold green] {len(pbix_files)} Power BI files...")
    
    semantic_models = []
    
    with Progress(console=console) as progress:
        task = progress.add_task("Loading files...", total=len(pbix_files))
        
        for pbix_file in pbix_files:
            try:
                extractor = PowerBIExtractor(pbix_file)
                model = extractor.extract()
                semantic_models.append(model)
                progress.advance(task)
            except Exception as e:
                console.print(f"[bold yellow]Warning:[/bold yellow] Failed to extract {pbix_file}: {e}")
    
    if not semantic_models:
        console.print("[bold red]Error:[/bold red] No valid semantic models extracted")
        sys.exit(1)
    
    # Analyze
    analyzer = SemanticAnalyzer(semantic_models)
    
    console.print("\n[bold]Analysis Results:[/bold]")
    
    # Conflicts
    conflicts = analyzer.detect_conflicts()
    console.print(f"\n[bold yellow]Conflicts:[/bold yellow] {len(conflicts)}")
    for conflict in conflicts[:5]:  # Show first 5
        console.print(f"  • {conflict.concept}: {conflict.dashboard1} vs {conflict.dashboard2}")
    if len(conflicts) > 5:
        console.print(f"  ... and {len(conflicts) - 5} more")
    
    # Semantic debt
    debt_report = analyzer.calculate_semantic_debt()
    console.print(f"\n[bold red]Semantic Debt:[/bold red] ${debt_report.total_cost:,.0f}")
    console.print(f"  {debt_report.message}")
    
    # Generate report
    if report:
        analyzer.generate_consolidation_report(report)
        console.print(f"\n[bold green]✓[/bold green] Report saved to {report}")


@cli.command()
@click.argument('ontology_file', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['fabric-iq', 'ontoguard', 'json-schema', 'owl']), required=True, help='Export format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def export(ontology_file, format, output):
    """Export ontology to different formats."""
    console.print(f"[bold green]Exporting[/bold green] {ontology_file} to {format} format...")
    
    # Load ontology (simplified - would need proper loading)
    console.print("[bold yellow]Note:[/bold yellow] Full export requires loading ontology from file")
    console.print("This is a simplified version. Use 'extract' command with --format option instead.")


@cli.command()
@click.argument('ontology_file', type=click.Path(exists=True))
@click.option('--schema', '-s', type=click.Path(), help='Current database schema JSON')
def validate(ontology_file, schema):
    """Validate schema bindings and detect drift."""
    console.print(f"[bold green]Validating[/bold green] {ontology_file}...")
    
    if schema:
        console.print(f"  Comparing against schema: {schema}")
        # Load and compare schemas
        console.print("[bold yellow]Note:[/bold yellow] Full validation requires schema mapping setup")
    else:
        console.print("[bold yellow]Warning:[/bold yellow] No schema provided. Cannot detect drift.")


@cli.command()
@click.argument('ontology_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output image file')
@click.option('--interactive', '-i', is_flag=True, help='Generate interactive HTML')
@click.option('--format', '-f', type=click.Choice(['png', 'svg', 'pdf']), default='png', help='Image format')
def visualize(ontology_file, output, interactive, format):
    """Visualize ontology as entity-relationship diagram."""
    console.print(f"[bold green]Visualizing[/bold green] {ontology_file}...")
    
    console.print("[bold yellow]Note:[/bold yellow] Full visualization requires loading ontology from file")
    console.print("This is a simplified version. Use 'extract' command first.")


@cli.command()
@click.option('--input-dir', '-i', type=click.Path(exists=True), required=True, help='Input directory with .pbix files')
@click.option('--output-dir', '-o', type=click.Path(), required=True, help='Output directory for ontologies')
def batch(input_dir, output_dir):
    """Process multiple .pbix files in batch."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    pbix_files = list(input_path.glob("*.pbix"))
    
    if not pbix_files:
        console.print(f"[bold red]Error:[/bold red] No .pbix files found in {input_dir}")
        sys.exit(1)
    
    console.print(f"[bold green]Processing[/bold green] {len(pbix_files)} files...")
    
    with Progress(console=console) as progress:
        task = progress.add_task("Processing...", total=len(pbix_files))
        
        for pbix_file in pbix_files:
            try:
                extractor = PowerBIExtractor(str(pbix_file))
                semantic_model = extractor.extract()
                
                generator = OntologyGenerator(semantic_model)
                ontology = generator.generate()
                
                output_file = output_path / f"{pbix_file.stem}_ontology.json"
                ontology_dict = {
                    "name": ontology.name,
                    "version": ontology.version,
                    "source": ontology.source,
                    "entities": len(ontology.entities),
                    "relationships": len(ontology.relationships),
                    "businessRules": len(ontology.business_rules)
                }
                
                with open(output_file, 'w') as f:
                    json.dump(ontology_dict, f, indent=2)
                
                progress.advance(task)
            except Exception as e:
                console.print(f"[bold yellow]Warning:[/bold yellow] Failed to process {pbix_file}: {e}")
                progress.advance(task)
    
    console.print(f"[bold green]✓[/bold green] Batch processing complete. Output: {output_dir}")


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()
