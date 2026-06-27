import csv
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

def ensure_exports_dir():
    if not os.path.exists(EXPORTS_DIR):
        os.makedirs(EXPORTS_DIR)

def export_units_to_csv(units):
    """
    Exports the list of refinery units to a CSV file.
    """
    ensure_exports_dir()
    filename = f"refinery_units_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    file_path = os.path.join(EXPORTS_DIR, filename)
    
    headers = ["ID", "Name", "Code", "Description", "Throughput Capacity (bbl/day)", "Status", "Created At"]
    
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for u in units:
            writer.writerow([
                u.id,
                u.name,
                u.code,
                u.description,
                u.throughput_capacity,
                u.status,
                u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else ""
            ])
            
    return file_path

def export_history_to_csv(history_records):
    """
    Exports a list of operational history records to a CSV file.
    """
    ensure_exports_dir()
    filename = f"operational_history_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    file_path = os.path.join(EXPORTS_DIR, filename)
    
    headers = [
        "Record ID", "Unit ID", "Unit Code", "Unit Name", 
        "Throughput (bbl/day)", "Pressure (psi/bar)", "Temperature (°F/°C)", 
        "Flow Rate (bbl/hr)", "Downtime (hr)", "Yield (%)", 
        "Energy Consumption (MMBtu/hr)", "Timestamp"
    ]
    
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for h in history_records:
            writer.writerow([
                h.id,
                h.unit_id,
                h.unit.code if h.unit else "",
                h.unit.name if h.unit else "",
                h.throughput,
                h.pressure,
                h.temperature,
                h.flow_rate,
                h.downtime,
                h.yield_,
                h.energy_consumption,
                h.timestamp.strftime("%Y-%m-%d %H:%M:%S") if h.timestamp else ""
            ])
            
    return file_path

def export_simulation_results_to_csv(run):
    """
    Exports simulation run results (Before vs After) to a CSV file.
    """
    ensure_exports_dir()
    filename = f"simulation_results_{run.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    file_path = os.path.join(EXPORTS_DIR, filename)
    
    headers = [
        "Simulation ID", "Scenario Name", "Scenario Type", "Risk Score", "Bottleneck Unit",
        "Unit Code", "Parameter Name", "Before Value", "After Value", "Delta Change", "Percentage Change"
    ]
    
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for r in run.results:
            delta = r.after_value - r.before_value
            pct_change = (delta / r.before_value * 100.0) if r.before_value != 0 else 0.0
            
            writer.writerow([
                run.id,
                run.scenario.name,
                run.scenario.type,
                run.risk_score,
                run.bottleneck_unit.code if run.bottleneck_unit else "None",
                r.unit.code,
                r.parameter_name,
                r.before_value,
                r.after_value,
                round(delta, 2),
                round(pct_change, 2)
            ])
            
    return file_path
