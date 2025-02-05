"""Tests for the GUI components of the Mafia Wiki Scraper."""
import os
import sys
import json
import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path
import customtkinter as ctk
from ..gui import MafiaWikiScraperGUI
from ..scraper import WikiScraper

class AsyncIteratorMock:
    """Mock for async iterator."""
    def __init__(self, items):
        self.items = items.copy()  # Make a copy to avoid modifying original
        self._iter = None

    def __aiter__(self):
        self._iter = self.items.copy()
        return self

    async def __anext__(self):
        if not self._iter:
            raise StopAsyncIteration
        try:
            return self._iter.pop(0)
        except IndexError:
            raise StopAsyncIteration

    def __call__(self, *args, **kwargs):
        # Return self directly for use as an async generator
        return self

@pytest.fixture
def mock_logo():
    """Mock the logo loading."""
    with patch('PIL.Image.open') as mock_open:
        mock_image = MagicMock()
        mock_image.width = 100
        mock_image.height = 100
        mock_open.return_value = mock_image
        yield mock_open

@pytest.fixture
def mock_pygame():
    """Mock pygame sound system."""
    with patch('pygame.mixer.init'), \
         patch('pygame.mixer.Sound') as mock_sound:
        mock_sound_instance = MagicMock()
        mock_sound.return_value = mock_sound_instance
        yield mock_sound_instance

@pytest.fixture
def gui(tmp_path, mock_logo, mock_pygame):
    """Create a GUI instance for testing."""
    app = MafiaWikiScraperGUI()
    app.settings_file = tmp_path / ".mafia_scraper_settings.json"
    app.output_dir = tk.StringVar()
    return app

@pytest.mark.asyncio
async def test_gui_initialization(gui):
    """Test that the GUI initializes correctly."""
    assert isinstance(gui, MafiaWikiScraperGUI)
    assert gui.scraping is False
    assert gui.current_output_file is None
    assert gui.base_url == "https://bnb-mafia.gitbook.io/bnb-mafia"
    assert isinstance(gui.output_dir, tk.StringVar)

def test_gui_components(gui):
    """Test that all GUI components are created."""
    # Check main containers
    assert isinstance(gui.container, ctk.CTkFrame)
    assert isinstance(gui.content_frame, ctk.CTkFrame)
    
    # Check progress bars
    assert hasattr(gui, 'inspection_progress')
    assert hasattr(gui, 'fetching_progress')
    assert hasattr(gui, 'progress_bar')
    
    # Check buttons
    assert hasattr(gui, 'scrape_button')
    assert hasattr(gui, 'open_button')
    
    # Check labels
    assert hasattr(gui, 'status_label')
    assert hasattr(gui, 'pages_label')
    assert hasattr(gui, 'time_label')

@pytest.mark.asyncio
async def test_browse_directory(gui, tmp_path):
    """Test the directory browsing functionality."""
    test_dir = str(tmp_path)
    
    # Mock the directory dialog
    with patch('tkinter.filedialog.askdirectory', return_value=test_dir):
        gui.browse_directory()
        
    assert gui.output_dir.get() == test_dir
    assert gui.settings["last_directory"] == test_dir

@pytest.mark.asyncio
async def test_start_stop_scraping(gui, tmp_path):
    """Test starting and stopping the scraping process."""
    # Set up a test directory
    gui.output_dir.set(str(tmp_path))
    
    # Mock the scraper
    mock_scraper = AsyncMock()
    mock_scraper.get_all_internal_links = AsyncMock(return_value=[(1, 2)])
    mock_scraper.fetch_pages_with_progress = AsyncMock(return_value=[(1, 2)])
    mock_scraper.scrape_all_pages_with_progress = AsyncMock(return_value=[
        {"title": "Test Page", "content": "Test Content"}
    ])
    
    with patch('mafia_wiki_scraper.gui.WikiScraper') as MockScraper:
        MockScraper.return_value.__aenter__.return_value = mock_scraper
        
        # Start scraping
        await gui.start_scraping()
        assert gui.scraping is True
        assert gui.scrape_button.cget("text") == "Stop Scraping"
        
        # Stop scraping
        await gui.start_scraping()
        assert gui.scraping is False
        assert gui.scrape_button.cget("text") == "Start Scraping"

