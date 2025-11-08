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
from jinja2 import Template
from config_loader import load_config
from theme_manager import list_themes, load_theme_css, ThemeManager
from markdown_renderer import render_markdown, extract_title
from renderer_client import RendererClient, RendererServerError

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
        config: Configuration dictionary with default format

    Returns:
        Selected format ('pdf' or 'html')

    Examples:
        Interactive menu:
        1. PDF
        2. HTML
    """
    click.echo("\n📄 Output Format")

    # Defensive: validate config structure
    try:
        default_format = config['output']['format']
    except (KeyError, TypeError):
        click.echo("⚠️  Warning: Invalid config, using default format (PDF)", err=True)
        default_format = 'pdf'

    default_num = 1 if default_format == 'pdf' else 2

    while True:
        click.echo("Select output format:")
        click.echo("  1. PDF (print-ready)")
        click.echo("  2. HTML (web-ready)")

        choice = click.prompt(
            "Format",
            type=int,
            default=default_num,
            show_default=True
        )

        if choice == 1:
            return 'pdf'
        elif choice == 2:
            return 'html'
        else:
            click.echo(f"❌ Invalid choice: {choice}. Please select 1 or 2.", err=True)
            continue

def prompt_theme_selection(config: dict) -> str:
    """
    Prompt user for theme selection.

    Args:
        config: Configuration dictionary with default theme

    Returns:
        Selected theme name

    Examples:
        Interactive menu:
        1. Academic (serif, traditional)
        2. Modern (sans-serif, colorful)
        3. Minimal (clean, simple)
        4. Presentation (large fonts, dark)
    """
    click.echo("\n🎨 Theme Selection")

    # Get available themes with error handling
    try:
        themes = list_themes()
    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
        click.echo("Using default theme: academic", err=True)
        return 'academic'

    if not themes:
        click.echo("❌ Error: No themes found in themes directory", err=True)
        click.echo("Using default theme: academic", err=True)
        return 'academic'

    # Theme descriptions
    descriptions = {
        'academic': 'Serif, traditional scholarly style',
        'modern': 'Sans-serif, colorful web style',
        'minimal': 'Clean, simple, maximum readability',
        'presentation': 'Large fonts, dark background'
    }

    # Find default theme index with defensive config access
    try:
        default_theme = config['output']['default_theme']
    except (KeyError, TypeError):
        click.echo("⚠️  Warning: Invalid config, using default theme (academic)", err=True)
        default_theme = 'academic'

    try:
        default_num = themes.index(default_theme) + 1
    except ValueError:
        default_num = 1

    while True:
        click.echo("Select theme:")
        for i, theme in enumerate(themes, 1):
            desc = descriptions.get(theme, 'Custom theme')
            click.echo(f"  {i}. {theme.capitalize()} - {desc}")

        choice = click.prompt(
            "Theme",
            type=int,
            default=default_num,
            show_default=True
        )

        if 1 <= choice <= len(themes):
            selected_theme = themes[choice - 1]
            click.echo(f"✓ Selected: {selected_theme}")
            return selected_theme
        else:
            click.echo(f"❌ Invalid choice: {choice}. Please select 1-{len(themes)}.", err=True)
            continue

def prompt_filename_default(input_file: Path, output_format: str) -> str:
    """
    Generate default output filename.

    Args:
        input_file: Input file path
        output_format: Output format ('pdf' or 'html')

    Returns:
        Default filename with correct extension

    Examples:
        >>> prompt_filename_default(Path("doc.md"), "pdf")
        'doc.pdf'

        >>> prompt_filename_default(Path("notes.md"), "html")
        'notes.html'
    """
    return f"{input_file.stem}.{output_format}"

def prompt_filename(input_file: Path, output_format: str) -> str:
    """
    Prompt user for output filename (single file only).

    Args:
        input_file: Input file path
        output_format: Output format ('pdf' or 'html')

    Returns:
        Output filename (with extension)

    Examples:
        Interactive flow:
        - Shows default: "document.pdf"
        - Asks: "Use default filename? [Y/n]"
        - If yes: returns default
        - If no: prompts for custom name
    """
    click.echo("\n📝 Output Filename")

    default_filename = prompt_filename_default(input_file, output_format)
    click.echo(f"Default: {default_filename}")

    if click.confirm("Use default filename?", default=True):
        return default_filename

    # Prompt for custom filename
    while True:
        custom_name = click.prompt("Custom filename", type=str)

        # Ensure extension matches output format
        if not custom_name.endswith(f".{output_format}"):
            click.echo(f"⚠️  Warning: Adding .{output_format} extension", err=True)
            custom_name = f"{custom_name}.{output_format}"

        return custom_name

def process_conversion(
    files: List[Path],
    output_format: str,
    theme: str,
    filename: Optional[str],
    config: dict
):
    """
    Process file conversion (markdown to PDF/HTML).

    Args:
        files: List of input markdown files
        output_format: Output format ('pdf' or 'html')
        theme: Selected theme name
        filename: Custom filename (single file only, None for batch)
        config: Configuration dictionary
    """
    click.echo(f"\n🔄 Processing {len(files)} file(s)")
    click.echo(f"Format: {output_format}, Theme: {theme}")

    # Load theme CSS
    try:
        theme_css = load_theme_css(theme)
    except FileNotFoundError as e:
        click.echo(f"❌ Error loading theme: {e}", err=True)
        return

    # Get Mermaid theme from config
    theme_manager = ThemeManager(config)
    mermaid_theme = theme_manager.get_mermaid_theme(theme)

    # Load HTML template
    template_path = Path(__file__).parent / "templates" / "base.html"
    if not template_path.exists():
        click.echo(f"❌ Error: Template not found: {template_path}", err=True)
        return

    with open(template_path, 'r', encoding='utf-8') as f:
        template = Template(f.read())

    # Start renderer service for PDF conversion
    client = None
    if output_format == 'pdf':
        click.echo("\n🚀 Starting renderer service...")
        client = RendererClient()
        try:
            client.start_server()
            click.echo("✓ Renderer service ready")
        except RendererServerError as e:
            click.echo(f"❌ Failed to start renderer: {e}", err=True)
            return

    # Process each file
    success_count = 0
    error_count = 0

    for file in files:
        try:
            # Read markdown file
            md_content = file.read_text(encoding='utf-8')

            # Convert markdown to HTML
            html_content = render_markdown(md_content)
            title = extract_title(md_content)

            # Render with template
            full_html = template.render(
                title=title,
                content=html_content,
                theme_css=theme_css,
                mermaid_theme=mermaid_theme
            )

            # Create output directory
            output_dir = file.parent / "converted"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Determine output filename
            if filename and len(files) == 1:
                output_path = output_dir / filename
            else:
                default_name = prompt_filename_default(file, output_format)
                output_path = output_dir / default_name

            # Render to PDF or save HTML
            if output_format == 'pdf':
                pdf_bytes = client.render_pdf(full_html, options={
                    'pageSize': config.get('pdf_options', {}).get('page_size', 'Letter'),
                    'margins': config.get('pdf_options', {}).get('margins', {
                        'top': '1in', 'bottom': '1in', 'left': '1in', 'right': '1in'
                    }),
                    'printBackground': config.get('pdf_options', {}).get('print_background', True),
                    'waitForRendering': config.get('rendering', {}).get('wait_for_rendering', 1000)
                })
                output_path.write_bytes(pdf_bytes)
            else:  # html
                output_path.write_text(full_html, encoding='utf-8')

            # Success
            file_size = output_path.stat().st_size
            click.echo(f"  ✓ {file.name} → {output_path.relative_to(file.parent)} ({file_size:,} bytes)")
            success_count += 1

        except Exception as e:
            click.echo(f"  ✗ {file.name} - Error: {e}", err=True)
            error_count += 1

    # Stop renderer service
    if client is not None:
        client.stop_server()
        click.echo("\n✓ Renderer service stopped")

    # Summary
    click.echo(f"\n📊 Conversion complete: {success_count} succeeded, {error_count} failed")

def main():
    """Main entry point"""
    cli()

if __name__ == '__main__':
    main()
