"""HTML document builder for md2pdf."""

from pathlib import Path
from jinja2 import Template
from markdown_renderer import render_markdown, extract_title
from theme_manager import load_theme_css, ThemeManager
from typing import Dict, Any


def build_html_document(
    md_content: str,
    theme_name: str,
    config: Dict[str, Any]
) -> str:
    """
    Build complete HTML document from markdown.

    Args:
        md_content: Markdown content
        theme_name: Theme name (e.g., 'academic')
        config: Configuration dictionary

    Returns:
        Complete HTML document string

    Example:
        >>> config = {'rendering': {'mermaid_theme': 'default'}}
        >>> html = build_html_document("# Test", "academic", config)
        >>> '<!DOCTYPE html>' in html
        True
    """
    # Extract title from markdown
    title = extract_title(md_content)

    # Render markdown to HTML
    content_html = render_markdown(md_content)

    # Load theme CSS
    theme_css = load_theme_css(theme_name)

    # Get mermaid theme
    theme_manager = ThemeManager(config)
    mermaid_theme = theme_manager.get_mermaid_theme(theme_name)

    # Load template
    template_path = Path(__file__).parent / "templates" / "base.html"
    template_content = template_path.read_text(encoding='utf-8')
    template = Template(template_content)

    # Render complete document
    html = template.render(
        title=title,
        theme_css=theme_css,
        mermaid_theme=mermaid_theme,
        content=content_html
    )

    return html
