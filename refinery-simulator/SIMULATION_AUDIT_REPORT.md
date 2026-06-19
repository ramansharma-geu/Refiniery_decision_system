# RDIS Simulation Quality Audit Report

**Audit Date:** Fri Jun 19 08:38:04 2026

This report reviews the simulation engine outputs across 50 extreme process scenarios (underloading, overloading, high backpressures, catalyst deactivations, and tank constraints) to audit parameter accuracy, safety warnings, and database compliance.

---

## Executive Quality Summary

| Quality Metric | Score / count | Percentage |
| :--- | :--- | :--- |
| **Total Audit Scenarios Executed** | 50 | 100.0% |
| **Structured Header Compliance** | 50 / 50 | 100.0% |
| **Safety/Risk Warning Compliance** | 50 / 50 | 100.0% |
| **Active Database Metric Binding** | 50 / 50 | 100.0% |

---

## Detailed Audit Log

| # | Question | Database Binding | Latency (s) | Structural Headers | Risks Addressed |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | If CDU feed drops to 500 BPD, what are the recommended parameters? | Yes | 0.02 | Yes | weeping |
| 2 | If CDU feed increases to 60000 BPD, what are the flooding consequences? | Yes | 0.0 | Yes | weeping |
| 3 | If CDU pressure drops to 12 psi, what happens to fractional yields? | Yes | 0.0 | Yes | nominal |
| 4 | If CDU temperature rises to 790 °F, what is the coking risk? | Yes | 0.0 | Yes | nominal |
| 5 | If CDU feed API gravity drops by 6 points, what changes are required? | Yes | 0.0 | Yes | nominal |
| 6 | If CDU throughput halves, what happens to the furnace duty? | Yes | 0.0 | Yes | weeping |
| 7 | If CDU temperature drops by 50°F, what happens to yield? | Yes | 0.0 | Yes | nominal |
| 8 | If CDU pressure rises by 25%, what are the consequences? | Yes | 0.0 | Yes | nominal |
| 9 | If CDU throughput is 45000 BPD, what are the recommended parameters? | Yes | 0.0 | Yes | weeping |
| 10 | If CDU temperature is 750 °F, what are the risks? | Yes | 0.0 | Yes | nominal |
| 11 | If VDU throughput drops to 1000 BPD, what happens to vacuum tower vapor flow? | Yes | 0.0 | Yes | weeping |
| 12 | If VDU throughput increases to 28000 BPD, what are the vacuum consequences? | Yes | 0.0 | Yes | weeping |
| 13 | If VDU pressure rises to 1.8 psi, what happens to gas oil recovery? | Yes | 0.0 | Yes | nominal |
| 14 | If VDU pressure drops to 0.4 psi, what are the mechanical risks? | Yes | 0.0 | Yes | nominal |
| 15 | If VDU feed increases by 25%, what are the vacuum system consequences? | Yes | 0.0 | Yes | nominal |
| 16 | If VDU temperature is 780 °F, what is the thermal cracking risk? | Yes | 0.0 | Yes | nominal |
| 17 | If VDU vacuum drops to 24 inHg, what adjustments are needed? | Yes | 0.0 | Yes | nominal |
| 18 | If VDU throughput halves, what happens to the ejector load? | Yes | 0.0 | Yes | weeping |
| 19 | If VDU pressure increases by 30%, what happens to distillation yield? | Yes | 0.0 | Yes | nominal |
| 20 | If VDU feed is 22000 BPD, what are the recommended parameters? | Yes | 0.0 | Yes | weeping |
| 21 | If FCC throughput drops to 5000 BPD, what is the riser residence time impact? | Yes | 0.0 | Yes | flooding |
| 22 | If FCC throughput increases to 38000 BPD, what is the catalyst circulation limit? | Yes | 0.0 | Yes | flooding |
| 23 | If FCC reactor temperature rises to 1045 °F, what is the gasoline yield impact? | Yes | 0.0 | Yes | nominal |
| 24 | If FCC reactor temperature drops by 30°C, what happens to yield? | Yes | 0.0 | Yes | nominal |
| 25 | If FCC catalyst ratio drops by 10%, what adjustments are needed? | Yes | 0.0 | Yes | nominal |
| 26 | If FCC catalyst activity drops by 15%, what is the yield penalty? | Yes | 0.0 | Yes | nominal |
| 27 | If FCC feed becomes 35000 BPD, what is the impact on gasoline yield? | Yes | 0.0 | Yes | flooding |
| 28 | If FCC pressure rises by 20%, what is the regenerator risk? | Yes | 0.0 | Yes | nominal |
| 29 | If FCC riser temperature is 960 °F, what is the under-cracking risk? | Yes | 0.0 | Yes | nominal |
| 30 | If FCC catalyst ratio reaches 0.19, what are the recommended parameters? | Yes | 0.0 | Yes | nominal |
| 31 | If Hydrotreater throughput drops to 2000 BPD, what is the channeling risk? | Yes | 0.0 | Yes | flooding |
| 32 | If Hydrotreater throughput increases to 28000 BPD, what is the HDS bottleneck impact? | Yes | 0.0 | Yes | flooding |
| 33 | If Hydrotreater reactor pressure exceeds 1100 psi, what are the limits? | Yes | 0.0 | Yes | nominal |
| 34 | If Hydrotreater sulfur feed doubles, what operating changes are required? | Yes | 0.0 | Yes | runaway |
| 35 | If Hydrotreater sulfur load increases to 3.0x, what is the pressure drop? | Yes | 0.0 | Yes | runaway |
| 36 | If Hydrotreater hydrogen rate drops to 150 norm, what is the catalyst coke rate? | Yes | 0.0 | Yes | nominal |
| 37 | If Hydrotreater temperature rises to 760 °F, what is the runaway risk? | Yes | 0.0 | Yes | nominal |
| 38 | If Hydrotreater feed increases by 20%, what hydrogen rate is recommended? | Yes | 0.0 | Yes | flooding |
| 39 | If Hydrotreater pressure is 650 psi, what are the desulfurization risks? | Yes | 0.0 | Yes | runaway |
| 40 | If Hydrotreater catalyst is deactivated, what temperature adjustment is needed? | Yes | 0.0 | Yes | nominal |
| 41 | If Storage Terminal tank utilization reaches 95%, what are the operational risks? | Yes | 0.0 | Yes | overflow |
| 42 | If Storage Terminal tank utilization drops to 5%, what are the feed continuity risks? | Yes | 0.0 | Yes | nominal |
| 43 | If Storage Terminal utilization reaches 92%, what is the confidence score? | Yes | 0.0 | Yes | overflow |
| 44 | If Storage Terminal crude receipt surges to 48000 BPD, what are the limits? | Yes | 0.0 | Yes | overflow |
| 45 | If Storage Terminal tank utilization is 90%, what transfer limit is recommended? | Yes | 0.0 | Yes | overflow |
| 46 | If Storage Terminal has a pump outage dropping transfer limit by 50%, what is the bottleneck? | Yes | 0.0 | Yes | overflow |
| 47 | If Storage Terminal tank utilization is 15%, what are the buffer capacities? | Yes | 0.0 | Yes | nominal |
| 48 | If Storage Terminal throughput is 42000 BPD, what are the recommended parameters? | Yes | 0.0 | Yes | overflow, weeping |
| 49 | If Storage Terminal tank utilization rises from 60% to 88%, what is the safety status? | Yes | 0.0 | Yes | nominal |
| 50 | If Storage Terminal transfer limit drops to 2000 BPD, what are the downstream unit impacts? | Yes | 0.0 | Yes | overflow |

