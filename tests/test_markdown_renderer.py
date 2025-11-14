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


def test_render_markdown_with_tables():
    """Test rendering markdown tables (GFM extension)"""
    md = """| Column 1 | Column 2 |
|----------|----------|
| Value A  | Value B  |
| Value C  | Value D  |"""

    html = render_markdown(md)

    assert '<table>' in html
    assert '<thead>' in html
    assert '<tbody>' in html
    assert '<th>Column 1</th>' in html
    assert '<th>Column 2</th>' in html
    assert '<td>Value A</td>' in html
    assert '<td>Value B</td>' in html


def test_render_markdown_with_strikethrough():
    """Test rendering strikethrough text (GFM extension)"""
    md = "This is ~~crossed out~~ text"
    html = render_markdown(md)

    assert '<s>crossed out</s>' in html
    assert 'This is' in html


def test_render_markdown_with_blockquotes():
    """Test rendering blockquotes"""
    md = "> This is a quote\n> Second line"
    html = render_markdown(md)

    assert '<blockquote>' in html
    assert 'This is a quote' in html
    assert 'Second line' in html


def test_render_markdown_with_long_code():
    """Test rendering code blocks with long lines"""
    md = """```python
def very_long_function_name(param1, param2, param3):
    return "very long string that exceeds normal line width"
```"""
    html = render_markdown(md)

    assert '<pre>' in html
    assert '<code' in html
    assert 'very_long_function_name' in html
