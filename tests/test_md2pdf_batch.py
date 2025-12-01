"""Tests for md2pdf_batch CLI."""

import subprocess
import sys


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
