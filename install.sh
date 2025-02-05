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

# Get the best Python for this system
PYTHON_CMD=$(get_best_python)
echo "Using Python: $PYTHON_CMD"
echo "Python version: $($PYTHON_CMD --version)"
echo "Python architecture: $($PYTHON_CMD -c 'import platform; print(platform.machine())')"

# Install/upgrade pip
$PYTHON_CMD -m ensurepip --upgrade
$PYTHON_CMD -m pip install --upgrade pip

# Uninstall existing packages to ensure clean installation
echo "Removing any existing installations..."
$PYTHON_CMD -m pip uninstall -y pillow customtkinter pygame mafia-wiki-scraper

# Install required packages
echo "Installing required packages..."
$PYTHON_CMD -m pip install --user --no-cache-dir customtkinter Pillow pygame

# Install the scraper in development mode
echo "Installing Mafia Wiki Scraper..."
$PYTHON_CMD -m pip install --user -e .

# Verify installation
echo "Verifying installation..."
if $PYTHON_CMD -c "import mafia_wiki_scraper; print('Package found at:', mafia_wiki_scraper.__file__)" 2>/dev/null; then
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

# Use the same Python that was used for installation
PYTHON_PATH="$PYTHON_CMD"
echo "Using Python at: \$PYTHON_PATH"
echo "Python version: \$(\$PYTHON_PATH --version)"
echo "Python architecture: \$(\$PYTHON_PATH -c 'import platform; print(platform.machine())')"

# Add Homebrew and common Python paths to PATH
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\$PATH"

# Get the actual path to the script
SCRIPT_PATH=\$(dirname "\$0")
cd "\$SCRIPT_PATH/../../.."

echo "Script path: \$SCRIPT_PATH"
echo "Current directory after cd: \$(pwd)"
echo "Checking if mafia_wiki_scraper is installed..."
\$PYTHON_PATH -c "import mafia_wiki_scraper; print('Package location:', mafia_wiki_scraper.__file__)"

echo "Running the scraper..."
exec "\$PYTHON_PATH" -m mafia_wiki_scraper.gui
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
Exec=$PYTHON_CMD -m mafia_wiki_scraper.gui
Type=Application
Terminal=false
Categories=Utility;
EOF
    
    # Create desktop shortcut
    ln -sf ~/.local/share/applications/mafia-wiki-scraper.desktop ~/Desktop/
fi

echo "Installation complete! You can now run Mafia Wiki Scraper from your desktop."
