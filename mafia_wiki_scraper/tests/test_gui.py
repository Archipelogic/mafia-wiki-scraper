"""Tests for the GUI module."""
import os
import sys
import pytest
import tkinter as tk
import asyncio
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mafia_wiki_scraper.gui import MafiaWikiScraperGUI, main

@pytest.fixture
def app(monkeypatch):
    """Create a test instance of the App."""
    # Mock pygame.mixer to avoid audio initialization
    monkeypatch.setattr('pygame.mixer.init', lambda: None)
    monkeypatch.setattr('pygame.mixer.Sound', lambda x: MagicMock())
    
    # Mock the main window
    with patch('customtkinter.CTk') as mock_ctk:
        app_instance = MafiaWikiScraperGUI()
        # Prevent the app from actually starting
        app_instance.mainloop = lambda: None
        return app_instance

def test_app_initialization(app):
    """Test that the app initializes correctly."""
    assert app is not None
    # Get the value from the StringVar
    default_dir = str(Path.home() / "Documents" / "Mafia_Wiki_Scraper_Output")
    assert app.output_dir.get() == default_dir
    assert app.base_url == "https://bnb-mafia.gitbook.io/bnb-mafia"

def test_update_progress(app):
    """Test the progress bar updates."""
    app.inspection_progress = MagicMock()
    app.fetching_progress = MagicMock()
    app.progress_bar = MagicMock()
    
    # Test progress update by calling _update_progress_safe directly
    # since update_progress uses after() which requires a running event loop
    app._update_progress_safe(50)  # Pass in non-normalized value
    app.inspection_progress.set.assert_called_with(0.5)
    app.fetching_progress.set.assert_called_with(0.5)
    app.progress_bar.set.assert_called_with(0.5)

def test_play_sound(app):
    """Test sound playing functionality."""
    # Create mock sound
    mock_sound = MagicMock()
    app.sounds = {'click': mock_sound}
    
    app.play_sound("click")  # Should call the mocked Sound.play()
    mock_sound.play.assert_called_once()

def test_main_function():
    """Test the main function."""
    with patch('mafia_wiki_scraper.gui.MafiaWikiScraperGUI') as mock_app:
        main()
        mock_app.assert_called_once()
        mock_app.return_value.mainloop.assert_called_once()
