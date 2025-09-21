#!/bin/bash

# Streamlit Chatbot Demo - Quick Start Script
# This script activates the virtual environment and runs the launcher

echo "🤖 Streamlit Chatbot Demo - Quick Start"
echo "======================================"

# Check if virtual environment exists
if [ ! -d "chatbot-env" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run the setup first:"
    echo "  python3 -m venv chatbot-env"
    echo "  source chatbot-env/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source chatbot-env/bin/activate

# Check if requirements are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "❌ Dependencies not installed!"
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Run the launcher
echo "🚀 Starting application launcher..."
python run_app.py

