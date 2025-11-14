"""
Markdown to HTML rendering module.

This module provides functions to convert Markdown content to HTML
and extract document titles from Markdown headings.
"""

from markdown_it import MarkdownIt
import re

# Module-level MarkdownIt instance for better performance
# Enable table plugin for GitHub Flavored Markdown table support
_markdown_parser = MarkdownIt('commonmark').enable('table')


def render_markdown(md_content: str) -> str:
    """
    Render markdown content to HTML.

    Converts Markdown text to HTML using the markdown-it-py library.
    Supports standard Markdown features including headings, lists,
    code blocks, emphasis, links, and more.

    Args:
        md_content: Markdown text to render

    Returns:
        HTML string representation of the markdown content

    Examples:
        >>> render_markdown("# Hello\\n\\nWorld")
        '<h1>Hello</h1>\\n<p>World</p>\\n'

        >>> render_markdown("- Item 1\\n- Item 2")
        '<ul>\\n<li>Item 1</li>\\n<li>Item 2</li>\\n</ul>\\n'
    """
    if not md_content:
        return ""

    return _markdown_parser.render(md_content)


def extract_title(md_content: str) -> str:
    """
    Extract document title from the first H1 heading.

    Searches for the first level-1 heading (# Title) in the markdown
    content and returns it as the document title. If no H1 heading
    is found, returns a default title.

    Args:
        md_content: Markdown text to extract title from

    Returns:
        Title string extracted from first H1 heading,
        or "Untitled Document" if no H1 found

    Examples:
        >>> extract_title("# My Document\\n\\nContent here")
        'My Document'

        >>> extract_title("Just plain text")
        'Untitled Document'

        >>> extract_title("## Not an H1\\n\\n# This is H1")
        'This is H1'
    """
    if not md_content:
        return "Untitled Document"

    # Look for first H1 heading (# Title pattern at start of line)
    # Match format: # Title (with optional leading/trailing whitespace)
    match = re.search(r'^#\s+(.+?)$', md_content, re.MULTILINE)

    if match:
        return match.group(1).strip()

    return "Untitled Document"
