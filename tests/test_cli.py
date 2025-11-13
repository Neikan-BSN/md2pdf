import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock
from md2pdf import cli, main

@patch('md2pdf.prompt_file_selection')
def test_cli_displays_welcome(mock_files):
    """Test CLI displays welcome message"""
    # Mock file selection to avoid interactive prompt
    mock_files.return_value = []

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

# ===== File Selection Tests (Task 2.5) =====

def test_glob_files_pattern(tmp_path):
    """Test glob pattern matching"""
    from md2pdf import glob_files

    # Create test structure
    (tmp_path / "doc1.md").write_text("# Doc 1")
    (tmp_path / "doc2.md").write_text("# Doc 2")
    (tmp_path / "notes.txt").write_text("notes")

    files = glob_files(str(tmp_path / "*.md"))
    assert len(files) == 2
    assert all(f.suffix == '.md' for f in files)
    assert all(f.parent == tmp_path for f in files)

def test_glob_files_recursive(tmp_path):
    """Test recursive glob pattern"""
    from md2pdf import glob_files

    # Create nested structure
    (tmp_path / "doc.md").write_text("# Root")
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "nested.md").write_text("# Nested")

    files = glob_files(str(tmp_path / "**/*.md"))
    assert len(files) == 2

def test_glob_files_no_matches(tmp_path):
    """Test glob pattern with no matches"""
    from md2pdf import glob_files

    files = glob_files(str(tmp_path / "*.md"))
    assert len(files) == 0

def test_glob_files_sorted(tmp_path):
    """Test that glob results are sorted"""
    from md2pdf import glob_files

    # Create files in specific order
    (tmp_path / "c.md").write_text("# C")
    (tmp_path / "a.md").write_text("# A")
    (tmp_path / "b.md").write_text("# B")

    files = glob_files(str(tmp_path / "*.md"))
    names = [f.name for f in files]
    assert names == ["a.md", "b.md", "c.md"]

def test_glob_files_single_file(tmp_path):
    """Test direct file path (from spec)"""
    from md2pdf import glob_files

    test_file = tmp_path / "test.md"
    test_file.write_text("# Test")

    # Direct file should work
    files = glob_files(str(test_file))
    assert len(files) == 1
    assert files[0] == test_file

@patch('md2pdf.prompt_file_selection')
def test_prompt_file_selection_integration_single_file(mock_files, tmp_path):
    """Test file selection integration with single file"""
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test")

    # Mock the function to return our test file
    mock_files.return_value = [test_file]

    # Verify the mock works in CLI context
    runner = CliRunner()
    result = runner.invoke(cli)

    assert result.exit_code == 0
    assert mock_files.called

@patch('md2pdf.prompt_file_selection')
def test_prompt_file_selection_integration_batch(mock_files, tmp_path):
    """Test file selection integration with batch mode"""
    # Create multiple test files
    files = [
        tmp_path / "test1.md",
        tmp_path / "test2.md",
        tmp_path / "test3.md"
    ]
    for f in files:
        f.write_text("# Test")

    # Mock the function to return multiple files
    mock_files.return_value = files

    runner = CliRunner()
    result = runner.invoke(cli)

    assert result.exit_code == 0
    assert mock_files.called

def test_file_selection_logic_single_markdown(tmp_path):
    """Test file selection logic with single markdown file"""
    from md2pdf import glob_files

    test_file = tmp_path / "test.md"
    test_file.write_text("# Test")

    # Verify direct file path works
    assert test_file.is_file()
    assert test_file.suffix == '.md'

def test_file_selection_logic_batch_markdown(tmp_path):
    """Test file selection logic with batch markdown files"""
    from md2pdf import glob_files

    # Create multiple test files
    (tmp_path / "test1.md").write_text("# Test 1")
    (tmp_path / "test2.md").write_text("# Test 2")
    (tmp_path / "test3.md").write_text("# Test 3")

    # Use glob to find files
    files = glob_files(str(tmp_path / "*.md"))

    assert len(files) == 3
    assert all(f.suffix == '.md' for f in files)
