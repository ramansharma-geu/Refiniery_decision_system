# RDIS System Performance & Latency Report

**Benchmark Date:** Fri Jun 19 08:38:11 2026

This report contains performance metrics compiled over **100 sequential queries** executed against the live Flask API endpoints using local SQLite database records and the local Ollama (qwen2.5:1.5b) model.

---

## Executive Metrics Summary

| Metric | Value |
| :--- | :--- |
| **Total Queries Run** | 100 |
| **Successful HTTP Requests** | 100 / 100 (100.0%) |
| **Total Execution Time** | 0.24 seconds |
| **Average Response Time** | 0.002 seconds |
| **Average Intent Classification Time** | 0.01 ms |
| **Average Simulation Processing Time** | 0.01 ms |
| **Average Ollama LLM Latency** | 0.0 seconds |
| **Memory Usage (Baseline)** | 62.7 MB |
| **Memory Usage (Peak)** | 65.81 MB |
| **Memory Usage (Post-Run)** | 65.81 MB |

---

## Performance by Query Intent

| Intent | Count | Avg Latency (s) | Min Latency (s) | Max Latency (s) |
| :--- | :--- | :--- | :--- | :--- |
| **KNOWLEDGE** | 20 | 0.003 | 0.002 | 0.014 |
| **CURRENT_DATA** | 20 | 0.002 | 0.002 | 0.003 |
| **ANALYSIS** | 20 | 0.002 | 0.002 | 0.003 |
| **SIMULATION** | 40 | 0.002 | 0.002 | 0.004 |

---

## Subcomponent Latency Breakdown

```mermaid
gantt
    title Subcomponent Average Latencies (Relative Ratio)
    dateFormat  X
    axisFormat %s
    section Intent Classifier : 0, 0
    section Simulation Rules  : 0, 0
    section Ollama Generative : 0, 0
```

## Raw Metric Distribution (Deciles)

| Percentile | Latency (s) |
| :--- | :--- |
| P10 | 0.002 s |
| P20 | 0.002 s |
| P30 | 0.002 s |
| P40 | 0.002 s |
| P50 | 0.002 s |
| P60 | 0.002 s |
| P70 | 0.002 s |
| P80 | 0.002 s |
| P90 | 0.003 s |
| P95 | 0.003 s |
| P99 | 0.014 s |

---

## Detailed Request Timings (First 20 Queries)

| # | Question | Intent | Status | Overall Time (s) | Intent Time (ms) | Sim Time (ms) | Ollama Time (s) | Memory (MB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | What is CDU? | KNOWLEDGE | 200 | 0.014 | 0.39 | 0.0 | 0.0 | 65.08 |
| 2 | What is VDU? | KNOWLEDGE | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.11 |
| 3 | What is FCC? | KNOWLEDGE | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.16 |
| 4 | Why is Hydrotreater used? | KNOWLEDGE | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.17 |
| 5 | What causes catalyst deactivation? | KNOWLEDGE | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.17 |
| 6 | What is a fractionating column? | KNOWLEDGE | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.17 |
| 7 | What is hydrotreating? | KNOWLEDGE | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.2 |
| 8 | What is catalyst regeneration? | KNOWLEDGE | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.2 |
| 9 | What is debottlenecking? | KNOWLEDGE | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.2 |
| 10 | What is a heat exchanger network? | KNOWLEDGE | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.2 |
| 11 | Show CDU flow rate. | CURRENT_DATA | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.2 |
| 12 | Show FCC temperature. | CURRENT_DATA | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.22 |
| 13 | Which unit has highest throughput? | CURRENT_DATA | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.33 |
| 14 | Which unit has maximum downtime? | CURRENT_DATA | 200 | 0.003 | 0.01 | 0.0 | 0.0 | 65.38 |
| 15 | Show hydrotreater pressure. | CURRENT_DATA | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.39 |
| 16 | Show VDU throughput. | CURRENT_DATA | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.39 |
| 17 | Show storage terminal utilization. | CURRENT_DATA | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.39 |
| 18 | Which unit has the highest energy consumption? | CURRENT_DATA | 200 | 0.003 | 0.01 | 0.0 | 0.0 | 65.41 |
| 19 | What is current VDU temperature? | CURRENT_DATA | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.42 |
| 20 | What is current Hydrotreater flow rate? | CURRENT_DATA | 200 | 0.002 | 0.01 | 0.0 | 0.0 | 65.44 |