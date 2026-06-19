"""
Engineering Analyzer Layer for RDIS.
Compares retrieved database metrics against engineering_rules.json boundaries.
Flags parameters as NORMAL, WARNING, or CRITICAL and highlights observed concerns.
"""
import json
from pathlib import Path
from typing import Dict, Any, Tuple, List

_KB_PATH = Path(__file__).resolve().parent / 'engineering_rules.json'
try:
    _KB = json.loads(_KB_PATH.read_text())
except Exception:
    _KB = {}

# Parameter mapping from database key to engineering_rules.json key
PARAM_MAP = {
    "CDU": {
        "throughput": "throughput_bpd",
        "flow_rate": "flow_rate_bph",
        "temperature": "temperature_F",
        "pressure": "pressure_psi",
        "yield": "yield_pct"
    },
    "VDU": {
        "throughput": "throughput_bpd",
        "flow_rate": "flow_rate_bph",
        "pressure": "pressure_psi",
        "vacuum": "vacuum_inHg"
    },
    "FCC": {
        "throughput": "throughput_bpd",
        "flow_rate": "flow_rate_bph",
        "temperature": "reactor_temp_F",
        "yield": "gasoline_yield_pct"
    },
    "Hydrotreater": {
        "throughput": "throughput_bpd",
        "flow_rate": "flow_rate_bph",
        "temperature": "temperature_F",
        "pressure": "pressure_psi"
    },
    "Storage Terminal": {
        "yield": "tank_utilization_pct",
        "throughput": "transfer_limit_bpd",
        "flow_rate": "flow_rate_bph"
    }
}