---

## Detailed Audit Outputs (First 10 Cases)

### Scenario 1: If CDU feed drops to 500 BPD, what are the recommended parameters?

- **DB Metrics Linked:** `Yes`

- **LLM Called:** `False`

- **Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Throughput: 12000.0 BPD
• Flow Rate: 500.0 BPH

Parameter Adjustments
• Temperature: 351.1 – 366.2°C
• Pressure: 2.05 – 2.14 bar

Expected Changes
• Reduced vapor velocities in CDU
• Energy consumption -50.0%

Operational Risks
• Tray weeping and poor fractionation

Recommendations
• Adjust reflux ratios and furnace firing
```

---

### Scenario 2: If CDU feed increases to 60000 BPD, what are the flooding consequences?

- **DB Metrics Linked:** `Yes`

- **LLM Called:** `False`

- **Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Throughput: 60000.0 BPD
• Flow Rate: 2500.0 BPH

Parameter Adjustments
• Temperature: 358.9 – 374.2°C
• Pressure: 2.14 – 2.23 bar

Expected Changes
• Reduced vapor velocities in CDU
• Energy consumption -46.1%

Operational Risks
• Tray weeping and poor fractionation

Recommendations
• Adjust reflux ratios and furnace firing
```

---

### Scenario 3: If CDU pressure drops to 12 psi, what happens to fractional yields?

