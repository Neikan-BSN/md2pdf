# md2pdf Skill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a Claude Code skill that wraps md2pdf with configurable defaults, interactive prompts, and parallel batch processing.

**Architecture:** Two components - (1) `md2pdf_batch.py` non-interactive CLI with argparse for scripted conversion, (2) `.claude/commands/md2pdf.md` skill file that handles UX and invokes the script. Config stored in `.claude/config/md2pdf-skill.json`.

**Tech Stack:** Python (argparse, pathlib, json), existing md2pdf modules (document_builder, renderer_client, theme_manager, config_loader)

---

## Task 1: Create md2pdf_batch.py CLI Skeleton

**Files:**
- Create: `md2pdf_batch.py`
- Test: `tests/test_md2pdf_batch.py`

**Step 1: Write failing test for CLI existence**

```python
# tests/test_md2pdf_batch.py
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
```

**Step 2: Run test to verify it fails**

Run: `cd .worktrees/md2pdf-skill && PYTHONPATH=. pytest tests/test_md2pdf_batch.py::test_cli_help -v`
Expected: FAIL with "No such file or directory" or similar

**Step 3: Write minimal implementation**

```python
#!/usr/bin/env python3
"""
md2pdf_batch - Non-interactive batch markdown converter.

CLI wrapper for scripted/automated markdown to PDF/HTML conversion.
"""

import argparse
import sys
from pathlib import Path


def parse_args(args=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="md2pdf_batch",
        description="Non-interactive batch markdown to PDF/HTML converter"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="Markdown file(s) or glob pattern(s) to convert"
    )
    parser.add_argument(
        "--format",
        choices=["pdf", "html"],
        default="pdf",
        help="Output format (default: pdf)"
    )
    parser.add_argument(
        "--theme",
        default="academic",
        help="Theme name (default: academic)"
    )
    parser.add_argument(
        "--output-mode",
        choices=["same-dir", "custom"],
        default="same-dir",
        help="Output location mode (default: same-dir)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Custom output directory (when --output-mode=custom)"
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as JSON (for automation)"
    )
    return parser.parse_args(args)


def main(args=None):
    """Main entry point."""
    parsed = parse_args(args)
    # TODO: Implementation
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 4: Run test to verify it passes**

Run: `cd .worktrees/md2pdf-skill && PYTHONPATH=. pytest tests/test_md2pdf_batch.py::test_cli_help -v`
Expected: PASS

**Step 5: Commit**

```bash
git add md2pdf_batch.py tests/test_md2pdf_batch.py
git commit -m "feat(batch): add CLI skeleton with argparse"
```

---

## Task 2: Add File Resolution Logic

**Files:**
- Modify: `md2pdf_batch.py`
- Test: `tests/test_md2pdf_batch.py`

**Step 1: Write failing test for file resolution**

```python
# Add to tests/test_md2pdf_batch.py

import pytest
from md2pdf_batch import resolve_files


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
```

**Step 2: Run tests to verify they fail**

Run: `cd .worktrees/md2pdf-skill && PYTHONPATH=. pytest tests/test_md2pdf_batch.py::test_resolve_single_file -v`
Expected: FAIL with "cannot import name 'resolve_files'"

**Step 3: Write implementation**

```python
# Add to md2pdf_batch.py after imports

import glob
from typing import List


def resolve_files(patterns: List[str]) -> List[Path]:
    """
    Resolve file patterns to actual file paths.

    Args:
        patterns: List of file paths or glob patterns

    Returns:
        List of resolved Path objects

    Raises:
        FileNotFoundError: If no files found
    """
    resolved = []

    for pattern in patterns:
        path = Path(pattern)

        # Direct file path
        if path.is_file():
            resolved.append(path)
            continue

        # Glob pattern
        matches = glob.glob(pattern, recursive=True)
        files = [Path(m) for m in matches if Path(m).is_file()]

        if not files and not path.is_file():
            raise FileNotFoundError(f"No files found matching: {pattern}")

        resolved.extend(files)

    if not resolved:
        raise FileNotFoundError("No files found")

    return sorted(set(resolved))
```

**Step 4: Run tests to verify they pass**

Run: `cd .worktrees/md2pdf-skill && PYTHONPATH=. pytest tests/test_md2pdf_batch.py -k "resolve" -v`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add md2pdf_batch.py tests/test_md2pdf_batch.py
git commit -m "feat(batch): add file resolution with glob support"
```

