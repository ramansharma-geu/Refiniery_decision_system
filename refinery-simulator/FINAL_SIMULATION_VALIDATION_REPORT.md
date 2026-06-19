# FINAL SIMULATION VALIDATION REPORT

**Validation Execution Date:** Fri Jun 19 09:42:07 2026

## Executive Summary

| Test Suite | Total Tests | Passed | Pass Rate |
| :--- | :---: | :---: | :---: |
| **Current Data Queries** | 20 | 20 | 100.0% |
| **Parameter Explanations** | 20 | 20 | 100.0% |
| **Simulations** | 50 | 50 | 100.0% |
| **OVERALL** | **90** | **90** | **100.0%** |


## Key Success Criteria Verification

- **No Hallucinations in Current Data:** [VERIFIED] All current data questions bypass Ollama/SLM and output database metrics.

- **Database Prepending on Explanation:** [VERIFIED] All parameter explanation queries output exact database values first, followed by the SLM explanation.

- **Realistic Engineering Values:** [VERIFIED] Absolute physical caps on temperature and pressure prevent generating unrealistic scaling values (e.g. >850°F / 454.4°C for CDU).

- **Independent Flow Rate Scaling:** [VERIFIED] Target flow rate increases to 6000 BPH do not scale throughput automatically, which remains at 95000 BPD.

- **Correct Target Extraction:** [VERIFIED] Evaluated query 'from 3767 to 6000' correctly outputs target flow = 6000 BPH, resolving current/target inversion.


## Detailed Results

### Phase 1: Current-Data Queries

| # | Question | LLM Bypassed | Clean DB Values | Status | Reason |
| :--- | :--- | :---: | :---: | :---: | :--- |
| 1 | Show current CDU parameters. | Yes | Yes | **PASS** | Pass |
| 2 | Show CDU flow rate. | Yes | Yes | **PASS** | Pass |
| 3 | Show FCC temperature. | Yes | Yes | **PASS** | Pass |
| 4 | Show hydrotreater pressure. | Yes | Yes | **PASS** | Pass |
| 5 | Show VDU throughput. | Yes | Yes | **PASS** | Pass |
| 6 | Show storage terminal utilization. | Yes | Yes | **PASS** | Pass |
| 7 | What is current VDU temperature? | Yes | Yes | **PASS** | Pass |
| 8 | What is current Hydrotreater flow rate? | Yes | Yes | **PASS** | Pass |
| 9 | Which unit has highest throughput? | Yes | Yes | **PASS** | Pass |
| 10 | Which unit has maximum downtime? | Yes | Yes | **PASS** | Pass |
| 11 | Which unit has the highest energy consumption? | Yes | Yes | **PASS** | Pass |
| 12 | What are the current parameters of CDU? | Yes | Yes | **PASS** | Pass |
| 13 | What are the FCC parameters? | Yes | Yes | **PASS** | Pass |
| 14 | Show current Hydrotreater metrics. | Yes | Yes | **PASS** | Pass |
| 15 | Show current VDU parameters. | Yes | Yes | **PASS** | Pass |
| 16 | Show current Storage Terminal parameters. | Yes | Yes | **PASS** | Pass |
| 17 | What are current CDU metrics? | Yes | Yes | **PASS** | Pass |
| 18 | Show the current status of FCC. | Yes | Yes | **PASS** | Pass |
| 19 | Show the current pressure of VDU. | Yes | Yes | **PASS** | Pass |
| 20 | What is the current yield of Hydrotreater? | Yes | Yes | **PASS** | Pass |

### Phase 2: Parameter Explanation Queries

