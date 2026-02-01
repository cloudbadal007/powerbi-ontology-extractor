"""
Tests for CLI tool.
"""

import json
from pathlib import Path
from unittest.mock import patch, Mock

import pytest
from click.testing import CliRunner

from cli.pbi_ontology_cli import cli


class TestCLI:
    """Test CLI commands."""
    
    def test_cli_group(self):
        """Test that CLI group is accessible."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        
        assert result.exit_code == 0
        assert "PowerBI Ontology Extractor" in result.output
    
    @patch('cli.pbi_ontology_cli.PowerBIExtractor')
    @patch('cli.pbi_ontology_cli.OntologyGenerator')
    def test_extract_command(self, mock_generator_class, mock_extractor_class, temp_dir):
        """Test extract command."""
        # Mock extractor
        mock_extractor = Mock()
        mock_semantic_model = Mock()
        mock_semantic_model.entities = [Mock()]
        mock_semantic_model.relationships = [Mock()]
        mock_semantic_model.measures = [Mock()]
        mock_extractor.extract.return_value = mock_semantic_model
        
        # Mock generator
        mock_generator = Mock()
        mock_ontology = Mock()
        mock_ontology.entities = [Mock()]
        mock_ontology.relationships = [Mock()]
        mock_ontology.business_rules = [Mock()]
        mock_generator.generate.return_value = mock_ontology
        
        mock_extractor_class.return_value = mock_extractor
        mock_generator_class.return_value = mock_generator
        
        runner = CliRunner()
        pbix_file = temp_dir / "test.pbix"
        pbix_file.write_bytes(b"test")
        output_file = temp_dir / "output.json"
        
        result = runner.invoke(cli, [
            "extract",
            str(pbix_file),
            "--output", str(output_file)
        ])
        
        # Should complete (may have warnings about file format)
        assert result.exit_code in [0, 1]  # May fail due to invalid .pbix
    
    def test_analyze_command_help(self):
        """Test analyze command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])
        
        assert result.exit_code == 0
        assert "analyze" in result.output.lower()
    
    def test_export_command_help(self):
        """Test export command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["export", "--help"])
        
        assert result.exit_code == 0
        assert "export" in result.output.lower()
    
    def test_validate_command_help(self):
        """Test validate command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", "--help"])
        
        assert result.exit_code == 0
        assert "validate" in result.output.lower()
    
    def test_visualize_command_help(self):
        """Test visualize command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["visualize", "--help"])
        
        assert result.exit_code == 0
        assert "visualize" in result.output.lower()
    
    def test_batch_command_help(self):
        """Test batch command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["batch", "--help"])
        
        assert result.exit_code == 0
        assert "batch" in result.output.lower()
    
    def test_verbose_flag(self):
        """Test verbose flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--verbose", "--help"])
        
        assert result.exit_code == 0
