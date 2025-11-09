"""Configuration loader and validator for md2pdf"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_CONFIG_PATH = Path(__file__).parent / "md2pdf.config.yaml"

def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file. Uses default if None.

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure.

    Args:
        config: Configuration dictionary

    Returns:
        True if valid, False otherwise
    """
    # Check top-level keys
    required_keys = ['output', 'pdf_options', 'rendering', 'themes']
    if not all(k in config for k in required_keys):
        return False

    # Validate output section
    output = config.get('output', {})
    if not isinstance(output, dict):
        return False
    if 'format' not in output or 'default_theme' not in output:
        return False
    if output['format'] not in ['pdf', 'html']:
        return False

    # Validate pdf_options section
    pdf_opts = config.get('pdf_options', {})
    if not isinstance(pdf_opts, dict):
        return False
    if 'page_size' not in pdf_opts or 'margins' not in pdf_opts:
        return False

    # Validate rendering section
    rendering = config.get('rendering', {})
    if not isinstance(rendering, dict):
        return False
    if 'math_engine' not in rendering or 'mermaid_theme' not in rendering:
        return False

    # Validate themes section
    themes = config.get('themes', {})
    if not isinstance(themes, dict):
        return False

    return True


def get_theme_config(theme_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get theme-specific configuration.

    Args:
        theme_name: Name of theme
        config: Main configuration dictionary

    Returns:
        Theme configuration dictionary
    """
    if theme_name in config.get('themes', {}):
        return config['themes'][theme_name]

    # Return default theme config
    return {
        'mermaid_theme': config['rendering']['mermaid_theme']
    }
