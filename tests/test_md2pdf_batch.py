"""Tests for md2pdf_batch CLI."""

import subprocess
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from md2pdf_batch import resolve_files, convert_file


def test_cli_help():
    """Test CLI responds to --help."""
    result = subprocess.run(
        [sys.executable, "md2pdf_batch.py", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert "--files" in result.stdout


def test_resolve_single_file(tmp_path):
    """Test resolving a single file path."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test")

    files = resolve_files([str(md_file)])
    assert len(files) == 1
    assert files[0] == md_file


def test_resolve_glob_pattern(tmp_path):
    """Test resolving glob patterns."""
    (tmp_path / "doc1.md").write_text("# Doc 1")
    (tmp_path / "doc2.md").write_text("# Doc 2")
    (tmp_path / "readme.txt").write_text("Not markdown")

    files = resolve_files([str(tmp_path / "*.md")])
    assert len(files) == 2
    assert all(f.suffix == ".md" for f in files)


def test_resolve_nonexistent_file():
    """Test error on nonexistent file."""
    with pytest.raises(FileNotFoundError):
        resolve_files(["nonexistent.md"])


def test_resolve_empty_glob(tmp_path):
    """Test error on glob with no matches."""
    with pytest.raises(FileNotFoundError):
        resolve_files([str(tmp_path / "*.md")])


def test_convert_file_pdf(tmp_path):
    """Test converting a single file to PDF."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test Document\n\nHello world.")

    # Mock the renderer to avoid actual PDF generation
    with patch("md2pdf_batch.RendererClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_instance.render_pdf.return_value = b"%PDF-1.4 fake pdf"
        mock_client.return_value = mock_instance

        result = convert_file(
            md_file,
            format="pdf",
            theme="academic",
            output_dir=None  # same-dir mode
        )

    assert result["success"] is True
    assert result["input"] == md_file
    assert result["output"].suffix == ".pdf"
    assert result["output"].parent == md_file.parent


def test_convert_file_html(tmp_path):
    """Test converting a single file to HTML."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test Document\n\nHello world.")

    result = convert_file(
        md_file,
        format="html",
        theme="minimal",
        output_dir=None
    )

    assert result["success"] is True
    assert result["output"].suffix == ".html"
    assert result["output"].exists()
