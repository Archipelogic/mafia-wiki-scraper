@echo off
echo Installing Mafia Wiki Scraper...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Downloading Python installer...
    curl -o python_installer.exe https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe
    echo Installing Python...
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
)

:: Install/upgrade pip
python -m ensurepip --upgrade

:: Install the scraper
pip install -e .

:: Create desktop shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > create_shortcut.vbs
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\Mafia Wiki Scraper.lnk" >> create_shortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> create_shortcut.vbs
echo oLink.TargetPath = "cmd.exe" >> create_shortcut.vbs
echo oLink.Arguments = "/c mafia-scraper-gui" >> create_shortcut.vbs
echo oLink.Save >> create_shortcut.vbs
cscript //nologo create_shortcut.vbs
del create_shortcut.vbs

echo Installation complete! You can now run Mafia Wiki Scraper from your desktop.
pause
