"""
Theme Manager Module

Handles theme discovery, CSS loading, and theme-specific configuration.
"""

from pathlib import Path
from typing import List, Dict, Any


def list_themes() -> List[str]:
    """
    List all available themes by scanning the themes directory.

    Returns:
        List[str]: List of theme names (without .css extension)

    Example:
        >>> themes = list_themes()
        >>> 'academic' in themes
        True
    """
    themes_dir = Path(__file__).parent / "themes"

    if not themes_dir.exists():
        raise FileNotFoundError(f"Themes directory not found: {themes_dir}")

    theme_files = themes_dir.glob("*.css")
    return sorted([theme_file.stem for theme_file in theme_files])


def load_theme_css(theme_name: str) -> str:
    """
    Load CSS content for a given theme.

    Args:
        theme_name (str): Name of the theme (without .css extension)

    Returns:
        str: CSS content as a string

    Raises:
        FileNotFoundError: If the theme file doesn't exist

    Example:
        >>> css = load_theme_css('academic')
        >>> '.markdown-body' in css
        True
    """
    themes_dir = Path(__file__).parent / "themes"
    theme_file = themes_dir / f"{theme_name}.css"

    if not theme_file.exists():
        available_themes = ", ".join(list_themes())
        raise FileNotFoundError(
            f"Theme '{theme_name}' not found. Available themes: {available_themes}"
        )

    return theme_file.read_text(encoding='utf-8')


class ThemeManager:
    """
    Manages theme configuration and provides theme-specific settings.

    Attributes:
        config (Dict[str, Any]): Configuration dictionary containing theme settings
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ThemeManager with configuration.

        Args:
            config (Dict[str, Any]): Configuration dictionary with themes section
        """
        self.config = config

    def get_mermaid_theme(self, theme_name: str) -> str:
        """
        Get the Mermaid diagram theme for a given theme.

        Args:
            theme_name (str): Name of the theme

        Returns:
            str: Mermaid theme name (e.g., 'default', 'forest', 'neutral', 'dark')

        Example:
            >>> config = {'themes': {'academic': {'mermaid_theme': 'default'}}}
            >>> manager = ThemeManager(config)
            >>> manager.get_mermaid_theme('academic')
            'default'
        """
        themes = self.config.get('themes', {})
        theme_config = themes.get(theme_name, {})
        return theme_config.get('mermaid_theme', 'default')
