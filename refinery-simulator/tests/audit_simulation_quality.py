"""
Simulation Quality Audit Script.
Runs 50 dynamic simulation questions including extreme parameters:
- Extreme low flow
- Extreme high flow
- High pressure
- Low pressure
- High sulfur
- High tank utilization
Generates SIMULATION_AUDIT_REPORT.md.
"""
import sys
import time
import json
from pathlib import Path

# Add project root to Python path
_ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT_DIR))

from app import create_app

def generate_50_simulation_questions():
    questions = []
    
    # 1. CDU Scenarios (10 questions)
    questions.append("If CDU feed drops to 500 BPD, what are the recommended parameters?")
    questions.append("If CDU feed increases to 60000 BPD, what are the flooding consequences?")
    questions.append("If CDU pressure drops to 12 psi, what happens to fractional yields?")
    questions.append("If CDU temperature rises to 790 °F, what is the coking risk?")
    questions.append("If CDU feed API gravity drops by 6 points, what changes are required?")
    questions.append("If CDU throughput halves, what happens to the furnace duty?")
    questions.append("If CDU temperature drops by 50°F, what happens to yield?")
    questions.append("If CDU pressure rises by 25%, what are the consequences?")
    questions.append("If CDU throughput is 45000 BPD, what are the recommended parameters?")
    questions.append("If CDU temperature is 750 °F, what are the risks?")

    # 2. VDU Scenarios (10 questions)
    questions.append("If VDU throughput drops to 1000 BPD, what happens to vacuum tower vapor flow?")
    questions.append("If VDU throughput increases to 28000 BPD, what are the vacuum consequences?")
    questions.append("If VDU pressure rises to 1.8 psi, what happens to gas oil recovery?")
    questions.append("If VDU pressure drops to 0.4 psi, what are the mechanical risks?")
    questions.append("If VDU feed increases by 25%, what are the vacuum system consequences?")
    questions.append("If VDU temperature is 780 °F, what is the thermal cracking risk?")
    questions.append("If VDU vacuum drops to 24 inHg, what adjustments are needed?")
    questions.append("If VDU throughput halves, what happens to the ejector load?")
    questions.append("If VDU pressure increases by 30%, what happens to distillation yield?")
    questions.append("If VDU feed is 22000 BPD, what are the recommended parameters?")

    # 3. FCC Scenarios (10 questions)
    questions.append("If FCC throughput drops to 5000 BPD, what is the riser residence time impact?")
    questions.append("If FCC throughput increases to 38000 BPD, what is the catalyst circulation limit?")
    questions.append("If FCC reactor temperature rises to 1045 °F, what is the gasoline yield impact?")
    questions.append("If FCC reactor temperature drops by 30°C, what happens to yield?")
    questions.append("If FCC catalyst ratio drops by 10%, what adjustments are needed?")
    questions.append("If FCC catalyst activity drops by 15%, what is the yield penalty?")
    questions.append("If FCC feed becomes 35000 BPD, what is the impact on gasoline yield?")
    questions.append("If FCC pressure rises by 20%, what is the regenerator risk?")
    questions.append("If FCC riser temperature is 960 °F, what is the under-cracking risk?")
    questions.append("If FCC catalyst ratio reaches 0.19, what are the recommended parameters?")

    # 4. Hydrotreater Scenarios (10 questions)
    questions.append("If Hydrotreater throughput drops to 2000 BPD, what is the channeling risk?")
    questions.append("If Hydrotreater throughput increases to 28000 BPD, what is the HDS bottleneck impact?")
    questions.append("If Hydrotreater reactor pressure exceeds 1100 psi, what are the limits?")
    questions.append("If Hydrotreater sulfur feed doubles, what operating changes are required?")
    questions.append("If Hydrotreater sulfur load increases to 3.0x, what is the pressure drop?")
    questions.append("If Hydrotreater hydrogen rate drops to 150 norm, what is the catalyst coke rate?")
    questions.append("If Hydrotreater temperature rises to 760 °F, what is the runaway risk?")
    questions.append("If Hydrotreater feed increases by 20%, what hydrogen rate is recommended?")
    questions.append("If Hydrotreater pressure is 650 psi, what are the desulfurization risks?")
    questions.append("If Hydrotreater catalyst is deactivated, what temperature adjustment is needed?")

    # 5. Storage Terminal Scenarios (10 questions)
    questions.append("If Storage Terminal tank utilization reaches 95%, what are the operational risks?")
    questions.append("If Storage Terminal tank utilization drops to 5%, what are the feed continuity risks?")
    questions.append("If Storage Terminal utilization reaches 92%, what is the confidence score?")
    questions.append("If Storage Terminal crude receipt surges to 48000 BPD, what are the limits?")
    questions.append("If Storage Terminal tank utilization is 90%, what transfer limit is recommended?")
    questions.append("If Storage Terminal has a pump outage dropping transfer limit by 50%, what is the bottleneck?")
    questions.append("If Storage Terminal tank utilization is 15%, what are the buffer capacities?")
    questions.append("If Storage Terminal throughput is 42000 BPD, what are the recommended parameters?")
    questions.append("If Storage Terminal tank utilization rises from 60% to 88%, what is the safety status?")
    questions.append("If Storage Terminal transfer limit drops to 2000 BPD, what are the downstream unit impacts?")
    
    return questions

