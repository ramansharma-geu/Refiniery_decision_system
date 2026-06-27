# Refinery Decision Intelligence System (RDIS)

The **Refinery Decision Intelligence System (RDIS)** is an industrial-themed decision support proof-of-concept. It demonstrates how chemical process operators and refinery managers can leverage simulation engines and Small Language Models (SLMs) to evaluate downstream operational impacts before making changes.

---

## Project Objective
This system is NOT a real-world refinery controller, but a **digital-twin sandbox**. It models relationships between refinery units and parameter adjustments.

RDIS is designed around a **decoupled, modular architecture**. The current rule-based simulation engine and local mock SLM chatbot can be easily replaced by future developers with:
- Machine Learning (ML) optimization frameworks
- Live refinery sensor data pipelines
- Fully integrated neural networks (via Ollama or HuggingFace)

---

## Technology Stack
- **Backend Framework:** Python 3.11+, Flask 3.0.3 (Modular blueprints architecture)
- **Database Layer:** SQLite with Flask-SQLAlchemy ORM
- **Report & Document Services:** ReportLab (PDF), CSV exports (stdlib)
- **Frontend Panel:** HTML5, CSS3, JavaScript, Chart.js 4.x, Bootstrap 5.3.3
- **UI Design Spec:** Carbon Design System (IBM Plex Sans typography)
- **AI/SLM:** Ollama, HuggingFace Transformers, Mock (rule-based)
- **Knowledge Graph:** Graphify

---

## Features

### Dashboard
- Real-time KPI cards (units, simulations, scenarios)
- 5 Chart.js visualizations (throughput, yield, energy, downtime, scenario distribution)
- Recent AI recommendations panel
- Recent simulation runs table

### Refinery Units
- 5 process units with live operational data
- Capacity utilization progress bars
- Detailed parameter cards (throughput, pressure, temperature, yield)
- Historical trend charts per unit

### Operational History
- Paginated log of 1000+ operational records
- Filter by unit
- Full parameter display (throughput, pressure, temperature, flow rate, downtime, yield, energy)

### Simulation Engine
- 5 pre-configured scenario types
- Rule-based parameter scaling
- Risk scoring (0-100)
- Bottleneck detection
- AI recommendation generation
- Before/after parameter comparison

### Hybrid AI Chatbot
- Intent classification (CURRENT_DATA, ANALYSIS, KNOWLEDGE, SIMULATION)
- SQL-based database queries for real-time values
- SLM integration for domain knowledge
- Quick query buttons
- Chat history with database context display

### Reports & Exports
- PDF report generation (ReportLab)
- CSV exports (units, history, simulation results)
- Report metadata tracking

### System Settings
- SLM provider selection (Mock, Ollama, HuggingFace)
- Ollama endpoint configuration
- HuggingFace model path configuration

### Health & Status
- `GET /api/health` - Database connectivity check
- `GET /api/status` - Full system status with DB statistics

---

## Directory Structure
```text
refinery-simulator/
├── app.py                   # Flask application factory + health/status endpoints
├── config.py                # Configuration (DB, SLM providers)
├── requirements.txt         # Python dependencies
├── refinery.db              # SQLite database (pre-seeded)
├── generate_seed_data.py    # Seed data generator
├── seed_data.sql            # SQL seed script
├── schema.sql               # Database schema
├── engineering_rules.json   # Engineering thresholds
├── refinery_knowledge.json  # Chatbot knowledge base
│
├── models/                  # SQLAlchemy ORM Models (9 models)
│   ├── __init__.py
│   ├── user.py
│   ├── unit.py
│   ├── operational_history.py
│   ├── scenario.py
│   ├── simulation.py
│   ├── recommendation.py
│   ├── chatbot.py
│   └── report.py
│
├── routes/                  # Flask Blueprints (6 blueprints)
│   ├── dashboard.py         # Dashboard + /api/analytics
│   ├── units.py             # Units list + details + history
│   ├── scenarios.py         # Scenario CRUD + simulation execution
│   ├── chatbot.py           # Chat UI + /chatbot/query
│   ├── reports.py           # Report generation + download
│   └── settings.py          # System settings
│
├── services/                # Business logic services
│   ├── db_service.py        # Database CRUD operations
│   ├── slm_service.py       # SLM adapter (Mock/Ollama/HuggingFace)
│   ├── report_service.py    # PDF generation (ReportLab)
│   └── export_service.py    # CSV export
│
├── simulation_engine/       # Simulation pipeline
│   ├── engine.py            # Core simulation executor
│   ├── rules.py             # Scenario rule definitions
│   └── estimator.py         # Parameter estimation
│
├── chatbot/                 # Hybrid AI chatbot
│   ├── hybrid_retriever.py  # Main chatbot logic
│   ├── knowledge_retriever.py
│   ├── parser.py            # Intent & entity extraction
│   └── intent_classifier.py
│
├── ai_engine/               # AI recommendation engine
│   └── recommender.py
│
├── static/                  # Frontend assets
│   ├── css/style.css        # Carbon Design System CSS
│   └── js/dashboard.js      # Dashboard chart rendering
│
├── templates/               # Jinja2 templates (12 templates)
│   ├── base.html
│   ├── dashboard.html
│   ├── units.html
│   ├── unit_details.html
│   ├── history.html
│   ├── scenarios.html
│   ├── scenario_form.html
│   ├── simulation_results.html
│   ├── chatbot.html
│   ├── reports.html
│   ├── settings.html
│   └── errors.html
│
├── tests/                   # Test suite
│   └── test_refinery.py
│
└── docs/                    # Documentation
    ├── database_design.md
    ├── api_documentation.md
    ├── installation_guide.md
    └── testing_guide.md
```

