# Simulation Engine V2 Scenario Validation Report

This document records the validation results for 20 distinct what-if simulation scenarios run against **Simulation Engine V2** in the **Refinery Decision Intelligence System (RDIS)**.

Each scenario is evaluated under two distinct baseline SQLite database states (State A and State B) to verify that parameter estimation, changes, risks, and recommendations adapt dynamically to the plant conditions.

---

## Summary of Scaling Formulas Used

The following engineering scaling formulas are dynamically applied relative to current database state values:

- **Throughput/Flow Scaling Ratio:** `flow_ratio = target_flow / current_flow`

- **Temperature Scaling:**

  - *CDU/VDU:* `t_temp = current_temp * (1.0 + 0.04 * (flow_ratio - 1.0))`

  - *FCC:* `t_temp = current_temp * (1.0 + 0.03 * (flow_ratio - 1.0))`

  - *Hydrotreater:* `t_temp = current_temp * (1.0 + 0.02 * (flow_ratio - 1.0))`

- **Pressure/Pressure-Drop Scaling:**

  - *Hydrotreater (highly sensitive catalyst bed):* `t_press = current_press * (1.0 + 0.15 * (flow_ratio - 1.0))`

  - *CDU/VDU/FCC:* `t_press = current_press * (1.0 + 0.08 * (flow_ratio - 1.0))`

- **Yield Scaling:**

  - *Residence Time Penalty:* `t_yield = current_yield - 1.5 * (flow_ratio - 1.0)`

  - *VDU Vacuum Loss:* `t_yield = current_yield - 0.2 * pressure_pct`

  - *Hydrotreater Sulfur Load:* `t_yield = current_yield - 0.5 * (sulfur_mult - 1.0)`

- **Utility Energy Change:** `energy_change = 100.0 * (flow_ratio - 1.0) * 1.25`

---

## Scenario Test Results

### SC-01: CDU Flow 3000/5500 -> 6000 BPD

**Unit:** `CDU` | **Change Inputs:** `{'throughput_bpd': 6000}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=3200, Temp=680, Press=35, Yield=91, Energy=180

- **Recommended Parameters:** `{'Throughput_bpd': 6000.0, 'Temperature_F': 703.8, 'Pressure_psi': 37.45, 'Yield_pct': 89.7}`

- **Expected Consequences:** *Energy consumption +50.0%*

- **Operational Risks:** *Column flooding risk*


#### State B (High baseline)

- **Current DB values:** Throughput=5500, Temp=730, Press=48, Yield=93, Energy=220

- **Recommended Parameters:** `{'Throughput_bpd': 6000.0, 'Temperature_F': 732.7, 'Pressure_psi': 48.35, 'Yield_pct': 92.9}`

- **Expected Consequences:** *Energy consumption +11.4%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


---

### SC-02: CDU Flow High Rate 30k/48k -> 55k BPD

**Unit:** `CDU` | **Change Inputs:** `{'throughput_bpd': 55000}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=30000, Temp=700, Press=40, Yield=92, Energy=200

- **Recommended Parameters:** `{'Throughput_bpd': 55000.0, 'Temperature_F': 723.3, 'Pressure_psi': 42.67, 'Yield_pct': 90.8}`

- **Expected Consequences:** *Energy consumption +50.0%*

- **Operational Risks:** *Column flooding risk*


#### State B (High baseline)

- **Current DB values:** Throughput=48000, Temp=740, Press=52, Yield=90, Energy=240

- **Recommended Parameters:** `{'Throughput_bpd': 55000.0, 'Temperature_F': 744.3, 'Pressure_psi': 52.61, 'Yield_pct': 89.8}`

- **Expected Consequences:** *Energy consumption +18.2%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


---

### SC-03: CDU Temperature delta +10°F

