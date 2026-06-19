# RDIS Codebase Software Architecture Audit Report

This report evaluates the software architecture, code quality, performance potential, and reliability of the **Refinery Decision Intelligence System (RDIS)** codebase.

---

## 1. Codebase Overview & Module Directory

The RDIS codebase is structured into clear separation of concerns (web routing, DB access, text parsing, chemical process simulation, SLM querying, and compliance checking):
- **`app.py` & `config.py`**: App initialization and configuration loader.
- **`chatbot/intent_classifier.py`**: Maps keywords to routing pipelines.
- **`chatbot/parser.py`**: Extracts parameters and entities.
- **`chatbot/hybrid_retriever.py`**: Central execution orchestrator.
- **`simulation_engine.py`**: Calculates process estimates using empirical chemical engineering formulas.
- **`services/db_service.py`**: Accesses SQLite operational database.
- **`services/slm_service.py`**: Manages LLM connections and reflective retries.
- **`response_validator.py`**: Performs output compliance checks.

---

## 2. Key Findings & Code Quality Gaps

### 2.1. SLM Service Exception Handling Leak (High Severity)
* **File:** [slm_service.py](file:///Users/shivam/Desktop/refinery_decision_system/refinery-simulator/services/slm_service.py)
* **Issue:** In the `_query_ollama` method, the try-except block catches connection exceptions and sets `last_good_text` to the raw error traceback:
  ```python
  except Exception as e:
      last_good_text = f"Ollama request exception: {e}"
      break
  ```
  Since `last_good_text` is non-empty, the service directly returns this string to the chatbot. This bypasses the mock fallback logic (`_query_mock`), causing raw network or connection exceptions to bubble up directly to the chatbot response (and be displayed in the user interface).
* **Impact:** Leakage of internal infrastructure URLs/ports and very poor user experience (crashes appear as raw Python HTTP pool tracebacks).

### 2.2. Clamping Collapse Bug on Extreme Out-of-Bounds Values (Medium Severity)
* **File:** [simulation_engine.py](file:///Users/shivam/Desktop/refinery_decision_system/refinery-simulator/simulation_engine.py)
* **Issue:** The clamping range calculation logic is vulnerable to range inversion:
  ```python
  low = max(bounds[0], val * (1.0 - tol_pct / 100.0))
  high = min(bounds[1], val * (1.0 + tol_pct / 100.0))
  if low > high:
      low = high
  ```
  If `val` (the calculated parameter value) is significantly above the absolute maximum limit `bounds[1]`, the target low value (`val * 0.98`) will exceed the maximum limit. Consequently, `low` becomes greater than `high`. The safety check `if low > high: low = high` handles this by setting `low = high = bounds[1]`.
* **Impact:** The estimated range collapses to a single point (e.g. `60000.0 - 60000.0` BPD) rather than showing a reasonable margin of tolerance around the clamped max boundary.

### 2.3. Missing Error Handling in `execute_db_query` (Medium Severity)
* **File:** [hybrid_retriever.py](file:///Users/shivam/Desktop/refinery_decision_system/refinery-simulator/chatbot/hybrid_retriever.py)
* **Issue:** Database query execution within `execute_db_query` does not catch raw SQLite/SQLAlchemy exceptions. If the database file is locked, corrupt, or missing tables, the exception is raised directly. While the main endpoint in `chatbot.py` catches general exceptions, the internal query logic is not resilient.
* **Impact:** Leads to unhandled HTTP 500 errors and direct system log writes, exposing system details when simple retries or database connection fallbacks could be attempted.

### 2.4. Basic Substring Matching in Classifier and Parser (Low Severity)
* **Files:** [intent_classifier.py](file:///Users/shivam/Desktop/refinery_decision_system/refinery-simulator/chatbot/intent_classifier.py), [parser.py](file:///Users/shivam/Desktop/refinery_decision_system/refinery-simulator/chatbot/parser.py)
* **Issue:** Intents and parameters are determined using simple keyword checks. For example, if a user queries *"Show the coking history"*, it matches "co**king**" which triggers `KNOWLEDGE` or `SIMULATION` due to partial matching (since `king` is in `coking` and `king` or `coking` matches keywords). Also, substring checks like `'used'` can match `'uses'` or `'user'`.
* **Impact:** False positives during intent mapping for complex conversational phrasing.

---

## 3. Architecture & Code Audit Checklist

| Item Checked | Status | Details |
| :--- | :--- | :--- |
| **Dead Code** | Clean | No large unused modules or function blocks found. |
| **Duplicate Code** | Minor | Unit default midpoints are hardcoded in both `simulation_engine.py` and models, rather than referencing a single module configuration. |
| **Unused Imports** | Clean | Imports are well-scoped. |
| **Circular Imports** | Resolved | The shadowed package `simulation_engine/` was resolved using runtime dynamic reloading, avoiding cycles. |
| **Hardcoded Constants** | Low | Design limits and constants (such as pressure multipliers) are written directly into formulas instead of config maps. |
| **Module Shadowing** | Clean | Resolved in `simulation_engine/estimator.py`. |
| **Performance Bottlenecks** | Moderate | The serial, synchronous Ollama calls with retries block Flask worker threads. An async task queue is recommended for production. |

---

## 4. Recommendations for Next Development Cycle

1. **Fix Exception Handling in SLM Service:** Ensure connection exceptions call the mock fallback service (`_query_mock`) rather than returning the raw traceback message to the UI.
2. **Refactor Clamping Range Logic:** Compute the range bounds *first* using a safe interval, and clamp the resulting range boundaries cleanly without collapsing them to a single point.
3. **Externalize Formula Coefficients:** Move simulation constants (like thermal expansion rates or pressure drop scaling factors) out of `simulation_engine.py` and into the database or `engineering_rules.json`.
