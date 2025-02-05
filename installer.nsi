!include "MUI2.nsh"

Name "Mafia Wiki Scraper"
OutFile "dist\MafiaWikiScraper-Setup.exe"
InstallDir "$PROGRAMFILES\Mafia Wiki Scraper"

!define MUI_ICON "mafia_wiki_scraper\resources\logo.ico"
!define MUI_UNICON "mafia_wiki_scraper\resources\logo.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    SetOverwrite ifnewer
    
    File /r "dist\app\*.*"
    
    CreateDirectory "$SMPROGRAMS\Mafia Wiki Scraper"
    CreateShortCut "$SMPROGRAMS\Mafia Wiki Scraper\Mafia Wiki Scraper.lnk" "$INSTDIR\Mafia Wiki Scraper.exe"
    CreateShortCut "$DESKTOP\Mafia Wiki Scraper.lnk" "$INSTDIR\Mafia Wiki Scraper.exe"
    
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\uninstall.exe"
    RMDir /r "$INSTDIR"
    Delete "$SMPROGRAMS\Mafia Wiki Scraper\Mafia Wiki Scraper.lnk"
    RMDir "$SMPROGRAMS\Mafia Wiki Scraper"
    Delete "$DESKTOP\Mafia Wiki Scraper.lnk"
SectionEnd