**Unit:** `CDU` | **Change Inputs:** `{'temperature_C_delta': 10}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=40000, Temp=680, Press=40, Yield=92, Energy=200

- **Recommended Parameters:** `{'Throughput_bpd': 40000.0, 'Temperature_F': 698.0, 'Pressure_psi': 40.0, 'Yield_pct': 92.0}`

- **Expected Consequences:** *Energy consumption +5.3%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


#### State B (High baseline)

- **Current DB values:** Throughput=40000, Temp=720, Press=42, Yield=91, Energy=210

- **Recommended Parameters:** `{'Throughput_bpd': 40000.0, 'Temperature_F': 738.0, 'Pressure_psi': 42.0, 'Yield_pct': 91.0}`

- **Expected Consequences:** *Energy consumption +5.0%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


---

### SC-04: CDU Temperature delta -15°F

**Unit:** `CDU` | **Change Inputs:** `{'temperature_C_delta': -15}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=40000, Temp=710, Press=41, Yield=92, Energy=205

- **Recommended Parameters:** `{'Throughput_bpd': 40000.0, 'Temperature_F': 683.0, 'Pressure_psi': 41.0, 'Yield_pct': 92.0}`

- **Expected Consequences:** *Energy consumption -7.6%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


#### State B (High baseline)

- **Current DB values:** Throughput=40000, Temp=750, Press=44, Yield=89, Energy=215

- **Recommended Parameters:** `{'Throughput_bpd': 40000.0, 'Temperature_F': 723.0, 'Pressure_psi': 44.0, 'Yield_pct': 89.0}`

- **Expected Consequences:** *Energy consumption -7.2%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


---

### SC-05: CDU API gravity drops by 4 points

**Unit:** `CDU` | **Change Inputs:** `{'api_gravity_delta': -4}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=42000, Temp=700, Press=40, Yield=92, Energy=200

- **Recommended Parameters:** `{'Throughput_bpd': 42000.0, 'Temperature_F': 712.0, 'Pressure_psi': 40.0, 'Yield_pct': 92.0}`

- **Expected Consequences:** *Energy consumption +3.4%*

- **Operational Risks:** *Overloading downstream VDU with heavier bottoms*


#### State B (High baseline)

- **Current DB values:** Throughput=42000, Temp=730, Press=45, Yield=90, Energy=220

- **Recommended Parameters:** `{'Throughput_bpd': 42000.0, 'Temperature_F': 742.0, 'Pressure_psi': 45.0, 'Yield_pct': 90.0}`

- **Expected Consequences:** *Energy consumption +3.3%*

- **Operational Risks:** *Overloading downstream VDU with heavier bottoms*


---

### SC-06: CDU Heater duty drop by 10%

**Unit:** `CDU` | **Change Inputs:** `{'heater_duty_pct_change': -10}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=41000, Temp=720, Press=40, Yield=92, Energy=200

- **Recommended Parameters:** `{'Throughput_bpd': 41000.0, 'Temperature_F': 648.0, 'Pressure_psi': 40.0, 'Yield_pct': 92.0}`

- **Expected Consequences:** *Energy consumption -10%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


#### State B (High baseline)

- **Current DB values:** Throughput=41000, Temp=750, Press=43, Yield=89, Energy=215

- **Recommended Parameters:** `{'Throughput_bpd': 41000.0, 'Temperature_F': 675.0, 'Pressure_psi': 43.0, 'Yield_pct': 89.0}`

- **Expected Consequences:** *Energy consumption -10%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


---

### SC-07: VDU Throughput 10k/13k -> 15k BPD

**Unit:** `VDU` | **Change Inputs:** `{'throughput_bpd': 15000}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=10000, Temp=740, Press=0.8, Yield=89, Energy=130

- **Recommended Parameters:** `{'Throughput_bpd': 15000.0, 'Temperature_F': 754.8, 'Pressure_psi': 0.83, 'Yield_pct': 88.2}`

- **Expected Consequences:** *Energy consumption +50.0%*

- **Operational Risks:** *Column flooding risk*


#### State B (High baseline)

- **Current DB values:** Throughput=13000, Temp=770, Press=1.3, Yield=87, Energy=150

- **Recommended Parameters:** `{'Throughput_bpd': 15000.0, 'Temperature_F': 774.7, 'Pressure_psi': 1.32, 'Yield_pct': 86.8}`

- **Expected Consequences:** *Energy consumption +19.2%*

- **Operational Risks:** *Column flooding risk*


---

### SC-08: VDU Throughput High 20k/25k -> 28k BPD

**Unit:** `VDU` | **Change Inputs:** `{'throughput_bpd': 28000}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=20000, Temp=750, Press=1.1, Yield=88, Energy=140

