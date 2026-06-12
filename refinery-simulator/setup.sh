#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== RDIS Automation Setup Script (macOS/Linux) ==="

# 1. Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install Python 3.12+ and retry."
    exit 1
fi

echo "✓ Python 3 is installed: $(python3 --version)"

# 2. Check SQLite3 installation
if ! command -v sqlite3 &> /dev/null; then
    echo "Error: sqlite3 CLI is not installed. Please install sqlite3 and retry."
    exit 1
fi

echo "✓ SQLite3 is installed: $(sqlite3 --version | head -n 1)"

# 3. Create python virtual environment
echo "Initializing Python virtual environment (.venv)..."
python3 -m venv .venv
source .venv/bin/activate
echo "✓ Virtual environment created and activated."

# 4. Install dependencies
echo "Installing python packages from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed successfully."

# 5. Build SQLite Database
echo "Building SQLite database (refinery.db) and running seed generator..."
# Remove existing database if any, to start fresh
if [ -f "refinery.db" ]; then
    echo "Found existing refinery.db. Rebuilding fresh..."
    rm refinery.db
fi

sqlite3 refinery.db < schema.sql
python3 generate_seed_data.py
sqlite3 refinery.db < seed_data.sql

echo "✓ Database initialized and seeded with 1,000+ operational records."

# 6. Run Automated Tests
echo "Executing automated unit tests..."
python3 -m unittest discover -s tests -p "test_refinery.py"
echo "✓ All automated checks passed successfully."

# 7. Start Flask Application
echo "======================================================"
echo "RDIS setup completed successfully!"
echo "Starting Flask web server on port 5001..."
echo "Open your browser and navigate to: http://127.0.0.1:5001"
echo "======================================================"

python3 app.py