| # | Question | DB Prepend First | Status | Reason |
| :--- | :--- | :---: | :---: | :--- |
| 1 | Explain current FCC parameters. | Yes | **PASS** | Pass |
| 2 | Explain CDU parameters. | Yes | **PASS** | Pass |
| 3 | Explain current CDU parameters. | Yes | **PASS** | Pass |
| 4 | Explain VDU parameters. | Yes | **PASS** | Pass |
| 5 | Explain current VDU parameters. | Yes | **PASS** | Pass |
| 6 | Explain Hydrotreater parameters. | Yes | **PASS** | Pass |
| 7 | Explain current Hydrotreater parameters. | Yes | **PASS** | Pass |
| 8 | Explain Storage Terminal parameters. | Yes | **PASS** | Pass |
| 9 | Explain current Storage Terminal parameters. | Yes | **PASS** | Pass |
| 10 | Explain the current parameters of CDU. | Yes | **PASS** | Pass |
| 11 | Explain the current parameters of FCC. | Yes | **PASS** | Pass |
| 12 | Explain the current parameters of VDU. | Yes | **PASS** | Pass |
| 13 | Explain the current parameters of Hydrotreater. | Yes | **PASS** | Pass |
| 14 | Explain the current parameters of Storage Terminal. | Yes | **PASS** | Pass |
| 15 | Explain CDU flow rate. | Yes | **PASS** | Pass |
| 16 | Explain FCC temperature. | Yes | **PASS** | Pass |
| 17 | Explain hydrotreater pressure. | Yes | **PASS** | Pass |
| 18 | Explain VDU throughput. | Yes | **PASS** | Pass |
| 19 | Explain storage terminal utilization. | Yes | **PASS** | Pass |
| 20 | Explain the current metrics of CDU. | Yes | **PASS** | Pass |

### Phase 3: Simulation Queries

| # | Question | Temp Bounds | Press Bounds | Decoupled OK | Target Extracted | Status | Reason |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | If CDU flow rate increases from 3767 to 6000 BPH | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 2 | What happens if CDU throughput increases by 10% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 3 | If CDU temperature rises by 20 degrees | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 4 | What if CDU pressure increases by 5 psi | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 5 | If CDU throughput drops to 70000 BPD | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 6 | What happens if CDU flow rate decreases by 20% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 7 | If CDU feed rate doubles | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 8 | What if CDU throughput increases to 90000 BPD | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 9 | If CDU flow halves what adjustments needed | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 10 | What happens if CDU crude charge increases by 15% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 11 | If FCC throughput increases by 10% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 12 | What happens if FCC catalyst activity drops by 15% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 13 | If FCC flow rate increases to 1500 BPH | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 14 | What if FCC temperature rises by 30 degrees | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 15 | If FCC throughput decreases to 20000 BPD | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 16 | What happens if FCC pressure increases by 10% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 17 | If FCC catalyst ratio increases | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 18 | What if FCC feed rate drops by 25% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 19 | If FCC throughput goes to 30000 BPD | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 20 | What happens if FCC temperature increases by 15% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 21 | If VDU throughput increases by 10% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 22 | What happens if VDU pressure increases by 20% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 23 | If VDU flow rate goes to 1500 BPH | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 24 | What if VDU temperature rises by 25 degrees | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 25 | If VDU throughput decreases to 30000 BPD | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 26 | What happens if VDU vacuum drops | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 27 | If VDU feed rate increases by 5000 BPD | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 28 | What if VDU throughput increases to 43000 BPD | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 29 | If VDU pressure rises what are the risks | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 30 | What happens if VDU flow rate decreases by 15% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 31 | If Hydrotreater throughput increases by 10% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 32 | What happens if Hydrotreater sulfur feed doubles | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 33 | If Hydrotreater flow rate goes to 900 BPH | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 34 | What if Hydrotreater temperature rises by 15 degrees | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 35 | If Hydrotreater throughput decreases to 12000 BPD | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 36 | What happens if Hydrotreater pressure increases by 10% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 37 | If Hydrotreater feed rate increases by 20% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 38 | What if Hydrotreater throughput increases to 22000 BPD | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 39 | If Hydrotreater pressure drops what are the risks | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 40 | What happens if Hydrotreater flow rate decreases by 15% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 41 | If Storage Terminal throughput increases by 10% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 42 | What happens if Storage Terminal utilization reaches 92% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 43 | If Storage Terminal flow rate goes to 5000 BPH | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 44 | What if Storage Terminal capacity increases by 20% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 45 | If Storage Terminal throughput decreases to 90000 BPD | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 46 | What happens if Storage Terminal utilization drops to 50% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 47 | If Storage Terminal flow rate increases by 15% | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 48 | What if Storage Terminal throughput increases to 140000 BPD | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 49 | If Storage Terminal utilization reaches 95% what are the risks | Yes | Yes | Yes | Yes | **PASS** | Pass |
| 50 | What happens if Storage Terminal flow rate decreases by 20% | Yes | Yes | Yes | Yes | **PASS** | Pass |