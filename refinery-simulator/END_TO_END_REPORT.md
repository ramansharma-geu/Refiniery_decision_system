# RDIS End-to-End System Validation Report

**Verification Run Date:** Fri Jun 19 08:38:07 2026

This report documents the end-to-end execution of RDIS using a **real SQLite database**, **real Flask routes**, and a **real local Ollama model (qwen2.5:1.5b)**.

---

## Executive Summary

| Metric | Value |
| :--- | :--- |
| **Total Queries Executed** | 50 |
| **Validation Pass Rate** | 20 / 50 (40.0%) |
| **Average Response Latency** | 0.0 seconds |

---

## Detailed Question Executions

| # | Question | Intent | Latency (s) | Validation | Details |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | What is CDU? | KNOWLEDGE | 0.01 | **PASS** | Normal |
| 2 | What is VDU? | KNOWLEDGE | 0.0 | **PASS** | Normal |
| 3 | What is FCC? | KNOWLEDGE | 0.0 | **PASS** | Normal |
| 4 | Why is Hydrotreater used? | KNOWLEDGE | 0.0 | **PASS** | Normal |
| 5 | What causes catalyst deactivation? | KNOWLEDGE | 0.0 | **PASS** | Normal |
| 6 | What is a fractionating column? | KNOWLEDGE | 0.0 | **PASS** | Normal |
| 7 | What is hydrotreating? | KNOWLEDGE | 0.0 | **PASS** | Normal |
| 8 | What is catalyst regeneration? | KNOWLEDGE | 0.0 | **PASS** | Normal |
| 9 | What is debottlenecking? | KNOWLEDGE | 0.0 | **PASS** | Normal |
| 10 | What is a heat exchanger network? | KNOWLEDGE | 0.0 | **PASS** | Normal |
| 11 | Show CDU flow rate. | CURRENT_DATA | 0.0 | **PASS** | Normal |
| 12 | Show FCC temperature. | CURRENT_DATA | 0.0 | **PASS** | Normal |
| 13 | Which unit has highest throughput? | CURRENT_DATA | 0.0 | **PASS** | Normal |
| 14 | Which unit has maximum downtime? | CURRENT_DATA | 0.0 | **PASS** | Normal |
| 15 | Show hydrotreater pressure. | CURRENT_DATA | 0.0 | **PASS** | Normal |
| 16 | Show VDU throughput. | CURRENT_DATA | 0.0 | **PASS** | Normal |
| 17 | Show storage terminal utilization. | CURRENT_DATA | 0.0 | **PASS** | Normal |
| 18 | Which unit has the highest energy consumption? | CURRENT_DATA | 0.0 | **PASS** | Normal |
| 19 | What is current VDU temperature? | CURRENT_DATA | 0.0 | **PASS** | Normal |
| 20 | What is current Hydrotreater flow rate? | CURRENT_DATA | 0.0 | **PASS** | Normal |
| 21 | Why is FCC yield decreasing? | ANALYSIS | 0.0 | **FAIL** | Failed: ['Current Values', 'Observed Concerns', 'Possible Causes', 'Operational Impact', 'Recommendations', 'Confidence Level'] |
| 22 | Why is CDU pressure increasing? | ANALYSIS | 0.0 | **FAIL** | Failed: ['Current Values', 'Observed Concerns', 'Possible Causes', 'Operational Impact', 'Recommendations', 'Confidence Level'] |
| 23 | Why is energy consumption rising? | ANALYSIS | 0.0 | **FAIL** | Failed: ['Current Values', 'Observed Concerns', 'Possible Causes', 'Operational Impact', 'Recommendations', 'Confidence Level'] |
| 24 | Why is throughput decreasing? | ANALYSIS | 0.0 | **FAIL** | Failed: ['Current Values', 'Observed Concerns', 'Possible Causes', 'Operational Impact', 'Recommendations', 'Confidence Level'] |
| 25 | What can cause hydrotreater shutdown? | ANALYSIS | 0.0 | **FAIL** | Failed: ['Current Values', 'Observed Concerns', 'Possible Causes', 'Operational Impact', 'Recommendations', 'Confidence Level'] |
| 26 | Why might FCC selectivity shift to heavier products? | ANALYSIS | 0.0 | **FAIL** | Failed: ['Current Values', 'Observed Concerns', 'Possible Causes', 'Operational Impact', 'Recommendations', 'Confidence Level'] |
| 27 | Why are CDU heater outlet temps fluctuating? | ANALYSIS | 0.0 | **FAIL** | Failed: ['Current Values', 'Observed Concerns', 'Possible Causes', 'Operational Impact', 'Recommendations', 'Confidence Level'] |
| 28 | Why would plant steam use increase unexpectedly? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 29 | Why is VDU vacuum pressure dropping? | ANALYSIS | 0.0 | **FAIL** | Failed: ['Current Values', 'Observed Concerns', 'Possible Causes', 'Operational Impact', 'Recommendations', 'Confidence Level'] |
| 30 | Why is Storage Terminal utilization surging? | ANALYSIS | 0.0 | **FAIL** | Failed: ['Current Values', 'Observed Concerns', 'Possible Causes', 'Operational Impact', 'Recommendations', 'Confidence Level'] |
| 31 | If CDU flow becomes 6000 BPD, what should temperature be? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 32 | If CDU flow becomes 8000 BPD, what are the risks? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 33 | If FCC temperature drops by 20°C, what happens to gasoline yield? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 34 | If FCC feed increases by 15%, what parameters should change? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 35 | If VDU vacuum pressure rises, what are the consequences? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 36 | If hydrotreater sulfur feed doubles, what operating changes are required? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 37 | If storage terminal utilization reaches 95%, what are the operational risks? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 38 | If CDU feed API gravity drops by 5 points, what changes are required? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 39 | If FCC catalyst activity drops by 10%, what adjustments are needed? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 40 | If a heater tube leaks reducing duty by 20%, what immediate actions? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 41 | If CDU throughput halves for one day, what plant-wide actions are recommended? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 42 | If VDU feed increases by 25%, what are the vacuum system consequences? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 43 | If Hydrotreater reactor pressure exceeds 1100 psi, what are the limits? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 44 | If CDU flow becomes 50000 BPD, what are the Recommended Parameters? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 45 | If FCC feed becomes 35000 BPD, what is the impact on gasoline yield? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 46 | If Hydrotreater throughput becomes 28000 BPD, what are the recommendations? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 47 | If VDU throughput becomes 28000 BPD, what are the consequences? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 48 | If Storage Terminal tank utilization reaches 92%, what is the confidence score? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 49 | If CDU furnace duty drops by 10%, what is the impact on flash zone temperature? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |
| 50 | If Hydrotreater sulfur load increases to 3.0x, what is the pressure drop? | SIMULATION | 0.0 | **FAIL** | Failed: ['Economic Impact'] |

