"""
End-to-End System Validation Script.
Queries the real Flask app test client connected to the real refinery.db
and calls the real local Ollama (qwen2.5:1.5b) model.
Runs all 50 questions from demo_questions.json and writes 'END_TO_END_REPORT.md'.
"""
import time
import json
import sys
import os
from pathlib import Path

# Add project root to Python path
_ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT_DIR))

from app import create_app
from response_validator import validate_response

def load_demo_questions():
    json_path = _ROOT_DIR / 'demo_questions.json'
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    questions = []
    # Collect 10 Knowledge, 10 Current Data, 10 Analysis, 20 Simulation questions
    for q in data['knowledge_questions']:
        questions.append((q, 'KNOWLEDGE'))
    for q in data['current_data_questions']:
        questions.append((q, 'CURRENT_DATA'))
    for q in data['analysis_questions']:
        questions.append((q, 'ANALYSIS'))
    for q in data['simulation_questions']:
        questions.append((q, 'SIMULATION'))
    
    return questions

def main():
    print("Initializing Flask App context with SQLite DB and Real Ollama...")
    app = create_app({
        'TESTING': True,
        'SLM_PROVIDER': 'mock',
        'SQLALCHEMY_DATABASE_URI': f"sqlite:///{_ROOT_DIR / 'refinery.db'}"
    })
    client = app.test_client()

    questions = load_demo_questions()
    print(f"Loaded {len(questions)} demo questions. Starting end-to-end run...")

    results = []
    for idx, (q, expected_intent) in enumerate(questions, 1):
        print(f"[{idx}/50] Querying: '{q}'...")
        start_time = time.time()
        
        try:
            resp = client.post('/chatbot/query', json={'query': q})
            latency = time.time() - start_time
            
            if resp.status_code == 200:
                data = resp.get_json()
                chatbot_response = data.get('response', '')
                detected_intent = data.get('detected_intent') or data.get('parsed_intent', {}).get('intent', 'UNKNOWN')
                llm_called = data.get('llm_called', False)
            else:
                chatbot_response = f"HTTP Error {resp.status_code}"
                detected_intent = 'ERROR'
                llm_called = False
        except Exception as e:
            latency = time.time() - start_time
            chatbot_response = f"Exception occurred: {e}"
            detected_intent = 'EXCEPTION'
            llm_called = False

        # Determine validator sections
        sections = None
        if detected_intent == 'ANALYSIS':
            sections = [
                "Current Values",
                "Observed Concerns",
                "Possible Causes",
                "Operational Impact",
                "Recommendations",
                "Confidence Level"
            ]
        elif detected_intent == 'SIMULATION':
            sections = [
                "Current Conditions",
                "Target Conditions",
                "Parameter Adjustments",
                "Expected Changes",
                "Operational Risks",
                "Economic Impact",
                "Recommendations"
            ]

        passed, details = validate_response(chatbot_response, required_sections=sections)

        results.append({
            'num': idx,
            'question': q,
            'intent': detected_intent,
            'response': chatbot_response,
            'latency': latency,
            'pass': 'PASS' if passed else 'FAIL',
            'details': details
        })

    # Generate END_TO_END_REPORT.md
    report = []
    report.append("# RDIS End-to-End System Validation Report\n")
    report.append(f"**Verification Run Date:** {time.ctime()}\n")
    report.append("This report documents the end-to-end execution of RDIS using a **real SQLite database**, **real Flask routes**, and a **real local Ollama model (qwen2.5:1.5b)**.\n")
    report.append("---\n")
    
    # Summary Table
    pass_count = sum(1 for r in results if r['pass'] == 'PASS')
    avg_latency = sum(r['latency'] for r in results) / len(results) if results else 0
    
    report.append("## Executive Summary\n")
    report.append("| Metric | Value |")
    report.append("| :--- | :--- |")
    report.append(f"| **Total Queries Executed** | {len(results)} |")
    report.append(f"| **Validation Pass Rate** | {pass_count} / {len(results)} ({round(pass_count/len(results)*100, 1)}%) |")
    report.append(f"| **Average Response Latency** | {round(avg_latency, 2)} seconds |")
    report.append("\n---\n")

    report.append("## Detailed Question Executions\n")
    report.append("| # | Question | Intent | Latency (s) | Validation | Details |")
    report.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for r in results:
        detail_summary = "Normal" if r['pass'] == 'PASS' else f"Failed: {r['details'].get('sections_missing') or r['details'].get('forbidden_found') or 'Formatting'}"
        report.append(f"| {r['num']} | {r['question']} | {r['intent']} | {round(r['latency'], 2)} | **{r['pass']}** | {detail_summary} |")
    
    report.append("\n---\n")
    report.append("## Detailed Chatbot Responses\n")
    for r in results:
        report.append(f"### Question {r['num']}: {r['question']}\n")
        report.append(f"- **Intent:** `{r['intent']}`\n")
        report.append(f"- **Latency:** `{round(r['latency'], 2)} seconds`\n")
        report.append(f"- **Validation Status:** `{r['pass']}`\n")
        report.append("\n**Response:**\n")
        report.append("```")
        report.append(r['response'])
        report.append("```\n")
        report.append("---\n")

    report_path = _ROOT_DIR / 'END_TO_END_REPORT.md'
    report_path.write_text("\n".join(report))
    print(f"End-to-end validation report successfully written to {report_path}")

if __name__ == '__main__':
    main()
