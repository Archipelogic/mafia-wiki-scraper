# Mafia Wiki Scraper

A desktop application to scrape and archive content from the Mafia Wiki.

## Features

- User-friendly graphical interface
- Progress tracking with status bars
- Sound effects for notifications
- Saves content in JSON format
- Dark mode support

## Installation

### macOS

#### Option 1: Easy Install (Recommended)
1. Download the latest `MafiaWikiScraper.dmg` from the [Releases](https://github.com/Archipelogic/mafia-wiki-scraper/releases) page
2. Double-click the downloaded DMG file
3. Drag "Mafia Wiki Scraper" to your Applications folder
4. Double-click the app icon to run

#### Option 2: Manual Install
1. Make sure you have Python 3.12 or later installed
2. Open Terminal and run:
   ```bash
   git clone https://github.com/Archipelogic/mafia-wiki-scraper.git
   cd mafia-wiki-scraper
   ./install.sh
   ```
3. Find "Mafia Wiki Scraper" on your Desktop and double-click to run

### Windows

#### Option 1: Easy Install (Recommended)
1. Download the latest `MafiaWikiScraper-Setup.exe` from the [Releases](https://github.com/Archipelogic/mafia-wiki-scraper/releases) page
2. Run the installer
3. Find "Mafia Wiki Scraper" on your Desktop and double-click to run

#### Option 2: Manual Install
1. Install [Python 3.12 or later](https://www.python.org/downloads/) (make sure to check "Add Python to PATH")
2. Download this repository as ZIP and extract it
3. Double-click `install.bat`
4. Find "Mafia Wiki Scraper" on your Desktop and double-click to run

## Usage

1. Launch the app by double-clicking its icon
2. The app will save files to your Documents folder in a "Mafia Wiki Scraper" directory
3. Click "Start Scraping" to begin
4. Progress bars will show the current status
5. When complete, you'll find a JSON file with all the scraped content

## Development

To contribute to this project:

1. Fork the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. Make your changes
5. Run tests:
   ```bash
   pytest
   ```
6. Submit a pull request

## License

MIT License - see LICENSE file for details