---

## Detailed Chatbot Responses

### Question 1: What is CDU?

- **Intent:** `KNOWLEDGE`

- **Latency:** `0.01 seconds`

- **Validation Status:** `PASS`


**Response:**

```
The Crude Distillation Unit (CDU) performs atmospheric fractional distillation to separate raw crude oil into boiling-point fractions.

• Separates crude oil fractions based on boiling points under atmospheric pressure.
• Produces Light Naphtha, Heavy Naphtha, Kerosene, Light Gas Oil (Atmospheric Gas Oil), and Atmospheric Residue.
• Atmospheric residue serves as the primary feedstock for the Vacuum Distillation Unit (VDU).
```

---

### Question 2: What is VDU?

- **Intent:** `KNOWLEDGE`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
The Vacuum Distillation Unit (VDU) distills atmospheric residue under deep vacuum to extract vacuum gas oils without thermal cracking.

• Operates under vacuum (typically 0.5 to 1.5 psi absolute) to reduce boiling points of heavy hydrocarbons.
• Separates Atmospheric Residue into Light Vacuum Gas Oil (LVGO), Heavy Vacuum Gas Oil (HVGO), and Vacuum Residue.
• Prevents thermal cracking of heavy hydrocarbons which occurs at temperatures above 800°F (427°C).
```

---

### Question 3: What is FCC?

- **Intent:** `KNOWLEDGE`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
Fluid Catalytic Cracking (FCC) is a catalytic conversion process that cracks heavy vacuum gas oil feedstocks into high-value light products.

• Uses a circulating fluidized bed of zeolite catalyst at high temperatures (950°F to 1050°F).
• Cracks long-chain vacuum gas oils (VGO) into lighter products like high-octane gasoline, diesel/light cycle oil (LCO), and LPG.
• Does NOT extract aromatics from heavy fuel oil; it is a catalytic cracking conversion process.
• Catalyst deactivation is primarily caused by coke deposition (reversible via regeneration) and metal poisoning (nickel, vanadium, iron; irreversible).
```

