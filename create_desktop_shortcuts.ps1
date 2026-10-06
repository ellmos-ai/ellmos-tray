# create_desktop_shortcuts.ps1 - Erstellt Desktop-Shortcuts fuer BACH & OCEAN Tray Steuerzentrale
$desktopPath = [System.Environment]::GetFolderPath('Desktop')
$wsh = New-Object -ComObject WScript.Shell

# 1. Bach Tray Shortcut
$bachCmd = Join-Path $PSScriptRoot "start_bach_tray.cmd"
$bachShortcutPath = Join-Path $desktopPath "BACH Steuerzentrale (Tray).lnk"
$bachShortcut = $wsh.CreateShortcut($bachShortcutPath)
$bachShortcut.TargetPath = $bachCmd
$bachShortcut.WorkingDirectory = $PSScriptRoot
$bachShortcut.Description = "Startet den BACH System Tray Steuerungsdienst"
$bachShortcut.Save()
Write-Host "Erstellt: $bachShortcutPath"

# 2. Ocean Tray Shortcut
$oceanCmd = Join-Path $PSScriptRoot "start_ocean_tray.cmd"
$oceanShortcutPath = Join-Path $desktopPath "OCEAN Steuerzentrale (Tray).lnk"
$oceanShortcut = $wsh.CreateShortcut($oceanShortcutPath)
$oceanShortcut.TargetPath = $oceanCmd
$oceanShortcut.WorkingDirectory = $PSScriptRoot
$oceanShortcut.Description = "Startet den OCEAN System Tray Steuerungsdienst"
$oceanShortcut.Save()
Write-Host "Erstellt: $oceanShortcutPath"
