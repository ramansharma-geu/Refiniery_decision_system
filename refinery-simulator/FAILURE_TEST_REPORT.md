# RDIS Failure Testing Report

This report documents system behavior under extreme failure states, missing database configurations, and network outages.

---

## Test 1: Empty Question

- **Expected Behavior:** API rejects request with HTTP 400 and clear error message.

- **Observed Behavior:**
```
Status: 400
Data: {"error":"Empty query query parameter."}

```

- **Result:** **PASS**

---

## Test 2: Invalid Unit in Simulation Query

- **Expected Behavior:** System defaults to CDU or handles invalid unit gracefully without crashing.

- **Observed Behavior:**
```
Status: 200
Data: {"db_data":[{"downtime":0.0,"energy_consumption":250.0,"flow_rate":3767.02,"id":200,"pressure":32.64,"temperature":702.12,"throughput":95000.0,"timestamp":"2026-06-12 09:47:11","unit_code":"CDU","unit_id":1,"unit_name":"Crude Distillation Unit","yield":93.51}],"detected_intent":"SIMULATION","llm_called":false,"parsed_intent":{"extreme_type":null,"intent":"query_current","limit":5,"parameter":"throughput","unit_code":null},"response":"Current Conditions\n\u2022 Throughput: 95000.0 BPD\n\u2022 Flow Rate: 3767.0 BPH\n\u2022 Temperature: 372.3\u00b0C\n\u2022 Pressure: 2.25 bar\n\nTarget Conditions\n\u2022 Throughput: 104500.0 BPD\n\u2022 Flow Rate: 4354.2 BPH\n\nParameter Adjustments\n\u2022 Temperature: 365.3 \u2013 380.9\u00b0C\n\u2022 Pressure: 2.21 \u2013 2.31 bar\n\nExpected Changes\n\u2022 Energy consumption +6.6%\n\u2022 CDU parameters within normal operating window\n\nOperational Risks\n\u2022 No immediate risks identified \u2014 monitor during transition\n\nRecommendations\n\u2022 Maintain routine checks and log metric deltas"}

```

- **Result:** **PASS**

---

## Test 3: Missing Database Values in Simulation Engine

- **Expected Behavior:** Simulation engine falls back to midpoint values from the engineering rules config.

- **Observed Behavior:**
```
{
  "current_display": {
    "flow_rate_bph": 2187.5,
    "throughput_bpd": 52500.0,
    "temperature_c": 371.1,
    "pressure_bar": 2.41,
    "yield_pct": 82.5,
    "energy_mwh": 200.0
  },
  "target_display": {
    "throughput_bpd": 5000.0,
    "flow_rate_bph": 208.3
  },
  "adjustments": {
    "temperature_range_c": "349.6 \u2013 364.6\u00b0C",
    "pressure_range_bar": "2.19 \u2013 2.28 bar",
    "energy_pct_change": "-50.0%"
  },
  "consequences": [
    "Reduced vapor velocities in CDU",
    "Energy consumption -50.0%"
  ],
  "risks": [
    "Tray weeping and poor fractionation"
  ],
  "recommendations": [
    "Adjust reflux ratios and furnace firing"
  ],
  "Recommended Parameters": {
    "Throughput_bpd": 5000.0,
    "Temperature_F": 674.8,
    "Pressure_psi": 32.48,
    "Yield_pct": 82.5
  },
  "Possible Consequences": [
    "Reduced vapor velocities in CDU",
    "Energy consumption -50.0%"
  ],
  "Operational Risks": [
    "Tray weeping and poor fractionation"
  ],
  "internal": {
    "flow_ratio": 0.1,
    "c_tp": 52500.0,
    "t_tp": 5000.0,
    "c_temp_f": 700.0,
    "t_temp_f": 674.8,
    "c_press_psi": 35.0,
    "t_press_psi": 32.48,
    "t_yield": 82.5,
    "t_energy_pct": -50.0
  }
}
```

- **Result:** **PASS**

---

## Test 4: SQLite Database Unavailable

- **Expected Behavior:** App handles SQLAlchemy query error gracefully and returns a database error response rather than crashing.

- **Observed Behavior:**
```
Status: 500
Data: {"db_data":[],"llm_called":false,"response":"Internal chatbot service error occurred. Please contact plant system engineering."}

```

- **Result:** **PASS**

---

## Test 5: Ollama Model Service Unavailable

- **Expected Behavior:** LLM service queries fail connection timeout; system falls back to high-fidelity domain mock response without crashing.

- **Observed Behavior:**
```
Status: 200
Data: {"db_data":[],"detected_intent":"KNOWLEDGE","llm_called":true,"parsed_intent":{"extreme_type":null,"intent":"general","limit":5,"parameter":null,"unit_code":"CDU"},"response":"The Crude Distillation Unit (CDU) performs atmospheric fractional distillation to separate raw crude oil into boiling-point fractions.\n\n\u2022 Separates crude oil fractions based on boiling points under atmospheric pressure.\n\u2022 Produces Light Naphtha, Heavy Naphtha, Kerosene, Light Gas Oil (Atmospheric Gas Oil), and Atmospheric Residue.\n\u2022 Atmospheric residue serves as the primary feedstock for the Vacuum Distillation Unit (VDU)."}

```

- **Result:** **PASS**

---

## Test 6: Corrupted engineering_rules.json

- **Expected Behavior:** Simulation engine handles decoding exception, falls back to empty dictionary, and applies base scaling without crashing.

- **Observed Behavior:**
```
{
  "current_display": {
    "flow_rate_bph": 2187.5,
    "throughput_bpd": 52500.0,
    "temperature_c": 371.1,
    "pressure_bar": 2.41,
    "yield_pct": 82.5,
    "energy_mwh": 200.0
  },
  "target_display": {
    "throughput_bpd": 5000.0,
    "flow_rate_bph": 208.3
  },
  "adjustments": {
    "temperature_range_c": "349.6 \u2013 364.6\u00b0C",
    "pressure_range_bar": "2.19 \u2013 2.28 bar",
    "energy_pct_change": "-50.0%"
  },
  "consequences": [
    "Reduced vapor velocities in CDU",
    "Energy consumption -50.0%"
  ],
  "risks": [
    "Tray weeping and poor fractionation"
  ],
  "recommendations": [
    "Adjust reflux ratios and furnace firing"
  ],
  "Recommended Parameters": {
    "Throughput_bpd": 5000.0,
    "Temperature_F": 674.8,
    "Pressure_psi": 32.48,
    "Yield_pct": 82.5
  },
  "Possible Consequences": [
    "Reduced vapor velocities in CDU",
    "Energy consumption -50.0%"
  ],
  "Operational Risks": [
    "Tray weeping and poor fractionation"
  ],
  "internal": {
    "flow_ratio": 0.1,
    "c_tp": 52500.0,
    "t_tp": 5000.0,
    "c_temp_f": 700.0,
    "t_temp_f": 674.8,
    "c_press_psi": 35.0,
    "t_press_psi": 32.48,
    "t_yield": 82.5,
    "t_energy_pct": -50.0
  }
}
```

- **Result:** **PASS**

---
