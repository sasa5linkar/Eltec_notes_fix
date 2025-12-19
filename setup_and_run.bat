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

REM Prepare logging paths
set "LOG_FILE=Output\run.log"
set "SUMMARY_FILE=Output\run_summary.csv"

if exist "%LOG_FILE%" del "%LOG_FILE%"
if exist "%SUMMARY_FILE%" del "%SUMMARY_FILE%"

REM Run the script and capture output
echo ========================================
echo Running endnote inlining transformation
echo ========================================
echo.
echo Logging output to %LOG_FILE%
python inline_notes.py Input Output > "%LOG_FILE%" 2>&1
set "PYTHON_EXIT=%ERRORLEVEL%"

REM Echo the log to the console for visibility
type "%LOG_FILE%"

REM Build run summary table from log
call :build_summary

echo.
echo ========================================
echo Script execution complete
echo ========================================
echo Summary table written to %SUMMARY_FILE%
echo.
echo Check the Output folder for transformed files
echo.

set "FINAL_EXIT=%PYTHON_EXIT%"

if %ERROR_FOUND% neq 0 (
    echo ERROR: Processing errors detected. See %SUMMARY_FILE% for details.
    set "FINAL_EXIT=1"
)

if %PYTHON_EXIT% neq 0 (
    echo ERROR: inline_notes.py exited with code %PYTHON_EXIT%.
)

pause
exit /b %FINAL_EXIT%

:build_summary
setlocal EnableDelayedExpansion
set "localError=0"
echo file,status,details > "%SUMMARY_FILE%"

for /f "usebackq delims=" %%L in ("%LOG_FILE%") do (
    set "line=%%L"

    if "!line!"=="" (
        rem Skip blank lines
    ) else if "!line:~0,24!"=="  Successfully processed" (
        for /f "tokens=3" %%A in ("!line!") do (
            set "file=%%A"
        )
        >>"%SUMMARY_FILE%" echo !file!,Processed,Processed successfully
    ) else if "!line:~0,23!"=="  No endnotes found in" (
        for /f "tokens=5" %%A in ("!line!") do (
            set "file=%%A"
        )
        >>"%SUMMARY_FILE%" echo !file!,No endnotes,No endnotes found
    ) else if "!line:~0,19!"=="  ERROR processing" (
        for /f "tokens=3,*" %%A in ("!line!") do (
            set "file=%%A"
            set "details=%%B"
        )

        if "!file:~-1!"==":" set "file=!file:~0,-1!"
        if defined details (
            set "details=!details:~2!"
        ) else (
            set "details=Processing error"
        )

        >>"%SUMMARY_FILE%" echo !file!,ERROR,!details!
        set "localError=1"
    )
)

endlocal & set "ERROR_FOUND=%localError%"
exit /b 0
