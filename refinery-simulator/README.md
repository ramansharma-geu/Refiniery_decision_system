# Refinery Decision Intelligence System (RDIS)

The **Refinery Decision Intelligence System (RDIS)** is an industrial-themed decision support proof-of-concept. It demonstrates how chemical process operators and refinery managers can leverage simulation engines and Small Language Models (SLMs) to evaluate downstream operational impacts before making changes.

---

## ⚡ Project Objective
This system is NOT a real-world refinery controller, but a **digital-twin sandbox**. It models relationships between refinery units and parameter adjustments.

RDIS is designed around a **decoupled, modular architecture**. The current rule-based simulation engine and local mock SLM chatbot can be easily replaced by future developers with:
- Machine Learning (ML) optimization frameworks
- Live refinery sensor data pipelines
- Fully integrated neural networks (via Ollama or HuggingFace)

---

## 🛠️ Technology Stack
- **Backend Framework:** Python 3.12+, Flask (Modular blueprints architecture)
- **Database Layer:** SQLite (Structured local schemas using Flask-SQLAlchemy)
- **Report & Document Services:** ReportLab (Formatted PDF outputs), CSV exports
- **Frontend Panel:** HTML5, CSS3, JavaScript, Chart.js, Bootstrap 5
- **UI Design Spec:** Styled under the **IBM Carbon Design System** (flat 0px geometry, crisp white/gray surfaces, confident blue accent color, IBM Plex Sans typography)

---

## 📁 Directory Structure
```text
refinery-simulator/
├── app.py                   # Main Flask application entry point
├── config.py                # System config profiles
├── requirements.txt         # Dependency packages manifest
├── schema.sql               # SQLite schema design
├── generate_seed_data.py    # Seeding generator script
├── seed_data.sql            # Generated SQL script (1,000+ records)
├── refinery.db              # Active SQLite database file
│
├── models/                  # SQLAlchemy Database Models
│   ├── user.py
│   ├── unit.py
│   ├── operational_history.py
│   ├── scenario.py
│   ├── simulation.py
│   ├── recommendation.py
│   ├── chatbot.py
│   └── report.py
│
├── routes/                  # Controller blueprints (Routing)
│   ├── dashboard.py
│   ├── units.py
│   ├── scenarios.py
│   ├── chatbot.py
│   ├── reports.py
│   └── settings.py
│
├── services/                # Core business services
│   ├── db_service.py        # Database CRUD service
│   ├── slm_service.py       # SLM adapter (Mock/Ollama/HuggingFace)
│   ├── report_service.py    # ReportLab PDF compile engine
│   └── export_service.py    # CSV exporter
│
├── simulation_engine/       # Sandbox Simulator Engine
│   ├── rules.py             # Scenario rules catalog
│   └── engine.py            # Simulation pipeline coordinator
│
├── chatbot/                 # Hybrid AI Chatbot Assistant
│   ├── parser.py            # intent & entity extractor
│   ├── hybrid_retriever.py  # SQLite fetcher + SLM query coordinator
│   └── dataset/             # Fine-tuning dataset profiles
│
├── ai_engine/               # AI recommendation engine
│   └── recommender.py
│
├── static/                  # Stylesheets & Javascript charts
│   ├── css/style.css
│   └── js/dashboard.js
│
├── templates/               # Layouts & Jinja2 page templates
│
├── docs/                    # System Documentation sheets
│   ├── database_design.md
│   ├── api_documentation.md
│   ├── installation_guide.md
│   └── testing_guide.md
│
└── tests/                   # Automated unittest suite
    └── test_refinery.py
```

---

## 🚀 Quickstart Guide

Navigate to `refinery-simulator` and run the bootstrap sequence:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Build and seed SQLite database
sqlite3 refinery.db < schema.sql
python3 generate_seed_data.py
sqlite3 refinery.db < seed_data.sql

# 3. Execute automated test suite
python3 -m unittest discover -s tests -p "test_refinery.py"

# 4. Start Flask web server
python3 app.py
```

Open [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser.

---

## 🏭 Configured Refinery Units
RDIS models the downstream flow across exactly 5 units:
1. **CDU (Crude Distillation Unit):** Distillation tower separating raw crude.
2. **VDU (Vacuum Distillation Unit):** Low-pressure tower extracting vacuum gas oils.
3. **FCC (Fluid Catalytic Cracking Unit):** High-temperature cracking converter producing gasoline.
4. **Hydrotreater:** Reactor removing sulfur impurities.
5. **Storage Terminal:** Feedstock and product tank inventory buffers.

---

## ⚡ Simulation Scenarios
The simulator models 5 scenarios:
- **FCC Shutdown:** Models conversion outage, upstream backup, and yield drop.
- **Throughput Increase (+10%):** Stress-tests hydraulic limits, highlighting the Hydrotreater bottleneck.
- **Maintenance Delay:** Increases unplanned outages and fatigue indices on the CDU.
- **Energy Reduction (-20%):** Forces units to turndown rates due to utility grid caps.
- **Demand Increase:** Models operational stress when pushing units to maximum limits.