---

### Question 4: Why is Hydrotreater used?

- **Intent:** `KNOWLEDGE`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
A hydrotreater is a catalytic purification unit that uses hydrogen to remove sulfur and other impurities from refinery streams.

• Reacts hydrocarbon feedstocks with hydrogen in the presence of a metal catalyst (e.g., CoMo or NiMo on alumina).
• Removes sulfur (hydrodesulfurization), nitrogen (hydrodenitrogenation), and trace metals, and saturates olefins.
• Does NOT remove water from crude oil (that is done by the desalter in/before the CDU).
• Protects downstream reforming and isomerization catalysts from poisoning (e.g., protecting reformer platinum catalysts).
```

---

### Question 5: What causes catalyst deactivation?

- **Intent:** `KNOWLEDGE`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
Catalyst deactivation is the loss of catalytic activity and selectivity over time due to operational, thermal, and chemical mechanisms.

• Coking: Deposition of carbonaceous residue (coke) on catalyst active sites (reversible via regenerator burning).
• Poisoning: Irreversible chemical bonding of impurities (heavy metals like nickel, vanadium, sodium, iron; or sulfur/nitrogen on reforming catalysts) to active sites.
• Sintering: Thermal degradation and loss of active surface area due to exposure to high temperatures.
• Fouling/Plugging: Physical blockage of catalyst pores or bed by particulates or polymer formation.
```

---

### Question 6: What is a fractionating column?

- **Intent:** `KNOWLEDGE`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
I am the RDIS Decision Intelligence Chatbot. I can answer questions about CDU, VDU, FCC, Hydrotreater, Storage Terminal, and explain operational parameters. Try asking 'What is FCC?' or 'What are the current parameters of CDU?'
```

---

### Question 7: What is hydrotreating?

- **Intent:** `KNOWLEDGE`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
A hydrotreater is a catalytic purification unit that uses hydrogen to remove sulfur and other impurities from refinery streams.

• Reacts hydrocarbon feedstocks with hydrogen in the presence of a metal catalyst (e.g., CoMo or NiMo on alumina).
• Removes sulfur (hydrodesulfurization), nitrogen (hydrodenitrogenation), and trace metals, and saturates olefins.
• Does NOT remove water from crude oil (that is done by the desalter in/before the CDU).
• Protects downstream reforming and isomerization catalysts from poisoning (e.g., protecting reformer platinum catalysts).
```

---

### Question 8: What is catalyst regeneration?

- **Intent:** `KNOWLEDGE`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
Catalyst deactivation is the loss of catalytic activity and selectivity over time due to operational, thermal, and chemical mechanisms.

• Coking: Deposition of carbonaceous residue (coke) on catalyst active sites (reversible via regenerator burning).
• Poisoning: Irreversible chemical bonding of impurities (heavy metals like nickel, vanadium, sodium, iron; or sulfur/nitrogen on reforming catalysts) to active sites.
• Sintering: Thermal degradation and loss of active surface area due to exposure to high temperatures.
• Fouling/Plugging: Physical blockage of catalyst pores or bed by particulates or polymer formation.
```

---

### Question 9: What is debottlenecking?

- **Intent:** `KNOWLEDGE`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
I am the RDIS Decision Intelligence Chatbot. I can answer questions about CDU, VDU, FCC, Hydrotreater, Storage Terminal, and explain operational parameters. Try asking 'What is FCC?' or 'What are the current parameters of CDU?'
```

---

### Question 10: What is a heat exchanger network?

- **Intent:** `KNOWLEDGE`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
I am the RDIS Decision Intelligence Chatbot. I can answer questions about CDU, VDU, FCC, Hydrotreater, Storage Terminal, and explain operational parameters. Try asking 'What is FCC?' or 'What are the current parameters of CDU?'
```

---

### Question 11: Show CDU flow rate.

- **Intent:** `CURRENT_DATA`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
Current Plant Data

• Value: 3767.02 
• Timestamp: 2026-06-12 09:47:11
• Status: Normal Operating Range
```