@pytest.mark.asyncio
async def test_complete_scraping_workflow(gui, tmp_path):
    """Test the complete scraping workflow."""
    # Set up test directory
    gui.output_dir.set(str(tmp_path))

    # Create test data
    test_pages = [
        {"title": "Page 1", "content": "Content 1"},
        {"title": "Page 2", "content": "Content 2"},
        {"title": "Page 3", "content": "Content 3"}
    ]

    # Mock scraper with realistic data
    mock_scraper = AsyncMock()
    mock_scraper.results = test_pages  # Set results directly

    # Set up mock iterators
    mock_scraper.get_all_internal_links = AsyncIteratorMock([
        (1, 3), (2, 3), (3, 3)  # Simulates finding 3 links
    ])
    mock_scraper.fetch_pages_with_progress = AsyncIteratorMock([
        (1, 3), (2, 3), (3, 3)  # Simulates fetching 3 pages
    ])
    mock_scraper.scrape_all_pages_with_progress = AsyncIteratorMock(test_pages)

    # Mock the WikiScraper class
    with patch('mafia_wiki_scraper.gui.WikiScraper') as MockScraper:
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_scraper
        mock_context.__aexit__.return_value = None
        MockScraper.return_value = mock_context

        # Start scraping
        await gui._run_scraper()

        # Verify output file
        output_file = Path(tmp_path) / "mafia_wiki.json"
        assert output_file.exists()

        # Verify file contents
        with open(output_file) as f:
            data = json.load(f)
            assert len(data) == 3
            assert data[0]["title"] == "Page 1"
            assert data[1]["content"] == "Content 2"

        # Verify final state
        assert gui.scraping is False
        assert gui.scrape_button.cget("text") == "Start Scraping"
        assert gui.status_label.cget("text") == "Scraping completed successfully!"

@pytest.mark.asyncio
async def test_scraping_without_directory(gui):
    """Test starting scraping without selecting directory."""
    await gui._run_scraper()
    assert gui.status_label.cget("text") == "Error: Please select an output directory first."
    assert gui.scraping is False

def test_update_progress(gui):
    """Test progress bar updates."""
    gui.update_progress(50)
    gui.update()  # Process pending events
    
    assert abs(gui.inspection_progress.get() - 0.5) < 0.01
    assert abs(gui.fetching_progress.get() - 0.5) < 0.01
    assert abs(gui.progress_bar.get() - 0.5) < 0.01

def test_settings_management(gui, tmp_path):
    """Test saving and loading settings."""
    test_dir = str(tmp_path)
    gui.output_dir.set(test_dir)
    gui.save_settings()
    
    # Create new GUI instance to test loading
    new_gui = MafiaWikiScraperGUI()
    new_gui.settings_file = gui.settings_file
    loaded_settings = new_gui.load_settings()
    
    assert loaded_settings["last_directory"] == test_dir

def test_error_handling(gui):
    """Test error handling and display."""
    test_error = "Test error message"
    gui.show_error(test_error)
    gui.update()  # Process pending events
    
    assert gui.status_label.cget("text") == f"Error: {test_error}"
    assert gui.scraping is False
    assert gui.scrape_button.cget("text") == "Start Scraping"

def test_sound_system(gui, mock_pygame):
    """Test sound system functionality."""
    gui.play_sound('success')
    mock_pygame.play.assert_called_once()

def test_update_status(gui):
    """Test status updates."""
    test_status = "Test status"
    gui.update_status(test_status)
    gui.update()
    
    assert gui.status_label.cget("text") == test_status
    
    # Test error status
    gui.update_status(test_status, error=True)
    gui.update()
    assert gui.status_label.cget("text") == test_status

def test_open_output_file(gui, tmp_path):
    """Test opening output file."""
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    
    gui.current_output_file = str(test_file)
    
    # Mock platform-specific open commands
    with patch('subprocess.run') as mock_run:
        gui.open_output_file()
        mock_run.assert_called_once_with(
            ["open" if sys.platform == "darwin" else "xdg-open", str(test_file)])