- **DB Metrics Linked:** `Yes`

- **LLM Called:** `False`

- **Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Pressure: 1.42 bar

Parameter Adjustments
• Temperature: 364.5 – 380.1°C
• Pressure: 1.39 – 1.45 bar

Expected Changes
• Energy consumption +0.0%
• CDU parameters within normal operating window

Operational Risks
• No immediate risks identified — monitor during transition

Recommendations
• Maintain routine checks and log metric deltas
```

---

### Scenario 4: If CDU temperature rises to 790 °F, what is the coking risk?

- **DB Metrics Linked:** `Yes`

- **LLM Called:** `False`

- **Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Temperature: 1162.3°C

Parameter Adjustments
• Temperature: 1138.7 – 1185.9°C
• Pressure: 2.21 – 2.3 bar

Expected Changes
• Energy consumption +50.0%
• CDU parameters within normal operating window

Operational Risks
• Furnace outlet near metallurgical limits

Recommendations
• Check furnace tube skin temperatures
```

---

### Scenario 5: If CDU feed API gravity drops by 6 points, what changes are required?

- **DB Metrics Linked:** `Yes`

- **LLM Called:** `False`

- **Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Throughput: 90264.5 BPD
• Flow Rate: 3761.0 BPH

Parameter Adjustments
• Temperature: 374.3 – 390.3°C
• Pressure: 2.2 – 2.29 bar

Expected Changes
• Energy consumption -6.2%
• CDU parameters within normal operating window

Operational Risks
• Overloading downstream VDU with heavier bottoms

Recommendations
• Trim throughput 5–10% and adjust stripping steam
```

---

### Scenario 6: If CDU throughput halves, what happens to the furnace duty?

- **DB Metrics Linked:** `Yes`

- **LLM Called:** `False`

- **Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Throughput: 47500.0 BPD
• Flow Rate: 1979.2 BPH

Parameter Adjustments
• Temperature: 356.8 – 372.1°C
• Pressure: 2.12 – 2.2 bar

Expected Changes
• Reduced vapor velocities in CDU
• Energy consumption -50.0%

Operational Risks
• Tray weeping and poor fractionation

Recommendations
• Adjust reflux ratios and furnace firing
```

---

### Scenario 7: If CDU temperature drops by 50°F, what happens to yield?

- **DB Metrics Linked:** `Yes`

- **LLM Called:** `False`

- **Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Temperature: 322.3°C

Parameter Adjustments
• Temperature: 315.5 – 329.1°C
• Pressure: 2.21 – 2.3 bar

Expected Changes
• Energy consumption -25.6%
• CDU parameters within normal operating window

Operational Risks
• No immediate risks identified — monitor during transition

Recommendations
• Maintain routine checks and log metric deltas
```

---

### Scenario 8: If CDU pressure rises by 25%, what are the consequences?

- **DB Metrics Linked:** `Yes`

- **LLM Called:** `False`

- **Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Pressure: 2.81 bar

Parameter Adjustments
• Temperature: 364.5 – 380.1°C
• Pressure: 2.76 – 2.87 bar

Expected Changes
• Energy consumption +0.0%
• CDU parameters within normal operating window

Operational Risks
• No immediate risks identified — monitor during transition

Recommendations
• Maintain routine checks and log metric deltas
```

---

### Scenario 9: If CDU throughput is 45000 BPD, what are the recommended parameters?

- **DB Metrics Linked:** `Yes`

- **LLM Called:** `False`

- **Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Throughput: 45000.0 BPD
• Flow Rate: 1875.0 BPH

Parameter Adjustments
• Temperature: 356.4 – 371.7°C
• Pressure: 2.11 – 2.2 bar

Expected Changes
• Reduced vapor velocities in CDU
• Energy consumption -50.0%

Operational Risks
• Tray weeping and poor fractionation

Recommendations
• Adjust reflux ratios and furnace firing
```

---

### Scenario 10: If CDU temperature is 750 °F, what are the risks?

- **DB Metrics Linked:** `Yes`

- **LLM Called:** `False`

- **Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Temperature: 420.2°C

Parameter Adjustments
• Temperature: 411.4 – 428.9°C
• Pressure: 2.21 – 2.3 bar

Expected Changes
• Energy consumption +24.5%
• CDU parameters within normal operating window

Operational Risks
• Furnace outlet near metallurgical limits

Recommendations
• Check furnace tube skin temperatures
```

---
