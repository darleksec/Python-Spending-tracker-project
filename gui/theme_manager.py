import json
import os

from PyQt6.QtCore import QObject, pyqtSignal


class ThemeManager(QObject):
    """Centralised theme manager for light/dark mode switching and QSS generation."""

    theme_changed = pyqtSignal(str)

    LIGHT_PALETTE = {
        "@bg_primary@": "#FFFFFF",
        "@bg_secondary@": "#F6F8FA",
        "@bg_tertiary@": "#EDF0F3",
        "@text_primary@": "#1F2328",
        "@text_secondary@": "#656D76",
        "@border@": "#D0D7DE",
        "@accent@": "#1a67b3",
        "@accent_hover@": "#1558a0",
        "@accent_pressed@": "#0f4a8a",
    }

    DARK_PALETTE = {
        "@bg_primary@": "#0D1117",
        "@bg_secondary@": "#161B22",
        "@bg_tertiary@": "#21262D",
        "@text_primary@": "#E6EDF3",
        "@text_secondary@": "#8B949E",
        "@border@": "#30363D",
        "@accent@": "#58A6FF",
        "@accent_hover@": "#79B8FF",
        "@accent_pressed@": "#3D8BFD",
    }

    CHART_COLORS = {
        "light": {
            "bg": "#FFFFFF",
            "text": "#1F2328",
            "grid": "#D0D7DE",
            "accent": "#1a67b3",
        },
        "dark": {
            "bg": "#0D1117",
            "text": "#E6EDF3",
            "grid": "#30363D",
            "accent": "#58A6FF",
        },
    }

    def __init__(self, config_path=None):
        super().__init__()
        self._styles_dir = os.path.join(os.path.dirname(__file__), "styles")
        self._config_path = config_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "theme_config.json"
        )
        self._current_theme = self._load_theme_preference()

    def _load_theme_preference(self):
        """Load saved theme from config file, defaulting to 'light'."""
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                theme = data.get("theme", "light")
                if theme in ("light", "dark"):
                    return theme
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass
        return "light"

    def _save_theme_preference(self):
        """Persist theme choice to config file."""
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump({"theme": self._current_theme}, f, indent=2)
        except OSError:
            pass

    def _load_qss_template(self, theme_name):
        """Load the raw QSS template for the given theme."""
        qss_path = os.path.join(self._styles_dir, f"{theme_name}.qss")
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                return f.read()
        except (FileNotFoundError, OSError):
            return ""

    def _apply_palette(self, template, palette):
        """Replace colour placeholders in a QSS template with actual values."""
        result = template
        for placeholder, value in palette.items():
            result = result.replace(placeholder, value)
        return result

    def get_current_theme(self):
        """Return the current theme name ('light' or 'dark')."""
        return self._current_theme

    def get_stylesheet(self):
        """Return the fully resolved QSS string for the current theme."""
        template = self._load_qss_template(self._current_theme)
        palette = self.LIGHT_PALETTE if self._current_theme == "light" else self.DARK_PALETTE
        return self._apply_palette(template, palette)

    def set_theme(self, name):
        """Switch to the given theme and emit theme_changed signal."""
        if name not in ("light", "dark"):
            return
        if name != self._current_theme:
            self._current_theme = name
            self._save_theme_preference()
            self.theme_changed.emit(name)

    def get_chart_colors(self):
        """Return a dict of colours for matplotlib chart theming."""
        return dict(self.CHART_COLORS[self._current_theme])
