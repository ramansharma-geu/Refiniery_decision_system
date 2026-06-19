"""
Engineering rules engine module (Simulation Engine V3) for hypothetical scenarios.
Computes estimated parameters using current DB values, engineering rules JSON, and process scaling formulas.

KEY DESIGN DECISIONS:
- throughput = total volume processed per day (BPD)
- flow_rate = instantaneous volumetric flow (BPH ≈ throughput/24)
- temperature stored in °F internally, displayed in °C
- pressure stored in psi internally, displayed in bar
- All sanity checks clamp values to physical operating limits
"""
from typing import Dict, Any, List, Optional
import json
from pathlib import Path

# Load engineering rules KB
_KB_PATH = Path(__file__).resolve().parent / 'engineering_rules.json'
try:
    _KB = json.loads(_KB_PATH.read_text())
except Exception:
    _KB = {}

# ── Unit conversion helpers ──────────────────────────────────────────────
def f_to_c(f: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return round((f - 32) * 5.0 / 9.0, 1)

def c_to_f(c: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return round(c * 9.0 / 5.0 + 32, 1)

def psi_to_bar(psi: float) -> float:
    """Convert PSI to bar."""
    return round(psi * 0.0689476, 2)

def bar_to_psi(bar: float) -> float:
    """Convert bar to PSI."""
    return round(bar / 0.0689476, 2)

def bph_to_bpd(bph: float) -> float:
    """Convert barrels per hour to barrels per day."""
    return round(bph * 24.0, 1)

def bpd_to_bph(bpd: float) -> float:
    """Convert barrels per day to barrels per hour."""
    return round(bpd / 24.0, 1)

# ── Design capacity limits (BPD) ────────────────────────────────────────
DESIGN_CAPACITY_BPD = {
    'CDU': 100000.0,
    'VDU': 45000.0,
    'FCC': 40000.0,
    'Hydrotreater': 30000.0,
    'Storage Terminal': 150000.0,
}

# ── Absolute Physical Refinery Limits ───────────────────────────────────
# Temperatures stored in °F, pressures in psi. Clamped to guarantee realistic values.
PHYSICAL_LIMITS = {
    'CDU': {
        'temp_min': 550.0, 'temp_max': 849.9,
        'press_min': 5.0, 'press_max': 64.9
    },
    'VDU': {
        'temp_min': 650.0, 'temp_max': 849.9,
        'press_min': 0.1, 'press_max': 4.9
    },
    'FCC': {
        'temp_min': 900.0, 'temp_max': 1099.9,
        'press_min': 10.0, 'press_max': 54.9
    },
    'Hydrotreater': {
        'temp_min': 550.0, 'temp_max': 849.9,
        'press_min': 500.0, 'press_max': 1299.0
    },
    'Storage Terminal': {
        'temp_min': 40.0, 'temp_max': 109.9,
        'press_min': 5.0, 'press_max': 39.9
    }
}

# ── Sanity bounds ────────────────────────────────────────────────────────
MAX_FLOW_RATIO = 3.0       # No more than 3× current throughput
MIN_FLOW_RATIO = 0.1       # No less than 10% of current throughput
MAX_ENERGY_PCT_CHANGE = 50.0  # Cap energy change at ±50%


def _get_bounds(unit: str) -> dict:
    """Get engineering rules for a unit."""
    if not unit:
        return {}
    unit_upper = unit.upper()
    if 'STORAGE' in unit_upper or 'TERMINAL' in unit_upper:
        return _KB.get('Storage Terminal', {})
    if 'HYDRO' in unit_upper:
        return _KB.get('Hydrotreater', {})
    return _KB.get(unit_upper, {})


def estimate_parameters(unit: str, changes: Dict[str, float], current_values: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Estimate refinery operating parameters using current values (if available),
    engineering rules JSON, and chemical engineering scaling formulas.
    
    Changes can include:
        throughput_bpd: target throughput in BPD
        flow_rate_bph: target flow rate in BPH
        temperature_C_delta: temperature change in °C (converted to °F internally)
        pressure_pct: pressure change percentage
        heater_duty_pct_change: heater duty change %
        api_gravity_delta: API gravity change
        sulfur_feed_mult: sulfur feed multiplier
        catalyst_activity_pct_change: catalyst activity change %
        tank_utilization_pct: target tank utilization %
    """
    if not unit:
        unit = 'CDU'
    unit_upper = unit.upper()
    if unit_upper == 'CDU': unit = 'CDU'
    elif unit_upper == 'VDU': unit = 'VDU'
    elif unit_upper == 'FCC': unit = 'FCC'
    elif 'HYDRO' in unit_upper: unit = 'Hydrotreater'
    elif 'STORAGE' in unit_upper or 'TERMINAL' in unit_upper: unit = 'Storage Terminal'

    kb = _get_bounds(unit)
    changes = changes or {}
    current_values = current_values or {}

    def mid(bounds) -> float:
        if not bounds or not isinstance(bounds, list) or len(bounds) < 2:
            return 1.0
        return (bounds[0] + bounds[1]) / 2.0

    # ── 1. Establish current baseline values from DB or fallbacks ────────
    if unit == 'CDU':
        c_tp = float(current_values.get('throughput') or mid(kb.get('throughput_bpd')) or 80000.0)
        c_flow = float(current_values.get('flow_rate') or bpd_to_bph(c_tp))
        c_temp = float(current_values.get('temperature') or mid(kb.get('temperature_F')) or 700.0)
        c_press = float(current_values.get('pressure') or mid(kb.get('pressure_psi')) or 40.0)
        c_yield = float(current_values.get('yield') or mid(kb.get('yield_pct')) or 92.0)
        c_energy = float(current_values.get('energy_consumption') or 200.0)
    elif unit == 'VDU':
        c_tp = float(current_values.get('throughput') or mid(kb.get('throughput_bpd')) or 36000.0)
        c_flow = float(current_values.get('flow_rate') or bpd_to_bph(c_tp))
        c_temp = float(current_values.get('temperature') or mid(kb.get('temperature_F')) or 750.0)
        c_press = float(current_values.get('pressure') or mid(kb.get('pressure_psi')) or 1.0)
        c_yield = float(current_values.get('yield') or mid(kb.get('yield_pct')) or 88.0)
        c_energy = float(current_values.get('energy_consumption') or 140.0)
    elif unit == 'FCC':
        c_tp = float(current_values.get('throughput') or mid(kb.get('throughput_bpd')) or 28000.0)
        c_flow = float(current_values.get('flow_rate') or bpd_to_bph(c_tp))
        c_temp = float(current_values.get('temperature') or mid(kb.get('reactor_temp_F')) or 1000.0)
        c_press = float(current_values.get('pressure') or mid(kb.get('pressure_psi')) or 30.0)
        c_yield = float(current_values.get('yield') or mid(kb.get('gasoline_yield_pct')) or 80.0)
        c_energy = float(current_values.get('energy_consumption') or 260.0)
    elif unit == 'Hydrotreater':
        c_tp = float(current_values.get('throughput') or mid(kb.get('throughput_bpd')) or 20000.0)
        c_flow = float(current_values.get('flow_rate') or bpd_to_bph(c_tp))
        c_temp = float(current_values.get('temperature') or mid(kb.get('temperature_F')) or 650.0)
        c_press = float(current_values.get('pressure') or mid(kb.get('pressure_psi')) or 800.0)
        c_yield = float(current_values.get('yield') or mid(kb.get('yield_pct')) or 98.0)
        c_energy = float(current_values.get('energy_consumption') or 110.0)
    else:  # Storage Terminal
        c_tp = float(current_values.get('throughput') or mid(kb.get('throughput_bpd')) or 120000.0)
        c_flow = float(current_values.get('flow_rate') or bpd_to_bph(c_tp))
        c_temp = float(current_values.get('temperature') or 75.0)
        c_press = float(current_values.get('pressure') or 18.0)
        c_yield = float(current_values.get('yield') or 99.9)
        c_energy = float(current_values.get('energy_consumption') or 20.0)
        # Storage Terminal uses yield field as tank utilization
    
    c_util = float(current_values.get('yield') or 55.0) if unit == 'Storage Terminal' else 0.0

    # ── 2. Determine target throughput & flow rate ──────────────────────
    t_flow = c_flow
    t_tp = c_tp
    flow_ratio = 1.0

    # Decouple flow rate and throughput target adjustments
    if 'flow_rate_bph' in changes and changes['flow_rate_bph'] is not None:
        t_flow = float(changes['flow_rate_bph'])
        if c_flow > 0:
            flow_ratio = t_flow / c_flow
    elif 'throughput_bpd' in changes and changes['throughput_bpd'] is not None:
        t_tp = float(changes['throughput_bpd'])
        design_cap = DESIGN_CAPACITY_BPD.get(unit, 150000.0)
        if t_tp > design_cap:
            t_tp = design_cap
        if t_tp < 0:
            t_tp = 0.0
        if c_tp > 0:
            flow_ratio = t_tp / c_tp
        t_flow = bpd_to_bph(t_tp)
    elif 'flow_rate_bpd' in changes and changes['flow_rate_bpd'] is not None:
        t_tp = float(changes['flow_rate_bpd'])
        design_cap = DESIGN_CAPACITY_BPD.get(unit, 150000.0)
        if t_tp > design_cap:
            t_tp = design_cap
        if t_tp < 0:
            t_tp = 0.0
        if c_tp > 0:
            flow_ratio = t_tp / c_tp
        t_flow = bpd_to_bph(t_tp)

    # Clamp flow ratio to prevent unrealistic scaling
    flow_ratio = max(MIN_FLOW_RATIO, min(MAX_FLOW_RATIO, flow_ratio))

    # ── 3. Estimate temperature (internal: °F) ──────────────────────────
    base_temp = c_temp
    
    if 'temperature_target_f' in changes and changes['temperature_target_f'] is not None:
        t_temp = float(changes['temperature_target_f'])
    elif 'temperature_target_c' in changes and changes['temperature_target_c'] is not None:
        t_temp = c_to_f(float(changes['temperature_target_c']))
    elif 'temperature_C_delta' in changes and changes['temperature_C_delta'] is not None:
        t_temp = base_temp + float(changes['temperature_C_delta']) * 1.8
    elif 'temperature_F_delta' in changes and changes['temperature_F_delta'] is not None:
        t_temp = base_temp + float(changes['temperature_F_delta'])
    else:
        # Scale temperature slightly with flow rate
        if unit in ['CDU', 'VDU']:
            t_temp = base_temp * (1.0 + 0.04 * (flow_ratio - 1.0))
        elif unit == 'FCC':
            t_temp = base_temp * (1.0 + 0.03 * (flow_ratio - 1.0))
        elif unit == 'Hydrotreater':
            t_temp = base_temp * (1.0 + 0.02 * (flow_ratio - 1.0))
        else:
            t_temp = base_temp

    # Specific overrides
    if 'heater_duty_pct_change' in changes:
        t_temp = base_temp * (1.0 + changes['heater_duty_pct_change'] / 100.0)
    if 'api_gravity_delta' in changes:
        t_temp = base_temp - 3.0 * changes['api_gravity_delta']

    # Physical Limits Clamping for Temperature
    lims = PHYSICAL_LIMITS.get(unit, {'temp_min': 40.0, 'temp_max': 1200.0})
    t_temp = max(lims['temp_min'], min(lims['temp_max'], t_temp))

    # ── 4. Estimate pressure (internal: psi) ────────────────────────────
    base_press = c_press

    if 'pressure_target_psi' in changes and changes['pressure_target_psi'] is not None:
        t_press = float(changes['pressure_target_psi'])
    elif 'pressure_target_bar' in changes and changes['pressure_target_bar'] is not None:
        t_press = bar_to_psi(float(changes['pressure_target_bar']))
    elif 'pressure_psi_delta' in changes and changes['pressure_psi_delta'] is not None:
        t_press = base_press + float(changes['pressure_psi_delta'])
    elif 'pressure_bar_delta' in changes and changes['pressure_bar_delta'] is not None:
        t_press = base_press + bar_to_psi(float(changes['pressure_bar_delta']))
    elif 'pressure_pct' in changes and changes['pressure_pct'] is not None:
        t_press = base_press * (1.0 + float(changes['pressure_pct']) / 100.0)
    else:
        if unit == 'Hydrotreater':
            t_press = base_press * (1.0 + 0.15 * (flow_ratio - 1.0))
        elif unit in ['CDU', 'VDU', 'FCC']:
            t_press = base_press * (1.0 + 0.08 * (flow_ratio - 1.0))
        else:
            t_press = base_press

    if unit == 'Hydrotreater' and 'sulfur_feed_mult' in changes:
        t_press *= (1.0 + 0.1 * (changes['sulfur_feed_mult'] - 1.0))

    # Physical Limits Clamping for Pressure
    lims = PHYSICAL_LIMITS.get(unit, {'press_min': 0.1, 'press_max': 2000.0})
    t_press = max(lims['press_min'], min(lims['press_max'], t_press))

    # ── 5. Estimate yield ────────────────────────────────────────────────
    if unit == 'FCC' and 'catalyst_activity_pct_change' in changes:
        t_yield = c_yield + 0.3 * changes['catalyst_activity_pct_change']
    elif unit == 'VDU' and 'pressure_pct' in changes and changes['pressure_pct'] > 0:
        t_yield = c_yield - 0.2 * changes['pressure_pct']
    elif unit == 'Hydrotreater' and 'sulfur_feed_mult' in changes:
        t_yield = c_yield - 0.5 * (changes['sulfur_feed_mult'] - 1.0)
    else:
        if flow_ratio > 1.0:
            t_yield = c_yield - 1.5 * (flow_ratio - 1.0)
        else:
            t_yield = c_yield
    
    t_yield = max(0.0, min(100.0, t_yield))

    # ── 6. Estimate energy consumption % change ─────────────────────────
    if 'heater_duty_pct_change' in changes:
        t_energy_pct = changes['heater_duty_pct_change']
    else:
        if flow_ratio != 1.0:
            t_energy_pct = round(100.0 * (flow_ratio - 1.0) * 1.25, 1)
        else:
            t_energy_pct = round(100.0 * (t_temp - c_temp) / c_temp * 2.0, 1) if c_temp > 0 else 0.0

    # Clamp energy change
    t_energy_pct = max(-MAX_ENERGY_PCT_CHANGE, min(MAX_ENERGY_PCT_CHANGE, t_energy_pct))

    # Tank utilization (Storage Terminal specific)
    t_util = float(changes.get('tank_utilization_pct') if changes.get('tank_utilization_pct') is not None else c_util)

    # ── 7. Build recommended parameter ranges ────────────────────────────
    def get_range_str(val: float, bounds_key: str, tol_pct: float = 2.0) -> str:
        """Return a range string clamped to engineering bounds."""
        bounds = kb.get(bounds_key)
        if bounds:
            if val >= bounds[1]:
                return f"{round(bounds[1] * 0.95, 1)} – {round(bounds[1], 1)} (at design limit)"
            if val <= bounds[0]:
                return f"{round(bounds[0], 1)} – {round(bounds[0] * 1.05, 1)} (at minimum)"
            low = max(bounds[0], val * (1.0 - tol_pct / 100.0))
            high = min(bounds[1], val * (1.0 + tol_pct / 100.0))
            if low > high:
                low = high
            return f"{round(low, 1)} – {round(high, 1)}"
        return f"{round(val * 0.98, 1)} – {round(val * 1.02, 1)}"

    # Convert to display units (°C and bar)
    c_temp_c = f_to_c(c_temp)
    t_temp_c = f_to_c(t_temp)
    c_press_bar = psi_to_bar(c_press)
    t_press_bar = psi_to_bar(t_press)
    # Build current conditions dict (display units)
    # flow_rate is stored in BPH in the database — display as-is
    current_display = {
        'flow_rate_bph': round(c_flow, 1),
        'throughput_bpd': round(c_tp, 1),
        'temperature_c': c_temp_c,
        'pressure_bar': c_press_bar,
        'yield_pct': round(c_yield, 1),
        'energy_mwh': round(c_energy, 1),
    }

    # Build target conditions dict (display units)
    target_display = {
        'throughput_bpd': round(t_tp, 1),
        'flow_rate_bph': round(t_flow, 1),
    }

    # Build parameter adjustment ranges in display units
    lims = PHYSICAL_LIMITS.get(unit, {'temp_min': 40.0, 'temp_max': 1200.0, 'press_min': 0.1, 'press_max': 2000.0})
    t_temp_low = max(lims['temp_min'], min(lims['temp_max'], t_temp * 0.98))
    t_temp_high = max(lims['temp_min'], min(lims['temp_max'], t_temp * 1.02))
    t_press_low = max(lims['press_min'], min(lims['press_max'], t_press * 0.98))
    t_press_high = max(lims['press_min'], min(lims['press_max'], t_press * 1.02))

    t_temp_low_c = f_to_c(t_temp_low)
    t_temp_high_c = f_to_c(t_temp_high)
    t_press_low_bar = psi_to_bar(t_press_low)
    t_press_high_bar = psi_to_bar(t_press_high)

    adjustments = {
        'temperature_range_c': f"{t_temp_low_c} – {t_temp_high_c}°C",
        'pressure_range_bar': f"{t_press_low_bar} – {t_press_high_bar} bar",
        'energy_pct_change': f"{'+' if t_energy_pct >= 0 else ''}{t_energy_pct}%",
    }

    if unit == 'FCC':
        cat_ratio = max(5.0, min(10.0, 6.0 + 1.0 * (flow_ratio - 1.0)))
        if 'catalyst_activity_pct_change' in changes:
            cat_ratio = max(5.0, min(10.0, cat_ratio * (1.0 + changes['catalyst_activity_pct_change'] / 100.0)))
        adjustments['catalyst_ratio'] = f"{round(cat_ratio, 2)} – {round(cat_ratio * 1.05, 2)}"

    if unit == 'Hydrotreater':
        h_rate = max(100.0, min(1000.0, 500.0 * flow_ratio))
        if 'sulfur_feed_mult' in changes:
            h_rate = min(1000.0, h_rate * changes['sulfur_feed_mult'])
        adjustments['hydrogen_rate_norm'] = f"{int(h_rate * 0.98)} – {int(h_rate * 1.02)}"

    if unit == 'Storage Terminal':
        adjustments['tank_utilization_pct'] = get_range_str(t_util, 'tank_utilization_pct')

    # ── 8. Generate consequences, risks, and recommendations ─────────────
    consequences = []
    risks = []
    recommendations = []

    # High flow rates
    if flow_ratio > 1.15:
        consequences.append(f"Energy consumption {'+' if t_energy_pct >= 0 else ''}{t_energy_pct}%")
        consequences.append(f"Increased furnace duty on {unit}")
        risks.append("Column flooding risk")
        risks.append("Increased pressure drop across trays")
        recommendations.append("Increase feed gradually in 5% steps")
        recommendations.append("Monitor column differential pressure")
    elif flow_ratio < 0.85:
        consequences.append(f"Reduced vapor velocities in {unit}")
        consequences.append(f"Energy consumption {'+' if t_energy_pct >= 0 else ''}{t_energy_pct}%")
        risks.append("Tray weeping and poor fractionation")
        recommendations.append("Adjust reflux ratios and furnace firing")
    else:
        consequences.append(f"Energy consumption {'+' if t_energy_pct >= 0 else ''}{t_energy_pct}%")
        consequences.append(f"{unit} parameters within normal operating window")

    # Unit-specific checks
    if unit == 'CDU':
        if 'api_gravity_delta' in changes and changes['api_gravity_delta'] < 0:
            risks.append("Overloading downstream VDU with heavier bottoms")
            recommendations.append("Trim throughput 5–10% and adjust stripping steam")
        if t_temp > 780:
            risks.append("Furnace outlet near metallurgical limits")
            recommendations.append("Check furnace tube skin temperatures")

    elif unit == 'VDU':
        if 'pressure_pct' in changes and changes['pressure_pct'] > 15:
            risks.append("Thermal cracking of heavy residue")
            recommendations.append("Inspect vacuum ejector motive steam pressure")

    elif unit == 'FCC':
        if 'catalyst_activity_pct_change' in changes and changes['catalyst_activity_pct_change'] < 0:
            risks.append("Increased slurry oil production")
            recommendations.append("Increase catalyst fresh make-up rate")

    elif unit == 'Hydrotreater':
        if 'sulfur_feed_mult' in changes and changes['sulfur_feed_mult'] >= 1.8:
            risks.append("Catalyst bed temperature runaway")
            recommendations.append("Increase recycle gas rate and step up quench flows")

    elif unit == 'Storage Terminal':
        if t_util >= 90.0:
            risks.append("Tank overflow hazard and demurrage penalties")
            recommendations.append("Divert incoming shipments and expedite export pumps")

    # Fallbacks
    if not risks:
        risks.append("No immediate risks identified — monitor during transition")
    if not recommendations:
        recommendations.append("Maintain routine checks and log metric deltas")

    # Compatibility keys for older unit tests
    recommended_params = {
        'Throughput_bpd': round(t_tp, 1),
        'Temperature_F': round(t_temp, 1),
        'Pressure_psi': round(t_press, 2),
        'Yield_pct': round(t_yield, 1),
    }

    return {
        'current_display': current_display,
        'target_display': target_display,
        'adjustments': adjustments,
        'consequences': consequences,
        'risks': risks,
        'recommendations': recommendations,
        'Recommended Parameters': recommended_params,
        'Possible Consequences': consequences,
        'Operational Risks': risks,
        'internal': {
            'flow_ratio': round(flow_ratio, 3),
            'c_tp': c_tp,
            't_tp': t_tp,
            'c_temp_f': c_temp,
            't_temp_f': t_temp,
            'c_press_psi': c_press,
            't_press_psi': t_press,
            't_yield': round(t_yield, 1),
            't_energy_pct': t_energy_pct,
        }
    }
