@echo off
REM Script to setup virtual environment and run endnote inlining transformation
REM This batch file creates a virtual environment, installs dependencies, and runs the script

echo ========================================
echo Endnote Inlining Transformation Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
    echo.
) else (
    echo Virtual environment already exists
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

REM Install dependencies
echo Installing dependencies from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Check if Input and Output folders exist
if not exist "Input" (
    echo ERROR: Input folder not found
    echo Please create an Input folder with TEI XML files
    pause
    exit /b 1
)

if not exist "Output" (
    echo Creating Output folder...
    mkdir Output
)
echo.

REM Run the script
echo ========================================
echo Running endnote inlining transformation
echo ========================================
echo.
python inline_notes.py Input Output

echo.
echo ========================================
echo Script execution complete
echo ========================================
echo.
echo Check the Output folder for transformed files
echo.

pause
