# Rules Catalog for RDIS Simulation Engine

def apply_fcc_shutdown(before_state):
    """
    FCC Shutdown scenario rules:
    - FCC is completely down (throughput=0, flow=0, yield=0, downtime=24h, energy=0).
    - VDU (upstream feeder) drops throughput by 40% (residue backing up).
    - CDU (primary distiller) drops throughput by 10% (refinery balance pull-back).
    - Hydrotreater drops throughput by 15% (less feed available).
    - Storage Terminal throughput drops by 20% (logistics slowdown).
    """
    after_state = {}
    for code, param in before_state.items():
        after = dict(param)
        if code == "FCC":
            after["throughput"] = 0.0
            after["flow_rate"] = 0.0
            after["yield"] = 0.0
            after["downtime"] = 24.0
            after["energy_consumption"] = 0.0
            after["pressure"] = 0.0
            after["temperature"] = 60.0 # cooled down to ambient
        elif code == "VDU":
            after["throughput"] = round(param["throughput"] * 0.60, 2)
            after["flow_rate"] = round(param["flow_rate"] * 0.60, 2)
            after["energy_consumption"] = round(param["energy_consumption"] * 0.70, 2)
            after["pressure"] = round(param["pressure"] * 0.90, 2)
            after["temperature"] = round(param["temperature"] * 0.95, 2)
        elif code == "CDU":
            after["throughput"] = round(param["throughput"] * 0.90, 2)
            after["flow_rate"] = round(param["flow_rate"] * 0.90, 2)
            after["energy_consumption"] = round(param["energy_consumption"] * 0.92, 2)
            after["pressure"] = round(param["pressure"] * 0.95, 2)
        elif code == "Hydrotreater":
            after["throughput"] = round(param["throughput"] * 0.85, 2)
            after["flow_rate"] = round(param["flow_rate"] * 0.85, 2)
            after["energy_consumption"] = round(param["energy_consumption"] * 0.88, 2)
        elif code == "Storage Terminal":
            after["throughput"] = round(param["throughput"] * 0.80, 2)
            after["flow_rate"] = round(param["flow_rate"] * 0.80, 2)
            
        after_state[code] = after
        
    return after_state, 85, "FCC"

def apply_throughput_increase(before_state):
    """
    Refinery-wide 10% crude throughput increase:
    - CDU throughput +10%, VDU +10%, FCC +10%, Hydrotreater +10%.
    - Pressures and temperatures increase due to system loading.
    - Yields drop slightly due to lower residence time / conversion efficiency.
    - Energy consumption rises.
    """
    after_state = {}
    bottleneck = None
    max_hydrotreater_capacity = 25000.0 # Design capacity limit
    
    for code, param in before_state.items():
        after = dict(param)
        if code in ["CDU", "VDU", "FCC", "Hydrotreater"]:
            new_tp = param["throughput"] * 1.10
            after["throughput"] = round(new_tp, 2)
            after["flow_rate"] = round(param["flow_rate"] * 1.10, 2)
            after["energy_consumption"] = round(param["energy_consumption"] * 1.12, 2)
            
            # Stress variables
            if code == "CDU":
                after["pressure"] = round(param["pressure"] * 1.15, 2)
                after["temperature"] = round(param["temperature"] * 1.05, 2)
                after["yield"] = round(param["yield"] - 1.5, 2)
            elif code == "VDU":
                after["pressure"] = round(param["pressure"] * 1.10, 2)
                after["temperature"] = round(param["temperature"] * 1.04, 2)
                after["yield"] = round(param["yield"] - 1.0, 2)
            elif code == "FCC":
                after["pressure"] = round(param["pressure"] * 1.08, 2)
                after["temperature"] = round(param["temperature"] * 1.03, 2)
                after["yield"] = round(param["yield"] - 2.0, 2)
            elif code == "Hydrotreater":
                after["pressure"] = round(param["pressure"] * 1.20, 2)
                after["temperature"] = round(param["temperature"] * 1.06, 2)
                # Check for capacity bottleneck
                if new_tp > max_hydrotreater_capacity:
                    bottleneck = "Hydrotreater"
        elif code == "Storage Terminal":
            after["throughput"] = round(param["throughput"] * 1.10, 2)
            after["flow_rate"] = round(param["flow_rate"] * 1.10, 2)
            
        after_state[code] = after
        
    risk_score = 55 if bottleneck else 35
    return after_state, risk_score, bottleneck or "None"

