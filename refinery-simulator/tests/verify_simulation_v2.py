"""
Verification script for Simulation Engine V2.
Runs 20 process simulation scenarios with varying baseline SQLite database states.
Checks that outputs vary dynamically based on current DB values.
Generates 'simulation_v2_test_report.md' inside the project directory.
"""
import sys
from pathlib import Path

# Add project root to path
_ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT_DIR))

from simulation_engine import estimate_parameters

# 20 Scenarios configuration
# (scenario_id, unit, changes, state_a_db, state_b_db, description)
SCENARIOS = [
    # CDU
    ("SC-01", "CDU", {"throughput_bpd": 6000}, 
     {"throughput": 3200, "temperature": 680, "pressure": 35, "yield": 91, "energy_consumption": 180},
     {"throughput": 5500, "temperature": 730, "pressure": 48, "yield": 93, "energy_consumption": 220},
     "CDU Flow 3000/5500 -> 6000 BPD"),
    
    ("SC-02", "CDU", {"throughput_bpd": 55000},
     {"throughput": 30000, "temperature": 700, "pressure": 40, "yield": 92, "energy_consumption": 200},
     {"throughput": 48000, "temperature": 740, "pressure": 52, "yield": 90, "energy_consumption": 240},
     "CDU Flow High Rate 30k/48k -> 55k BPD"),
    
    ("SC-03", "CDU", {"temperature_C_delta": 10},
     {"throughput": 40000, "temperature": 680, "pressure": 40, "yield": 92, "energy_consumption": 200},
     {"throughput": 40000, "temperature": 720, "pressure": 42, "yield": 91, "energy_consumption": 210},
     "CDU Temperature delta +10°F"),
    
    ("SC-04", "CDU", {"temperature_C_delta": -15},
     {"throughput": 40000, "temperature": 710, "pressure": 41, "yield": 92, "energy_consumption": 205},
     {"throughput": 40000, "temperature": 750, "pressure": 44, "yield": 89, "energy_consumption": 215},
     "CDU Temperature delta -15°F"),
    
    ("SC-05", "CDU", {"api_gravity_delta": -4},
     {"throughput": 42000, "temperature": 700, "pressure": 40, "yield": 92, "energy_consumption": 200},
     {"throughput": 42000, "temperature": 730, "pressure": 45, "yield": 90, "energy_consumption": 220},
     "CDU API gravity drops by 4 points"),
    
    ("SC-06", "CDU", {"heater_duty_pct_change": -10},
     {"throughput": 41000, "temperature": 720, "pressure": 40, "yield": 92, "energy_consumption": 200},
     {"throughput": 41000, "temperature": 750, "pressure": 43, "yield": 89, "energy_consumption": 215},
     "CDU Heater duty drop by 10%"),

    # VDU
    ("SC-07", "VDU", {"throughput_bpd": 15000},
     {"throughput": 10000, "temperature": 740, "pressure": 0.8, "yield": 89, "energy_consumption": 130},
     {"throughput": 13000, "temperature": 770, "pressure": 1.3, "yield": 87, "energy_consumption": 150},
     "VDU Throughput 10k/13k -> 15k BPD"),
    
    ("SC-08", "VDU", {"throughput_bpd": 28000},
     {"throughput": 20000, "temperature": 750, "pressure": 1.1, "yield": 88, "energy_consumption": 140},
     {"throughput": 25000, "temperature": 780, "pressure": 1.4, "yield": 86, "energy_consumption": 160},
     "VDU Throughput High 20k/25k -> 28k BPD"),
    
    ("SC-09", "VDU", {"pressure_pct": 20},
     {"throughput": 22000, "temperature": 760, "pressure": 0.9, "yield": 88, "energy_consumption": 140},
     {"throughput": 22000, "temperature": 760, "pressure": 1.4, "yield": 86, "energy_consumption": 145},
     "VDU Vacuum pressure rises by 20% (vacuum loss)"),
    
    ("SC-10", "VDU", {"pressure_pct": -10},
     {"throughput": 22000, "temperature": 760, "pressure": 1.2, "yield": 87, "energy_consumption": 145},
     {"throughput": 22000, "temperature": 760, "pressure": 1.5, "yield": 85, "energy_consumption": 150},
     "VDU Vacuum pressure drops by 10% (deeper vacuum)"),

    # FCC
    ("SC-11", "FCC", {"throughput_bpd": 28000},
     {"throughput": 22000, "temperature": 980, "pressure": 28, "yield": 78, "energy_consumption": 240},
     {"throughput": 26000, "temperature": 1010, "pressure": 32, "yield": 81, "energy_consumption": 270},
     "FCC Feed 22k/26k -> 28k BPD"),
    
    ("SC-12", "FCC", {"throughput_bpd": 34000},
     {"throughput": 27000, "temperature": 990, "pressure": 30, "yield": 80, "energy_consumption": 260},
     {"throughput": 31000, "temperature": 1020, "pressure": 34, "yield": 82, "energy_consumption": 290},
     "FCC Feed High 27k/31k -> 34k BPD"),
    
    ("SC-13", "FCC", {"catalyst_activity_pct_change": -5},
     {"throughput": 28000, "temperature": 1000, "pressure": 30, "yield": 80, "energy_consumption": 260},
     {"throughput": 28000, "temperature": 1000, "pressure": 30, "yield": 74, "energy_consumption": 260},
     "FCC Catalyst activity drop by 5%"),
    
    ("SC-14", "FCC", {"catalyst_activity_pct_change": 10},
     {"throughput": 28000, "temperature": 1000, "pressure": 30, "yield": 78, "energy_consumption": 260},
     {"throughput": 28000, "temperature": 1000, "pressure": 30, "yield": 83, "energy_consumption": 260},
     "FCC Catalyst activity increases by 10%"),
    
    ("SC-15", "FCC", {"temperature_C_delta": 15},
     {"throughput": 28000, "temperature": 980, "pressure": 30, "yield": 79, "energy_consumption": 250},
     {"throughput": 28000, "temperature": 1020, "pressure": 32, "yield": 81, "energy_consumption": 270},
     "FCC Reactor Temperature increases by 15°F"),

    # Hydrotreater
    ("SC-16", "Hydrotreater", {"throughput_bpd": 10000},
     {"throughput": 5000, "temperature": 620, "pressure": 750, "yield": 98.5, "energy_consumption": 95},
     {"throughput": 8000, "temperature": 660, "pressure": 820, "yield": 97.8, "energy_consumption": 115},
     "Hydrotreater throughput 5k/8k -> 10k BPD"),
    
    ("SC-17", "Hydrotreater", {"throughput_bpd": 22000},
     {"throughput": 15000, "temperature": 640, "pressure": 800, "yield": 98.2, "energy_consumption": 110},
     {"throughput": 19000, "temperature": 670, "pressure": 900, "yield": 97.5, "energy_consumption": 130},
     "Hydrotreater throughput 15k/19k -> 22k BPD"),
    
    ("SC-18", "Hydrotreater", {"sulfur_feed_mult": 2.0},
     {"throughput": 18000, "temperature": 630, "pressure": 780, "yield": 98.5, "energy_consumption": 100},
     {"throughput": 18000, "temperature": 660, "pressure": 860, "yield": 97.8, "energy_consumption": 115},
     "Hydrotreater Sulfur feed doubles (2.0x)"),
    
    ("SC-19", "Hydrotreater", {"sulfur_feed_mult": 3.0},
     {"throughput": 18000, "temperature": 630, "pressure": 780, "yield": 98.5, "energy_consumption": 100},
     {"throughput": 18000, "temperature": 660, "pressure": 860, "yield": 97.8, "energy_consumption": 115},
     "Hydrotreater Sulfur feed triples (3.0x)"),

    # Storage Terminal
    ("SC-20", "Storage Terminal", {"tank_utilization_pct": 95},
     {"throughput": 120000, "temperature": 70, "pressure": 16, "yield": 99.9, "energy_consumption": 20, "utilization": 40},
     {"throughput": 140000, "temperature": 80, "pressure": 19, "yield": 100.0, "energy_consumption": 25, "utilization": 85},
     "Storage Terminal utilization reaches 95%"),
]

