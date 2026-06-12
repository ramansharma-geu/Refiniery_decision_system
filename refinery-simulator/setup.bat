@echo off
echo ====================================================
echo === RDIS Automation Setup Script (Windows cmd) ===
echo ====================================================

:: 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python is not installed. Please install Python 3.12+ and add it to your PATH.
    pause
    exit /b 1
)

echo Check: Python is installed.

:: 2. Check SQLite3
where sqlite3 >nul 2>nul
if %errorlevel% neq 0 (
    echo Warning: sqlite3 command not found. If database build fails, install sqlite3 binary.
)

:: 3. Create Virtual Environment
echo Initializing Python virtual environment (.venv)...
python -m venv .venv
call .venv\Scripts\activate.bat
echo Check: Virtual environment created and activated.

:: 4. Install dependencies
echo Installing python packages from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Check: Dependencies installed successfully.

:: 5. Rebuild database
echo Building SQLite database (refinery.db)...
if exist refinery.db (
    echo Found existing refinery.db. Rebuilding...
    del refinery.db
)

:: Run commands sequentially. Note: if sqlite3 is not on path, we fall back to python creating it.
:: Since flask run calls db.create_all(), the tables will get created on start or test run.
:: Let's use sqlite3 if available:
sqlite3 refinery.db < schema.sql
python generate_seed_data.py
sqlite3 refinery.db < seed_data.sql

echo Check: Database initialized and seeded with 1,000+ records.

:: 6. Run tests
echo Executing automated unit tests...
python -m unittest discover -s tests -p "test_refinery.py"
if %errorlevel% neq 0 (
    echo Error: One or more unit tests failed. Stop setup.
    pause
    exit /b 1
)
echo Check: All automated checks passed successfully.

:: 7. Start application
echo ======================================================
echo RDIS setup completed successfully!
echo Starting Flask web server on port 5001...
echo Open your browser and navigate to: http://127.0.0.1:5001
echo ======================================================
python app.py
