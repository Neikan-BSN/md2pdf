import pytest
from pathlib import Path
import yaml
from config_loader import load_config, validate_config, get_theme_config

def test_load_config_default():
    """Test loading default config file"""
    config = load_config()
    assert config is not None
    assert 'output' in config
    assert config['output']['format'] == 'pdf'

def test_load_config_custom(tmp_path):
    """Test loading custom config file"""
    custom_config = tmp_path / "custom.yaml"
    custom_config.write_text("output:\n  format: html\n")

    config = load_config(custom_config)
    assert config['output']['format'] == 'html'

def test_validate_config_valid():
    """Test validation of valid config"""
    config = {
        'output': {'format': 'pdf', 'default_theme': 'academic'},
        'pdf_options': {'page_size': 'letter'},
        'rendering': {'math_engine': 'katex'},
        'themes': {}
    }
    assert validate_config(config) == True

def test_validate_config_missing_required():
    """Test validation fails for missing required fields"""
    config = {'output': {}}
    assert validate_config(config) == False

def test_get_theme_config():
    """Test getting theme-specific configuration"""
    config = {
        'themes': {
            'academic': {'mermaid_theme': 'default'}
        }
    }
    theme_cfg = get_theme_config('academic', config)
    assert theme_cfg['mermaid_theme'] == 'default'
