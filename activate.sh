#!/bin/bash

# Activation script for Spoticron development environment
# Usage: source activate.sh

# Check if we're already in a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Already in a virtual environment: $VIRTUAL_ENV"
    echo "Deactivate first with: deactivate"
    return 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment"
        return 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/pyvenv.cfg" ] || [ ! -d "venv/lib" ]; then
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

echo "✅ Spoticron development environment activated!"
echo "📁 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"
echo "📦 Pip packages: $(pip list --format=freeze | wc -l) installed"
echo ""
echo "Quick start commands:"
echo "  python spoticron.py --help    # Show all commands"
echo "  python spoticron.py setup     # Setup guide"
echo "  python spoticron.py auth      # Test authentication"
echo "  python spoticron.py current   # Show current track"
echo ""
echo "To deactivate: deactivate"
