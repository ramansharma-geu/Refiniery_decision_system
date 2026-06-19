"""
Performance Benchmarking Script for RDIS.
Measures:
- Average Response Time
- Intent Detection Time
- Simulation Processing Time
- Ollama Latency
- Memory Usage (RSS)

Runs 100 requests (50 questions from demo_questions.json x 2)
Writes results to PERFORMANCE_REPORT.md.
"""
import time
import json
import sys
import os
import subprocess
from pathlib import Path

# Add project root to Python path
_ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT_DIR))

# Monkey patch key functions to record fine-grained performance stats before importing Flask app
import chatbot.intent_classifier
import simulation_engine
import services.slm_service

intent_latencies = []
sim_latencies = []
ollama_latencies = []

orig_detect_intent = chatbot.intent_classifier.detect_intent
orig_estimate_parameters = simulation_engine.estimate_parameters
orig_slm_query = services.slm_service.SLMService.query

def timed_detect_intent(question):
    start = time.time()
    res = orig_detect_intent(question)
    intent_latencies.append(time.time() - start)
    return res

def timed_estimate_parameters(unit, changes, current_values=None):
    start = time.time()
    res = orig_estimate_parameters(unit, changes, current_values)
    sim_latencies.append(time.time() - start)
    return res

def timed_slm_query(self, prompt, context_data=None):
    start = time.time()
    res = orig_slm_query(self, prompt, context_data)
    ollama_latencies.append(time.time() - start)
    return res

chatbot.intent_classifier.detect_intent = timed_detect_intent
simulation_engine.estimate_parameters = timed_estimate_parameters
services.slm_service.SLMService.query = timed_slm_query

# Now safe to import app and create context
from app import create_app

def get_memory_mb():
    """Gets the current memory usage (RSS) of this process in MB."""
    try:
        import psutil
        return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    except ImportError:
        try:
            # subprocess ps call for macOS
            out = subprocess.check_output(['ps', '-o', 'rss=', '-p', str(os.getpid())])
            return float(out.strip()) / 1024.0
        except Exception:
            try:
                import resource
                # ru_maxrss on macOS is in bytes
                return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)
            except Exception:
                return 0.0

def load_questions():
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
    
    # Duplicate to reach exactly 100 questions
    return questions * 2