---

### Question 12: Show FCC temperature.

- **Intent:** `CURRENT_DATA`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
Current Plant Data

• Value: 1003.03 
• Timestamp: 2026-06-12 09:47:11
• Status: Normal Operating Range
```

---

### Question 13: Which unit has highest throughput?

- **Intent:** `CURRENT_DATA`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
The highest throughput was recorded at Storage Terminal with a value of 127365.57.
```

---

### Question 14: Which unit has maximum downtime?

- **Intent:** `CURRENT_DATA`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
The highest downtime was recorded at Storage Terminal with a value of 11.6.
```

---

### Question 15: Show hydrotreater pressure.

- **Intent:** `CURRENT_DATA`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
Current Plant Data

• Value: 777.84 
• Timestamp: 2026-06-12 09:47:11
• Status: Normal Operating Range
```

---

### Question 16: Show VDU throughput.

- **Intent:** `CURRENT_DATA`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
Current Plant Data

• Value: 39747.67 
• Timestamp: 2026-06-12 09:47:11
• Status: Normal Operating Range
```

---

### Question 17: Show storage terminal utilization.

- **Intent:** `CURRENT_DATA`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
Please specify a parameter (e.g. highest energy).
```

---

### Question 18: Which unit has the highest energy consumption?

- **Intent:** `CURRENT_DATA`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
The highest energy_consumption was recorded at FCC with a value of 320.0.
```

---

### Question 19: What is current VDU temperature?

- **Intent:** `CURRENT_DATA`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
Current Plant Data

• Value: 766.54 
• Timestamp: 2026-06-12 09:47:11
• Status: Normal Operating Range
```

---

### Question 20: What is current Hydrotreater flow rate?

- **Intent:** `CURRENT_DATA`

- **Latency:** `0.0 seconds`

- **Validation Status:** `PASS`


**Response:**

```
Current Plant Data

• Value: 730.3 
• Timestamp: 2026-06-12 09:47:11
• Status: Normal Operating Range
```

---

### Question 21: Why is FCC yield decreasing?

- **Intent:** `ANALYSIS`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
I am the RDIS Decision Intelligence Chatbot. I can answer questions about CDU, VDU, FCC, Hydrotreater, Storage Terminal, and explain operational parameters. Try asking 'What is FCC?' or 'What are the current parameters of CDU?'
```

---

### Question 22: Why is CDU pressure increasing?

- **Intent:** `ANALYSIS`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
I am the RDIS Decision Intelligence Chatbot. I can answer questions about CDU, VDU, FCC, Hydrotreater, Storage Terminal, and explain operational parameters. Try asking 'What is FCC?' or 'What are the current parameters of CDU?'
```

---

### Question 23: Why is energy consumption rising?

- **Intent:** `ANALYSIS`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
I am the RDIS Decision Intelligence Chatbot. I can answer questions about CDU, VDU, FCC, Hydrotreater, Storage Terminal, and explain operational parameters. Try asking 'What is FCC?' or 'What are the current parameters of CDU?'
```

---

### Question 24: Why is throughput decreasing?

- **Intent:** `ANALYSIS`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
I am the RDIS Decision Intelligence Chatbot. I can answer questions about CDU, VDU, FCC, Hydrotreater, Storage Terminal, and explain operational parameters. Try asking 'What is FCC?' or 'What are the current parameters of CDU?'
```

---

### Question 25: What can cause hydrotreater shutdown?

- **Intent:** `ANALYSIS`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
I am the RDIS Decision Intelligence Chatbot. I can answer questions about CDU, VDU, FCC, Hydrotreater, Storage Terminal, and explain operational parameters. Try asking 'What is FCC?' or 'What are the current parameters of CDU?'
```

---

### Question 26: Why might FCC selectivity shift to heavier products?

- **Intent:** `ANALYSIS`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
I am the RDIS Decision Intelligence Chatbot. I can answer questions about CDU, VDU, FCC, Hydrotreater, Storage Terminal, and explain operational parameters. Try asking 'What is FCC?' or 'What are the current parameters of CDU?'
```

---

### Question 27: Why are CDU heater outlet temps fluctuating?

