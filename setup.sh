#!/bin/bash
# Setup script for Writing Assistant

echo "======================================"
echo "Writing Assistant Setup"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "llm_venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv llm_venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "Activating virtual environment..."
source llm_venv/bin/activate

echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "To get started:"
echo "  1. Activate the environment: source llm_venv/bin/activate"
echo "  2. Edit config.yaml to customize settings (optional)"
echo "  3. Run: python main.py start --username YOUR_NAME"
echo ""
