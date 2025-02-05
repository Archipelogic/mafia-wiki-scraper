"""Tests for the WikiScraper class."""
import pytest
import pytest_asyncio
from aioresponses import aioresponses
from bs4 import BeautifulSoup

from ..scraper import WikiScraper

@pytest.fixture
def base_url():
    """Fixture for base URL."""
    return "https://example.com"

@pytest.fixture
def mock_html():
    """Fixture for mock HTML content."""
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <p>Test content</p>
            <a href="/page1">Internal Link 1</a>
            <a href="https://example.com/page2">Internal Link 2</a>
            <a href="https://external.com">External Link</a>
        </body>
    </html>
    """

@pytest_asyncio.fixture
async def scraper(base_url):
    """Fixture for WikiScraper instance."""
    async with WikiScraper(base_url) as scraper:
        yield scraper

@pytest.mark.asyncio
async def test_scrape_page_success(scraper, base_url, mock_html):
    """Test successful page scraping."""
    with aioresponses() as m:
        m.get(f"{base_url}", status=200, body=mock_html)
        result = await scraper.scrape_page(base_url)
        
        assert result is not None
        assert result["url"] == base_url
        assert result["title"] == "Test Page"
        assert "Test content" in result["content"]

@pytest.mark.asyncio
async def test_scrape_page_failure(scraper, base_url):
    """Test failed page scraping."""
    with aioresponses() as m:
        m.get(f"{base_url}", status=404)
        result = await scraper.scrape_page(base_url)
        assert result is None

@pytest.mark.asyncio
async def test_get_internal_links(scraper, base_url, mock_html):
    """Test internal links extraction."""
    with aioresponses() as m:
        m.get(f"{base_url}", status=200, body=mock_html)
        links = await scraper.get_internal_links(base_url)
        
        assert len(links) == 2
        assert f"{base_url}/page1" in links
        assert f"{base_url}/page2" in links
        assert "https://external.com" not in links

@pytest.mark.asyncio
async def test_scrape_all_pages(scraper, base_url):
    """Test scraping of all pages."""
    mock_pages = {
        f"{base_url}": """
            <html>
                <head><title>Main</title></head>
                <body>
                    <a href="/page1">Link 1</a>
                </body>
            </html>
        """,
        f"{base_url}/page1": """
            <html>
                <head><title>Page 1</title></head>
                <body>Content 1</body>
            </html>
        """
    }
    
    with aioresponses() as m:
        # Mock both the initial page and the link extraction requests
        for url, html in mock_pages.items():
            m.get(url, status=200, body=html)
            # Mock the same URL again for link extraction
            m.get(url, status=200, body=html)
        
        results = await scraper.scrape_all_pages()
        
        assert len(results) == 2
        assert any(r["title"] == "Main" for r in results)
        assert any(r["title"] == "Page 1" for r in results)