- **Intent:** `ANALYSIS`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
I am the RDIS Decision Intelligence Chatbot. I can answer questions about CDU, VDU, FCC, Hydrotreater, Storage Terminal, and explain operational parameters. Try asking 'What is FCC?' or 'What are the current parameters of CDU?'
```

---

### Question 28: Why would plant steam use increase unexpectedly?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3958.3 BPH

Parameter Adjustments
• Temperature: 364.5 – 380.1°C
• Pressure: 2.21 – 2.3 bar

Expected Changes
• Energy consumption +0.0%
• CDU parameters within normal operating window

Operational Risks
• No immediate risks identified — monitor during transition

Recommendations
• Maintain routine checks and log metric deltas
```

---

### Question 29: Why is VDU vacuum pressure dropping?

- **Intent:** `ANALYSIS`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
I am the RDIS Decision Intelligence Chatbot. I can answer questions about CDU, VDU, FCC, Hydrotreater, Storage Terminal, and explain operational parameters. Try asking 'What is FCC?' or 'What are the current parameters of CDU?'
```

---

### Question 30: Why is Storage Terminal utilization surging?

- **Intent:** `ANALYSIS`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
I am the RDIS Decision Intelligence Chatbot. I can answer questions about CDU, VDU, FCC, Hydrotreater, Storage Terminal, and explain operational parameters. Try asking 'What is FCC?' or 'What are the current parameters of CDU?'
```

---

### Question 31: If CDU flow becomes 6000 BPD, what should temperature be?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Temperature: 5670.2°C

Parameter Adjustments
• Temperature: 5556.4 – 5783.9°C
• Pressure: 2.21 – 2.31 bar

Expected Changes
• Energy consumption +6.6%
• CDU parameters within normal operating window

Operational Risks
• Furnace outlet near metallurgical limits

Recommendations
• Check furnace tube skin temperatures
```

---

### Question 32: If CDU flow becomes 8000 BPD, what are the risks?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Throughput: 192000.0 BPD
• Flow Rate: 8000.0 BPH

Parameter Adjustments
• Temperature: 365.3 – 380.9°C
• Pressure: 2.21 – 2.31 bar

Expected Changes
• Energy consumption +6.6%
• CDU parameters within normal operating window

Operational Risks
• No immediate risks identified — monitor during transition

Recommendations
• Maintain routine checks and log metric deltas
```

---

### Question 33: If FCC temperature drops by 20°C, what happens to gasoline yield?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 27760.4 BPD
• Flow Rate: 1155.4 BPH
• Temperature: 539.5°C
• Pressure: 2.61 bar

Target Conditions
• Temperature: 519.5°C

Parameter Adjustments
• Temperature: 508.7 – 530.2°C
• Pressure: 2.56 – 2.67 bar

Expected Changes
• Energy consumption -7.2%
• FCC parameters within normal operating window

Operational Risks
• No immediate risks identified — monitor during transition

Recommendations
• Maintain routine checks and log metric deltas
```

---

### Question 34: If FCC feed increases by 15%, what parameters should change?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 27760.4 BPD
• Flow Rate: 1155.4 BPH
• Temperature: 539.5°C
• Pressure: 2.61 bar

Target Conditions
• Throughput: 31924.4 BPD
• Flow Rate: 1330.2 BPH

Parameter Adjustments
• Temperature: 530.8 – 553.2°C
• Pressure: 2.59 – 2.7 bar

Expected Changes
• Energy consumption +18.7%
• FCC parameters within normal operating window

Operational Risks
• No immediate risks identified — monitor during transition

Recommendations
• Maintain routine checks and log metric deltas
```

---

### Question 35: If VDU vacuum pressure rises, what are the consequences?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 39747.7 BPD
• Flow Rate: 1595.7 BPH
• Temperature: 408.1°C
• Pressure: 0.1 bar

Target Conditions
• Pressure: 0.12 bar

Parameter Adjustments
• Temperature: 399.6 – 416.6°C
• Pressure: 0.12 – 0.12 bar

Expected Changes
• Energy consumption +0.0%
• VDU parameters within normal operating window

Operational Risks
• No immediate risks identified — monitor during transition

