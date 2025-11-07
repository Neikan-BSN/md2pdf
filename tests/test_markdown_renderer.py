import pytest
from pathlib import Path
from markdown_renderer import render_markdown, extract_title


def test_render_markdown_simple():
    """Test rendering simple markdown"""
    md = "# Hello World\n\nThis is a test."
    html = render_markdown(md)

    assert '<h1>Hello World</h1>' in html
    assert '<p>This is a test.</p>' in html


def test_render_markdown_with_code():
    """Test rendering code blocks"""
    md = "```python\nprint('hello')\n```"
    html = render_markdown(md)

    assert '<pre>' in html
    assert '<code' in html
    assert "print('hello')" in html


def test_render_markdown_with_lists():
    """Test rendering lists"""
    md = "- Item 1\n- Item 2\n- Item 3"
    html = render_markdown(md)

    assert '<ul>' in html
    assert '<li>Item 1</li>' in html
    assert '<li>Item 2</li>' in html


def test_extract_title_from_first_heading():
    """Test extracting title from first H1"""
    md = "# My Title\n\nSome content"
    title = extract_title(md)

    assert title == "My Title"


def test_extract_title_default():
    """Test default title when no H1 present"""
    md = "Just some content without headings"
    title = extract_title(md)

    assert title == "Untitled Document"
