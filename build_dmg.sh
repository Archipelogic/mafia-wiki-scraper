#!/bin/bash

echo "Building Mafia Wiki Scraper DMG..."

# Create a temporary directory for the DMG
TEMP_DIR=$(mktemp -d)
APP_NAME="Mafia Wiki Scraper"
DMG_NAME="MafiaWikiScraper"

# Clean up any existing virtual environment
rm -rf ~/.mafia_wiki_scraper_venv

# Create and activate virtual environment
python3 -m venv ~/.mafia_wiki_scraper_venv
source ~/.mafia_wiki_scraper_venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install py2app
pip install -e .

# Create setup.py for py2app
cat > setup.py << EOL
from setuptools import setup

APP = ['mafia_wiki_scraper/gui.py']
DATA_FILES = [
    ('resources', ['mafia_wiki_scraper/resources/logo.ico', 'mafia_wiki_scraper/resources/success.wav'])
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['customtkinter', 'PIL', 'pygame', 'aiohttp', 'bs4', 'lxml'],
    'iconfile': 'mafia_wiki_scraper/resources/logo.ico',
    'plist': {
        'CFBundleName': "Mafia Wiki Scraper",
        'CFBundleDisplayName': "Mafia Wiki Scraper",
        'CFBundleGetInfoString': "Scrape content from the Mafia Wiki",
        'CFBundleIdentifier': "com.archipelogic.mafiawikiscraper",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': "Copyright 2024 Archipelogic"
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
EOL

# Build the app bundle
rm -rf build dist
python setup.py py2app

# Create DMG directory structure
mkdir -p "$TEMP_DIR/dmg"
cp -r "dist/$APP_NAME.app" "$TEMP_DIR/dmg/"

# Create a symbolic link to /Applications
ln -s /Applications "$TEMP_DIR/dmg/Applications"

# Create the DMG
mkdir -p dist
hdiutil create -volname "$APP_NAME" -srcfolder "$TEMP_DIR/dmg" -ov -format UDZO "dist/$DMG_NAME.dmg"

# Clean up
rm -rf "$TEMP_DIR" build setup.py
deactivate

echo "DMG created at dist/$DMG_NAME.dmg"