Recommendations
• Maintain routine checks and log metric deltas
```

---

### Question 36: If hydrotreater sulfur feed doubles, what operating changes are required?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 16903.3 BPD
• Flow Rate: 730.3 BPH
• Temperature: 366.2°C
• Pressure: 53.63 bar

Target Conditions
• Throughput: 16903.3 BPD
• Flow Rate: 704.3 BPH

Parameter Adjustments
• Temperature: 358.5 – 373.9°C
• Pressure: 57.81 – 60.17 bar

Expected Changes
• Energy consumption +0.0%
• Hydrotreater parameters within normal operating window

Operational Risks
• Catalyst bed temperature runaway

Recommendations
• Increase recycle gas rate and step up quench flows
```

---

### Question 37: If storage terminal utilization reaches 95%, what are the operational risks?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 108133.9 BPD
• Flow Rate: 4467.9 BPH
• Temperature: 25.0°C
• Pressure: 1.38 bar

Target Conditions
• Throughput: 108133.9 BPD
• Flow Rate: 4505.6 BPH

Parameter Adjustments
• Temperature: 24.2 – 25.9°C
• Pressure: 1.35 – 1.41 bar

Expected Changes
• Energy consumption +0.0%
• Storage Terminal parameters within normal operating window

Operational Risks
• Tank overflow hazard and demurrage penalties

Recommendations
• Divert incoming shipments and expedite export pumps
```

---

### Question 38: If CDU feed API gravity drops by 5 points, what changes are required?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Throughput: 90288.5 BPD
• Flow Rate: 3762.0 BPH

Parameter Adjustments
• Temperature: 372.7 – 388.6°C
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

### Question 39: If FCC catalyst activity drops by 10%, what adjustments are needed?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 27760.4 BPD
• Flow Rate: 1155.4 BPH
• Temperature: 539.5°C
• Pressure: 2.61 bar

Target Conditions
• Throughput: 27760.4 BPD
• Flow Rate: 1156.7 BPH

Parameter Adjustments
• Temperature: 528.3 – 550.6°C
• Pressure: 2.56 – 2.67 bar

Expected Changes
• Energy consumption +0.0%
• FCC parameters within normal operating window

Operational Risks
• Increased slurry oil production

Recommendations
• Increase catalyst fresh make-up rate
```

---

### Question 40: If a heater tube leaks reducing duty by 20%, what immediate actions?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3958.3 BPH

Parameter Adjustments
• Temperature: 288.0 – 300.5°C
• Pressure: 2.21 – 2.3 bar

Expected Changes
• Energy consumption -20.0%
• CDU parameters within normal operating window

Operational Risks
• No immediate risks identified — monitor during transition

Recommendations
• Maintain routine checks and log metric deltas
```

---

### Question 41: If CDU throughput halves for one day, what plant-wide actions are recommended?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

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

### Question 42: If VDU feed increases by 25%, what are the vacuum system consequences?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 39747.7 BPD
• Flow Rate: 1595.7 BPH
• Temperature: 408.1°C
• Pressure: 0.1 bar

Target Conditions
• Throughput: 49684.6 BPD
• Flow Rate: 2070.2 BPH
• Pressure: 0.13 bar

Parameter Adjustments
• Temperature: 401.8 – 418.9°C
• Pressure: 0.13 – 0.13 bar

Expected Changes
• Energy consumption +16.5%
• VDU parameters within normal operating window

Operational Risks
• Thermal cracking of heavy residue

Recommendations
• Inspect vacuum ejector motive steam pressure
```

---

### Question 43: If Hydrotreater reactor pressure exceeds 1100 psi, what are the limits?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 16903.3 BPD
• Flow Rate: 730.3 BPH
• Temperature: 366.2°C
• Pressure: 53.63 bar

Target Conditions
• Pressure: 75.84 bar

Parameter Adjustments
• Temperature: 358.5 – 373.9°C
• Pressure: 74.33 – 77.36 bar

Expected Changes
• Energy consumption +0.0%
• Hydrotreater parameters within normal operating window

Operational Risks
• No immediate risks identified — monitor during transition

Recommendations
• Maintain routine checks and log metric deltas
```

---

### Question 44: If CDU flow becomes 50000 BPD, what are the Recommended Parameters?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Throughput: 50000.0 BPD
• Flow Rate: 2083.3 BPH

Parameter Adjustments
• Temperature: 357.2 – 372.6°C
• Pressure: 2.12 – 2.21 bar

Expected Changes
• Reduced vapor velocities in CDU
• Energy consumption -50.0%

Operational Risks
• Tray weeping and poor fractionation

Recommendations
• Adjust reflux ratios and furnace firing
```

