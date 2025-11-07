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

    with open(config_path, 'r') as f:
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
    required_keys = ['output', 'pdf_options', 'rendering', 'themes']

    for key in required_keys:
        if key not in config:
            return False

    # Validate output section
    if 'format' not in config['output']:
        return False
    if 'default_theme' not in config['output']:
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
