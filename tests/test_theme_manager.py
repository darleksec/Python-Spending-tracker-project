"""Tests for gui/theme_manager.py — palette, QSS generation, persistence."""

import json
import os
import tempfile

import pytest

from gui.theme_manager import ThemeManager


@pytest.fixture
def tmp_config(tmp_path):
    """Return a path to a temporary theme config file."""
    return str(tmp_path / "theme_config.json")


@pytest.fixture
def manager(tmp_config):
    """Create a ThemeManager using a temporary config path."""
    return ThemeManager(config_path=tmp_config)


class TestThemeManagerDefaults:
    def test_default_theme_is_light(self, manager):
        assert manager.get_current_theme() == "light"

    def test_get_chart_colors_returns_dict(self, manager):
        colors = manager.get_chart_colors()
        assert isinstance(colors, dict)
        assert "bg" in colors
        assert "text" in colors

    def test_light_chart_colors(self, manager):
        colors = manager.get_chart_colors()
        assert colors == ThemeManager.CHART_COLORS["light"]


class TestThemeSwitching:
    def test_set_dark_theme(self, manager):
        manager.set_theme("dark")
        assert manager.get_current_theme() == "dark"

    def test_set_invalid_theme_ignored(self, manager):
        manager.set_theme("neon")
        assert manager.get_current_theme() == "light"

    def test_dark_chart_colors(self, manager):
        manager.set_theme("dark")
        colors = manager.get_chart_colors()
        assert colors == ThemeManager.CHART_COLORS["dark"]

    def test_set_same_theme_no_op(self, manager):
        """Setting the same theme should not trigger a change."""
        manager.set_theme("light")  # already light
        assert manager.get_current_theme() == "light"


class TestPersistence:
    def test_saves_theme_preference(self, tmp_config):
        mgr = ThemeManager(config_path=tmp_config)
        mgr.set_theme("dark")
        with open(tmp_config, "r") as f:
            data = json.load(f)
        assert data["theme"] == "dark"

    def test_loads_saved_preference(self, tmp_config):
        # Save dark preference
        with open(tmp_config, "w") as f:
            json.dump({"theme": "dark"}, f)
        mgr = ThemeManager(config_path=tmp_config)
        assert mgr.get_current_theme() == "dark"

    def test_corrupt_config_defaults_to_light(self, tmp_config):
        with open(tmp_config, "w") as f:
            f.write("NOT JSON")
        mgr = ThemeManager(config_path=tmp_config)
        assert mgr.get_current_theme() == "light"

    def test_missing_config_defaults_to_light(self, tmp_path):
        mgr = ThemeManager(config_path=str(tmp_path / "nonexistent.json"))
        assert mgr.get_current_theme() == "light"


class TestPalette:
    def test_light_palette_has_required_keys(self):
        required = ["@bg_primary@", "@text_primary@", "@accent@", "@border@"]
        for key in required:
            assert key in ThemeManager.LIGHT_PALETTE

    def test_dark_palette_has_required_keys(self):
        required = ["@bg_primary@", "@text_primary@", "@accent@", "@border@"]
        for key in required:
            assert key in ThemeManager.DARK_PALETTE

    def test_apply_palette_replaces_placeholders(self, manager):
        template = "color: @bg_primary@; border: @border@;"
        result = manager._apply_palette(template, ThemeManager.LIGHT_PALETTE)
        assert "@bg_primary@" not in result
        assert "@border@" not in result
        assert "#FFFFFF" in result


class TestStylesheet:
    def test_get_stylesheet_returns_string(self, manager):
        ss = manager.get_stylesheet()
        assert isinstance(ss, str)
