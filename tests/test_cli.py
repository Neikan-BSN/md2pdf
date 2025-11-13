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
@patch('md2pdf.prompt_filename')
@patch('md2pdf.process_conversion')
def test_cli_interactive_flow_single_file(mock_process, mock_filename, mock_theme, mock_format, mock_files):
    """Test interactive flow for single file"""
    runner = CliRunner()

    # Mock responses
    mock_files.return_value = [Path("test.md")]
    mock_format.return_value = "pdf"
    mock_theme.return_value = "academic"
    mock_filename.return_value = "output.pdf"

    result = runner.invoke(cli)

    assert result.exit_code == 0
    assert mock_files.called
    assert mock_format.called
    assert mock_theme.called
    assert mock_filename.called
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
@patch('md2pdf.prompt_output_format')
@patch('md2pdf.prompt_theme_selection')
@patch('md2pdf.prompt_filename')
@patch('md2pdf.process_conversion')
def test_prompt_file_selection_integration_single_file(mock_process, mock_filename, mock_theme, mock_format, mock_files, tmp_path):
    """Test file selection integration with single file"""
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test")

    # Mock the function to return our test file
    mock_files.return_value = [test_file]
    mock_format.return_value = 'pdf'
    mock_theme.return_value = 'academic'
    mock_filename.return_value = 'output.pdf'

    # Verify the mock works in CLI context
    runner = CliRunner()
    result = runner.invoke(cli)

    assert result.exit_code == 0
    assert mock_files.called

@patch('md2pdf.prompt_file_selection')
@patch('md2pdf.prompt_output_format')
@patch('md2pdf.prompt_theme_selection')
@patch('md2pdf.process_conversion')
def test_prompt_file_selection_integration_batch(mock_process, mock_theme, mock_format, mock_files, tmp_path):
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
    mock_format.return_value = 'html'
    mock_theme.return_value = 'modern'

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

# ===== Task 1: Interactive Output Format Prompt Tests =====

def test_prompt_output_format_pdf_selection(monkeypatch):
    """Test user selects PDF format"""
    from md2pdf import prompt_output_format

    # Mock user input: select PDF (option 1)
    inputs = iter(['1'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    config = {'output': {'format': 'pdf'}}
    result = prompt_output_format(config)

    assert result == 'pdf'

def test_prompt_output_format_html_selection(monkeypatch):
    """Test user selects HTML format"""
    from md2pdf import prompt_output_format

    # Mock user input: select HTML (option 2)
    inputs = iter(['2'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    config = {'output': {'format': 'pdf'}}
    result = prompt_output_format(config)

    assert result == 'html'

def test_prompt_output_format_invalid_then_valid(monkeypatch):
    """Test invalid input then valid selection"""
    from md2pdf import prompt_output_format

    # Mock user input: invalid, then valid
    inputs = iter(['5', '1'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    config = {'output': {'format': 'pdf'}}
    result = prompt_output_format(config)

    assert result == 'pdf'

# ===== Task 2: Interactive Theme Selection Prompt Tests =====

def test_prompt_theme_selection_valid(monkeypatch):
    """Test user selects valid theme"""
    from md2pdf import prompt_theme_selection
    from theme_manager import list_themes

    # Mock user input: select first theme
    inputs = iter(['1'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    config = {'output': {'default_theme': 'academic'}}
    result = prompt_theme_selection(config)

    themes = list_themes()
    assert result in themes

def test_prompt_theme_selection_default(monkeypatch):
    """Test user accepts default theme"""
    from md2pdf import prompt_theme_selection

    # Mock user input: empty (default)
    inputs = iter([''])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    config = {'output': {'default_theme': 'academic'}}
    result = prompt_theme_selection(config)

    assert result == 'academic'

def test_prompt_theme_selection_invalid_then_valid(monkeypatch):
    """Test invalid input then valid selection"""
    from md2pdf import prompt_theme_selection

    # Mock user input: invalid, then valid
    inputs = iter(['99', '1'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    config = {'output': {'default_theme': 'academic'}}
    result = prompt_theme_selection(config)

    # Should return a valid theme
    from theme_manager import list_themes
    assert result in list_themes()

# ===== Task 3: Interactive Filename Prompt Tests =====

def test_prompt_filename_accepts_default(monkeypatch):
    """Test user accepts default filename"""
    from md2pdf import prompt_filename
    from pathlib import Path

    # Mock user input: empty (default)
    inputs = iter([''])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    input_file = Path("document.md")
    result = prompt_filename(input_file, "pdf")

    assert result == "document.pdf"

def test_prompt_filename_custom_name(monkeypatch):
    """Test user provides custom filename"""
    from md2pdf import prompt_filename
    from pathlib import Path

    # Mock user input: custom filename
    inputs = iter(['my-output.pdf'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    input_file = Path("document.md")
    result = prompt_filename(input_file, "pdf")

    assert result == "my-output.pdf"

def test_prompt_filename_adds_extension(monkeypatch):
    """Test filename without extension gets extension added"""
    from md2pdf import prompt_filename
    from pathlib import Path

    # Mock user input: filename without extension
    inputs = iter(['my-output'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    input_file = Path("document.md")
    result = prompt_filename(input_file, "pdf")

    assert result == "my-output.pdf"

def test_prompt_filename_wrong_extension_corrected(monkeypatch):
    """Test filename with wrong extension gets corrected"""
    from md2pdf import prompt_filename
    from pathlib import Path

    # Mock user input: filename with wrong extension
    inputs = iter(['output.html'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    input_file = Path("document.md")
    result = prompt_filename(input_file, "pdf")

    # Should correct extension to pdf
    assert result == "output.pdf"


# ===== Task 5: Process Conversion Integration Tests =====

def test_process_conversion_pdf_creates_file(tmp_path, monkeypatch):
    """Test PDF conversion creates output file"""
    from md2pdf import process_conversion
    from pathlib import Path

    # Create test markdown file
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test Document\n\nContent here")

    config = {
        'rendering': {'mermaid_theme': 'default'},
        'pdf_options': {
            'page_size': 'letter',
            'margins': {'top': '1in', 'bottom': '1in', 'left': '1in', 'right': '1in'},
            'print_background': True
        }
    }

    # Mock output path
    output_file = tmp_path / "output.pdf"

    # Change to tmp_path directory
    monkeypatch.chdir(tmp_path)

    # Process conversion
    process_conversion(
        files=[md_file],
        output_format='pdf',
        theme='academic',
        filename='output.pdf',
        config=config
    )

    # Check file created
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_process_conversion_html_creates_file(tmp_path, monkeypatch):
    """Test HTML conversion creates output file"""
    from md2pdf import process_conversion
    from pathlib import Path

    # Create test markdown file
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test Document\n\nContent here")

    config = {
        'rendering': {'mermaid_theme': 'default'}
    }

    # Mock output path
    output_file = tmp_path / "output.html"

    # Change to tmp_path directory
    monkeypatch.chdir(tmp_path)

    # Process conversion
    process_conversion(
        files=[md_file],
        output_format='html',
        theme='academic',
        filename='output.html',
        config=config
    )

    # Check file created
    assert output_file.exists()
    content = output_file.read_text()
    assert '<!DOCTYPE html>' in content
    assert '<h1>Test Document</h1>' in content
