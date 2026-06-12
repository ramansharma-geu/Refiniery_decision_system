# RDIS API Documentation

This document describes the routing architecture, blueprint controllers, and endpoints exposed by the Refinery Decision Intelligence System.

---

## 1. Web Page Controllers (Jinja2 Templates)

These routes handle HTML page rendering and inject standard Jinja2 model contexts.

### Dashboard Routes
- **`GET /`** or **`GET /dashboard`**
  - Renders: `dashboard.html`
  - Injected context: `stats` (dashboard count metrics), `recent_runs` (last 5 runs).

### Units & History Routes
- **`GET /units`**
  - Renders: `units.html`
  - Injected context: `units` (all 5 units configurations), `latest_map` (latest parameters).
- **`GET /units/<string:code>`**
  - Renders: `unit_details.html`
  - Injected context: `unit`, `latest`, `history` (last 30 time-series points).
- **`GET /history`**
  - Renders: `history.html`
  - Arguments: `unit_id` (optional filter), `page` (pagination offset, default `1`).
  - Injected context: `records`, `pagination`, `units`, `selected_unit_id`.

### Scenario Routes
- **`GET /scenarios`**
  - Renders: `scenarios.html`
  - Injected context: `scenarios` (all template profiles), `recent_runs` (simulation logs).
- **`GET /scenarios/create`**
  - Renders: `scenario_form.html` (blank create form).
- **`POST /scenarios/create`**
  - Payload: Form fields (`name`, `type`, `description`).
  - Redirects: `/scenarios` on success.
- **`GET /scenarios/<int:scenario_id>/edit`**
  - Renders: `scenario_form.html` (edit form pre-filled).
- **`POST /scenarios/<int:scenario_id>/edit`**
  - Payload: Form fields (`name`, `description`).
  - Redirects: `/scenarios` on success.
- **`POST /scenarios/<int:scenario_id>/delete`**
  - Redirects: `/scenarios` on success.
- **`POST /scenarios/<int:scenario_id>/run`**
  - Triggers the Core Simulation Engine rules.
  - Redirects: `/simulation/results/<run_id>` on successful execution.
- **`GET /simulation/results/<int:run_id>`**
  - Renders: `simulation_results.html`
  - Injected context: `run`, `grouped_results` (before vs after comparisons grouped by unit).

### Chatbot Routes
- **`GET /chatbot`**
  - Renders: `chatbot.html`
  - Injected context: `logs` (previous conversation logs thread).

### Report Center Routes
- **`GET /reports`**
  - Renders: `reports.html`
  - Injected context: `reports` (metadata catalog list), `runs` (simulation history).
- **`GET /reports/generate/pdf/<int:run_id>`**
  - Compiles PDF report for the run.
  - Redirects: `/reports` on success.
- **`GET /reports/generate/csv/units`**
  - Exports units schema configurations to CSV.
  - Redirects: `/reports` on success.
- **`GET /reports/generate/csv/history`**
  - Exports complete operational log to CSV.
  - Redirects: `/reports` on success.
- **`GET /reports/generate/csv/run/<int:run_id>`**
  - Exports simulation run data parameters comparison to CSV.
  - Redirects: `/reports` on success.
- **`GET /reports/download/<int:report_id>`**
  - Serves the compiled PDF or CSV file from server disk as an attachment download.

### Settings Routes
- **`GET /settings`**
  - Renders: `settings.html`
  - Injected context: `config` (current in-memory SLM configurations).
- **`POST /settings/update`**
  - Payload: Form fields (`slm_provider`, `ollama_url`, `ollama_model`, `hf_model_path`).
  - Redirects: `/settings` on success.

---

## 2. API Endpoints (JSON payloads)

These endpoints provide data to client-side scripts.

### Analytics Data
- **`GET /api/analytics`**
  - Response:
    ```json
    {
      "scenario_distribution": {
        "FCC Shutdown": 2,
        "Throughput Increase (+10%)": 5
      },
      "trends": {
        "CDU": {
          "timestamps": ["06-01", "06-02"],
          "throughput": [80000.0, 81200.0],
          "yield": [92.1, 91.8],
          "energy_consumption": [180.0, 185.0],
          "downtime": [0.0, 0.0]
        }
      }
    }
    ```

### Chatbot Query Process
- **`POST /chatbot/query`**
  - Payload:
    ```json
    {
      "query": "What is the current throughput of CDU?"
    }
    ```
  - Response (Factual database matching):
    ```json
    {
      "response": "According to the database, CDU current throughput is 80,000 bbl/day. This unit processes raw crude...",
      "db_data": [
        {
          "unit_code": "CDU",
          "unit_name": "Crude Distillation Unit",
          "throughput": 80000.0,
          "pressure": 40.0,
          "temperature": 700.0,
          "flow_rate": 3300.0,
          "yield": 92.0,
          "energy_consumption": 180.0,
          "downtime": 0.0,
          "timestamp": "2026-06-12 00:00:00"
        }
      ],
      "llm_called": true,
      "parsed_intent": {
        "intent": "query_current",
        "unit_code": "CDU",
        "parameter": "throughput",
        "limit": 5,
        "extreme_type": null
      }
    }
    ```
