#!/bin/bash
# md2pdf Installation Script
# Supports macOS and Linux

set -e

echo "=== md2pdf Installation Script ==="
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Darwin*)    OS_TYPE="macOS";;
    Linux*)     OS_TYPE="Linux";;
    *)          OS_TYPE="UNKNOWN";;
esac

echo "Detected OS: ${OS_TYPE}"
echo ""

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo "✓ Python ${PYTHON_VERSION} found"
else
    echo "✗ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Check Node.js
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ Node.js ${NODE_VERSION} found"
else
    echo "✗ Node.js not found. Please install Node.js 16 or higher."
    echo "  Download from: https://nodejs.org/"
    exit 1
fi

# Check npm
echo "Checking npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✓ npm ${NPM_VERSION} found"
else
    echo "✗ npm not found (should come with Node.js)"
    exit 1
fi

echo ""
echo "=== Installing Dependencies ==="
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt
echo "✓ Python dependencies installed"

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
cd renderer
npm install
cd ..
echo "✓ Node.js dependencies installed"

echo ""
echo "=== Testing Installation ==="
echo ""

# Test Python imports
echo "Testing Python modules..."
python3 -c "import click, yaml, jinja2, markdown_it, requests" && echo "✓ Python imports successful" || {
    echo "✗ Python import test failed"
    exit 1
}

# Test Node.js modules
echo "Testing Node.js modules..."
node -e "require('express'); require('puppeteer'); require('body-parser')" && echo "✓ Node.js imports successful" || {
    echo "✗ Node.js import test failed"
    exit 1
}

echo ""
echo "=== Running Tests ==="
echo ""

# Run pytest if available
if command -v pytest &> /dev/null; then
    echo "Running test suite..."
    pytest tests/ -v || {
        echo "⚠️  Some tests failed, but installation is complete"
    }
else
    echo "pytest not installed, skipping test suite"
    echo "Install with: pip3 install pytest"
fi

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "Usage:"
echo "  python3 md2pdf.py"
echo ""
echo "For help:"
echo "  python3 md2pdf.py --help"
echo ""
echo "Documentation:"
echo "  README.md - Full documentation"
echo "  TESTING.md - Manual testing guide"
echo ""