---

## Task 3: Add Single File Conversion

**Files:**
- Modify: `md2pdf_batch.py`
- Test: `tests/test_md2pdf_batch.py`

**Step 1: Write failing test for conversion**

```python
# Add to tests/test_md2pdf_batch.py

from unittest.mock import patch, MagicMock
from md2pdf_batch import convert_file


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
```

**Step 2: Run tests to verify they fail**

Run: `cd .worktrees/md2pdf-skill && PYTHONPATH=. pytest tests/test_md2pdf_batch.py::test_convert_file_pdf -v`
Expected: FAIL with "cannot import name 'convert_file'"

**Step 3: Write implementation**

```python
# Add to md2pdf_batch.py after resolve_files

from typing import Dict, Any, Optional
from document_builder import build_html_document
from renderer_client import RendererClient
from config_loader import load_config


def convert_file(
    input_file: Path,
    format: str,
    theme: str,
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Convert a single markdown file.

    Args:
        input_file: Path to markdown file
        format: Output format ('pdf' or 'html')
        theme: Theme name
        output_dir: Custom output directory (None = same as input)

    Returns:
        Dict with success, input, output, error keys
    """
    try:
        # Determine output path
        if output_dir:
            output_path = output_dir / f"{input_file.stem}.{format}"
        else:
            output_path = input_file.parent / f"{input_file.stem}.{format}"

        # Read markdown
        md_content = input_file.read_text(encoding="utf-8")

        # Load config
        config = load_config()

        # Build HTML
        html = build_html_document(md_content, theme, config)

        # Convert based on format
        if format == "pdf":
            pdf_opts = config.get("pdf_options", {})
            render_options = {
                "format": pdf_opts.get("page_size", "letter"),
                "printBackground": pdf_opts.get("print_background", True),
                "margin": pdf_opts.get("margins", {
                    "top": "1in", "bottom": "1in",
                    "left": "1in", "right": "1in"
                })
            }

            with RendererClient() as client:
                pdf_bytes = client.render_pdf(html, render_options)

            output_path.write_bytes(pdf_bytes)
        else:
            output_path.write_text(html, encoding="utf-8")

        return {
            "success": True,
            "input": input_file,
            "output": output_path,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "input": input_file,
            "output": None,
            "error": str(e)
        }
```

**Step 4: Run tests to verify they pass**

Run: `cd .worktrees/md2pdf-skill && PYTHONPATH=. pytest tests/test_md2pdf_batch.py -k "convert_file" -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add md2pdf_batch.py tests/test_md2pdf_batch.py
git commit -m "feat(batch): add single file conversion"
```

---

## Task 4: Add Batch Processing with JSON Output

**Files:**
- Modify: `md2pdf_batch.py`
- Test: `tests/test_md2pdf_batch.py`

**Step 1: Write failing test for batch processing**

```python
# Add to tests/test_md2pdf_batch.py

import json
from md2pdf_batch import process_batch


def test_process_batch(tmp_path):
    """Test batch processing multiple files."""
    (tmp_path / "doc1.md").write_text("# Doc 1")
    (tmp_path / "doc2.md").write_text("# Doc 2")

    files = [tmp_path / "doc1.md", tmp_path / "doc2.md"]

    results = process_batch(
        files=files,
        format="html",
        theme="academic",
        output_dir=None
    )

    assert len(results) == 2
    assert all(r["success"] for r in results)
    assert (tmp_path / "doc1.html").exists()
    assert (tmp_path / "doc2.html").exists()


def test_cli_json_output(tmp_path):
    """Test CLI with --json-output flag."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test")

    result = subprocess.run(
        [
            sys.executable, "md2pdf_batch.py",
            "--files", str(md_file),
            "--format", "html",
            "--json-output"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["total"] == 1
    assert output["success"] == 1
    assert len(output["results"]) == 1
```

**Step 2: Run tests to verify they fail**

Run: `cd .worktrees/md2pdf-skill && PYTHONPATH=. pytest tests/test_md2pdf_batch.py::test_process_batch -v`
Expected: FAIL with "cannot import name 'process_batch'"

**Step 3: Write implementation**