---

### Question 45: If FCC feed becomes 35000 BPD, what is the impact on gasoline yield?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 27760.4 BPD
• Flow Rate: 1155.4 BPH
• Temperature: 539.5°C
• Pressure: 2.61 bar

Target Conditions
• Throughput: 35000.0 BPD
• Flow Rate: 1458.3 BPH

Parameter Adjustments
• Temperature: 532.6 – 555.1°C
• Pressure: 2.61 – 2.72 bar

Expected Changes
• Energy consumption +32.6%
• Increased furnace duty on FCC

Operational Risks
• Column flooding risk
• Increased pressure drop across trays

Recommendations
• Increase feed gradually in 5% steps
• Monitor column differential pressure
```

---

### Question 46: If Hydrotreater throughput becomes 28000 BPD, what are the recommendations?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 16903.3 BPD
• Flow Rate: 730.3 BPH
• Temperature: 366.2°C
• Pressure: 53.63 bar

Target Conditions
• Throughput: 28000.0 BPD
• Flow Rate: 1166.7 BPH

Parameter Adjustments
• Temperature: 363.5 – 379.0°C
• Pressure: 57.73 – 60.09 bar

Expected Changes
• Energy consumption +50.0%
• Increased furnace duty on Hydrotreater

Operational Risks
• Column flooding risk
• Increased pressure drop across trays

Recommendations
• Increase feed gradually in 5% steps
• Monitor column differential pressure
```

---

### Question 47: If VDU throughput becomes 28000 BPD, what are the consequences?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 39747.7 BPD
• Flow Rate: 1595.7 BPH
• Temperature: 408.1°C
• Pressure: 0.1 bar

Target Conditions
• Throughput: 28000.0 BPD
• Flow Rate: 1166.7 BPH

Parameter Adjustments
• Temperature: 394.6 – 411.5°C
• Pressure: 0.1 – 0.1 bar

Expected Changes
• Reduced vapor velocities in VDU
• Energy consumption -36.9%

Operational Risks
• Tray weeping and poor fractionation

Recommendations
• Adjust reflux ratios and furnace firing
```

---

### Question 48: If Storage Terminal tank utilization reaches 92%, what is the confidence score?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 108133.9 BPD
• Flow Rate: 4467.9 BPH
• Temperature: 25.0°C
• Pressure: 1.38 bar

Target Conditions
• Throughput: 108133.9 BPD
• Flow Rate: 4505.6 BPH

Parameter Adjustments
• Temperature: 24.2 – 25.9°C
• Pressure: 1.35 – 1.41 bar

Expected Changes
• Energy consumption +0.0%
• Storage Terminal parameters within normal operating window

Operational Risks
• Tank overflow hazard and demurrage penalties

Recommendations
• Divert incoming shipments and expedite export pumps
```

---

### Question 49: If CDU furnace duty drops by 10%, what is the impact on flash zone temperature?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 95000.0 BPD
• Flow Rate: 3767.0 BPH
• Temperature: 372.3°C
• Pressure: 2.25 bar

Target Conditions
• Temperature: 333.3°C

Parameter Adjustments
• Temperature: 326.3 – 340.3°C
• Pressure: 2.21 – 2.3 bar

Expected Changes
• Energy consumption -10.0%
• CDU parameters within normal operating window

Operational Risks
• No immediate risks identified — monitor during transition

Recommendations
• Maintain routine checks and log metric deltas
```

---

### Question 50: If Hydrotreater sulfur load increases to 3.0x, what is the pressure drop?

- **Intent:** `SIMULATION`

- **Latency:** `0.0 seconds`

- **Validation Status:** `FAIL`


**Response:**

```
Current Conditions
• Throughput: 16903.3 BPD
• Flow Rate: 730.3 BPH
• Temperature: 366.2°C
• Pressure: 53.63 bar

Target Conditions
• Pressure: 64.11 bar

Parameter Adjustments
• Temperature: 358.5 – 373.9°C
• Pressure: 62.83 – 65.39 bar

Expected Changes
• Energy consumption +0.0%
• Hydrotreater parameters within normal operating window

Operational Risks
• Catalyst bed temperature runaway

Recommendations
• Increase recycle gas rate and step up quench flows
```

---
