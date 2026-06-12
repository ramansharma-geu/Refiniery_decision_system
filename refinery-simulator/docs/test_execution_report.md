# RDIS Test Execution Report

This document records the automated and manual verification results for the Refinery Decision Intelligence System (RDIS).

---

## 1. System Environment
- **Operating System:** macOS (Mac OS X 14.x+)
- **Python Version:** 3.9.6 / 3.12.x
- **Flask Version:** 3.0.3
- **SQLite Version:** 3.43.2+
- **SQLAlchemy Version:** 2.0.30

---

## 2. Database Verification Results

Database builds and seeding completed successfully. The seeded `refinery.db` contains the following metrics:

### Table Row Counts
| Table Name | Description | Row Count | Status |
|---|---|---|---|
| `users` | Console operators | 4 | PASS |
| `refinery_units` | Process units | 5 | PASS |
| `operational_history` | Historical logs (200 records per unit) | 1,000 | PASS |
| `scenarios` | Rules profiles templates | 5 | PASS |
| `scenario_parameters` | Quantitative delta values | 15 | PASS |
| `simulation_runs` | Logs of simulation executions | 1+ (Dynamic) | PASS |
| `simulation_results` | Parameter details for runs | 35+ (Dynamic) | PASS |
| `ai_recommendations` | safety actions generated | 5+ (Dynamic) | PASS |
| `chatbot_logs` | Chat logs registry | 2+ (Dynamic) | PASS |
| `reports` | Compiled file sheets index | 1+ (Dynamic) | PASS |

---

## 3. Web Route & Controller Testing

We verified all major Flask controllers return HTTP `200 OK` status and output correct Jinja templates:

| Route Pattern | HTTP Method | Expected Output | Status |
|---|---|---|---|
| `/` | GET | `dashboard.html` showing KPIs and Chart.js canvases | `200 OK` |
| `/units` | GET | `units.html` showing 5 active refinery unit cards | `200 OK` |
| `/units/<code_upper>` | GET | `unit_details.html` showing time-series data for a single unit | `200 OK` |
| `/history` | GET | `history.html` paginating operational records table | `200 OK` |
| `/scenarios` | GET | `scenarios.html` listing simulation templates | `200 OK` |
| `/scenarios/<id>/run` | POST | Triggers rule execution and redirects to results | `302 Redirect` |
| `/simulation/results/<run_id>`| GET | `simulation_results.html` showing risk levels and advice | `200 OK` |
| `/chatbot` | GET | `chatbot.html` conversation log portal | `200 OK` |
| `/chatbot/query` | POST | JSON response with data lists and SLM reasoning | `200 OK` |
| `/reports` | GET | `reports.html` showing PDF/CSV download buttons | `200 OK` |
| `/settings` | GET | `settings.html` configuration profile form | `200 OK` |

---

## 4. Hybrid Chatbot Testing

We tested the chatbot using the default **Mock offline SLM service** for three query types:

### Case A: Database-First Retrieval
- **Question:** *"What is the current throughput of CDU?"*
- **Database Context Retrieved:** `{'CDU': {'throughput': 80000.0, ...}}`
- **System Answer:** *"The current throughput of CDU is 80,000.0 bbl/day. This represents normal operational load..."*
- **Status:** PASS

### Case B: SLM Fallback
- **Question:** *"What is FCC?"*
- **Database Context Retrieved:** None
- **System Answer:** *"FCC stands for Fluid Catalytic Cracking Unit. It is one of the most critical conversion units..."*
- **Status:** PASS

### Case C: Hybrid Response
- **Question:** *"What is current FCC throughput and explain its significance?"*
- **Database Context Retrieved:** `{'FCC': {'throughput': 28000.0, ...}}`
- **System Answer:** *"According to current database records, FCC is operating at 28,000.0 bbl/day... Fluid Catalytic Cracking takes vacuum gas oils and cracks them into gasoline..."*
- **Status:** PASS

---

## 5. Simulation Testing Logs

We executed simulation triggers to verify the mathematical models:

| Scenario Type | Critical Inputs | Primary Outputs | Primary Bottleneck | Risk Score | Status |
|---|---|---|---|---|---|
| **FCC Shutdown** | FCC Throughput drops by 100% | FCC Throughput = 0. VDU Throughput -40%. | `FCC` | 85 | PASS |
| **Throughput Surge**| Refinery charge +10% | CDU Throughput +10%, Hydrotreater Throughput +10% | `Hydrotreater` (Exceeds 25k cap) | 55 | PASS |
| **Maintenance Delay**| CDU delay triggers | CDU downtime increases by 6.0 hours | `CDU` | 70 | PASS |
| **Energy Reduction** | Grid curtailment -20% | All unit throughputs -20%, downtime +4.0 hrs | `Global Power Grid`| 60 | PASS |
| **Demand Increase** | Demand surge | Units pushed +5-8% | `Storage Terminal` | 40 | PASS |

---

## 6. Bugs Discovered & Resolved

During development and automated test runs, the following issues were discovered and resolved:

1. **Typos in Imports:**
   - *Discovery:* Test suite failed with `ImportError: cannot import name 'render_name' from 'flask'` in `routes/dashboard.py`.
   - *Fix:* Corrected import statement to import only `render_template` and `jsonify`.
2. **Database Session Contamination in Tests:**
   - *Discovery:* Integration tests threw `sqlite3.IntegrityError: UNIQUE constraint failed: refinery_units.code` when trying to seed units because it wrote to the physical database file on disk instead of in-memory.
   - *Fix:* Refactored `create_app()` inside `app.py` to accept configuration override dictionaries, allowing the test suite to push an isolated, blank in-memory database.
3. **Template Syntax Errors:**
   - *Discovery:* Jinja failed to compile templates because of plain text `endfor` tags.
   - *Fix:* Replaced plain text `endfor` lines with correct Jinja block tags `{% endfor %}` in `scenarios.html` and `simulation_results.html`.
4. **Intent Classifier Mappings:**
   - *Discovery:* General questions containing unit names (e.g. "What is FCC?") were incorrectly classified as `query_current` instead of `general`.
   - *Fix:* Updated the router inside `chatbot/parser.py` to skip `query_current` if the query contains informational words like "what is", "why", or "explain" without mapping both a unit and a parameter.

---

## 7. Final Test Summary
- **Total Tests Run:** 5 (covering all system layers)
- **Total Failures:** 0
- **Total Errors:** 0
- **Final QA Status:** **PASS**