```python
# Add to md2pdf_batch.py after convert_file

import json as json_module


def process_batch(
    files: List[Path],
    format: str,
    theme: str,
    output_dir: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Process multiple files sequentially.

    Args:
        files: List of markdown files
        format: Output format
        theme: Theme name
        output_dir: Custom output directory

    Returns:
        List of result dicts from convert_file
    """
    results = []
    for f in files:
        result = convert_file(f, format, theme, output_dir)
        results.append(result)
    return results


# Update main() function
def main(args=None):
    """Main entry point."""
    parsed = parse_args(args)

    try:
        # Resolve files
        files = resolve_files(parsed.files)

        # Determine output directory
        output_dir = parsed.output_dir if parsed.output_mode == "custom" else None

        # Process files
        results = process_batch(
            files=files,
            format=parsed.format,
            theme=parsed.theme,
            output_dir=output_dir
        )

        # Calculate summary
        success_count = sum(1 for r in results if r["success"])

        # Output results
        if parsed.json_output:
            output = {
                "total": len(results),
                "success": success_count,
                "failed": len(results) - success_count,
                "results": [
                    {
                        "input": str(r["input"]),
                        "output": str(r["output"]) if r["output"] else None,
                        "success": r["success"],
                        "error": r["error"]
                    }
                    for r in results
                ]
            }
            print(json_module.dumps(output, indent=2))
        else:
            # Human-readable output
            print(f"Converted {success_count}/{len(results)} files")
            for r in results:
                status = "+" if r["success"] else "x"
                if r["success"]:
                    print(f"  {status} {r['input'].name} -> {r['output'].name}")
                else:
                    print(f"  {status} {r['input'].name} ({r['error']})")

        return 0 if success_count == len(results) else 1

    except FileNotFoundError as e:
        if parsed.json_output:
            print(json_module.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1
```

**Step 4: Run tests to verify they pass**

Run: `cd .worktrees/md2pdf-skill && PYTHONPATH=. pytest tests/test_md2pdf_batch.py -k "batch or json" -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add md2pdf_batch.py tests/test_md2pdf_batch.py
git commit -m "feat(batch): add batch processing with JSON output"
```

---

## Task 5: Add Theme Validation

**Files:**
- Modify: `md2pdf_batch.py`
- Test: `tests/test_md2pdf_batch.py`

**Step 1: Write failing test**

```python
# Add to tests/test_md2pdf_batch.py

def test_invalid_theme_error(tmp_path):
    """Test error on invalid theme."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test")

    result = subprocess.run(
        [
            sys.executable, "md2pdf_batch.py",
            "--files", str(md_file),
            "--theme", "nonexistent_theme",
            "--json-output"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 1
    output = json.loads(result.stdout)
    assert "error" in output
    assert "theme" in output["error"].lower()
```

**Step 2: Run test to verify it fails**

Run: `cd .worktrees/md2pdf-skill && PYTHONPATH=. pytest tests/test_md2pdf_batch.py::test_invalid_theme_error -v`
Expected: FAIL (currently returns success or different error)

**Step 3: Write implementation**

```python
# Add to md2pdf_batch.py after imports

from theme_manager import list_themes


def validate_theme(theme: str) -> None:
    """
    Validate theme exists.

    Raises:
        ValueError: If theme not found
    """
    available = list_themes()
    if theme not in available:
        raise ValueError(
            f"Theme '{theme}' not found. Available: {', '.join(available)}"
        )


# Update main() to validate theme early
def main(args=None):
    """Main entry point."""
    parsed = parse_args(args)

    try:
        # Validate theme first
        validate_theme(parsed.theme)

        # ... rest of existing code
```

**Step 4: Run test to verify it passes**

Run: `cd .worktrees/md2pdf-skill && PYTHONPATH=. pytest tests/test_md2pdf_batch.py::test_invalid_theme_error -v`
Expected: PASS

**Step 5: Commit**

```bash
git add md2pdf_batch.py tests/test_md2pdf_batch.py
git commit -m "feat(batch): add theme validation"
```

---

## Task 6: Create Skill Config Schema

**Files:**
- Create: `.claude/config/md2pdf-skill.json` (template/example)
- Modify: `md2pdf_batch.py` (add config loading)
- Test: `tests/test_md2pdf_batch.py`

**Step 1: Write failing test**

