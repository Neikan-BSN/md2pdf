#!/usr/bin/env python3
"""
md2pdf - Interactive Markdown to PDF/HTML converter

Interactive CLI for converting markdown files with Mermaid diagrams,
math equations, and syntax highlighting to PDF or HTML.
"""

import click
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

def prompt_file_selection() -> List[Path]:
    """Prompt user for file selection (single or batch)"""
    # Placeholder - will be implemented in next task
    click.echo("File selection (placeholder)")
    return []

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
