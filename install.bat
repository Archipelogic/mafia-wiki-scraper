@echo off
echo Installing Mafia Wiki Scraper...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please download and install Python 3.12 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo After installing Python, run this script again.
    pause
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
if exist "%USERPROFILE%\.mafia_wiki_scraper_venv" (
    echo Removing old virtual environment...
    rmdir /s /q "%USERPROFILE%\.mafia_wiki_scraper_venv"
)
python -m venv "%USERPROFILE%\.mafia_wiki_scraper_venv"
if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

:: Activate virtual environment
call "%USERPROFILE%\.mafia_wiki_scraper_venv\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install/upgrade pip
echo Installing/upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Failed to upgrade pip.
    pause
    exit /b 1
)

:: Install required packages
echo Installing required packages...
python -m pip install customtkinter Pillow pygame
if errorlevel 1 (
    echo Failed to install required packages.
    pause
    exit /b 1
)

:: Install the scraper
echo Installing Mafia Wiki Scraper...
python -m pip install -e .
if errorlevel 1 (
    echo Failed to install Mafia Wiki Scraper.
    pause
    exit /b 1
)

:: Create output directory
echo Creating output directory...
if not exist "%USERPROFILE%\Documents\Mafia Wiki Scraper" (
    mkdir "%USERPROFILE%\Documents\Mafia Wiki Scraper"
)

:: Create desktop shortcut
echo Creating desktop shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > create_shortcut.vbs
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\Mafia Wiki Scraper.lnk" >> create_shortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> create_shortcut.vbs
echo pythonw = "%USERPROFILE%\.mafia_wiki_scraper_venv\Scripts\pythonw.exe" >> create_shortcut.vbs
echo oLink.TargetPath = pythonw >> create_shortcut.vbs
echo oLink.Arguments = "-m mafia_wiki_scraper.gui" >> create_shortcut.vbs
echo oLink.IconLocation = "%~dp0mafia_wiki_scraper\resources\logo.ico" >> create_shortcut.vbs
echo oLink.Save >> create_shortcut.vbs
cscript //nologo create_shortcut.vbs
del create_shortcut.vbs

echo.
echo Installation complete! You can now run Mafia Wiki Scraper from your desktop.
echo The app will save files to your Documents\Mafia Wiki Scraper folder.
echo.
pause
