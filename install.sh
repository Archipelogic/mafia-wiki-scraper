#!/bin/bash

echo "Installing Mafia Wiki Scraper..."

# Function to get the best Python for M1/M2 Macs
get_best_python() {
    # Check for Homebrew Python first (preferred for M1/M2)
    if command -v /opt/homebrew/bin/python3 &> /dev/null; then
        echo "/opt/homebrew/bin/python3"
    elif command -v /usr/local/bin/python3 &> /dev/null; then
        echo "/usr/local/bin/python3"
    else
        echo "python3"
    fi
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Please install Python using Homebrew:"
        echo "1. Install Homebrew from https://brew.sh"
        echo "2. Run: brew install python"
        echo "After installing Python, run this script again."
        exit 1
    else
        echo "Installing Python..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3 python3-pip python3-venv
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip python3-venv
        else
            echo "Could not install Python. Please install Python 3 manually."
            exit 1
        fi
    fi
fi

# Get the best Python for this system
PYTHON_CMD=$(get_best_python)
echo "Using Python: $PYTHON_CMD"
echo "Python version: $($PYTHON_CMD --version)"
echo "Python architecture: $($PYTHON_CMD -c 'import platform; print(platform.machine())')"

# Create virtual environment
VENV_PATH="$HOME/.mafia_wiki_scraper_venv"
echo "Creating virtual environment at $VENV_PATH..."
$PYTHON_CMD -m venv "$VENV_PATH"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Install/upgrade pip in the virtual environment
python -m pip install --upgrade pip

# Install required packages in the virtual environment
echo "Installing required packages..."
python -m pip install customtkinter Pillow pygame

# Install the scraper in development mode
echo "Installing Mafia Wiki Scraper..."
python -m pip install -e .

# Verify installation
echo "Verifying installation..."
if python -c "import mafia_wiki_scraper; print('Package found at:', mafia_wiki_scraper.__file__)" 2>/dev/null; then
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
    cat > "$APP_PATH/Contents/MacOS/launcher" << EOF
#!/bin/bash

# Set up logging
exec 1> "\$HOME/Desktop/mafia_scraper_log.txt" 2>&1

echo "Starting Mafia Wiki Scraper..."
echo "Current directory: \$(pwd)"

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Get the actual path to the script
SCRIPT_PATH=\$(dirname "\$0")
cd "\$SCRIPT_PATH/../../.."

echo "Script path: \$SCRIPT_PATH"
echo "Current directory after cd: \$(pwd)"
echo "Python version: \$(python --version)"
echo "Checking if mafia_wiki_scraper is installed..."
python -c "import mafia_wiki_scraper; print('Package location:', mafia_wiki_scraper.__file__)"

echo "Running the scraper..."
exec python -m mafia_wiki_scraper.gui
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
Exec=bash -c "source $VENV_PATH/bin/activate && python -m mafia_wiki_scraper.gui"
Type=Application
Terminal=false
Categories=Utility;
EOF
    
    # Create desktop shortcut
    ln -sf ~/.local/share/applications/mafia-wiki-scraper.desktop ~/Desktop/
fi

echo "Installation complete! You can now run Mafia Wiki Scraper from your desktop."
