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
from document_builder import build_html_document
from renderer_client import RendererClient

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
    """
    Prompt user for output format (PDF or HTML).

    Args:
        config: Configuration dictionary

    Returns:
        Selected format: 'pdf' or 'html'
    """
    click.echo("\n📄 Output Format Selection")
    click.echo("1. PDF (portable document)")
    click.echo("2. HTML (web page)")

    default_format = config['output']['format']
    default_num = '1' if default_format == 'pdf' else '2'

    while True:
        choice = input(f"Select format [1-2] (default: {default_num}): ").strip()

        # Use default if empty
        if not choice:
            choice = default_num

        if choice == '1':
            return 'pdf'
        elif choice == '2':
            return 'html'
        else:
            click.echo("❌ Invalid choice. Please enter 1 or 2.", err=True)

def prompt_theme_selection(config: dict) -> str:
    """
    Prompt user for theme selection.

    Args:
        config: Configuration dictionary

    Returns:
        Selected theme name
    """
    click.echo("\n🎨 Theme Selection")

    themes = list_themes()
    default_theme = config['output']['default_theme']

    # Display themes with numbers
    for idx, theme in enumerate(themes, 1):
        default_marker = " (default)" if theme == default_theme else ""
        click.echo(f"{idx}. {theme}{default_marker}")

    # Find default theme number
    try:
        default_num = str(themes.index(default_theme) + 1)
    except ValueError:
        default_num = '1'

    while True:
        choice = input(f"Select theme [1-{len(themes)}] (default: {default_num}): ").strip()

        # Use default if empty
        if not choice:
            choice = default_num

        try:
            theme_idx = int(choice) - 1
            if 0 <= theme_idx < len(themes):
                return themes[theme_idx]
            else:
                click.echo(f"❌ Invalid choice. Please enter 1-{len(themes)}.", err=True)
        except ValueError:
            click.echo(f"❌ Invalid choice. Please enter a number 1-{len(themes)}.", err=True)

def prompt_filename(input_file: Path, output_format: str) -> str:
    """
    Prompt user for output filename (single file only).

    Args:
        input_file: Input file path
        output_format: Output format ('pdf' or 'html')

    Returns:
        Output filename with correct extension
    """
    default_name = f"{input_file.stem}.{output_format}"

    click.echo("\n💾 Output Filename")
    click.echo(f"Default: {default_name}")

    while True:
        filename = input(f"Output filename (default: {default_name}): ").strip()

        # Use default if empty
        if not filename:
            return default_name

        # Ensure correct extension
        file_path = Path(filename)
        expected_ext = f".{output_format}"

        if file_path.suffix.lower() != expected_ext:
            # Add or replace extension
            filename = f"{file_path.stem}{expected_ext}"
            click.echo(f"ℹ️  Corrected filename: {filename}")

        return filename

def process_conversion(
    files: List[Path],
    output_format: str,
    theme: str,
    filename: Optional[str],
    config: dict
):
    """
    Process file conversion.

    Args:
        files: List of markdown files to convert
        output_format: Output format ('pdf' or 'html')
        theme: Theme name
        filename: Output filename (for single file) or None (for batch)
        config: Configuration dictionary
    """
    for idx, md_file in enumerate(files):
        click.echo(f"\n📄 Processing: {md_file.name}")

        # Read markdown content
        md_content = md_file.read_text(encoding='utf-8')

        # Build HTML document
        html = build_html_document(md_content, theme, config)

        # Determine output filename
        if filename and len(files) == 1:
            # Single file with custom filename
            output_name = filename
        else:
            # Batch mode or default: use input filename with new extension
            output_name = f"{md_file.stem}.{output_format}"

        output_path = Path(output_name)

        # Convert based on format
        if output_format == 'pdf':
            click.echo(f"  ⚙️  Converting to PDF...")

            # Prepare PDF options
            pdf_opts = config.get('pdf_options', {})
            render_options = {
                'format': pdf_opts.get('page_size', 'letter'),
                'printBackground': pdf_opts.get('print_background', True),
                'margin': pdf_opts.get('margins', {
                    'top': '1in',
                    'bottom': '1in',
                    'left': '1in',
                    'right': '1in'
                })
            }

            # Use renderer client
            with RendererClient() as client:
                pdf_bytes = client.render_pdf(html, render_options)

            # Write PDF
            output_path.write_bytes(pdf_bytes)

        else:  # html
            click.echo(f"  ⚙️  Saving HTML...")
            output_path.write_text(html, encoding='utf-8')

        click.echo(f"  ✅ Saved: {output_path}")

def main():
    """Main entry point"""
    cli()

if __name__ == '__main__':
    main()
