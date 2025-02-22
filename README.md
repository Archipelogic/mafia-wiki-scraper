# Mafia Wiki Scraper

A desktop application that helps you download and archive content from the BNB Mafia Wiki.

![Mafia Wiki Scraper Screenshot](docs/images/gui_image.png)

## Features

- Easy-to-use interface
- Shows download progress
- Sound effects for notifications
- Choose where to save files
- Automatically handles errors and retries

## Installation Guide

### Step 1: Install Python
First, you'll need Python on your computer.

**Windows Users:**
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Click "Install Now"

**Mac Users:**
1. Open Terminal (press Cmd + Space, type "terminal", press Enter)
2. Copy and paste this command:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. After Homebrew installs, run:
   ```
   brew install python
   ```

### Step 2: Get the App
1. Go to the "Actions" tab at the top of this page
2. Click on the latest successful workflow run (one with a green checkmark ✓)
3. Scroll down to "Artifacts"
4. Download the ZIP file
5. Extract the ZIP file somewhere on your computer

### Step 3: Install & Run
Open Terminal (Mac) or Command Prompt (Windows) and type these commands:

**Windows:**
```
cd path/to/extracted/folder
python -m pip install -e .
python -m mafia_wiki_scraper.gui
```

**Mac:**
```
cd path/to/extracted/folder
python3 -m pip install -e .
python3 -m mafia_wiki_scraper.gui
```

## Using the App

1. When you first open the app, it will create a default output folder in your Documents folder
2. You can change where files are saved by clicking the "Browse" button
3. Click "Start Scraping" to begin downloading the wiki content
4. The progress bars will show you how far along the process is
5. When it's done, you'll find all the downloaded files in your chosen output folder

## Using the Downloaded Content

The app saves the wiki content in a format that's perfect for using with AI language models. Here's how you can use it:

### Claude.ai (Recommended)
1. Go to [Claude.ai](https://claude.ai)
2. Create a free account
3. Upload the downloaded JSON files
4. Ask Claude anything about BNB Mafia!

### Other AI Options
- [ChatGPT](https://chat.openai.com) - Paste sections of the content directly into your chat
- [Perplexity](https://perplexity.ai) - Upload or paste the content
- [Bard](https://bard.google.com) - Share the content through file upload
- [Bing Chat](https://bing.com/chat) - Copy and paste relevant sections

The downloaded content is organized in a way that makes it easy for AI to understand and answer questions about BNB Mafia's mechanics, strategies, and gameplay elements.

## Troubleshooting

Having problems? Try these fixes:

1. **App won't start**:
   - Make sure Python is installed:
     - Open Terminal (Mac) or Command Prompt (Windows)
     - Type `python --version` (Windows) or `python3 --version` (Mac)
     - If it says "command not found", go back to Step 1
   - Try running the install commands again (Step 3)

2. **Can't find downloaded files**:
   - Look in your Documents folder for "Mafia_Wiki_Scraper_Output"
   - Or check the folder you picked using the "Browse" button

3. **Still having issues?**:
   - Create an issue on GitHub and we'll help you out!

## License

MIT License - Feel free to use and modify this software as you like!