---

## Quickstart Guide

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# 1. Navigate to project directory
cd refinery-simulator

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the application
python app.py
```

Open [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser.

### Environment Variables (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `refinery-decision-intelligence-secret-key-9988` | Flask session secret |
| `DATABASE_URL` | `sqlite:///refinery.db` | Database connection string |
| `SLM_PROVIDER` | `mock` | SLM provider: `mock`, `ollama`, `huggingface` |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Ollama API endpoint |
| `OLLAMA_MODEL` | `qwen2.5:1.5b` | Ollama model name |
| `HF_MODEL_PATH` | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | HuggingFace model path |

---

## API Endpoints

### JSON APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analytics` | GET | Dashboard chart data (trends + scenario distribution) |
| `/api/health` | GET | Database health check |
| `/api/status` | GET | System status with DB statistics |
| `/chatbot/query` | POST | Chatbot query (accepts `{"query": "..."}`) |

### HTML Pages

| Endpoint | Description |
|----------|-------------|
| `/` or `/dashboard` | Dashboard with KPIs and charts |
| `/units` | Refinery units list |
| `/units/<code>` | Unit detail page (CDU, VDU, FCC, Hydrotreater, Storage Terminal) |
| `/history` | Operational history with pagination |
| `/chatbot` | AI chatbot interface |
| `/scenarios` | Scenario management |
| `/simulation/results/<id>` | Simulation results |
| `/reports` | Report manager |
| `/settings` | System settings |

---

## Configured Refinery Units
RDIS models the downstream flow across exactly 5 units:
1. **CDU (Crude Distillation Unit):** Distillation tower separating raw crude (100,000 bbl/day capacity)
2. **VDU (Vacuum Distillation Unit):** Low-pressure tower extracting vacuum gas oils (45,000 bbl/day)
3. **FCC (Fluid Catalytic Cracking Unit):** High-temperature cracking converter (35,000 bbl/day)
4. **Hydrotreater:** Reactor removing sulfur impurities (25,000 bbl/day)
5. **Storage Terminal:** Feedstock and product tank inventory (1,000,000 bbl/day)

---

## Simulation Scenarios
The simulator models 5 scenarios:
- **FCC Shutdown:** Models conversion outage, upstream backup, and yield drop
- **Throughput Increase (+10%):** Stress-tests hydraulic limits
- **Maintenance Delay:** Increases unplanned outages and fatigue indices
- **Energy Reduction (-20%):** Forces units to turndown rates
- **Demand Increase:** Models operational stress at maximum limits

---

## Performance

| Metric | P50 | P95 |
|--------|-----|-----|
| Page loads | <1ms | <25ms |
| Chatbot queries | <4ms | <15ms |
| Simulation runs | <9ms | <24ms |
| SQLite queries | <0.5ms | <1ms |
| PDF generation | <15ms | <22ms |
| CSV export | <26ms | <29ms |
| Peak memory | - | 14.4 MB |

---

## Security

- SQLAlchemy ORM prevents SQL injection
- Jinja2 auto-escaping prevents XSS
- Input validation on all API endpoints
- Environment variables for sensitive configuration
- Error handlers prevent stack trace exposure
- Timestamped export filenames prevent overwrites

---

## Known Limitations

- SQLite is single-threaded (not suitable for production concurrent access)
- Mock SLM returns pre-scripted responses (no real inference)
- Simulation engine uses rule-based scaling (not physics-based)
- No user authentication/authorization
- No HTTPS (development server only)

---

## Future Scope

- PostgreSQL migration for production use
- Real SLM integration with fine-tuned models
- WebSocket real-time updates
- User authentication and role-based access
- Docker containerization
- CI/CD pipeline
- Physics-based simulation engine
- Live sensor data integration
