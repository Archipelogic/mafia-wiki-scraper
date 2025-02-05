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

# Install/upgrade pip
python3 -m ensurepip --upgrade

# Install the scraper
pip3 install -e .

# Create desktop shortcut
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Create an AppleScript application
    DESKTOP_PATH="$HOME/Desktop"
    APP_PATH="$DESKTOP_PATH/Mafia Wiki Scraper.app"
    mkdir -p "$APP_PATH/Contents/MacOS"
    
    # Create the launcher script
    cat > "$APP_PATH/Contents/MacOS/launcher" << 'EOF'
#!/bin/bash
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
mafia-scraper-gui
EOF
    
    chmod +x "$APP_PATH/Contents/MacOS/launcher"
    
    # Create the Info.plist
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
</dict>
</plist>
EOF
else
    # Create .desktop file for Linux
    mkdir -p ~/.local/share/applications
    cat > ~/.local/share/applications/mafia-wiki-scraper.desktop << EOF
[Desktop Entry]
Name=Mafia Wiki Scraper
Exec=mafia-scraper-gui
Type=Application
Terminal=false
Categories=Utility;
EOF
    
    # Create desktop shortcut
    ln -sf ~/.local/share/applications/mafia-wiki-scraper.desktop ~/Desktop/
fi

echo "Installation complete! You can now run Mafia Wiki Scraper from your desktop."
