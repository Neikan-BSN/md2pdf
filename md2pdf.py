#!/usr/bin/env python3
"""
md2pdf - Interactive Markdown to PDF/HTML converter

Interactive CLI for converting markdown files with Mermaid diagrams,
math equations, and syntax highlighting to PDF or HTML.
"""

import click
import glob
from pathlib import Path
from typing import List, Optional
from config_loader import load_config
from theme_manager import list_themes

@click.command()
@click.option('--config', type=click.Path(exists=True), help='Path to config file')
def cli(config: Optional[str]):
    """Interactive Markdown to PDF/HTML converter"""
    click.echo("=== md2pdf: Markdown to PDF/HTML Converter ===\n")

    # Load configuration
    cfg = load_config(Path(config) if config else None)

    # Interactive prompt flow
    files = prompt_file_selection()
    if not files:
        click.echo("No files selected. Exiting.")
        return

    output_format = prompt_output_format(cfg)
    theme = prompt_theme_selection(cfg)

    # For single files, prompt for filename
    if len(files) == 1:
        filename = prompt_filename(files[0], output_format)
    else:
        filename = None  # Batch mode uses defaults

    # Process conversion
    process_conversion(files, output_format, theme, filename, cfg)

    click.echo("\n✓ Conversion complete!")

def glob_files(pattern: str) -> List[Path]:
    """
    Find files matching glob pattern.

    Args:
        pattern: Glob pattern (e.g., "*.md", "docs/**/*.md")

    Returns:
        List of matching file paths

    Examples:
        >>> glob_files("*.md")
        [Path("readme.md"), Path("notes.md")]

        >>> glob_files("docs/**/*.md")  # Recursive
        [Path("docs/guide.md"), Path("docs/api/reference.md")]
    """
    # Check if it's a direct file path first
    direct_path = Path(pattern)
    if direct_path.is_file():
        return [direct_path]

    # Use glob to find matching files
    matches = glob.glob(pattern, recursive=True)

    # Convert to Path objects and filter for files only
    files = [Path(m) for m in matches if Path(m).is_file()]

    return sorted(files)

def prompt_file_selection() -> List[Path]:
    """
    Prompt user for file selection (single or batch).

    Returns:
        List of selected file paths

    Examples:
        Interactive prompts:
        - Single file: "document.md"
        - Multiple files: "*.md"
        - Recursive: "docs/**/*.md"
    """
    click.echo("\n📄 File Selection")
    click.echo("Enter a file path or glob pattern (e.g., *.md, docs/**/*.md)")

    while True:
        pattern = click.prompt("Files", type=str)

        # Check if it's a direct file path
        direct_path = Path(pattern)
        if direct_path.is_file():
            # Single file
            if direct_path.suffix.lower() not in ['.md', '.markdown']:
                click.echo(f"⚠️  Warning: {direct_path.name} is not a markdown file", err=True)
                if not click.confirm("Continue anyway?"):
                    continue
            return [direct_path]

        # Try as glob pattern
        files = glob_files(pattern)

        if not files:
            click.echo(f"❌ No files found matching: {pattern}", err=True)
            if not click.confirm("Try again?", default=True):
                return []
            continue

        # Filter for markdown files
        md_files = [f for f in files if f.suffix.lower() in ['.md', '.markdown']]

        if not md_files:
            click.echo(f"❌ No markdown files found matching: {pattern}", err=True)
            if not click.confirm("Try again?", default=True):
                return []
            continue

        # Show found files
        click.echo(f"\n✓ Found {len(md_files)} markdown file(s):")
        for f in md_files[:5]:  # Show first 5
            click.echo(f"  - {f}")
        if len(md_files) > 5:
            click.echo(f"  ... and {len(md_files) - 5} more")

        if click.confirm("Proceed with these files?", default=True):
            return md_files

def prompt_output_format(config: dict) -> str:
    """Prompt user for output format (PDF or HTML)"""
    # Placeholder - will be implemented in next task
    click.echo("Format selection (placeholder)")
    return config['output']['format']

def prompt_theme_selection(config: dict) -> str:
    """Prompt user for theme selection"""
    # Placeholder - will be implemented in next task
    click.echo("Theme selection (placeholder)")
    return config['output']['default_theme']

def prompt_filename(input_file: Path, output_format: str) -> str:
    """Prompt user for output filename (single file only)"""
    # Placeholder - will be implemented in next task
    default = f"{input_file.stem}.{output_format}"
    click.echo(f"Filename prompt (placeholder): {default}")
    return default

def process_conversion(
    files: List[Path],
    output_format: str,
    theme: str,
    filename: Optional[str],
    config: dict
):
    """Process file conversion (placeholder)"""
    # Placeholder - will be integrated in later task
    click.echo(f"Processing {len(files)} file(s) with {theme} theme to {output_format}")

def main():
    """Main entry point"""
    cli()

if __name__ == '__main__':
    main()
