#!/bin/bash

echo "Installing Mafia Wiki Scraper..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Please install Python from: https://www.python.org/downloads/"
        echo "After installing Python, run this script again."
        exit 1
    else
        echo "Installing Python..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3 python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip
        else
            echo "Could not install Python. Please install Python 3 manually."
            exit 1
        fi
    fi
fi

echo "Using Python: $(which python3)"
echo "Python version: $(python3 --version)"

# Install/upgrade pip
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip

# Install required packages
echo "Installing required packages..."
python3 -m pip install --user customtkinter Pillow pygame

# Install the scraper in development mode
echo "Installing Mafia Wiki Scraper..."
python3 -m pip install --user -e .

# Verify installation
echo "Verifying installation..."
if python3 -c "import mafia_wiki_scraper" 2>/dev/null; then
    echo "Package installed successfully!"
else
    echo "Error: Package installation failed!"
    exit 1
fi

# Create desktop shortcut
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Create an AppleScript application
    DESKTOP_PATH="$HOME/Desktop"
    APP_PATH="$DESKTOP_PATH/Mafia Wiki Scraper.app"
    mkdir -p "$APP_PATH/Contents/MacOS"
    mkdir -p "$APP_PATH/Contents/Resources"
    
    # Create the launcher script
    cat > "$APP_PATH/Contents/MacOS/launcher" << 'EOF'
#!/bin/bash

# Set up logging
exec 1> "$HOME/Desktop/mafia_scraper_log.txt" 2>&1

echo "Starting Mafia Wiki Scraper..."
echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"
echo "PATH: $PATH"

# Get the directory where Python is installed
PYTHON_PATH=$(which python3)
if [ -z "$PYTHON_PATH" ]; then
    echo "Error: Could not find python3"
    PYTHON_PATH="/usr/local/bin/python3"
fi

echo "Using Python at: $PYTHON_PATH"

# Add common Python paths to PATH
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# Get the actual path to the script and the virtual environment
SCRIPT_PATH=$(dirname "$0")
cd "$SCRIPT_PATH/../../.."
VENV_PATH="$HOME/Library/Python/3.12/lib/python/site-packages"

echo "Script path: $SCRIPT_PATH"
echo "Current directory after cd: $(pwd)"
echo "Checking if mafia_wiki_scraper is installed..."
$PYTHON_PATH -c "import mafia_wiki_scraper; print('Package location:', mafia_wiki_scraper.__file__)"

# Add the virtual environment to PYTHONPATH
export PYTHONPATH="$VENV_PATH:$PYTHONPATH"

echo "Running the scraper..."
"$PYTHON_PATH" -m mafia_wiki_scraper.gui
EOF
    
    chmod +x "$APP_PATH/Contents/MacOS/launcher"
    
    # Create Info.plist with more details
    cat > "$APP_PATH/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.mafiawiki.scraper</string>
    <key>CFBundleName</key>
    <string>Mafia Wiki Scraper</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.10</string>
    <key>LSBackgroundOnly</key>
    <string>0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

    # Copy the app icon (using the logo.png as the app icon)
    cp "$(dirname "$0")/mafia_wiki_scraper/resources/logo.png" "$APP_PATH/Contents/Resources/AppIcon.icns"
    
    echo "Created Mac application at: $APP_PATH"
    
else
    # Create .desktop file for Linux
    mkdir -p ~/.local/share/applications
    cat > ~/.local/share/applications/mafia-wiki-scraper.desktop << EOF
[Desktop Entry]
Name=Mafia Wiki Scraper
Exec=python3 -m mafia_wiki_scraper.gui
Type=Application
Terminal=false
Categories=Utility;
EOF
    
    # Create desktop shortcut
    ln -sf ~/.local/share/applications/mafia-wiki-scraper.desktop ~/Desktop/
fi

echo "Installation complete! You can now run Mafia Wiki Scraper from your desktop."
