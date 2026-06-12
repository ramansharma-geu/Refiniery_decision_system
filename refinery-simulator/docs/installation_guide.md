# RDIS Installation & Setup Guide

Follow these instructions to install, configure, and launch the Refinery Decision Intelligence System (RDIS) proof-of-concept application.

## 1. Prerequisites
- **Python 3.12+** installed on your system.
- **SQLite 3** CLI (usually pre-installed on macOS and Linux).
- Optional: **Ollama** installed locally if you wish to run local SLMs (Phi-3, Qwen 2.5, Gemma).

---

## 2. Directory Initialization & Setup
Clone the directory or navigate to the project root:

```bash
cd /Users/shivam/Desktop/refinery_decision_system/refinery-simulator
```

---

## 3. Install Python Dependencies
It is recommended to use a virtual environment, but dependencies can also be installed directly to user-space:

```bash
# Optional: Create and activate virtualenv
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

---

## 4. Initialize the Database
RDIS ships with a schema template and programmatic data seeding script:

```bash
# Step A: Build tables layout in SQLite
sqlite3 refinery.db < schema.sql

# Step B: Generate seed data statements containing 1,000+ operational records
python3 generate_seed_data.py

# Step C: Populate database with generated seed data
sqlite3 refinery.db < seed_data.sql
```

You can verify that the database contains exactly 1,000 records:
```bash
sqlite3 refinery.db "SELECT count(*) FROM operational_history;"
```
*(Should return `1000`)*

---

## 5. Launch the Web Console
Start the Flask application server:

```bash
python3 app.py
```

The terminal will confirm the local server is running:
`* Running on http://127.0.0.1:5001` (or `http://0.0.0.0:5001`)

Open your web browser and navigate to:
[http://127.0.0.1:5001](http://127.0.0.1:5001)

---

## 6. Configuring Ollama Local SLM (Optional)
To query a real local Small Language Model instead of the Mock knowledge base:
1. Open your terminal and start Ollama:
   ```bash
   ollama run qwen2.5:1.5b
   ```
2. Navigate to **App Settings** (⚙️) on the RDIS web interface.
3. Set **SLM Provider** to: `Local Ollama API`.
4. Enter Ollama Model Name: `qwen2.5:1.5b` (or whichever model you ran in step 1).
5. Click **Save Settings**.
6. Navigate to the **Hybrid AI Chatbot** page and begin chat queries!
