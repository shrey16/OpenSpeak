@echo off
REM ------------------------
REM OpenSpeak quick-launch
REM ------------------------
REM 1. Edit OPEN_SPEAK_DIR below so it points to the folder that contains main.py
REM 2. Save this file anywhere (e.g. your Desktop) and double-click to run.
REM ---------------------------------------------------------------

set "OPEN_SPEAK_DIR=C:\Path\to\OpenSpeak"

cd /d "%OPEN_SPEAK_DIR%"

REM (optional) activate virtual-env if it exists
if exist "%OPEN_SPEAK_DIR%\venv\Scripts\activate.bat" (
    call "%OPEN_SPEAK_DIR%\venv\Scripts\activate.bat"
)

python main.py 