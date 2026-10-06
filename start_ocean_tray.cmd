@echo off
rem Startet den Ocean System Tray fensterlos im Hintergrund mit Fehlerprotokollierung
setlocal enabledelayedexpansion
cd /d "%~dp0"
set PYTHONPATH=%~dp0src;%PYTHONPATH%

rem PythonW ermitteln
set "PYW_BIN="
where pythonw >nul 2>&1 && for /f "delims=" %%I in ('where pythonw') do if not defined PYW_BIN set "PYW_BIN=%%I"
if not defined PYW_BIN if exist "C:\Program Files\Python312\pythonw.exe" set "PYW_BIN=C:\Program Files\Python312\pythonw.exe"
if not defined PYW_BIN (
    where python >nul 2>&1 && for /f "delims=" %%I in ('where python') do if not defined PYW_BIN set "PYW_BIN=%%I"
)

if not defined PYW_BIN (
    echo [%DATE% %TIME%] [ERROR] Kein Python/PythonW Interpreter gefunden! >> "%~dp0tray.err.log"
    exit /b 1
)

start "" "%PYW_BIN%" -m ellmos_tray --brand ocean --host 127.0.0.1 --port 8081 %* >> "%~dp0tray.err.log" 2>&1
endlocal