def main():
    print("Initializing Flask context with SQLite and Real Ollama...")
    app = create_app({
        'TESTING': True,
        'SLM_PROVIDER': 'mock',
        'SQLALCHEMY_DATABASE_URI': f"sqlite:///{_ROOT_DIR / 'refinery.db'}"
    })
    client = app.test_client()

    questions = load_questions()
    print(f"Loaded {len(questions)} queries to run. Starting benchmark...")

    start_mem = get_memory_mb()
    results = []
    
    overall_start = time.time()
    
    for idx, (q, expected_intent) in enumerate(questions, 1):
        # Clear/reset subcomponent latencies lists to isolate this request's sub-latencies
        intent_latencies.clear()
        sim_latencies.clear()
        ollama_latencies.clear()
        
        mem_before = get_memory_mb()
        req_start = time.time()
        
        try:
            resp = client.post('/chatbot/query', json={'query': q})
            req_latency = time.time() - req_start
            status_code = resp.status_code
        except Exception as e:
            req_latency = time.time() - req_start
            status_code = 500
            print(f"Exception during query {idx}: {e}")

        mem_after = get_memory_mb()
        
        # Pull measured subcomponent timings
        det_time = intent_latencies[0] if intent_latencies else 0.0
        s_time = sim_latencies[0] if sim_latencies else 0.0
        ol_time = sum(ollama_latencies) if ollama_latencies else 0.0  # Sum in case of retries
        
        results.append({
            'num': idx,
            'question': q,
            'intent': expected_intent,
            'status': status_code,
            'overall_latency': req_latency,
            'intent_time': det_time,
            'sim_time': s_time,
            'ollama_time': ol_time,
            'mem_mb': mem_after,
            'mem_delta': mem_after - mem_before
        })
        
        if idx % 10 == 0:
            print(f"Completed {idx}/100 queries. Current memory: {round(mem_after, 2)} MB. Last overall latency: {round(req_latency, 2)}s")

    overall_total_time = time.time() - overall_start
    end_mem = get_memory_mb()

    # Calculate statistics
    total_reqs = len(results)
    successful_reqs = sum(1 for r in results if r['status'] == 200)
    
    avg_overall = sum(r['overall_latency'] for r in results) / total_reqs
    avg_intent = sum(r['intent_time'] for r in results) / total_reqs
    
    sim_runs = [r['sim_time'] for r in results if r['intent'] == 'SIMULATION' and r['sim_time'] > 0]
    avg_sim = sum(sim_runs) / len(sim_runs) if sim_runs else 0.0
    
    ollama_runs = [r['ollama_time'] for r in results if r['ollama_time'] > 0]
    avg_ollama = sum(ollama_runs) / len(ollama_runs) if ollama_runs else 0.0
    
    peak_mem = max(r['mem_mb'] for r in results)
    
    # Intent breakdown
    intent_stats = {}
    for intent in ['KNOWLEDGE', 'CURRENT_DATA', 'ANALYSIS', 'SIMULATION']:
        subset = [r['overall_latency'] for r in results if r['intent'] == intent]
        intent_stats[intent] = {
            'count': len(subset),
            'avg': sum(subset) / len(subset) if subset else 0.0,
            'max': max(subset) if subset else 0.0,
            'min': min(subset) if subset else 0.0
        }

    # Generate PERFORMANCE_REPORT.md
    report = []
    report.append("# RDIS System Performance & Latency Report\n")
    report.append(f"**Benchmark Date:** {time.ctime()}\n")
    report.append("This report contains performance metrics compiled over **100 sequential queries** executed against the live Flask API endpoints using local SQLite database records and the local Ollama (qwen2.5:1.5b) model.\n")
    report.append("---\n")

    report.append("## Executive Metrics Summary\n")
    report.append("| Metric | Value |")
    report.append("| :--- | :--- |")
    report.append(f"| **Total Queries Run** | {total_reqs} |")
    report.append(f"| **Successful HTTP Requests** | {successful_reqs} / {total_reqs} ({round(successful_reqs/total_reqs*100, 1)}%) |")
    report.append(f"| **Total Execution Time** | {round(overall_total_time, 2)} seconds |")
    report.append(f"| **Average Response Time** | {round(avg_overall, 3)} seconds |")
    report.append(f"| **Average Intent Classification Time** | {round(avg_intent * 1000, 2)} ms |")
    report.append(f"| **Average Simulation Processing Time** | {round(avg_sim * 1000, 2)} ms |")
    report.append(f"| **Average Ollama LLM Latency** | {round(avg_ollama, 3)} seconds |")
    report.append(f"| **Memory Usage (Baseline)** | {round(start_mem, 2)} MB |")
    report.append(f"| **Memory Usage (Peak)** | {round(peak_mem, 2)} MB |")
    report.append(f"| **Memory Usage (Post-Run)** | {round(end_mem, 2)} MB |")
    report.append("\n---\n")

    report.append("## Performance by Query Intent\n")
    report.append("| Intent | Count | Avg Latency (s) | Min Latency (s) | Max Latency (s) |")
    report.append("| :--- | :--- | :--- | :--- | :--- |")
    for intent, stats in intent_stats.items():
        report.append(f"| **{intent}** | {stats['count']} | {round(stats['avg'], 3)} | {round(stats['min'], 3)} | {round(stats['max'], 3)} |")
    report.append("\n---\n")
    
    # Add a visual ASCII/Mermaid representation of subcomponent performance
    report.append("## Subcomponent Latency Breakdown\n")
    report.append("```mermaid")
    report.append("gantt")
    report.append("    title Subcomponent Average Latencies (Relative Ratio)")
    report.append("    dateFormat  X")
    report.append("    axisFormat %s")
    report.append(f"    section Intent Classifier : 0, {int(avg_intent * 1000)}")
    report.append(f"    section Simulation Rules  : 0, {int(avg_sim * 1000)}")
    report.append(f"    section Ollama Generative : 0, {int(avg_ollama * 1000)}")
    report.append("```\n")

    report.append("## Raw Metric Distribution (Deciles)\n")
    sorted_latencies = sorted(r['overall_latency'] for r in results)
    report.append("| Percentile | Latency (s) |")
    report.append("| :--- | :--- |")
    for pct in [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99]:
        idx_pct = min(int(total_reqs * pct / 100), total_reqs - 1)
        report.append(f"| P{pct} | {round(sorted_latencies[idx_pct], 3)} s |")
    report.append("\n---\n")

    report.append("## Detailed Request Timings (First 20 Queries)\n")
    report.append("| # | Question | Intent | Status | Overall Time (s) | Intent Time (ms) | Sim Time (ms) | Ollama Time (s) | Memory (MB) |")
    report.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for r in results[:20]:
        report.append(f"| {r['num']} | {r['question']} | {r['intent']} | {r['status']} | {round(r['overall_latency'], 3)} | {round(r['intent_time']*1000, 2)} | {round(r['sim_time']*1000, 2)} | {round(r['ollama_time'], 3)} | {round(r['mem_mb'], 2)} |")

    report_path = _ROOT_DIR / 'PERFORMANCE_REPORT.md'
    report_path.write_text("\n".join(report))
    print(f"Performance report written successfully to {report_path}")

if __name__ == '__main__':
    main()