- **Recommended Parameters:** `{'Throughput_bpd': 28000.0, 'Temperature_F': 762.0, 'Pressure_psi': 1.14, 'Yield_pct': 87.4}`

- **Expected Consequences:** *Energy consumption +50.0%*

- **Operational Risks:** *Column flooding risk*


#### State B (High baseline)

- **Current DB values:** Throughput=25000, Temp=780, Press=1.4, Yield=86, Energy=160

- **Recommended Parameters:** `{'Throughput_bpd': 28000.0, 'Temperature_F': 783.7, 'Pressure_psi': 1.41, 'Yield_pct': 85.8}`

- **Expected Consequences:** *Energy consumption +15.0%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


---

### SC-09: VDU Vacuum pressure rises by 20% (vacuum loss)

**Unit:** `VDU` | **Change Inputs:** `{'pressure_pct': 20}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=22000, Temp=760, Press=0.9, Yield=88, Energy=140

- **Recommended Parameters:** `{'Throughput_bpd': 22000.0, 'Temperature_F': 760.0, 'Pressure_psi': 1.08, 'Yield_pct': 84.0}`

- **Expected Consequences:** *Energy consumption +0.0%*

- **Operational Risks:** *Thermal cracking of heavy residue*


#### State B (High baseline)

- **Current DB values:** Throughput=22000, Temp=760, Press=1.4, Yield=86, Energy=145

- **Recommended Parameters:** `{'Throughput_bpd': 22000.0, 'Temperature_F': 760.0, 'Pressure_psi': 1.68, 'Yield_pct': 82.0}`

- **Expected Consequences:** *Energy consumption +0.0%*

- **Operational Risks:** *Thermal cracking of heavy residue*


---

### SC-10: VDU Vacuum pressure drops by 10% (deeper vacuum)

**Unit:** `VDU` | **Change Inputs:** `{'pressure_pct': -10}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=22000, Temp=760, Press=1.2, Yield=87, Energy=145

- **Recommended Parameters:** `{'Throughput_bpd': 22000.0, 'Temperature_F': 760.0, 'Pressure_psi': 1.08, 'Yield_pct': 87.0}`

- **Expected Consequences:** *Energy consumption +0.0%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


#### State B (High baseline)

- **Current DB values:** Throughput=22000, Temp=760, Press=1.5, Yield=85, Energy=150

- **Recommended Parameters:** `{'Throughput_bpd': 22000.0, 'Temperature_F': 760.0, 'Pressure_psi': 1.35, 'Yield_pct': 85.0}`

- **Expected Consequences:** *Energy consumption +0.0%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


---

### SC-11: FCC Feed 22k/26k -> 28k BPD

**Unit:** `FCC` | **Change Inputs:** `{'throughput_bpd': 28000}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=22000, Temp=980, Press=28, Yield=78, Energy=240

- **Recommended Parameters:** `{'Throughput_bpd': 28000.0, 'Temperature_F': 988.0, 'Pressure_psi': 28.61, 'Yield_pct': 77.6}`

- **Expected Consequences:** *Energy consumption +34.1%*

- **Operational Risks:** *Column flooding risk*


#### State B (High baseline)

- **Current DB values:** Throughput=26000, Temp=1010, Press=32, Yield=81, Energy=270

- **Recommended Parameters:** `{'Throughput_bpd': 28000.0, 'Temperature_F': 1012.3, 'Pressure_psi': 32.2, 'Yield_pct': 80.9}`

- **Expected Consequences:** *Energy consumption +9.6%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


---

### SC-12: FCC Feed High 27k/31k -> 34k BPD

**Unit:** `FCC` | **Change Inputs:** `{'throughput_bpd': 34000}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=27000, Temp=990, Press=30, Yield=80, Energy=260

- **Recommended Parameters:** `{'Throughput_bpd': 34000.0, 'Temperature_F': 997.7, 'Pressure_psi': 30.62, 'Yield_pct': 79.6}`

- **Expected Consequences:** *Energy consumption +32.4%*

- **Operational Risks:** *Column flooding risk*


#### State B (High baseline)

- **Current DB values:** Throughput=31000, Temp=1020, Press=34, Yield=82, Energy=290

