"""Core scraping functionality for the Mafia Wiki Scraper."""
import asyncio
import ssl
from typing import List, Dict, Optional, Set, AsyncGenerator, Tuple
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
import lxml

class WikiScraper:
    """Main scraper class for extracting content from wiki pages."""

    def __init__(self, base_url: str, session: Optional[aiohttp.ClientSession] = None, max_concurrent: int = 5):
        """Initialize the scraper with a base URL and optional session."""
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        # Create SSL context that doesn't verify certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context, limit=max_concurrent)
        self.session = session or aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=10)
        )
        self.scraped_urls: Set[str] = set()
        self.all_links: Set[str] = set()
        self.results: List[Dict[str, str]] = []
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def scrape_page(self, url: str) -> Optional[Dict[str, str]]:
        """Scrape a single page for its title and content."""
        async with self.semaphore:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'lxml')
                        title = soup.title.string if soup.title else ""
                        content = soup.get_text(separator=' ', strip=True)
                        return {
                            "url": url,
                            "title": title,
                            "content": content,
                        }
            except Exception as e:
                print(f"Error when scraping {url}: {str(e)}")
            return None

    async def get_internal_links(self, url: str) -> Set[str]:
        """Extract all internal links from the given URL."""
        async with self.semaphore:
            try:
                print(f"Fetching links from {url}")  # Debug log
                timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout
                async with self.session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'lxml')
                        links = set()
                        for link in soup.find_all('a', href=True):
                            href = link.get('href')
                            if href:
                                full_url = urljoin(self.base_url, href)
                                if full_url.startswith(self.base_url):
                                    links.add(full_url)
                        print(f"Found {len(links)} links in {url}")  # Debug log
                        return links
                    else:
                        print(f"Error {response.status} when fetching {url}")  # Debug log
                        return set()
            except asyncio.TimeoutError:
                print(f"Timeout when fetching {url}")  # Debug log
                return set()
            except Exception as e:
                print(f"Error extracting links from {url}: {str(e)}")  # Debug log
                return set()

    async def get_all_internal_links(self) -> AsyncGenerator[tuple[int, int], None]:
        """Recursively get all internal links from the base URL with progress updates."""
        print("Starting link discovery...")  # Debug log
        self.all_links = {self.base_url}  # Store as instance variable
        to_check = {self.base_url}
        checked = set()
        
        # Process URLs in parallel batches for speed
        batch_size = 10  # Process 10 URLs at once
        
        while to_check:
            # Take a batch of URLs to process
            current_batch = set()
            while len(current_batch) < batch_size and to_check:
                if url := to_check.pop() if to_check else None:
                    if url not in checked:
                        current_batch.add(url)
                        checked.add(url)
            
            if not current_batch:
                break
                
            # Process the batch concurrently
            tasks = [self.get_internal_links(url) for url in current_batch]
            new_links_sets = await asyncio.gather(*tasks)
            
            # Update our sets with new links
            for links in new_links_sets:
                new_unchecked = links - checked
                to_check.update(new_unchecked)
                self.all_links.update(links)
            
            # Yield progress
            yield len(checked), max(len(self.all_links), len(checked) + len(to_check))
            print(f"Processed {len(checked)} pages, found {len(self.all_links)} total links")
        
        # Final yield with the complete count
        print(f"Link discovery complete. Found {len(self.all_links)} pages")
        yield len(self.all_links), len(self.all_links)

    async def fetch_pages_with_progress(self) -> AsyncGenerator[tuple[int, int], None]:
        """Fetch all pages with progress updates."""
        total_pages = len(self.all_links)
        fetched = 0
        batch_size = self.max_concurrent * 2  # Fetch more pages at once
        
        # Convert to list for batch processing
        urls = list(self.all_links)
        
        while urls:
            # Take next batch
            batch = urls[:batch_size]
            urls = urls[batch_size:]
            
            # Fetch batch concurrently
            tasks = [self.scrape_page(url) for url in batch]
            results = await asyncio.gather(*tasks)
            
            # Store valid results
            for result in results:
                if result:
                    self.results.append(result)
            
            # Update progress
            fetched += len(batch)
            yield fetched, total_pages
            print(f"Fetched {fetched}/{total_pages} pages")
            
            # Small delay to prevent overload
            await asyncio.sleep(0.01)
        
        # Final yield
        yield total_pages, total_pages

    async def scrape_all_pages_with_progress(self) -> AsyncGenerator[Dict[str, str], None]:
        """Process all fetched pages and yield results."""
        for result in self.results:
            self.scraped_urls.add(result['url'])
            yield result
            await asyncio.sleep(0.01)  # Small delay to prevent CPU overload

    async def scrape_all_pages(self) -> List[Dict[str, str]]:
        """Scrape all internal pages starting from the base URL."""
        # First discover all links
        async for _ in self.get_all_internal_links():
            pass  # Process all links
            
        # Then fetch all pages
        async for _ in self.fetch_pages_with_progress():
            pass  # Wait for all pages to be fetched
            
        # Finally process and return all results
        results = []
        async for page in self.scrape_all_pages_with_progress():
            results.append(page)
        return results
