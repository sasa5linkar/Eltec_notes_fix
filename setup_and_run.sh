#!/bin/bash
# Script to setup virtual environment and run endnote inlining transformation
# This shell script creates a virtual environment, installs dependencies, and runs the script

echo "========================================"
echo "Endnote Inlining Transformation Setup"
echo "========================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

echo "Python found:"
python3 --version
echo

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully"
    echo
else
    echo "Virtual environment already exists"
    echo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi
echo

# Install dependencies
echo "Installing dependencies from requirements.txt..."
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "Dependencies installed successfully"
echo

# Check if Input folder exists
if [ ! -d "Input" ]; then
    echo "ERROR: Input folder not found"
    echo "Please create an Input folder with TEI XML files"
    exit 1
fi

# Create Output folder if it doesn't exist
if [ ! -d "Output" ]; then
    echo "Creating Output folder..."
    mkdir Output
fi
echo

# Run the script
echo "========================================"
echo "Running endnote inlining transformation"
echo "========================================"
echo
python inline_notes.py Input Output

echo
echo "========================================"
echo "Script execution complete"
echo "========================================"
echo
echo "Check the Output folder for transformed files"
echo

# Deactivate virtual environment
deactivate