- **Recommended Parameters:** `{'Throughput_bpd': 34000.0, 'Temperature_F': 1023.0, 'Pressure_psi': 34.26, 'Yield_pct': 81.9}`

- **Expected Consequences:** *Energy consumption +12.1%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


---

### SC-13: FCC Catalyst activity drop by 5%

**Unit:** `FCC` | **Change Inputs:** `{'catalyst_activity_pct_change': -5}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=28000, Temp=1000, Press=30, Yield=80, Energy=260

- **Recommended Parameters:** `{'Throughput_bpd': 28000.0, 'Temperature_F': 1000.0, 'Pressure_psi': 30.0, 'Yield_pct': 78.5}`

- **Expected Consequences:** *Energy consumption +0.0%*

- **Operational Risks:** *Increased slurry oil production*


#### State B (High baseline)

- **Current DB values:** Throughput=28000, Temp=1000, Press=30, Yield=74, Energy=260

- **Recommended Parameters:** `{'Throughput_bpd': 28000.0, 'Temperature_F': 1000.0, 'Pressure_psi': 30.0, 'Yield_pct': 72.5}`

- **Expected Consequences:** *Energy consumption +0.0%*

- **Operational Risks:** *Increased slurry oil production*


---

### SC-14: FCC Catalyst activity increases by 10%

**Unit:** `FCC` | **Change Inputs:** `{'catalyst_activity_pct_change': 10}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=28000, Temp=1000, Press=30, Yield=78, Energy=260

- **Recommended Parameters:** `{'Throughput_bpd': 28000.0, 'Temperature_F': 1000.0, 'Pressure_psi': 30.0, 'Yield_pct': 81.0}`

- **Expected Consequences:** *Energy consumption +0.0%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


#### State B (High baseline)

- **Current DB values:** Throughput=28000, Temp=1000, Press=30, Yield=83, Energy=260

- **Recommended Parameters:** `{'Throughput_bpd': 28000.0, 'Temperature_F': 1000.0, 'Pressure_psi': 30.0, 'Yield_pct': 86.0}`

- **Expected Consequences:** *Energy consumption +0.0%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


---

### SC-15: FCC Reactor Temperature increases by 15°F

**Unit:** `FCC` | **Change Inputs:** `{'temperature_C_delta': 15}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=28000, Temp=980, Press=30, Yield=79, Energy=250

- **Recommended Parameters:** `{'Throughput_bpd': 28000.0, 'Temperature_F': 1007.0, 'Pressure_psi': 30.0, 'Yield_pct': 79.0}`

- **Expected Consequences:** *Energy consumption +5.5%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


#### State B (High baseline)

- **Current DB values:** Throughput=28000, Temp=1020, Press=32, Yield=81, Energy=270

- **Recommended Parameters:** `{'Throughput_bpd': 28000.0, 'Temperature_F': 1047.0, 'Pressure_psi': 32.0, 'Yield_pct': 81.0}`

- **Expected Consequences:** *Energy consumption +5.3%*

- **Operational Risks:** *No immediate risks identified — monitor during transition*


---

### SC-16: Hydrotreater throughput 5k/8k -> 10k BPD

**Unit:** `Hydrotreater` | **Change Inputs:** `{'throughput_bpd': 10000}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=5000, Temp=620, Press=750, Yield=98.5, Energy=95

- **Recommended Parameters:** `{'Throughput_bpd': 10000.0, 'Temperature_F': 632.4, 'Pressure_psi': 862.5, 'Yield_pct': 97.0}`

- **Expected Consequences:** *Energy consumption +50.0%*

- **Operational Risks:** *Column flooding risk*


#### State B (High baseline)

- **Current DB values:** Throughput=8000, Temp=660, Press=820, Yield=97.8, Energy=115

- **Recommended Parameters:** `{'Throughput_bpd': 10000.0, 'Temperature_F': 663.3, 'Pressure_psi': 850.75, 'Yield_pct': 97.4}`

- **Expected Consequences:** *Energy consumption +31.2%*

- **Operational Risks:** *Column flooding risk*


---

### SC-17: Hydrotreater throughput 15k/19k -> 22k BPD

