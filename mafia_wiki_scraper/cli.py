"""Command-line interface for the Mafia Wiki Scraper."""
import argparse
import asyncio
import os
from datetime import datetime
import json
from typing import List, Dict

from .scraper import WikiScraper

def save_output(data: List[Dict[str, str]], output_format: str) -> str:
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
    
    return output_file

async def run_scraper(args: argparse.Namespace) -> None:
    """Run the scraper with the provided arguments."""
    start_url = args.url or "https://mafiagame.gitbook.io/bnb-mafia"
    
    async with WikiScraper(start_url) as scraper:
        print(f"Starting scrape from: {start_url}")
        all_data = await scraper.scrape_all_pages()
        
        if all_data:
            output_file = save_output(all_data, args.format)
            print(f"Scraped {len(all_data)} pages")
            print(f"Data saved to: {output_file}")
        else:
            print("No data was scraped. Please check the URL and try again.")

async def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Scrape Mafia Game website")
    parser.add_argument('--format', choices=['json', 'txt'], default='txt',
                      help='Output format (json or txt)')
    parser.add_argument('--url', type=str,
                      help='Starting URL (default: https://mafiagame.gitbook.io/bnb-mafia)')
    args = parser.parse_args()

    try:
        await run_scraper(args)
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

def cli_main() -> None:
    """Entry point for the CLI that sets up the event loop."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    cli_main()
