import asyncio
import aiohttp
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import json
import os
from datetime import datetime
import argparse
import time
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
import lxml

async def create_driver():
    """Create and return a new WebDriver instance."""
    brave_options = Options()
    brave_options.add_argument("--headless")
    brave_options.add_argument("--no-sandbox")
    brave_options.add_argument("--disable-dev-shm-usage")
    
    brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    brave_options.binary_location = brave_path

    service = Service()
    return webdriver.Chrome(service=service, options=brave_options)

async def scrape_page(session: aiohttp.ClientSession, url: str, max_retries: int = 3) -> Optional[Dict[str, str]]:
    """Scrape a single page for its title and content with retries."""
    for attempt in range(max_retries):
        try:
            async with session.get(url) as response:
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
            print(f"Error when scraping {url} (Attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt == max_retries - 1:
                print(f"Failed to scrape {url} after {max_retries} attempts")
        await asyncio.sleep(1)
    
    return None

async def get_internal_links(session: aiohttp.ClientSession, url: str, base_url: str) -> Set[str]:
    """Extract all internal links from the given URL."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                print(f"Received HTML content (first 100 characters): {html[:100]}")  # Debug print
                soup = BeautifulSoup(html, 'lxml')
                links = set()
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if href:
                        full_url = urljoin(base_url, href)
                        if full_url.startswith(base_url):
                            links.add(full_url)
                print(f"Found {len(links)} internal links")  # Debug print
                return links
    except Exception as e:
        print(f"Error extracting links from {url}: {str(e)}")
        print(f"Exception type: {type(e)}")  # Debug print
    return set()

async def scrape_all_pages(start_url: str) -> List[Dict[str, str]]:
    """Scrape all internal pages starting from the given URL."""
    scraped_data = []
    to_scrape = {start_url}
    scraped_urls = set()
    base_url = f"{urlparse(start_url).scheme}://{urlparse(start_url).netloc}"

    async with aiohttp.ClientSession() as session:
        while to_scrape:
            print(f"URLs to scrape: {len(to_scrape)}")  # Debug print
            tasks = [asyncio.create_task(scrape_page(session, url)) for url in to_scrape]
            results = await asyncio.gather(*tasks)

            new_to_scrape = set()
            for result in results:
                if result and result['url'] not in scraped_urls:
                    scraped_data.append(result)
                    scraped_urls.add(result['url'])
                    print(f"Scraped: {result['url']}")  # Debug print
                    link_tasks = [asyncio.create_task(get_internal_links(session, result['url'], base_url))]
                    new_links = await asyncio.gather(*link_tasks)
                    new_to_scrape.update(*new_links)

            to_scrape = new_to_scrape - scraped_urls
            print(f"New URLs to scrape: {len(to_scrape)}")  # Debug print

    return scraped_data

def save_output(data: List[Dict[str, str]], output_format: str) -> None:
    """Save the scraped data to a file in the specified format."""
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    if output_format == 'json':
        output_file = os.path.join(output_dir, f"mafia_game_wiki_{current_date}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        output_file = os.path.join(output_dir, f"mafia_game_wiki_{current_date}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            for page in data:
                f.write(f"URL: {page['url']}\n")
                f.write(f"Title: {page['title']}\n")
                f.write(f"Content:\n{page['content']}\n\n")
                f.write("-" * 80 + "\n\n")
    
    print(f"Data saved to {output_file}")

async def main() -> None:
    """Main function to run the scraper with command-line arguments."""
    print("Starting main function")
    parser = argparse.ArgumentParser(description="Scrape Mafia Game website")
    parser.add_argument('--format', choices=['json', 'txt'], default='txt', help='Output format (json or txt)')
    args = parser.parse_args()
    print(f"Format argument: {args.format}")

    start_url = "https://mafiagame.gitbook.io/bnb-mafia"
    print(f"Starting URL: {start_url}")
    
    try:
        print("Starting scrape_all_pages")
        all_data = await scrape_all_pages(start_url)
        print(f"Scraped {len(all_data)} pages")
        if all_data:
            print("Saving output")
            save_output(all_data, args.format)
        else:
            print("No data was scraped. Please check the URL and try again.")
    except Exception as e:
        print(f"An error occurred during scraping: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