```python
# Add to tests/test_md2pdf_batch.py

from md2pdf_batch import load_skill_config, save_skill_config, DEFAULT_CONFIG


def test_load_skill_config_default(tmp_path, monkeypatch):
    """Test loading default config when none exists."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))

    config = load_skill_config()

    assert config == DEFAULT_CONFIG
    assert config["defaults"]["format"] == "pdf"
    assert config["defaults"]["theme"] == "academic"


def test_save_and_load_config(tmp_path, monkeypatch):
    """Test saving and loading config."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))

    custom = {
        "defaults": {
            "format": "html",
            "theme": "modern",
            "output_mode": "same-dir"
        },
        "prompt_behavior": {
            "always_confirm": True,
            "prompt_on_batch": False
        }
    }

    save_skill_config(custom)
    loaded = load_skill_config()

    assert loaded == custom
```

**Step 2: Run test to verify it fails**

Run: `cd .worktrees/md2pdf-skill && PYTHONPATH=. pytest tests/test_md2pdf_batch.py::test_load_skill_config_default -v`
Expected: FAIL with "cannot import name 'load_skill_config'"

**Step 3: Write implementation**

```python
# Add to md2pdf_batch.py near top

import os

DEFAULT_CONFIG = {
    "defaults": {
        "format": "pdf",
        "theme": "academic",
        "output_mode": "same-dir"
    },
    "prompt_behavior": {
        "always_confirm": False,
        "prompt_on_batch": True
    }
}


def get_config_path() -> Path:
    """Get path to skill config file."""
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR", ".claude/config")
    return Path(config_dir) / "md2pdf-skill.json"


def load_skill_config() -> Dict[str, Any]:
    """Load skill configuration, returning defaults if not found."""
    config_path = get_config_path()

    if config_path.exists():
        return json_module.loads(config_path.read_text(encoding="utf-8"))

    return DEFAULT_CONFIG.copy()


def save_skill_config(config: Dict[str, Any]) -> None:
    """Save skill configuration."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json_module.dumps(config, indent=2),
        encoding="utf-8"
    )
```

**Step 4: Run tests to verify they pass**

Run: `cd .worktrees/md2pdf-skill && PYTHONPATH=. pytest tests/test_md2pdf_batch.py -k "skill_config" -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add md2pdf_batch.py tests/test_md2pdf_batch.py
git commit -m "feat(batch): add skill config load/save"
```

---

## Task 7: Create the Skill File

**Files:**
- Create: `.claude/commands/md2pdf.md`

**Step 1: Create skill directory**

```bash
mkdir -p .claude/commands
```

**Step 2: Write skill file**

Use the `superpowers:writing-skills` skill to create this file, then test with `superpowers:testing-skills-with-subagents`.

**Skill file content:**

```markdown
---
model: haiku
description: Convert markdown files to PDF/HTML with configurable defaults
---

# md2pdf Skill

Convert markdown files to PDF or HTML using the md2pdf renderer.

## Usage

```
/md2pdf <file-or-pattern>
/md2pdf docs/report.md
/md2pdf "slides/*.md"
/md2pdf file1.md file2.md
```

## Behavior

1. **Parse input** - Extract file path(s) from arguments
2. **Resolve files** - Expand globs, validate files exist
3. **Load config** - Read defaults from `.claude/config/md2pdf-skill.json`
4. **Present settings** - Show current defaults
5. **Prompt if needed** - Ask to override defaults
6. **Execute conversion** - Run `md2pdf_batch.py`
7. **Report results** - Show success/failure summary
8. **Offer to save** - Ask to save settings as new defaults

## Instructions

When this skill is invoked with file arguments:

1. Extract the file pattern from the user's command (everything after `/md2pdf `)

2. Run file resolution:
   ```bash
   python md2pdf_batch.py --files "<pattern>" --json-output --format pdf --theme academic 2>&1 | head -1
   ```
   Check if this returns an error. If files not found, report and stop.

3. Load skill config if exists:
   ```bash
   cat .claude/config/md2pdf-skill.json 2>/dev/null || echo '{"defaults":{"format":"pdf","theme":"academic"}}'
   ```

4. Report to user:
   ```
   Found N file(s) to convert
   Current settings: PDF format, academic theme

   Proceed with these settings? [Y/n/customize]
   ```

5. If user says customize (c), prompt for:
   - Format: pdf or html
   - Theme: academic, clinical, journal, minimal, modern, or presentation

6. Execute conversion:
   ```bash
   python md2pdf_batch.py --files "<pattern>" --format <format> --theme <theme>
   ```

7. Report results from output

8. If successful, ask:
   ```
   Save these settings as defaults? [y/N]
   ```
   If yes, update `.claude/config/md2pdf-skill.json`

## Parallel Processing (6+ files)

When batch contains 6 or more files:

1. Split files into chunks of ~4 files each
2. Spawn parallel Task agents (max 5) with model=haiku
3. Each agent runs: `python md2pdf_batch.py --files <chunk> --json-output ...`
4. Collect JSON results from all agents
5. Report consolidated summary

Example parallel dispatch:
```
Files: doc1.md doc2.md doc3.md doc4.md doc5.md doc6.md doc7.md doc8.md

