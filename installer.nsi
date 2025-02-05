!include "MUI2.nsh"

Name "Mafia Wiki Scraper"
OutFile "dist\MafiaWikiScraper-Setup.exe"
InstallDir "$PROGRAMFILES64\Mafia Wiki Scraper"
RequestExecutionLevel admin

!define MUI_ICON "mafia_wiki_scraper\resources\logo.ico"
!define MUI_UNICON "mafia_wiki_scraper\resources\logo.ico"

!define MUI_WELCOMEPAGE_TITLE "Welcome to Mafia Wiki Scraper Setup"
!define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of Mafia Wiki Scraper.$\r$\n$\r$\nClick Next to continue."

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
    SetOverwrite on
    
    ; Copy all files from the app directory
    File /r "dist\app\*.*"
    
    ; Create output directory
    CreateDirectory "$DOCUMENTS\Mafia Wiki Scraper"
    
    ; Create Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\Mafia Wiki Scraper"
    CreateShortCut "$SMPROGRAMS\Mafia Wiki Scraper\Mafia Wiki Scraper.lnk" "$INSTDIR\Mafia Wiki Scraper.exe"
    CreateShortCut "$SMPROGRAMS\Mafia Wiki Scraper\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    
    ; Create desktop shortcut
    CreateShortCut "$DESKTOP\Mafia Wiki Scraper.lnk" "$INSTDIR\Mafia Wiki Scraper.exe"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Write registry keys for uninstall
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MafiaWikiScraper" \
                     "DisplayName" "Mafia Wiki Scraper"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MafiaWikiScraper" \
                     "UninstallString" "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$DESKTOP\Mafia Wiki Scraper.lnk"
    RMDir /r "$SMPROGRAMS\Mafia Wiki Scraper"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MafiaWikiScraper"
    
    ; Note: We don't remove the Documents folder to preserve user data
SectionEnd