**Unit:** `Hydrotreater` | **Change Inputs:** `{'throughput_bpd': 22000}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=15000, Temp=640, Press=800, Yield=98.2, Energy=110

- **Recommended Parameters:** `{'Throughput_bpd': 22000.0, 'Temperature_F': 646.0, 'Pressure_psi': 856.0, 'Yield_pct': 97.5}`

- **Expected Consequences:** *Energy consumption +50.0%*

- **Operational Risks:** *Column flooding risk*


#### State B (High baseline)

- **Current DB values:** Throughput=19000, Temp=670, Press=900, Yield=97.5, Energy=130

- **Recommended Parameters:** `{'Throughput_bpd': 22000.0, 'Temperature_F': 672.1, 'Pressure_psi': 921.32, 'Yield_pct': 97.3}`

- **Expected Consequences:** *Energy consumption +19.7%*

- **Operational Risks:** *Column flooding risk*


---

### SC-18: Hydrotreater Sulfur feed doubles (2.0x)

**Unit:** `Hydrotreater` | **Change Inputs:** `{'sulfur_feed_mult': 2.0}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=18000, Temp=630, Press=780, Yield=98.5, Energy=100

- **Recommended Parameters:** `{'Throughput_bpd': 18000.0, 'Temperature_F': 630.0, 'Pressure_psi': 858.0, 'Yield_pct': 98.0}`

- **Expected Consequences:** *Energy consumption +0.0%*

- **Operational Risks:** *Catalyst bed temperature runaway*


#### State B (High baseline)

- **Current DB values:** Throughput=18000, Temp=660, Press=860, Yield=97.8, Energy=115

- **Recommended Parameters:** `{'Throughput_bpd': 18000.0, 'Temperature_F': 660.0, 'Pressure_psi': 946.0, 'Yield_pct': 97.3}`

- **Expected Consequences:** *Energy consumption +0.0%*

- **Operational Risks:** *Catalyst bed temperature runaway*


---

### SC-19: Hydrotreater Sulfur feed triples (3.0x)

**Unit:** `Hydrotreater` | **Change Inputs:** `{'sulfur_feed_mult': 3.0}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=18000, Temp=630, Press=780, Yield=98.5, Energy=100

- **Recommended Parameters:** `{'Throughput_bpd': 18000.0, 'Temperature_F': 630.0, 'Pressure_psi': 936.0, 'Yield_pct': 97.5}`

- **Expected Consequences:** *Energy consumption +0.0%*

- **Operational Risks:** *Catalyst bed temperature runaway*


#### State B (High baseline)

- **Current DB values:** Throughput=18000, Temp=660, Press=860, Yield=97.8, Energy=115

- **Recommended Parameters:** `{'Throughput_bpd': 18000.0, 'Temperature_F': 660.0, 'Pressure_psi': 1032.0, 'Yield_pct': 96.8}`

- **Expected Consequences:** *Energy consumption +0.0%*

- **Operational Risks:** *Catalyst bed temperature runaway*


---

### SC-20: Storage Terminal utilization reaches 95%

**Unit:** `Storage Terminal` | **Change Inputs:** `{'tank_utilization_pct': 95}` | **Verification:** `PASS (Dynamic output)`


#### State A (Low baseline)

- **Current DB values:** Throughput=120000, Temp=70, Press=16, Yield=99.9, Energy=20

- **Recommended Parameters:** `{'Throughput_bpd': 120000.0, 'Temperature_F': 70.0, 'Pressure_psi': 16.0, 'Yield_pct': 99.9}`

- **Expected Consequences:** *Energy consumption +0.0%*

- **Operational Risks:** *Tank overflow hazard and demurrage penalties*


#### State B (High baseline)

- **Current DB values:** Throughput=140000, Temp=80, Press=19, Yield=100.0, Energy=25

- **Recommended Parameters:** `{'Throughput_bpd': 140000.0, 'Temperature_F': 80.0, 'Pressure_psi': 19.0, 'Yield_pct': 100.0}`

- **Expected Consequences:** *Energy consumption +0.0%*

- **Operational Risks:** *Tank overflow hazard and demurrage penalties*


---

## Validation Summary

- **Total Scenarios Evaluated:** 20

- **Passed (Dynamic outputs verified):** 20

- **Failed:** 0
