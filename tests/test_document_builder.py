"""Tests for HTML document builder."""

import pytest
from pathlib import Path
from document_builder import build_html_document


def test_build_html_document_basic():
    """Test basic HTML document generation"""
    md_content = "# Test Document\n\nHello world"
    config = {
        'rendering': {'mermaid_theme': 'default'}
    }

    html = build_html_document(
        md_content=md_content,
        theme_name='academic',
        config=config
    )

    # Check structure
    assert '<!DOCTYPE html>' in html
    assert '<title>Test Document</title>' in html
    assert '<h1>Test Document</h1>' in html
    assert 'Hello world' in html


def test_build_html_document_includes_theme_css():
    """Test theme CSS is injected"""
    md_content = "# Test"
    config = {
        'rendering': {'mermaid_theme': 'default'}
    }

    html = build_html_document(
        md_content=md_content,
        theme_name='academic',
        config=config
    )

    # Should contain CSS
    assert '<style>' in html
    assert '</style>' in html


def test_build_html_document_includes_mermaid_theme():
    """Test mermaid theme is injected"""
    md_content = "# Test"
    config = {
        'rendering': {'mermaid_theme': 'default'},
        'themes': {
            'academic': {'mermaid_theme': 'dark'}
        }
    }

    html = build_html_document(
        md_content=md_content,
        theme_name='academic',
        config=config
    )

    assert "theme: 'dark'" in html