Agent 1: doc1.md doc2.md doc3.md doc4.md
Agent 2: doc5.md doc6.md doc7.md doc8.md
```

## Error Handling

- File not found: Report error, do not proceed
- Invalid theme: Report available themes
- Renderer failure: Report which files failed, continue with others
- Partial batch failure: Report summary with successes and failures
```

**Step 3: Commit**

```bash
git add .claude/commands/md2pdf.md
git commit -m "feat(skill): add md2pdf slash command"
```

---

## Task 8: Integration Testing

**Files:**
- Test: `tests/test_md2pdf_batch.py` (add integration tests)

**Step 1: Write integration test**

```python
# Add to tests/test_md2pdf_batch.py

def test_full_cli_html_conversion(tmp_path):
    """Integration test: full CLI HTML conversion."""
    # Create test file
    md_file = tmp_path / "integration_test.md"
    md_file.write_text("# Integration Test\n\nThis is a test document.")

    # Run CLI
    result = subprocess.run(
        [
            sys.executable, "md2pdf_batch.py",
            "--files", str(md_file),
            "--format", "html",
            "--theme", "minimal"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "Converted 1/1" in result.stdout

    # Verify output file
    html_file = tmp_path / "integration_test.html"
    assert html_file.exists()
    content = html_file.read_text()
    assert "Integration Test" in content
    assert "minimal" in content.lower() or "stylesheet" in content.lower()


def test_full_cli_batch_conversion(tmp_path):
    """Integration test: batch conversion."""
    # Create multiple files
    for i in range(3):
        (tmp_path / f"batch{i}.md").write_text(f"# Batch Doc {i}")

    # Run CLI
    result = subprocess.run(
        [
            sys.executable, "md2pdf_batch.py",
            "--files", str(tmp_path / "batch*.md"),
            "--format", "html"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "Converted 3/3" in result.stdout

    # Verify all outputs exist
    for i in range(3):
        assert (tmp_path / f"batch{i}.html").exists()
```

**Step 2: Run integration tests**

Run: `cd .worktrees/md2pdf-skill && PYTHONPATH=. pytest tests/test_md2pdf_batch.py -k "integration" -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/test_md2pdf_batch.py
git commit -m "test(batch): add integration tests"
```

---

## Task 9: Final Validation and Documentation

**Step 1: Run full test suite**

```bash
cd .worktrees/md2pdf-skill
PYTHONPATH=. pytest tests/ -v
```

Expected: All tests pass (existing 59 + new batch tests)

**Step 2: Test skill manually**

```bash
# In Claude Code session in worktree:
/md2pdf test1.md
```

**Step 3: Update CLAUDE.md with skill documentation**

Add to CLAUDE.md:

```markdown
## Skills

### /md2pdf

Convert markdown files to PDF/HTML:

```bash
/md2pdf docs/report.md          # Single file
/md2pdf "slides/*.md"           # Batch with glob
/md2pdf file1.md file2.md       # Multiple files
```

Configuration stored in `.claude/config/md2pdf-skill.json`.
```

**Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add md2pdf skill to CLAUDE.md"
```

---

## Summary

| Task | Description | Tests |
|------|-------------|-------|
| 1 | CLI skeleton | 1 |
| 2 | File resolution | 4 |
| 3 | Single file conversion | 2 |
| 4 | Batch processing + JSON | 2 |
| 5 | Theme validation | 1 |
| 6 | Skill config | 2 |
| 7 | Skill file | - |
| 8 | Integration tests | 2 |
| 9 | Final validation | - |

**Total new tests:** ~14
**Estimated time:** 45-60 minutes