def apply_maintenance_delay(before_state):
    """
    Maintenance Delay scenario on CDU:
    - CDU downtime increases (representing unexpected micro-outages/leaks).
    - Yield and throughput remain stable initially.
    - Risk score rises significantly due to probability of catastrophic failure.
    """
    after_state = {}
    for code, param in before_state.items():
        after = dict(param)
        if code == "CDU":
            after["downtime"] = round(param["downtime"] + 6.0, 2)
            after["pressure"] = round(param["pressure"] * 1.08, 2) # rising pressure due to fouling
        after_state[code] = after
        
    return after_state, 70, "CDU"

def apply_energy_reduction(before_state):
    """
    Energy supply reduction scenario (-20% electricity cap):
    - All units reduce throughput by 20%.
    - Temperatures drop slightly.
    - Downtime increases (idle time waiting for energy window).
    """
    after_state = {}
    for code, param in before_state.items():
        after = dict(param)
        if code != "Storage Terminal":
            after["throughput"] = round(param["throughput"] * 0.80, 2)
            after["flow_rate"] = round(param["flow_rate"] * 0.80, 2)
            after["energy_consumption"] = round(param["energy_consumption"] * 0.80, 2)
            after["pressure"] = round(param["pressure"] * 0.85, 2)
            after["temperature"] = round(param["temperature"] * 0.95, 2)
            after["downtime"] = round(param["downtime"] + 4.0, 2)
            after["yield"] = round(param["yield"] - 1.0, 2)
        else:
            after["throughput"] = round(param["throughput"] * 0.90, 2)
            after["flow_rate"] = round(param["flow_rate"] * 0.90, 2)
            
        after_state[code] = after
        
    return after_state, 60, "Global Power Grid"

def apply_demand_increase(before_state):
    """
    High market demand scenario:
    - CDU, FCC, and Hydrotreater pushed to run faster (+5% to +8% throughputs).
    - Energy consumption spikes.
    - Yields optimized for high-value targets (FCC yield +1.5%).
    - Storage throughput spikes by 15%.
    """
    after_state = {}
    bottleneck = None
    
    # Capacity thresholds
    capacities = {"CDU": 100000.0, "VDU": 45000.0, "FCC": 35000.0, "Hydrotreater": 25000.0}
    
    for code, param in before_state.items():
        after = dict(param)
        if code == "CDU":
            new_tp = param["throughput"] * 1.05
            after["throughput"] = round(new_tp, 2)
            after["flow_rate"] = round(param["flow_rate"] * 1.05, 2)
            after["energy_consumption"] = round(param["energy_consumption"] * 1.08, 2)
            if new_tp > capacities[code]:
                bottleneck = "CDU"
        elif code == "VDU":
            new_tp = param["throughput"] * 1.04
            after["throughput"] = round(new_tp, 2)
            after["flow_rate"] = round(param["flow_rate"] * 1.04, 2)
            if new_tp > capacities[code]:
                bottleneck = "VDU"
        elif code == "FCC":
            new_tp = param["throughput"] * 1.08
            after["throughput"] = round(new_tp, 2)
            after["flow_rate"] = round(param["flow_rate"] * 1.08, 2)
            after["energy_consumption"] = round(param["energy_consumption"] * 1.15, 2)
            after["yield"] = round(param["yield"] + 1.5, 2) # optimized cracking
            if new_tp > capacities[code]:
                bottleneck = "FCC"
        elif code == "Hydrotreater":
            new_tp = param["throughput"] * 1.08
            after["throughput"] = round(new_tp, 2)
            after["flow_rate"] = round(param["flow_rate"] * 1.08, 2)
            if new_tp > capacities[code]:
                bottleneck = "Hydrotreater"
        elif code == "Storage Terminal":
            after["throughput"] = round(param["throughput"] * 1.15, 2)
            after["flow_rate"] = round(param["flow_rate"] * 1.15, 2)
            after["energy_consumption"] = round(param["energy_consumption"] * 1.10, 2)
            
        after_state[code] = after
        
    risk_score = 45 if bottleneck else 25
    return after_state, risk_score, bottleneck or "None"

def get_rule_executor(scenario_type):
    executors = {
        "FCC_SHUTDOWN": apply_fcc_shutdown,
        "THROUGHPUT_INCREASE": apply_throughput_increase,
        "MAINTENANCE_DELAY": apply_maintenance_delay,
        "ENERGY_REDUCTION": apply_energy_reduction,
        "DEMAND_INCREASE": apply_demand_increase
    }
    return executors.get(scenario_type)
