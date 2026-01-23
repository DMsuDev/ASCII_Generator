@echo off
setlocal EnableDelayedExpansion

:: ────────────────────────────────────────────────
:: Configuration (change it here easily)
:: ────────────────────────────────────────────────

set "VENV_FOLDER=.venv"
set "MAIN_SCRIPT=src\main.py"
set "CLEAN_SCRIPT=test\clean.py"

:: 1 = use venv    0 = use global python
set "USE_VENV=0"

:: ────────────────────────────────────────────────
:: Do not touch below unless you know what you are doing
:: ────────────────────────────────────────────────

cd /d "%~dp0" || (
    echo ERROR: Could not change to the script directory
    pause
    exit /b 1
)

if "%USE_VENV%"=="1" (
    if not exist "%VENV_FOLDER%\Scripts\activate.bat" (
        echo ERROR: Virtual environment not found in .\%VENV_FOLDER%\
        echo        Expected path: %CD%\%VENV_FOLDER%\Scripts\activate.bat
        pause
        exit /b 2
    )

    echo Activating virtual environment...
    call "%VENV_FOLDER%\Scripts\activate.bat" || (
        echo ERROR: Fail the activation of the virtual environment
        pause
        exit /b 3
    )

    echo Virtual environment activated - !VIRTUAL_ENV!
) else (
    python --version
)

echo.
echo =============================================
echo                  Running...
echo =============================================
echo.

python "%MAIN_SCRIPT%"
if errorlevel 1 (
    echo.
    echo ERROR: app.py finished with error code %errorlevel%
    goto :PAUSE_SECTION
)

echo.
echo Running cleanup...
python "%CLEAN_SCRIPT%"
if errorlevel 1 (
    echo WARNING: clean.py finished with code %errorlevel%
)

:PAUSE_SECTION
echo.
echo =============================================
echo                Finished
echo =============================================
echo.

:: If you want the window to close automatically when finished, comment out the pause line
:: and uncomment the following: pause >nul || exit (your choice)
echo Press any key to close...
exit