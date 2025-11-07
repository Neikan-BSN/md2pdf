import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock
from md2pdf import cli, main

def test_cli_displays_welcome():
    """Test CLI displays welcome message"""
    runner = CliRunner()
    result = runner.invoke(cli)

    assert result.exit_code == 0
    assert "md2pdf" in result.output.lower()

def test_main_entry_point():
    """Test main() entry point exists"""
    # main() should be callable
    assert callable(main)

@patch('md2pdf.prompt_file_selection')
@patch('md2pdf.prompt_output_format')
@patch('md2pdf.prompt_theme_selection')
@patch('md2pdf.process_conversion')
def test_cli_interactive_flow_single_file(mock_process, mock_theme, mock_format, mock_files):
    """Test interactive flow for single file"""
    runner = CliRunner()

    # Mock responses
    mock_files.return_value = [Path("test.md")]
    mock_format.return_value = "pdf"
    mock_theme.return_value = "academic"

    result = runner.invoke(cli)

    assert result.exit_code == 0
    assert mock_files.called
    assert mock_format.called
    assert mock_theme.called
    assert mock_process.called

@patch('md2pdf.prompt_file_selection')
@patch('md2pdf.prompt_output_format')
@patch('md2pdf.prompt_theme_selection')
@patch('md2pdf.process_conversion')
def test_cli_interactive_flow_batch_mode(mock_process, mock_theme, mock_format, mock_files):
    """Test interactive flow for batch processing"""
    runner = CliRunner()

    # Mock responses for batch
    mock_files.return_value = [Path("test1.md"), Path("test2.md")]
    mock_format.return_value = "html"
    mock_theme.return_value = "modern"

    result = runner.invoke(cli)

    assert result.exit_code == 0
    # Should skip filename prompt in batch mode
    assert mock_process.called
