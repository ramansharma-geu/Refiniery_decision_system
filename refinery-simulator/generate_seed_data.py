import datetime
import random
import os

def generate_seed():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "seed_data.sql")
    print(f"Generating seed data to {output_path}...")
    
    # Static data definitions
    users = [
        ("admin", "Administrator"),
        ("operator1", "Operator"),
        ("operator2", "Operator"),
        ("manager", "Refinery Manager")
    ]
    
    units = [
        ("CDU", "Crude Distillation Unit", "Separates crude oil into fractions based on boiling points.", 100000.0, "Active"),
        ("VDU", "Vacuum Distillation Unit", "Processes heavy residue from CDU under vacuum to extract gas oils.", 45000.0, "Active"),
        ("FCC", "Fluid Catalytic Cracking Unit", "Converts heavy gas oils from VDU into high-value gasoline and LPG.", 35000.0, "Active"),
        ("Hydrotreater", "Hydrotreater Unit", "Removes sulfur and impurities from fuel fractions using hydrogen.", 25000.0, "Active"),
        ("Storage Terminal", "Storage & Logistics Terminal", "Manages crude feedstocks and refined product inventory tanks.", 1000000.0, "Active")
    ]
    
    scenarios = [
        ("FCC Shutdown", "FCC_SHUTDOWN", "Simulate complete catalytic cracker outage. Evaluates downstream storage backing up, gasoline yield drop, and overall plant risk."),
        ("Throughput Increase (+10%)", "THROUGHPUT_INCREASE", "Test a refinery-wide 10% increase in crude throughput to identify processing bottlenecks in the hydrotreater and other units."),
        ("Maintenance Delay", "MAINTENANCE_DELAY", "Assess the impact of delaying scheduled inspection/maintenance on the CDU. Raises risk profiles significantly."),
        ("Energy Reduction (-20%)", "ENERGY_REDUCTION", "Evaluate operations under a 20% grid electricity supply constraint, forcing units to run at reduced rates."),
        ("Demand Increase", "DEMAND_INCREASE", "Push processing units to maximum capacity to meet high market demand, highlighting system stress.")
    ]
    
    # SQL generation
    sql_lines = []
    sql_lines.append("-- Seed data for Refinery Decision Intelligence System (RDIS)\n")
    sql_lines.append("PRAGMA foreign_keys = ON;\n")
    sql_lines.append("BEGIN TRANSACTION;\n\n")
    
    # 1. Insert Users
    sql_lines.append("-- Users\n")
    for username, role in users:
        sql_lines.append(f"INSERT INTO users (username, role) VALUES ('{username}', '{role}');\n")
    sql_lines.append("\n")
    
    # 2. Insert Units
    sql_lines.append("-- Refinery Units\n")
    for code, name, desc, cap, status in units:
        sql_lines.append(
            f"INSERT INTO refinery_units (name, code, description, throughput_capacity, status) "
            f"VALUES ('{name}', '{code}', '{desc}', {cap}, '{status}');\n"
        )
    sql_lines.append("\n")
    
    # Helper to map unit code to its database ID (1-indexed based on insertion order)
    # CDU=1, VDU=2, FCC=3, Hydrotreater=4, Storage Terminal=5
    unit_ids = {"CDU": 1, "VDU": 2, "FCC": 3, "Hydrotreater": 4, "Storage Terminal": 5}
    
    # 3. Generate 200 operational records per unit (total 1000)
    sql_lines.append("-- Operational History\n")
    
    # Base configuration ranges for generation:
    # (min_tp, max_tp, min_press, max_press, min_temp, max_temp, min_flow, max_flow, min_yield, max_yield, min_eng, max_eng)
    ranges = {
        "CDU": (70000, 95000, 30.0, 50.0, 650.0, 750.0, 2900.0, 4000.0, 90.0, 95.0, 150.0, 250.0),
        "VDU": (30000, 42000, 0.5, 1.5, 700.0, 800.0, 1200.0, 1750.0, 85.0, 92.0, 100.0, 180.0),
        "FCC": (22000, 33000, 25.0, 40.0, 950.0, 1050.0, 900.0, 1400.0, 75.0, 85.0, 200.0, 320.0),
        "Hydrotreater": (15000, 24000, 600.0, 1000.0, 600.0, 700.0, 620.0, 1000.0, 97.0, 99.5, 80.0, 150.0),
        "Storage Terminal": (100000, 150000, 15.0, 20.0, 60.0, 90.0, 4000.0, 6250.0, 99.8, 100.0, 10.0, 30.0)
    }
    
    start_date = datetime.datetime.now() - datetime.timedelta(days=205)
    
    for u_code, u_id in unit_ids.items():
        r = ranges[u_code]
        # Introduce some autocorrelation for realistic data (random walk within boundaries)
        tp_last = (r[0] + r[1]) / 2.0
        press_last = (r[2] + r[3]) / 2.0
        temp_last = (r[4] + r[5]) / 2.0
        flow_last = (r[6] + r[7]) / 2.0
        yield_last = (r[8] + r[9]) / 2.0
        eng_last = (r[10] + r[11]) / 2.0
        
        for d in range(200):
            current_date = start_date + datetime.timedelta(days=d)
            dt_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # Random walk + noise
            tp = tp_last + random.uniform(-2000, 2000)
            tp = max(min(tp, r[1]), r[0])
            tp_last = tp
            
            press = press_last + random.uniform(-1.5, 1.5)
            press = max(min(press, r[3]), r[2])
            press_last = press
            
            temp = temp_last + random.uniform(-5.0, 5.0)
            temp = max(min(temp, r[5]), r[4])
            temp_last = temp
            
            # Flow rate correlates with throughput
            flow = (tp / 24.0) * random.uniform(0.95, 1.05)
            flow = max(min(flow, r[7]), r[6])
            
            # Yield varies slightly
            yield_pct = yield_last + random.uniform(-0.5, 0.5)
            yield_pct = max(min(yield_pct, r[9]), r[8])
            yield_last = yield_pct
            
            # Energy scales with throughput + some variance
            eng = (tp / r[1]) * r[11] * random.uniform(0.9, 1.1)
            eng = max(min(eng, r[11]), r[10])
            
            # Downtime - usually 0, with a 3% chance of some downtime (1 to 12 hours)
            downtime = 0.0
            if random.random() < 0.03:
                downtime = round(random.uniform(1.0, 12.0), 1)
                
            sql_lines.append(
                f"INSERT INTO operational_history (unit_id, throughput, pressure, temperature, flow_rate, downtime, yield, energy_consumption, timestamp) "
                f"VALUES ({u_id}, {round(tp, 2)}, {round(press, 2)}, {round(temp, 2)}, {round(flow, 2)}, {downtime}, {round(yield_pct, 2)}, {round(eng, 2)}, '{dt_str}');\n"
            )
            
    sql_lines.append("\n")
    
    # 4. Insert Scenarios
    sql_lines.append("-- Scenarios\n")
    for name, type_code, desc in scenarios:
        sql_lines.append(f"INSERT INTO scenarios (name, type, description) VALUES ('{name}', '{type_code}', '{desc}');\n")
    sql_lines.append("\n")
    
    # 5. Insert Scenario Parameters (rules for simulation runs)
    sql_lines.append("-- Scenario Parameters (Rules mapping scenario outputs)\n")
    # FCC Shutdown: id=1
    sql_lines.append("-- FCC Shutdown Parameters\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (1, {unit_ids['FCC']}, 'throughput', 'PERCENTAGE', -1.0);\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (1, {unit_ids['FCC']}, 'yield', 'PERCENTAGE', -1.0);\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (1, {unit_ids['VDU']}, 'throughput', 'PERCENTAGE', -0.4);\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (1, {unit_ids['Storage Terminal']}, 'downtime', 'ABSOLUTE', 0.0);\n")
    
    # Throughput Increase (+10%): id=2
    sql_lines.append("-- Throughput Increase Parameters\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (2, {unit_ids['CDU']}, 'throughput', 'PERCENTAGE', 0.10);\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (2, {unit_ids['VDU']}, 'throughput', 'PERCENTAGE', 0.10);\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (2, {unit_ids['FCC']}, 'throughput', 'PERCENTAGE', 0.10);\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (2, {unit_ids['Hydrotreater']}, 'throughput', 'PERCENTAGE', 0.10);\n")
    
    # Maintenance Delay: id=3
    sql_lines.append("-- Maintenance Delay Parameters\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (3, {unit_ids['CDU']}, 'downtime', 'ABSOLUTE', 4.0);\n")
    
    # Energy Reduction (-20%): id=4
    sql_lines.append("-- Energy Reduction Parameters\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (4, {unit_ids['CDU']}, 'throughput', 'PERCENTAGE', -0.20);\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (4, {unit_ids['VDU']}, 'throughput', 'PERCENTAGE', -0.20);\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (4, {unit_ids['FCC']}, 'throughput', 'PERCENTAGE', -0.20);\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (4, {unit_ids['Hydrotreater']}, 'throughput', 'PERCENTAGE', -0.20);\n")
    
    # Demand Increase: id=5
    sql_lines.append("-- Demand Increase Parameters\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (5, {unit_ids['CDU']}, 'throughput', 'PERCENTAGE', 0.05);\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (5, {unit_ids['FCC']}, 'throughput', 'PERCENTAGE', 0.08);\n")
    sql_lines.append(f"INSERT INTO scenario_parameters (scenario_id, unit_id, parameter_name, value_change_type, value_change) VALUES (5, {unit_ids['Hydrotreater']}, 'throughput', 'PERCENTAGE', 0.08);\n")
    
    sql_lines.append("\nCOMMIT;\n")
    
    with open(output_path, "w") as f:
        f.writelines(sql_lines)
    print("Seed SQL generation completed successfully.")

if __name__ == "__main__":
    generate_seed()
