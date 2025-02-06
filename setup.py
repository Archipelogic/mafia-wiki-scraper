from setuptools import setup

setup(
    name="mafia_wiki_scraper",
    version="0.1.0-alpha",
    app=['mafia_wiki_scraper/gui.py'],
    data_files=[
        ('', ['mafia_wiki_scraper/resources/logo.png', 'mafia_wiki_scraper/resources/success.wav'])
    ],
    options={
        'py2app': {
            'argv_emulation': False,
            'packages': ['customtkinter', 'PIL', 'pygame', 'aiohttp', 'bs4', 'lxml'],
            'includes': ['tkinter', 'encodings'],
            'iconfile': 'mafia_wiki_scraper/resources/logo.png',
            'resources': ['mafia_wiki_scraper/resources'],
            'frameworks': ['/Library/Frameworks/Python.framework/Versions/3.12/Python'],
            'plist': {
                'CFBundleName': "Mafia Wiki Scraper",
                'CFBundleDisplayName': "Mafia Wiki Scraper",
                'CFBundleIdentifier': "com.archipelogic.mafiawikiscraper",
                'CFBundleVersion': "0.1.0-alpha",
                'CFBundleShortVersionString': "0.1.0-alpha",
                'LSMinimumSystemVersion': "10.10",
                'NSHighResolutionCapable': True
            }
        }
    }
)
