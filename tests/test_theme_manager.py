import pytest
from pathlib import Path
from theme_manager import ThemeManager, list_themes, load_theme_css

def test_list_themes():
    """Test listing available themes"""
    themes = list_themes()
    assert 'academic' in themes
    assert 'modern' in themes
    assert 'minimal' in themes
    assert 'presentation' in themes
    assert len(themes) == 4

def test_load_theme_css():
    """Test loading theme CSS"""
    css = load_theme_css('academic')
    assert css is not None
    assert '.markdown-body' in css
    assert 'font-family' in css

def test_load_theme_css_invalid():
    """Test loading non-existent theme"""
    with pytest.raises(FileNotFoundError):
        load_theme_css('nonexistent')

def test_theme_manager_get_mermaid_theme():
    """Test getting Mermaid theme for a given theme"""
    config = {
        'themes': {
            'academic': {'mermaid_theme': 'default'},
            'modern': {'mermaid_theme': 'forest'}
        }
    }
    manager = ThemeManager(config)

    assert manager.get_mermaid_theme('academic') == 'default'
    assert manager.get_mermaid_theme('modern') == 'forest'