def format_params(params: dict) -> str:
    parts = []
    for k, v in params.items():
        parts.append(f"{k}: {v}")
    return ", ".join(parts)

def main():
    print("Executing 20 Scenario Validation Tests...")
    report_lines = []
    
    # Header of markdown report
    report_lines.append("# Simulation Engine V2 Scenario Validation Report\n")
    report_lines.append("This document records the validation results for 20 distinct what-if simulation scenarios run against **Simulation Engine V2** in the **Refinery Decision Intelligence System (RDIS)**.\n")
    report_lines.append("Each scenario is evaluated under two distinct baseline SQLite database states (State A and State B) to verify that parameter estimation, changes, risks, and recommendations adapt dynamically to the plant conditions.\n")
    report_lines.append("---\n")
    
    report_lines.append("## Summary of Scaling Formulas Used\n")
    report_lines.append("The following engineering scaling formulas are dynamically applied relative to current database state values:\n")
    report_lines.append("- **Throughput/Flow Scaling Ratio:** `flow_ratio = target_flow / current_flow`\n")
    report_lines.append("- **Temperature Scaling:**\n")
    report_lines.append("  - *CDU/VDU:* `t_temp = current_temp * (1.0 + 0.04 * (flow_ratio - 1.0))`\n")
    report_lines.append("  - *FCC:* `t_temp = current_temp * (1.0 + 0.03 * (flow_ratio - 1.0))`\n")
    report_lines.append("  - *Hydrotreater:* `t_temp = current_temp * (1.0 + 0.02 * (flow_ratio - 1.0))`\n")
    report_lines.append("- **Pressure/Pressure-Drop Scaling:**\n")
    report_lines.append("  - *Hydrotreater (highly sensitive catalyst bed):* `t_press = current_press * (1.0 + 0.15 * (flow_ratio - 1.0))`\n")
    report_lines.append("  - *CDU/VDU/FCC:* `t_press = current_press * (1.0 + 0.08 * (flow_ratio - 1.0))`\n")
    report_lines.append("- **Yield Scaling:**\n")
    report_lines.append("  - *Residence Time Penalty:* `t_yield = current_yield - 1.5 * (flow_ratio - 1.0)`\n")
    report_lines.append("  - *VDU Vacuum Loss:* `t_yield = current_yield - 0.2 * pressure_pct`\n")
    report_lines.append("  - *Hydrotreater Sulfur Load:* `t_yield = current_yield - 0.5 * (sulfur_mult - 1.0)`\n")
    report_lines.append("- **Utility Energy Change:** `energy_change = 100.0 * (flow_ratio - 1.0) * 1.25`\n")
    report_lines.append("---\n")
    
    report_lines.append("## Scenario Test Results\n")
    
    pass_count = 0
    for sc_id, unit, changes, state_a, state_b, desc in SCENARIOS:
        print(f"Running Scenario {sc_id} ({unit}) - {desc}...")
        
        # Estimate with State A
        res_a = estimate_parameters(unit, changes, state_a)
        # Estimate with State B
        res_b = estimate_parameters(unit, changes, state_b)
        
        # Check that outputs differ
        diff_flag = "PASS (Dynamic output)"
        if res_a['Recommended Parameters'] == res_b['Recommended Parameters']:
            diff_flag = "FAIL (Static output)"
        else:
            pass_count += 1
            
        report_lines.append(f"### {sc_id}: {desc}\n")
        report_lines.append(f"**Unit:** `{unit}` | **Change Inputs:** `{changes}` | **Verification:** `{diff_flag}`\n\n")
        
        report_lines.append("#### State A (Low baseline)\n")
        report_lines.append(f"- **Current DB values:** Throughput={state_a['throughput']}, Temp={state_a['temperature']}, Press={state_a['pressure']}, Yield={state_a['yield']}, Energy={state_a['energy_consumption']}\n")
        report_lines.append(f"- **Recommended Parameters:** `{res_a['Recommended Parameters']}`\n")
        report_lines.append(f"- **Expected Consequences:** *{res_a['Possible Consequences'][0]}*\n")
        report_lines.append(f"- **Operational Risks:** *{res_a['Operational Risks'][0]}*\n\n")
        
        report_lines.append("#### State B (High baseline)\n")
        report_lines.append(f"- **Current DB values:** Throughput={state_b['throughput']}, Temp={state_b['temperature']}, Press={state_b['pressure']}, Yield={state_b['yield']}, Energy={state_b['energy_consumption']}\n")
        report_lines.append(f"- **Recommended Parameters:** `{res_b['Recommended Parameters']}`\n")
        report_lines.append(f"- **Expected Consequences:** *{res_b['Possible Consequences'][0]}*\n")
        report_lines.append(f"- **Operational Risks:** *{res_b['Operational Risks'][0]}*\n\n")
        report_lines.append("---\n")
        
    report_lines.append(f"## Validation Summary\n")
    report_lines.append(f"- **Total Scenarios Evaluated:** {len(SCENARIOS)}\n")
    report_lines.append(f"- **Passed (Dynamic outputs verified):** {pass_count}\n")
    report_lines.append(f"- **Failed:** {len(SCENARIOS) - pass_count}\n")
    
    report_path = _ROOT_DIR / "simulation_v2_test_report.md"
    report_path.write_text("\n".join(report_lines))
    print(f"Validation report successfully written to {report_path}")

if __name__ == "__main__":
    main()