def analyze_parameter(unit: str, param_db_key: str, value: float) -> Dict[str, Any]:
    """
    Compares a parameter value against rules and returns a dict with:
    - current: float
    - status: "NORMAL" | "WARNING" | "CRITICAL"
    - expected_range: str
    - concern: str or None
    """
    kb_unit = _KB.get(unit, {})
    param_map = PARAM_MAP.get(unit, {})
    rules_key = param_map.get(param_db_key)
    
    # Defaults if no rules found
    res = {
        "current": value,
        "status": "NORMAL",
        "expected_range": "N/A",
        "concern": None
    }
    
    if not kb_unit or not rules_key:
        return res
        
    # Get bounds
    bounds = kb_unit.get(rules_key)
    rec_range = kb_unit.get("recommended_ranges", {}).get(rules_key)
    warn = kb_unit.get("warning_thresholds", {})
    crit = kb_unit.get("critical_thresholds", {})
    limits = kb_unit.get("operating_limits", {})
    
    # Establish expected display range
    if rec_range:
        res["expected_range"] = f"{rec_range[0]} - {rec_range[1]}"
    elif bounds:
        res["expected_range"] = f"{bounds[0]} - {bounds[1]}"
        
    # Heuristics to determine status
    status = "NORMAL"
    concern = None
    
    # Check bounds or thresholds depending on parameter key
    val = float(value)
    
    # Throughput high thresholds
    if rules_key == "throughput_bpd":
        if limits.get("max_throughput_bpd") and val > limits["max_throughput_bpd"]:
            status = "CRITICAL"
            concern = f"{unit} throughput ({val} BPD) exceeds absolute design limit ({limits['max_throughput_bpd']} BPD)."
        elif crit.get("throughput_max_bpd") and val > crit["throughput_max_bpd"]:
            status = "CRITICAL"
            concern = f"{unit} throughput ({val} BPD) exceeds critical safe operational threshold ({crit['throughput_max_bpd']} BPD)."
        elif warn.get("throughput_high_bpd") and val > warn["throughput_high_bpd"]:
            status = "WARNING"
            concern = f"{unit} throughput ({val} BPD) is approaching limit. Recommended range is {rec_range[0]}-{rec_range[1]} BPD."
        elif rec_range and (val < rec_range[0] or val > rec_range[1]):
            # If slightly out of rec range but under warning, mark as normal or warning
            status = "NORMAL"
            
    # Flow rate high thresholds
    elif rules_key == "flow_rate_bph":
        max_limit = limits.get("max_flow_rate_bph")
        max_crit = crit.get("flow_rate_max_bph")
        max_warn = warn.get("flow_rate_high_bph")
        
        if max_limit and val > max_limit:
            status = "CRITICAL"
            concern = f"{unit} operating flow rate ({val} BPH) exceeds maximum design limit ({max_limit} BPH)."
        elif max_crit and val > max_crit:
            status = "CRITICAL"
            concern = f"{unit} operating flow rate ({val} BPH) exceeds critical safety threshold ({max_crit} BPH)."
        elif max_warn and val > max_warn:
            status = "WARNING"
            concern = f"{unit} operating flow rate ({val} BPH) is high. Recommended range is {rec_range[0]}-{rec_range[1]} BPH."
        elif rec_range and (val < rec_range[0] or val > rec_range[1]):
            if val < rec_range[0]:
                status = "WARNING"
                concern = f"{unit} operating flow rate ({val} BPH) is below recommended range ({rec_range[0]}-{rec_range[1]} BPH)."
            elif val > rec_range[1]:
                status = "WARNING"
                concern = f"{unit} operating flow rate ({val} BPH) is above recommended range ({rec_range[0]}-{rec_range[1]} BPH)."

    # Temperature high thresholds
    elif rules_key in ["temperature_F", "reactor_temp_F"]:
        max_limit = limits.get("max_temperature_F") or limits.get("max_reactor_temp_F")
        max_crit = crit.get("temperature_max_F") or crit.get("reactor_temp_max_F")
        max_warn = warn.get("temperature_high_F") or warn.get("reactor_temp_high_F")
        
        if max_limit and val > max_limit:
            status = "CRITICAL"
            concern = f"{unit} operating temperature ({val}°F) exceeds maximum safety limit ({max_limit}°F)."
        elif max_crit and val > max_crit:
            status = "CRITICAL"
            concern = f"{unit} operating temperature ({val}°F) exceeds critical thermal threshold ({max_crit}°F)."
        elif max_warn and val > max_warn:
            status = "WARNING"
            concern = f"{unit} operating temperature ({val}°F) is higher than recommended. Normal range is {rec_range[0]}-{rec_range[1]}°F."
        elif rec_range and (val < rec_range[0] or val > rec_range[1]):
            # Check for under/over-temperature concerns
            if val < rec_range[0]:
                status = "WARNING"
                concern = f"{unit} operating temperature ({val}°F) is below optimal range ({rec_range[0]}-{rec_range[1]}°F)."
            elif val > rec_range[1]:
                status = "WARNING"
                concern = f"{unit} operating temperature ({val}°F) is above optimal range ({rec_range[0]}-{rec_range[1]}°F)."
            
    # Pressure high thresholds
    elif rules_key == "pressure_psi":
        max_limit = limits.get("max_pressure_psi")
        max_crit = crit.get("pressure_max_psi") or crit.get("pressure_crit_psi")
        max_warn = warn.get("pressure_high_psi")
        
        if max_limit and val > max_limit:
            status = "CRITICAL"
            concern = f"{unit} operating pressure ({val} psi) exceeds mechanical vessel limit ({max_limit} psi)."
        elif max_crit and val > max_crit:
            status = "CRITICAL"
            concern = f"{unit} operating pressure ({val} psi) exceeds critical relief valve setting ({max_crit} psi)."
        elif max_warn and val > max_warn:
            status = "WARNING"
            concern = f"{unit} operating pressure ({val} psi) exceeds normal bounds. Recommended range is {rec_range[0]}-{rec_range[1]} psi."
            
    # Tank utilization
    elif rules_key == "tank_utilization_pct":
        max_limit = limits.get("max_tank_utilization_pct")
        max_crit = crit.get("tank_utilization_crit_pct")
        max_warn = warn.get("tank_utilization_high_pct")
        
        if max_limit and val > max_limit:
            status = "CRITICAL"
            concern = f"{unit} storage tank utilization ({val}%) exceeds physical containment limit ({max_limit}%)."
        elif max_crit and val > max_crit:
            status = "CRITICAL"
            concern = f"{unit} storage tank utilization ({val}%) exceeds critical warning limit ({max_crit}%)."
        elif max_warn and val > max_warn:
            status = "WARNING"
            concern = f"{unit} storage tank utilization ({val}%) is elevated. Recommended operating range is {rec_range[0]}-{rec_range[1]}%."

    # Yield checks (under-performing yield is a warning)
    elif rules_key in ["yield_pct", "gasoline_yield_pct"]:
        if rec_range and val < rec_range[0]:
            status = "WARNING"
            concern = f"{unit} product yield ({val}%) is below optimal refinery target ({rec_range[0]}%)."
            
    # Fallback bounds check
    if status == "NORMAL" and bounds:
        if val < bounds[0] or val > bounds[1]:
            status = "WARNING"
            concern = f"{unit} parameter ({val}) is out of absolute rule boundary [{bounds[0]}, {bounds[1]}]."
            
    res["status"] = status
    res["concern"] = concern
    return res

def analyze_unit_state(unit: str, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Performs batch parameter audits for a given unit.
    """
    analysis_results = []
    for k, v in metrics.items():
        if k in ["throughput", "temperature", "pressure", "yield", "flow_rate"]:
            res = analyze_parameter(unit, k, v)
            if res.get("concern"):
                res["parameter"] = k
                analysis_results.append(res)
    return analysis_results
