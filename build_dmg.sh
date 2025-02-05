#!/bin/bash

echo "Building Mafia Wiki Scraper DMG..."

# Create a temporary directory for the DMG
TEMP_DIR=$(mktemp -d)
APP_NAME="Mafia Wiki Scraper"
DMG_NAME="MafiaWikiScraper"

# Create the .app bundle in the temporary directory
./install.sh "$TEMP_DIR"

# Create DMG directory structure
mkdir -p "$TEMP_DIR/dmg"
mv "$TEMP_DIR/$APP_NAME.app" "$TEMP_DIR/dmg/"

# Create a symbolic link to /Applications
ln -s /Applications "$TEMP_DIR/dmg/Applications"

# Create the DMG
hdiutil create -volname "$APP_NAME" -srcfolder "$TEMP_DIR/dmg" -ov -format UDZO "dist/$DMG_NAME.dmg"

# Clean up
rm -rf "$TEMP_DIR"

echo "DMG created at dist/$DMG_NAME.dmg"
