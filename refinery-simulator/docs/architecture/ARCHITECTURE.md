# RDIS Software Architecture Documentation

This document describes the software architecture, modular directory layouts, data flow pipelines, and file descriptions for the **Refinery Decision Intelligence System (RDIS)** proof-of-concept.

---

## 1. System Block Diagram

```text
  +------------------+
  |    User Web UI   |
  +------------------+
        |        ^
  (POST Query) (Response JSON)
        v        |
  +-----------------------------------------------------+
  |                   Flask Backend                     |
  |  - app.py                                           |
  |  - routes/chatbot.py                                |
  +-----------------------------------------------------+
        |                                         ^
        v                                         |
  +-----------------------------------------------------+
  |                 hybrid_retriever.py                 |
  |  Coordinates classification, retrieval, & execution |
  +-----------------------------------------------------+
     |                   |                   |
     | (Query text)      | (Get latest data) | (Get limits/rules)
     v                   v                   v
  +--------------+   +--------------+    +-----------------------+
  |  intent_     |   |   db_service |    |  simulation_engine.py |
  |  classifier  |   |   (SQLAlchemy|    |  (V2 scaling formulas |
  |  (Regex /    |   |    SQLite)   |    |   & clamping engine)  |
  |   Keywords)  |   +--------------+    +-----------------------+
  +--------------+          |                        |
     |                      v                        v
     |                +--------------+       (Estimated values)
     |                |  refinery.db |               |
     |                +--------------+               v
     |                                       +-------------------+
     v                                       |  slm_service.py   |
  (Inferred Intent)                          |  (Ollama prompt   |
     |                                       |   builder)        |
     |                                       +-------------------+
     |                                               |
     |                                               v
     |                                       +-------------------+
     |                                       |  Ollama Service   |
     |                                       |  (qwen2.5:1.5b)   |
     |                                       +-------------------+
     |                                               |
     |                                               v
     v                                       +-------------------+
  (Validate response formatting & forbidden) | response_         |
  +----------------------------------------> | validator.py      |
                                             +-------------------+
```

---

## 2. Directory Structure

- **`app.py`:** Main entry point initializing the Flask application blueprints, context processors, database mappings, and port configurations.
- **`config.py`:** Configuration profiles storing database URIs, local Ollama URLs, model paths, and capability toggles.
- **`engineering_rules.json`:** JSON knowledge base storing operating limits, warning thresholds, critical thresholds, optimal ranges, and base confidence values for each refinery unit.
- **`simulation_engine.py`:** Standalone chemical process engineering rules engine containing V2 dynamic scaling formulas.
- **`simulation_engine/estimator.py`:** Package-level adapter that dynamically loads and delegates estimations to `simulation_engine.py` at runtime.
- **`chatbot/`**
  - **`intent_classifier.py`:** Parser determining if the query is a KNOWLEDGE, CURRENT_DATA, ANALYSIS, or SIMULATION question.
  - **`hybrid_retriever.py`:** Query controller that maps natural language terms to units, retrieves SQLite metrics, triggers simulation parameters, and handles SLM prompt synthesis.
  - **`parser.py`:** Regex extractor identifying targeted unit codes, metrics, history limits, and aggregation types.
- **`services/`**
  - **`db_service.py`:** Data Access Object (DAO) providing CRUD methods for operational history logging, scenario runs, and chatbot logs.
  - **`slm_service.py`:** Adapter querying local Ollama or HuggingFace pipelines, featuring a Reflective Re-prompting loop.
- **`response_validator.py`:** Regulated filter validating formatting criteria, bullet point inclusion, mandatory section headers, and stripping forbidden phrases.

---

## 3. Core Modules Explained

### 3.1. `intent_classifier.py`
Determines which engine processes the user question:
- Checks if the user asks for plant metrics (`C01`-`C08` queries matching `current`, `show`, `downtime`, etc.) and maps them to `CURRENT_DATA`.
- Checks for dynamic simulation indicator words (`if`, `suppose`, `becomes`, `increase`, `decrease`, etc.) using regex word boundary matching `\bif\b` to prevent false matches on words like `selectivity`. Routes to `SIMULATION`.
- Checks for diagnostic indicator words (`why`, `reason`, `causes`) and routes to `ANALYSIS`.
- Defaults to `KNOWLEDGE`.

### 3.2. `hybrid_retriever.py`
Acts as the central router:
- Under `SIMULATION`, it infers the target unit and parses numeric updates.
- Connects to `db_service` to retrieve the latest baseline row from `refinery.db` for the target unit.
- Calls `estimate_parameters(unit, changes, current_values)` to compute predictions.
- Packages results into the prompt context and queries the SLM.

### 3.3. `simulation_engine.py`
Performs dynamic chemical engineering estimations relative to the active database state. It applies:
- **Throughput scaling:** `flow_ratio = target_flow / current_flow`.
- **Pressure scaling:** Temperature and pressure drop scale with the flow ratio.
- **Yield scaling:** Residence time reductions decrease product yields at high throughput rates.
- Clamps values using rules from `engineering_rules.json` and dynamically calculates a confidence score based on proximity to warning/critical thresholds.

### 3.4. `slm_service.py`
Coordinates communication with the local Ollama LLM (`qwen2.5:1.5b`):
- Wraps context facts and user prompt in a strict prompt template.
- Implements a **Reflective Re-prompting Loop**: if a response fails validation, it parses the failure flags (e.g., missing header, forbidden words) and appends a clear corrective instruction to the prompt before resubmitting (up to 2 times).

### 3.5. `response_validator.py`
Performs compliance checks:
- Rejects answers containing forbidden phrases (e.g. *"it is important to note"* or *"based on available information"*).
- Enforces word limits (<150 words).
- Scans for required section headers (e.g. *Current Conditions*, *Recommended Parameters*, *Expected Changes*, *Operational Risks*, *Recommendations*).

### 3.6. `engineering_rules.json`
Stores static unit constraints:
```json
  "CDU": {
    "throughput_bpd": [1000, 60000],
    "temperature_F": [600, 800],
    "pressure_psi": [10, 60],
    "yield_pct": [70, 95],
    "operating_limits": { ... },
    "warning_thresholds": { ... },
    "critical_thresholds": { ... },
    "recommended_ranges": { ... },
    "base_simulation_confidence": 0.95
  }
```

---

## 4. End-to-End Chatbot Execution Lifecycle

```text
User asks: "If CDU flow becomes 6000 BPD, what should temperature be?"
  |
  v
routes/chatbot.py intercepts HTTP POST
  |
  v
chatbot.intent_classifier detects intent as SIMULATION
  |
  v
chatbot.parser extracts Target Unit = 'CDU', changes = {'throughput_bpd': 6000}
  |
  v
services.db_service fetches latest CDU operational record from SQLite
  |
  v
simulation_engine.py computes V2 scaling:
  - flow_ratio = 6000 / 3200 = 1.875
  - Establishes new Temperature = 708°F, Pressure = 38psi, Yield = 90.1%
  - Compares against warning threshold (55,000 BPD, 760°F). Parameters within bounds.
  - Dynamically calculates Confidence = 0.95
  |
  v
services.slm_service compiles prompt containing rules, data, and constraints
  |
  v
Requests local Ollama model (qwen2.5:1.5b)
  |
  v
Checks response formatting via response_validator.py
  |
  v
[IF FAIL]: Appends validation errors as reflective prompt context and retries
[IF PASS]: Returns JSON output response back to routes/chatbot.py -> Web Page UI
```
