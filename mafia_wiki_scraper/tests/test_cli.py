"""Tests for the CLI module."""
import json
import os
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from argparse import Namespace

from ..cli import save_output, run_scraper, main, cli_main

@pytest.fixture
def mock_data():
    """Fixture for mock scraped data."""
    return [
        {
            "url": "https://example.com",
            "title": "Test Page",
            "content": "Test content"
        }
    ]

@pytest.fixture
def temp_output_dir(tmp_path):
    """Fixture for temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_dir)

@pytest.fixture
def mock_scraper():
    """Fixture for mock WikiScraper instance."""
    mock_instance = AsyncMock()
    mock_instance.scrape_all_pages = AsyncMock(return_value=[{"url": "https://example.com", "title": "Test", "content": "Content"}])
    with patch("mafia_wiki_scraper.cli.WikiScraper") as MockScraper:
        MockScraper.return_value.__aenter__.return_value = mock_instance
        yield

def test_save_output_json(mock_data, temp_output_dir):
    """Test saving output in JSON format."""
    output_file = save_output(mock_data, "json")
    assert os.path.exists(output_file)
    
    with open(output_file, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
    assert saved_data == mock_data

def test_save_output_txt(mock_data, temp_output_dir):
    """Test saving output in TXT format."""
    output_file = save_output(mock_data, "txt")
    assert os.path.exists(output_file)
    
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    assert mock_data[0]["url"] in content
    assert mock_data[0]["title"] in content
    assert mock_data[0]["content"] in content

@pytest.mark.asyncio
async def test_run_scraper_success():
    """Test successful scraper run."""
    mock_data = [{"url": "https://example.com", "title": "Test", "content": "Content"}]
    args = Namespace(url="https://example.com", format="json")
    
    with patch("mafia_wiki_scraper.cli.WikiScraper") as MockScraper:
        mock_instance = AsyncMock()
        mock_instance.scrape_all_pages = AsyncMock(return_value=mock_data)
        MockScraper.return_value.__aenter__.return_value = mock_instance
        
        with patch("mafia_wiki_scraper.cli.save_output") as mock_save:
            mock_save.return_value = "output.json"
            await run_scraper(args)
            
            mock_instance.scrape_all_pages.assert_called_once()
            mock_save.assert_called_once_with(mock_data, "json")

@pytest.mark.asyncio
async def test_run_scraper_no_data():
    """Test scraper run with no data returned."""
    args = Namespace(url="https://example.com", format="json")
    
    with patch("mafia_wiki_scraper.cli.WikiScraper") as MockScraper:
        mock_instance = AsyncMock()
        mock_instance.scrape_all_pages = AsyncMock(return_value=[])
        MockScraper.return_value.__aenter__.return_value = mock_instance
        
        with patch("mafia_wiki_scraper.cli.save_output") as mock_save:
            await run_scraper(args)
            mock_save.assert_not_called()

@pytest.mark.asyncio
async def test_main_with_custom_format(tmp_path, mock_scraper):
    """Test main function with custom format."""
    test_args = ['--format', 'json']
    with patch('sys.argv', ['scraper'] + test_args):
        with patch('mafia_wiki_scraper.cli.run_scraper') as mock_run:
            mock_run.return_value = None  # Make it a coroutine that returns None
            await main()
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args.format == 'json'

@pytest.mark.asyncio
async def test_main_with_custom_url(tmp_path, mock_scraper):
    """Test main function with custom URL."""
    test_url = 'https://test.com'
    test_args = ['--url', test_url]
    with patch('sys.argv', ['scraper'] + test_args):
        with patch('mafia_wiki_scraper.cli.run_scraper') as mock_run:
            mock_run.return_value = None  # Make it a coroutine that returns None
            await main()
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args.url == test_url

@pytest.mark.asyncio
async def test_main_keyboard_interrupt(tmp_path, mock_scraper):
    """Test main function handling keyboard interrupt."""
    with patch('sys.argv', ['scraper']):
        with patch('mafia_wiki_scraper.cli.run_scraper', side_effect=KeyboardInterrupt):
            with patch('builtins.print') as mock_print:
                await main()
                mock_print.assert_called_once_with("\nScraping interrupted by user")

@pytest.mark.asyncio
async def test_main_general_exception(tmp_path, mock_scraper):
    """Test main function handling general exception."""
    test_error = "Test error"
    with patch('sys.argv', ['scraper']):
        with patch('mafia_wiki_scraper.cli.run_scraper', side_effect=Exception(test_error)):
            with patch('builtins.print') as mock_print:
                with pytest.raises(Exception, match=test_error):
                    await main()
                mock_print.assert_called_once_with(f"An error occurred: {test_error}")

def test_cli_main_keyboard_interrupt(tmp_path, mock_scraper):
    """Test CLI main function handling keyboard interrupt."""
    with patch('sys.argv', ['scraper']):
        with patch('mafia_wiki_scraper.cli.main', side_effect=KeyboardInterrupt):
            with patch('builtins.print') as mock_print:
                cli_main()
                mock_print.assert_called_once_with("\nScraping interrupted by user")

def test_cli_main_general_exception(tmp_path, mock_scraper):
    """Test CLI main function handling general exception."""
    test_error = "Test error"
    with patch('sys.argv', ['scraper']):
        with patch('mafia_wiki_scraper.cli.main', side_effect=Exception(test_error)):
            with patch('builtins.print') as mock_print:
                with pytest.raises(Exception, match=test_error):
                    cli_main()
                mock_print.assert_called_once_with(f"An error occurred: {test_error}")
