"""
Failure Testing script for RDIS.
Simulates and evaluates:
1. Empty question
2. Invalid unit
3. Missing database values
4. SQLite database unavailable
5. Ollama model unavailable
6. Corrupted engineering_rules.json
"""
import sys
import os
import json
import shutil
from pathlib import Path

# Add project root to Python path
_ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT_DIR))

from app import create_app
from simulation_engine import estimate_parameters
import simulation_engine

def run_test_case(name, func):
    print(f"\n==================================================")
    print(f"RUNNING TEST: {name}")
    print(f"==================================================")
    try:
        res = func()
        print("RESULT: SUCCESS (No crash)")
        print(f"RESPONSE:\n{res}")
        return True, res
    except Exception as e:
        print("RESULT: FAILED/CRASHED")
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)

def main():
    # Load app context for standard client testing
    app = create_app({
        'TESTING': True,
        'SLM_PROVIDER': 'mock',
        'SQLALCHEMY_DATABASE_URI': f"sqlite:///{_ROOT_DIR / 'refinery.db'}"
    })
    client = app.test_client()

    report = []
    report.append("# RDIS Failure Testing Report\n")
    report.append("This report documents system behavior under extreme failure states, missing database configurations, and network outages.\n")
    report.append("---\n")

    # Test 1: Empty Question
    def test_empty():
        resp = client.post('/chatbot/query', json={'query': ''})
        return f"Status: {resp.status_code}\nData: {resp.get_data(as_text=True)}"
    passed_empty, res_empty = run_test_case("1. Empty Question", test_empty)
    report.append("## Test 1: Empty Question\n")
    report.append(f"- **Expected Behavior:** API rejects request with HTTP 400 and clear error message.\n")
    report.append(f"- **Observed Behavior:**\n```\n{res_empty}\n```\n")
    report.append(f"- **Result:** {'**PASS**' if passed_empty and '400' in res_empty else '**FAIL**'}\n\n---\n")

    # Test 2: Invalid Unit
    def test_invalid_unit():
        # A simulation query with a garbage unit code
        resp = client.post('/chatbot/query', json={'query': "If XYZ throughput increases by 10%, what happens?"})
        return f"Status: {resp.status_code}\nData: {resp.get_data(as_text=True)}"
    passed_invalid, res_invalid = run_test_case("2. Invalid Unit", test_invalid_unit)
    report.append("## Test 2: Invalid Unit in Simulation Query\n")
    report.append(f"- **Expected Behavior:** System defaults to CDU or handles invalid unit gracefully without crashing.\n")
    report.append(f"- **Observed Behavior:**\n```\n{res_invalid}\n```\n")
    report.append(f"- **Result:** {'**PASS**' if passed_invalid else '**FAIL**'}\n\n---\n")

    # Test 3: Missing Database Values
    def test_missing_db_values():
        # Call estimate_parameters directly with empty current_values
        res = estimate_parameters("CDU", {"throughput_bpd": 5000}, current_values=None)
        return json.dumps(res, indent=2)
    passed_missing_db, res_missing_db = run_test_case("3. Missing Database Values", test_missing_db_values)
    report.append("## Test 3: Missing Database Values in Simulation Engine\n")
    report.append(f"- **Expected Behavior:** Simulation engine falls back to midpoint values from the engineering rules config.\n")
    report.append(f"- **Observed Behavior:**\n```\n{res_missing_db}\n```\n")
    report.append(f"- **Result:** {'**PASS**' if passed_missing_db and 'Recommended Parameters' in res_missing_db else '**FAIL**'}\n\n---\n")

    # Test 4: SQLite Database Unavailable
    def test_sqlite_unavailable():
        # Initialize app with a non-existent database file path and try to run query
        bad_app = create_app({
            'TESTING': True,
            'SLM_PROVIDER': 'ollama',
            'SQLALCHEMY_DATABASE_URI': "sqlite:////nonexistent_dir/refinery.db"
        })
        bad_client = bad_app.test_client()
        resp = bad_client.post('/chatbot/query', json={'query': "Show CDU flow rate."})
        return f"Status: {resp.status_code}\nData: {resp.get_data(as_text=True)}"
    passed_db_unavail, res_db_unavail = run_test_case("4. SQLite Database Unavailable", test_sqlite_unavailable)
    report.append("## Test 4: SQLite Database Unavailable\n")
    report.append(f"- **Expected Behavior:** App handles SQLAlchemy query error gracefully and returns a database error response rather than crashing.\n")
    report.append(f"- **Observed Behavior:**\n```\n{res_db_unavail}\n```\n")
    report.append(f"- **Result:** {'**PASS**' if passed_db_unavail and '500' in res_db_unavail else '**FAIL**'}\n\n---\n")

    # Test 5: Ollama Unavailable
    def test_ollama_unavailable():
        # Set Ollama URL to a dead port
        bad_app = create_app({
            'TESTING': True,
            'SLM_PROVIDER': 'ollama',
            'OLLAMA_URL': "http://localhost:9999/api/generate",
            'SQLALCHEMY_DATABASE_URI': f"sqlite:///{_ROOT_DIR / 'refinery.db'}"
        })
        bad_client = bad_app.test_client()
        resp = bad_client.post('/chatbot/query', json={'query': "What is CDU?"})
        return f"Status: {resp.status_code}\nData: {resp.get_data(as_text=True)}"
    passed_ollama_unavail, res_ollama_unavail = run_test_case("5. Ollama Model Service Unavailable", test_ollama_unavailable)
    report.append("## Test 5: Ollama Model Service Unavailable\n")
    report.append(f"- **Expected Behavior:** LLM service queries fail connection timeout; system falls back to high-fidelity domain mock response without crashing.\n")
    report.append(f"- **Observed Behavior:**\n```\n{res_ollama_unavail}\n```\n")
    report.append(f"- **Result:** {'**PASS**' if passed_ollama_unavail and 'CDU' in res_ollama_unavail else '**FAIL**'}\n\n---\n")

    # Test 6: Corrupted engineering_rules.json
    def test_corrupted_rules():
        # Backup engineering_rules.json
        rules_path = _ROOT_DIR / 'engineering_rules.json'
        backup_path = _ROOT_DIR / 'engineering_rules.json.bak'
        shutil.copyfile(rules_path, backup_path)
        
        try:
            # Corrupt the file
            rules_path.write_text("invalid json { content }")
            
            # Reload rules or force import
            import importlib
            importlib.reload(simulation_engine)
            
            # Run simulation query
            res = estimate_parameters("CDU", {"throughput_bpd": 5000}, current_values=None)
            return json.dumps(res, indent=2)
        finally:
            # Restore backup
            shutil.copyfile(backup_path, rules_path)
            os.remove(backup_path)
            importlib.reload(simulation_engine)

    passed_rules_corrupt, res_rules_corrupt = run_test_case("6. Corrupted engineering_rules.json", test_corrupted_rules)
    report.append("## Test 6: Corrupted engineering_rules.json\n")
    report.append(f"- **Expected Behavior:** Simulation engine handles decoding exception, falls back to empty dictionary, and applies base scaling without crashing.\n")
    report.append(f"- **Observed Behavior:**\n```\n{res_rules_corrupt}\n```\n")
    report.append(f"- **Result:** {'**PASS**' if passed_rules_corrupt and 'Recommended Parameters' in res_rules_corrupt else '**FAIL**'}\n\n---\n")

    # Write report
    report_path = _ROOT_DIR / 'FAILURE_TEST_REPORT.md'
    report_path.write_text("\n".join(report))
    print(f"\nWritten {report_path}")

if __name__ == '__main__':
    main()