def main():
    print("Initializing Flask context...")
    app = create_app({
        'TESTING': True,
        'SLM_PROVIDER': 'mock',
        'SQLALCHEMY_DATABASE_URI': f"sqlite:///{_ROOT_DIR / 'refinery.db'}"
    })
    client = app.test_client()

    questions = generate_50_simulation_questions()
    results = []

    print(f"Running {len(questions)} simulation questions...")
    for idx, q in enumerate(questions, 1):
        print(f"[{idx}/50] Querying: '{q}'")
        start = time.time()
        try:
            resp = client.post('/chatbot/query', json={'query': q})
            latency = time.time() - start
            if resp.status_code == 200:
                data = resp.get_json()
                chatbot_response = data.get('response', '')
                db_data = data.get('db_data', [])
                llm_called = data.get('llm_called', False)
            else:
                chatbot_response = f"HTTP Error {resp.status_code}"
                db_data = []
                llm_called = False
        except Exception as e:
            latency = time.time() - start
            chatbot_response = f"Exception: {e}"
            db_data = []
            llm_called = False

        results.append({
            'num': idx,
            'question': q,
            'response': chatbot_response,
            'db_data': db_data,
            'llm_called': llm_called,
            'latency': latency
        })

    # Generate SIMULATION_AUDIT_REPORT.md
    report = []
    report.append("# RDIS Simulation Quality Audit Report\n")
    report.append(f"**Audit Date:** {time.ctime()}\n")
    report.append("This report reviews the simulation engine outputs across 50 extreme process scenarios (underloading, overloading, high backpressures, catalyst deactivations, and tank constraints) to audit parameter accuracy, safety warnings, and database compliance.\n")
    report.append("---\n")

    report.append("## Executive Quality Summary\n")
    # We check if responses contain key headers or sections
    headers_ok = 0
    risk_warnings_ok = 0
    db_values_used = 0
    for r in results:
        resp_lower = r['response'].lower()
        if "recommended parameters" in resp_lower or "expected changes" in resp_lower:
            headers_ok += 1
        if "risk" in resp_lower or "flooding" in resp_lower or "runaway" in resp_lower or "coking" in resp_lower or "overflow" in resp_lower or "limit" in resp_lower:
            risk_warnings_ok += 1
        if r['db_data']:
            db_values_used += 1

    report.append(f"| Quality Metric | Score / count | Percentage |")
    report.append(f"| :--- | :--- | :--- |")
    report.append(f"| **Total Audit Scenarios Executed** | {len(results)} | 100.0% |")
    report.append(f"| **Structured Header Compliance** | {headers_ok} / {len(results)} | {round(headers_ok/len(results)*100, 1)}% |")
    report.append(f"| **Safety/Risk Warning Compliance** | {risk_warnings_ok} / {len(results)} | {round(risk_warnings_ok/len(results)*100, 1)}% |")
    report.append(f"| **Active Database Metric Binding** | {db_values_used} / {len(results)} | {round(db_values_used/len(results)*100, 1)}% |")
    report.append("\n---\n")

    report.append("## Detailed Audit Log\n")
    report.append("| # | Question | Database Binding | Latency (s) | Structural Headers | Risks Addressed |")
    report.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for r in results:
        db_bind = "Yes" if r['db_data'] else "No"
        resp_lower = r['response'].lower()
        struct_headers = "Yes" if ("recommended parameters" in resp_lower or "expected changes" in resp_lower) else "No"
        
        risks_found = []
        for word in ["flooding", "coking", "runaway", "overflow", "weeping", "outage", "bottleneck"]:
            if word in resp_lower:
                risks_found.append(word)
        risks_str = ", ".join(risks_found) if risks_found else "nominal"

        report.append(f"| {r['num']} | {r['question']} | {db_bind} | {round(r['latency'], 2)} | {struct_headers} | {risks_str} |")

    report.append("\n---\n")
    report.append("## Detailed Audit Outputs (First 10 Cases)\n")
    for r in results[:10]:
        report.append(f"### Scenario {r['num']}: {r['question']}\n")
        report.append(f"- **DB Metrics Linked:** `{'Yes' if r['db_data'] else 'No'}`\n")
        report.append(f"- **LLM Called:** `{r['llm_called']}`\n")
        report.append(f"- **Response:**\n\n```\n{r['response']}\n```\n")
        report.append("---\n")

    report_path = _ROOT_DIR / 'SIMULATION_AUDIT_REPORT.md'
    report_path.write_text("\n".join(report))
    print(f"Simulation audit report written to {report_path}")

if __name__ == '__main__':
    main()
