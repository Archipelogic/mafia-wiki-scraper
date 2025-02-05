"""Setup configuration for mafia_wiki_scraper."""
import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

def create_desktop_shortcut():
    """Create desktop shortcut for the GUI."""
    try:
        if sys.platform == "win32":
            # Windows shortcut
            import winshell
            from win32com.client import Dispatch
            desktop = winshell.desktop()
            path = os.path.join(desktop, "Mafia Wiki Scraper.lnk")
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = "-m mafia_wiki_scraper.gui"
            shortcut.save()
        elif sys.platform == "darwin":
            # macOS .command file
            desktop = Path.home() / "Desktop"
            path = desktop / "Mafia Wiki Scraper.command"
            with open(path, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write(f'{sys.executable} -m mafia_wiki_scraper.gui\n')
            os.chmod(path, 0o755)
        else:
            # Linux .desktop file
            desktop = Path.home() / "Desktop"
            path = desktop / "mafia-wiki-scraper.desktop"
            with open(path, 'w') as f:
                f.write("[Desktop Entry]\n")
                f.write("Type=Application\n")
                f.write("Name=Mafia Wiki Scraper\n")
                f.write(f"Exec={sys.executable} -m mafia_wiki_scraper.gui\n")
                f.write("Terminal=false\n")
            os.chmod(path, 0o755)
    except Exception as e:
        print(f"Warning: Could not create desktop shortcut: {e}")

setup(
    name="mafia_wiki_scraper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.9.0",
        "customtkinter>=5.2.0",
        "Pillow>=10.0.0",
        "pygame>=2.5.0",  # Add pygame for sound effects
    ],
    entry_points={
        "console_scripts": [
            "mafia-scraper=mafia_wiki_scraper.cli:main",
            "mafia-scraper-gui=mafia_wiki_scraper.gui:main",
        ],
    },
    python_requires=">=3.7",
    author="archipelogic",
    author_email="archipelogic@github.com",
    description="A web scraper for the Mafia GitBook wiki with a beautiful GUI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="web-scraper, mafia, gitbook, gui",
    url="https://github.com/Archipelogic/mafia-wiki-scraper",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: X11 Applications :: GTK",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,  # Add this to include resource files
    package_data={
        'mafia_wiki_scraper': ['resources/*'],  # Include all resource files
    },
)

# Create desktop shortcut during installation
if "install" in sys.argv:
    create_desktop_shortcut()
