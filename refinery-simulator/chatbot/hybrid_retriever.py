# Hybrid Retriever & Query Executor for RDIS Chatbot
from services import db_service
from chatbot.parser import parse_query
from chatbot.intent_classifier import (
    detect_intent, INTENT_KNOWLEDGE, INTENT_CURRENT,
    INTENT_ANALYSIS, INTENT_SIMULATION, INTENT_MIXED,
    INTENT_OPERATIONAL_IMPACT, INTENT_SEVERITY_RANKING
)
from chatbot.knowledge_retriever import retrieve_facts
from simulation_engine import estimate_parameters
from models import db, RefineryUnit, OperationalHistory
from sqlalchemy import func
import json
import re


def _f_to_c(f):
    return round((float(f) - 32) * 5.0 / 9.0, 1)


def _psi_to_bar(psi):
    return round(float(psi) * 0.0689476, 2)


# ── Unit-specific engineering knowledge ─────────────────────────────────
UNIT_ENGINEERING = {
    "CDU": {
        "name": "Crude Distillation Unit",
        "process": "Atmospheric fractional distillation",
        "key_params": ["Furnace duty", "Flash zone temperature", "Reflux ratio", "Tray loading", "Column flooding", "Pressure drop"],
        "common_issues": ["Column flooding", "Tray weeping", "Furnace tube hot spots", "Overhead condenser fouling"],
        "safety_limits": {"temp_max": 800, "press_max": 60},
        "description": "Separates crude oil into fractions based on boiling points under atmospheric pressure."
    },
    "VDU": {
        "name": "Vacuum Distillation Unit",
        "process": "Vacuum distillation of atmospheric residue",
        "key_params": ["Vacuum pressure", "Vacuum ejectors", "Heater outlet temperature", "Heavy gas oil recovery"],
        "common_issues": ["Vacuum loss", "Ejector malfunction", "Thermal cracking", "Fouling"],
        "safety_limits": {"temp_max": 850, "press_max": 2.0},
        "description": "Distills atmospheric residue under deep vacuum to extract vacuum gas oils without thermal cracking."
    },
    "FCC": {
        "name": "Fluid Catalytic Cracking Unit",
        "process": "Catalytic cracking of heavy gas oils",
        "key_params": ["Catalyst circulation", "Reactor temperature", "Coke formation", "Regenerator", "Catalyst activity"],
        "common_issues": ["Catalyst deactivation", "Coke buildup", "Temperature runaway", "Air grid plugging"],
        "safety_limits": {"temp_max": 1005, "press_max": 55},
        "description": "Cracks heavy vacuum gas oils into lighter high-value products using a fluidized zeolite catalyst."
    },
    "Hydrotreater": {
        "name": "Hydrotreater Unit",
        "process": "Catalytic hydrodesulfurization",
        "key_params": ["Hydrogen partial pressure", "Sulfur removal", "Catalyst poisoning", "Reactor severity"],
        "common_issues": ["Catalyst bed plugging", "Hydrogen deficiency", "Sulfur breakthrough", "Bed temperature runaway"],
        "safety_limits": {"temp_max": 800, "press_max": 1200},
        "description": "Uses hydrogen to remove sulfur, nitrogen, and metals from petroleum fractions."
    },
    "Storage Terminal": {
        "name": "Storage Terminal",
        "process": "Inventory management and blending",
        "key_params": ["Tank utilization", "Inventory", "Overflow risk", "Dispatch", "Pump loading"],
        "common_issues": ["Tank overflow", "Demurrage delays", "Blending contamination", "Pump failure"],
        "safety_limits": {"util_max": 95},
        "description": "Manages crude feedstock inventory and finished product distribution."
    }
}

# ── Unit-specific expert analysis templates ─────────────────────────────
UNIT_EXPERT_ANALYSIS = {
    "CDU": {
        "high_throughput": {
            "causes": ["High liquid load exceeding tray design throughput", "Over-firing in the main heater furnace", "Flooding in wash zone trays"],
            "impacts": ["Main column trays flooding and entrainment", "Extreme furnace tube skin temperatures (hot spots)", "Poor fractionation quality"],
            "recs": ["Check column delta pressure differential", "Inspect furnace tube skins", "Decrease feed rate gradually"]
        },
        "high_pressure": {
            "causes": ["Overhead condenser fouling", "Accumulated non-condensable gas lock", "Reflux accumulator vent valve failure"],
            "impacts": ["Overhead relief valve lifting hazard", "Loss of light naphtha distillation cut separation", "Tray mechanical deflection"],
            "recs": ["Monitor overhead condenser inlet/outlet delta temperature", "Check non-condensable accumulator purge vents", "Slowly trim furnace firing"]
        },
        "high_temperature": {
            "causes": ["Furnace tube hot spots", "Excessive firing rate", "Poor heat distribution"],
            "impacts": ["Metallurgical failure risk", "Thermal cracking in transfer lines", "Tube rupture hazard"],
            "recs": ["Check furnace tube skin temperatures", "Reduce firing rate", "Inspect tube condition"]
        },
        "default": {
            "causes": ["Feedstock quality shift", "Instrument calibration error", "Process upset propagation"],
            "impacts": ["Product quality deviation", "Energy inefficiency", "Downstream unit impact"],
            "recs": ["Audit local field instrumentation", "Review lab product quality logs", "Adjust reflux ratios"]
        }
    },
    "VDU": {
        "high_throughput": {
            "causes": ["Feed rate exceeding vacuum column capacity", "Ejector capacity limitation", "Internal flooding"],
            "impacts": ["Reduced vacuum efficiency", "Heavy gas oil carryover to residue", "Increased energy consumption"],
            "recs": ["Verify ejector steam pressure", "Check vacuum column internals", "Reduce feed rate"]
        },
        "high_pressure": {
            "causes": ["Vacuum ejector malfunction", "Air leakage into system", "Condenser fouling"],
            "impacts": ["Loss of vacuum causing thermal cracking", "Reduced VGO yield", "Increased residue quality degradation"],
            "recs": ["Inspect ejector nozzles", "Check vacuum seals", "Clean condenser tubes"]
        },
        "default": {
            "causes": ["Ejector steam pressure variation", "Feed temperature fluctuation", "Internal tray damage"],
            "impacts": ["Vacuum instability", "Product quality variation", "Energy waste"],
            "recs": ["Monitor ejector performance", "Check steam conditions", "Inspect column internals"]
        }
    },
    "FCC": {
        "high_temperature": {
            "causes": ["Excessive riser temperature causing overcracking", "Regenerator air grid issue", "Catalyst bypass flow"],
            "impacts": ["Riser thermal runaway coking risk", "High dry gas yield and reduced gasoline selectivity", "Catalyst thermal damage"],
            "recs": ["Check riser quench injection", "Inspect catalyst circulation slides", "Calibrate temperature thermocouples"]
        },
        "low_yield": {
            "causes": ["Catalyst deactivation or poison carryover", "Feedstock heavy metal poisoning", "Stripper steam blockages"],
            "impacts": ["Reduced conversion gasoline yield", "Coke buildup in cyclone grids", "Increased catalyst replacement rate"],
            "recs": ["Increase catalyst fresh make-up rate", "Audit catalyst activity logs", "Check feed sulfur levels"]
        },
        "default": {
            "causes": ["Catalyst circulation imbalance", "Regenerator temperature deviation", "Feed nozzle erosion"],
            "impacts": ["Conversion efficiency loss", "Product slate shift", "Catalyst losses"],
            "recs": ["Monitor catalyst circulation rate", "Check regenerator conditions", "Inspect feed nozzles"]
        }
    },
    "Hydrotreater": {
        "high_throughput": {
            "causes": ["Space velocity exceeding design desulfurization kinetics", "Hydrogen recycle compressor bottleneck", "Reactor temperature runaway hazard"],
            "impacts": ["Hydrogen deficiency in catalyst bed", "Sulfur breakthrough in ULSD pool", "High bed pressure drops"],
            "recs": ["Increase recycle gas rate", "Activate emergency reactor cold quench lines", "Adjust feed rate to design capacity"]
        },
        "high_pressure": {
            "causes": ["Catalyst bed particulate plugging or bed compaction", "Preheat exchanger train fouling", "Hydrogen feed gas compressor surge"],
            "impacts": ["Pressure drop exceeds catalyst bed collapse limits", "Feed pump motor high-amperage trip", "Catalyst poisoning"],
            "recs": ["Perform reactor pressure drop audit", "Verify hydrogen feed rate", "Prepare catalyst skimming maintenance schedule"]
        },
        "default": {
            "causes": ["Hydrogen purity variation", "Catalyst aging", "Feed sulfur content change"],
            "impacts": ["Desulfurization efficiency loss", "Product quality deviation", "Catalyst life reduction"],
            "recs": ["Monitor hydrogen purity", "Check catalyst activity", "Analyze feed composition"]
        }
    },
    "Storage Terminal": {
        "high_utilization": {
            "causes": ["Feed import flow rate exceeding outgoing export shipping volumes", "Demurrage delay at shipping docks", "Buffer tank maintenance lockouts"],
            "impacts": ["Tank overflow and containment hazard", "Downstream CDU throughput runback bottleneck", "Demurrage penalty accumulation"],
            "recs": ["Expedite cargo export pump dispatch", "Segregate high-utilization tanks", "Prepare pipeline transfer bypass routing"]
        },
        "default": {
            "causes": ["Shipping schedule variation", "Tank maintenance delays", "Blending recipe changes"],
            "impacts": ["Inventory imbalance", "Logistics delays", "Quality segregation issues"],
            "recs": ["Review shipping schedule", "Plan tank maintenance", "Optimize blending operations"]
        }
    }
}


def execute_db_query(parsed):
    intent = parsed["intent"]
    unit_code = parsed["unit_code"]
    parameter = parsed["parameter"]
    limit = parsed["limit"]
    extreme_type = parsed["extreme_type"]

    if intent == "general" and not unit_code and not parameter:
        return None, "", []

    units = db_service.get_all_units()
    unit_map = {u.code: u for u in units}
    unit_id_map = {u.id: u.code for u in units}

    col_attr = {
        "throughput": OperationalHistory.throughput,
        "pressure": OperationalHistory.pressure,
        "temperature": OperationalHistory.temperature,
        "flow_rate": OperationalHistory.flow_rate,
        "downtime": OperationalHistory.downtime,
        "yield": OperationalHistory.yield_,
        "energy_consumption": OperationalHistory.energy_consumption
    }

    if intent == "query_current":
        if unit_code:
            u_obj = unit_map.get(unit_code)
            if not u_obj:
                return None, f"Unit '{unit_code}' not found.", []
            latest = db_service.get_latest_operational_data(u_obj.id)
            if not latest:
                return None, f"No operational data available for {unit_code}.", []
            latest_dict = latest.to_dict()
            if parameter:
                if isinstance(parameter, list):
                    desc = ", ".join([f"The current {p} of {unit_code} is {latest_dict.get(p)}" for p in parameter])
                else:
                    val = latest_dict.get(parameter)
                    desc = f"The current {parameter} of {unit_code} is {val}."
                return [latest_dict], desc, [latest_dict]
            else:
                desc = f"Latest metrics for {unit_code} retrieved."
                return [latest_dict], desc, [latest_dict]
        elif parameter:
            latest_all = db_service.get_latest_operational_data()
            records = [r.to_dict() for r in latest_all]
            results = []
            for r in records:
                results.append(f"{r['unit_code']}: {r.get(parameter)}")
            desc = f"Current {parameter} across units: " + ", ".join(results)
            return records, desc, records

    elif intent == "query_history":
        if not unit_code:
            return None, "Please specify which unit's history you want to view.", []
        u_obj = unit_map.get(unit_code)
        if not u_obj:
            return None, f"Unit '{unit_code}' not found.", []
        history = db_service.get_historical_data(u_obj.id, limit=limit)
        records = [h.to_dict() for h in history]
        if parameter:
            vals = [f"{r['timestamp']}: {r.get(parameter)}" for r in records]
            desc = f"Historical {parameter} for {unit_code} (last {limit} records):\n" + "\n".join(vals)
            return records, desc, records
        else:
            desc = f"Operational history for {unit_code} (last {limit} records) retrieved."
            return records, desc, records

    elif intent == "query_average":
        if not parameter:
            return None, "Please specify a parameter to average (e.g., average yield).", []
        attr = col_attr.get(parameter)
        if unit_code:
            u_obj = unit_map.get(unit_code)
            if not u_obj:
                return None, f"Unit '{unit_code}' not found.", []
            avg_val = db.session.query(func.avg(attr)).filter_by(unit_id=u_obj.id).scalar()
            avg_val = round(avg_val, 2) if avg_val is not None else 0.0
            desc = f"The historical average {parameter} for {unit_code} is {avg_val}."
            return [{"unit_code": unit_code, "parameter": parameter, "average": avg_val}], desc, []
        else:
            results = db.session.query(OperationalHistory.unit_id, func.avg(attr)).group_by(OperationalHistory.unit_id).all()
            records = []
            desc_lines = []
            for uid, avg_v in results:
                code = unit_id_map.get(uid, f"Unit {uid}")
                avg_v = round(avg_v, 2) if avg_v is not None else 0.0
                records.append({"unit_code": code, "parameter": parameter, "average": avg_v})
                desc_lines.append(f"{code}: {avg_v}")
            desc = f"Historical average {parameter} across units:\n" + "\n".join(desc_lines)
            return records, desc, records

    elif intent == "query_extreme":
        if not parameter:
            return None, "Please specify a parameter (e.g. highest energy).", []
        attr = col_attr.get(parameter)
        if extreme_type == "MAX":
            func_ext = func.max(attr)
            word = "highest"
        else:
            func_ext = func.min(attr)
            word = "lowest"
        if unit_code:
            u_obj = unit_map.get(unit_code)
            ext_val = db.session.query(func_ext).filter_by(unit_id=u_obj.id).scalar()
            desc = f"The historical {word} {parameter} for {unit_code} is {ext_val}."
            return [{"unit_code": unit_code, "parameter": parameter, "extreme": ext_val}], desc, []
        else:
            query = db.session.query(OperationalHistory.unit_id, attr).order_by(attr.desc() if extreme_type == "MAX" else attr.asc()).limit(1).first()
            if query:
                uid, val = query
                code = unit_id_map.get(uid, f"Unit {uid}")
                desc = f"The {word} {parameter} was recorded at {code} with a value of {val}."
                return [{"unit_code": code, "parameter": parameter, "extreme": val}], desc, []

    return None, "Intent matched, but query execution returned no data.", []


def get_unit_db_values_header(unit_code):
    units = db_service.get_all_units()
    unit_map = {u.code: u for u in units}
    u_obj = unit_map.get(unit_code)
    if not u_obj:
        return ""
    latest = db_service.get_latest_operational_data(u_obj.id)
    if not latest:
        return ""
    rec = latest.to_dict()
    ts = rec.get('timestamp') or ''
    lines = [
        f"Current Database Values for {unit_code}:",
        f"Throughput: {rec.get('throughput')} BPD",
        f"Flow Rate: {rec.get('flow_rate')} BPH",
        f"Temperature: {rec.get('temperature')} °F",
        f"Pressure: {rec.get('pressure')} psi",
        f"Yield: {rec.get('yield') or rec.get('yield_')}%",
        f"Energy Consumption: {rec.get('energy_consumption')} MMBtu/hr",
        f"Timestamp: {ts}"
    ]
    return "\n".join(lines) + "\n"


def _get_severity_ranking():
    """Rank all units by operational severity."""
    latest_all = db_service.get_latest_operational_data()
    if not latest_all:
        return "No operational data available for severity ranking."
    
    units_data = []
    for r in latest_all:
        if not r.unit:
            continue
        code = r.unit.code
        unit_info = UNIT_ENGINEERING.get(code, {})
        safety_limits = unit_info.get("safety_limits", {})
        
        score = 0
        reasons = []
        
        # Temperature scoring
        temp_max = safety_limits.get("temp_max", 1000)
        if r.temperature:
            temp_pct = (r.temperature / temp_max) * 100
            if temp_pct > 95:
                score += 40
                reasons.append(f"Temperature {r.temperature}°F near max limit ({temp_max}°F)")
            elif temp_pct > 85:
                score += 25
                reasons.append(f"Temperature {r.temperature}°F elevated ({temp_pct:.0f}% of limit)")
            elif temp_pct > 75:
                score += 10
        
        # Pressure scoring
        press_max = safety_limits.get("press_max", 2000)
        if r.pressure:
            press_pct = (r.pressure / press_max) * 100
            if press_pct > 95:
                score += 40
                reasons.append(f"Pressure {r.pressure} psi near max limit ({press_max} psi)")
            elif press_pct > 85:
                score += 25
                reasons.append(f"Pressure {r.pressure} psi elevated ({press_pct:.0f}% of limit)")
            elif press_pct > 75:
                score += 10
        
        # Throughput scoring (higher is generally better, but near capacity is concerning)
        if r.throughput and r.unit.throughput_capacity:
            tp_pct = (r.throughput / r.unit.throughput_capacity) * 100
            if tp_pct > 95:
                score += 20
                reasons.append(f"Throughput {r.throughput:.0f} BPD near capacity ({tp_pct:.0f}%)")
        
        # Yield scoring (lower is worse)
        if r.yield_:
            if r.yield_ < 70:
                score += 30
                reasons.append(f"Yield {r.yield_:.1f}% critically low")
            elif r.yield_ < 80:
                score += 15
                reasons.append(f"Yield {r.yield_:.1f}% below optimal")
        
        # Energy consumption scoring
        if r.energy_consumption:
            if code == "CDU" and r.energy_consumption > 250:
                score += 15
                reasons.append(f"Energy {r.energy_consumption:.0f} MMBtu/hr high")
            elif code == "FCC" and r.energy_consumption > 300:
                score += 15
                reasons.append(f"Energy {r.energy_consumption:.0f} MMBtu/hr high")
        
        # Downtime scoring
        if r.downtime and r.downtime > 0:
            score += 20
            reasons.append(f"Downtime {r.downtime:.1f} hours")
        
        # Determine severity level
        if score >= 60:
            severity = "CRITICAL"
        elif score >= 40:
            severity = "HIGH"
        elif score >= 20:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        units_data.append({
            "code": code,
            "name": unit_info.get("name", code),
            "score": score,
            "severity": severity,
            "reasons": reasons,
            "temp": r.temperature,
            "press": r.pressure,
            "throughput": r.throughput,
            "yield": r.yield_
        })
    
    units_data.sort(key=lambda x: x["score"], reverse=True)
    
    lines = ["Refinery Unit Severity Ranking\n"]
    for i, u in enumerate(units_data, 1):
        lines.append(f"{i}. {u['name']} ({u['code']}) - {u['severity']} (Score: {u['score']})")
        if u["reasons"]:
            for reason in u["reasons"][:3]:
                lines.append(f"   - {reason}")
        lines.append(f"   Current: Temp={u['temp']}°F, Press={u['press']}psi, Throughput={u['throughput']:.0f}BPD, Yield={u['yield']:.1f}%")
        lines.append("")
    
    # Add recommendation for top unit
    if units_data and units_data[0]["severity"] in ["CRITICAL", "HIGH"]:
        top = units_data[0]
        lines.append(f"PRIORITY ACTION: {top['name']} ({top['code']}) requires immediate operator attention.")
    
    return "\n".join(lines)


def _format_simulation_response(unit, current_values, changes, estimates):
    cd = estimates['current_display']
    td = estimates['target_display']
    adj = estimates['adjustments']
    
    lines = []
    lines.append("Current Conditions")
    lines.append(f"Throughput: {cd['throughput_bpd']} BPD")
    lines.append(f"Flow Rate: {cd['flow_rate_bph']} BPH")
    lines.append(f"Temperature: {cd['temperature_c']}°C")
    lines.append(f"Pressure: {cd['pressure_bar']} bar")
    
    lines.append("")
    lines.append("Target Conditions")
    if 'throughput_bpd' in changes or 'flow_rate_bpd' in changes:
        lines.append(f"Throughput: {td['throughput_bpd']} BPD")
        lines.append(f"Flow Rate: {td['flow_rate_bph']} BPH")
    if 'temperature_C_delta' in changes or 'temperature_target_c' in changes or 'temperature_target_f' in changes or 'temperature_F_delta' in changes:
        target_temp_c = _f_to_c(estimates['internal']['t_temp_f'])
        lines.append(f"Temperature: {target_temp_c}°C")
    if 'pressure_pct' in changes or 'pressure_target_psi' in changes or 'pressure_target_bar' in changes or 'pressure_psi_delta' in changes or 'pressure_bar_delta' in changes:
        target_press_bar = _psi_to_bar(estimates['internal']['t_press_psi'])
        lines.append(f"Pressure: {target_press_bar} bar")
    if not any(k in changes for k in ['throughput_bpd', 'flow_rate_bpd', 'temperature_C_delta', 'temperature_target_c', 'temperature_target_f', 'temperature_F_delta', 'pressure_pct', 'pressure_target_psi', 'pressure_target_bar', 'pressure_psi_delta', 'pressure_bar_delta']):
        lines.append(f"Throughput: {td['throughput_bpd']} BPD")
        lines.append(f"Flow Rate: {td['flow_rate_bph']} BPH")
    
    lines.append("")
    lines.append("Parameter Adjustments")
    lines.append(f"Temperature: {adj['temperature_range_c']}")
    lines.append(f"Pressure: {adj['pressure_range_bar']}")
    
    lines.append("")
    lines.append("Expected Changes")
    for c in estimates['consequences'][:3]:
        lines.append(f"{c}")
    
    lines.append("")
    lines.append("Operational Risks")
    for r in estimates['risks'][:3]:
        lines.append(f"{r}")
    
    lines.append("")
    lines.append("Recommendations")
    for r in estimates['recommendations'][:3]:
        lines.append(f"{r}")
    
    lines.append("")
    lines.append("Engineering Reasoning")
    unit_info = UNIT_ENGINEERING.get(unit, {})
    lines.append(f"{unit_info.get('name', unit)} operates by {unit_info.get('process', 'standard refinery processes')}.")
    if estimates['internal']['flow_ratio'] > 1.15:
        lines.append(f"Increasing throughput by {(estimates['internal']['flow_ratio']-1)*100:.0f}% increases vapor loading, requiring higher furnace duty and reflux rates.")
    elif estimates['internal']['flow_ratio'] < 0.85:
        lines.append(f"Reducing throughput by {(1-estimates['internal']['flow_ratio'])*100:.0f}% reduces vapor velocities, risking tray weeping and poor fractionation.")
    
    lines.append("")
    lines.append("Confidence Level: HIGH")
    lines.append("Based on engineering rules and current database values.")
    
    return "\n".join(lines)


def get_hybrid_chatbot_response(user_query, slm_service):
    q_lower = user_query.lower()

    # ── SEVERITY RANKING ─────────────────────────────────────────────────
    if detect_intent(user_query) == INTENT_SEVERITY_RANKING:
        response = _get_severity_ranking()
        db_records = [r.to_dict() for r in db_service.get_latest_operational_data()]
        db_service.log_chatbot_query(
            user_query=user_query,
            system_response=response,
            retrieved_data_used=db_records,
            llm_called=False
        )
        return {
            "response": response,
            "db_data": db_records,
            "parsed_intent": {"intent": "severity_ranking"},
            "llm_called": False,
            "detected_intent": INTENT_SEVERITY_RANKING
        }

    # ── Pressure financial impact shortcut ────────────────────────────────
    if "pressure" in q_lower and any(k in q_lower for k in ["profit", "loss", "margin", "cost", "economic"]):
        unit_code = None
        if "cdu" in q_lower or "crude distillation" in q_lower:
            unit_code = "CDU"
        elif "vdu" in q_lower or "vacuum distillation" in q_lower:
            unit_code = "VDU"
        elif "fcc" in q_lower or "catalytic cracking" in q_lower:
            unit_code = "FCC"
        elif "hydrotreater" in q_lower or "treating" in q_lower:
            unit_code = "Hydrotreater"
        elif "storage" in q_lower or "terminal" in q_lower:
            unit_code = "Storage Terminal"

        if unit_code:
            nums = re.findall(r'\b\d+(?:\.\d+)?\b', q_lower)
            delta_val = float(nums[0]) if nums else 100.0
            is_increase = True
            if any(k in q_lower for k in ["decrease", "down", "lower", "drop", "reduction", "reduced"]):
                is_increase = False

            units = db_service.get_all_units()
            unit_map = {u.code: u for u in units}
            u_obj = unit_map.get(unit_code)
            if u_obj:
                latest = db_service.get_latest_operational_data(u_obj.id)
                if latest:
                    unit_specs = {
                        "CDU": (60.0, 30.0, 50.0, 40.0, 15.0, 650.0, 750.0, 700.0),
                        "VDU": (5.0, 0.5, 1.5, 1.0, 20.0, 700.0, 800.0, 750.0),
                        "FCC": (45.0, 25.0, 40.0, 30.0, 30.0, 950.0, 1050.0, 980.0),
                        "Hydrotreater": (1200.0, 600.0, 1000.0, 800.0, 25.0, 600.0, 700.0, 650.0),
                        "Storage Terminal": (30.0, 15.0, 20.0, 18.0, 5.0, 60.0, 90.0, 75.0)
                    }
                    max_press, min_norm_press, max_norm_press, opt_press, margin_per_bbl, min_temp, max_temp, opt_temp = unit_specs[unit_code]
                    new_pressure = latest.pressure + delta_val if is_increase else latest.pressure - delta_val
                    baseline_profit = latest.throughput * (latest.yield_ / 100.0) * margin_per_bbl

                    is_shutdown = False
                    shutdown_reason = ""
                    if new_pressure > max_press:
                        is_shutdown = True
                        shutdown_reason = f"New operating pressure ({new_pressure:.2f} psi) exceeds the maximum mechanical design safety limit ({max_press:.1f} psi) of the vessel."
                    elif new_pressure < 0:
                        is_shutdown = True
                        shutdown_reason = f"New operating pressure ({new_pressure:.2f} psi) is negative, causing vacuum collapse."

                    if is_shutdown:
                        loss_amount = baseline_profit
                        response = (
                            f"Unit: {u_obj.name} ({unit_code})\n"
                            f"Pressure Change: {'+' if is_increase else '-'}{delta_val:.1f} psi (Current: {latest.pressure:.2f} psi -> Target: {new_pressure:.2f} psi)\n"
                            f"Financial Impact: Net Loss of ${loss_amount:,.2f}/day (100% loss of daily operating margin due to safety shutdown).\n"
                            f"Safety Status: CRITICAL - Automatic Emergency Shutdown triggered. {shutdown_reason}\n\n"
                            f"Required Parameters for Safe & Profitable Operation:\n"
                            f"Operating Pressure: Maintain between {min_norm_press:.1f} and {max_norm_press:.1f} psi (Optimum: {opt_press:.1f} psi). Max mechanical safety limit: {max_press:.1f} psi.\n"
                            f"Throughput: Keep within {latest.throughput:,.1f} bbl/day (Max capacity: {u_obj.throughput_capacity:,.1f} bbl/day).\n"
                            f"Operating Temperature: Maintain between {min_temp:.1f}°F and {max_temp:.1f}°F (Optimum: {opt_temp:.1f}°F)."
                        )
                    else:
                        pressure_deviation = abs(new_pressure - opt_press)
                        yield_impact = -0.1 * pressure_deviation
                        new_yield = max(50.0, min(100.0, latest.yield_ + yield_impact))
                        new_profit = latest.throughput * (new_yield / 100.0) * margin_per_bbl
                        profit_diff = new_profit - baseline_profit
                        if profit_diff < 0:
                            impact_str = f"Net Loss of ${abs(profit_diff):,.2f}/day (Yield dropped from {latest.yield_:.2f}% to {new_yield:.2f}%)"
                        else:
                            impact_str = f"Net Profit of ${profit_diff:,.2f}/day (Yield changed to {new_yield:.2f}%)"
                        response = (
                            f"Unit: {u_obj.name} ({unit_code})\n"
                            f"Pressure Change: {'+' if is_increase else '-'}{delta_val:.1f} psi (Current: {latest.pressure:.2f} psi -> Target: {new_pressure:.2f} psi)\n"
                            f"Financial Impact: {impact_str}.\n"
                            f"Safety Status: Operating within safe nominal bounds.\n\n"
                            f"Required Parameters for Safe & Profitable Operation:\n"
                            f"Operating Pressure: Maintain between {min_norm_press:.1f} and {max_norm_press:.1f} psi (Optimum: {opt_press:.1f} psi).\n"
                            f"Throughput: Keep within {latest.throughput:,.1f} bbl/day (Max capacity: {u_obj.throughput_capacity:,.1f} bbl/day).\n"
                            f"Operating Temperature: Maintain between {min_temp:.1f}°F and {max_temp:.1f}°F (Optimum: {opt_temp:.1f}°F)."
                        )
                    db_records = [latest.to_dict()]
                    db_service.log_chatbot_query(user_query=user_query, system_response=response, retrieved_data_used=db_records, llm_called=False)
                    return {"response": response, "db_data": db_records, "parsed_intent": {"intent": "query_current", "unit_code": unit_code, "parameter": "pressure", "limit": 5, "extreme_type": None}, "llm_called": False, "detected_intent": INTENT_CURRENT}

    parsed = parse_query(user_query)
    intent = detect_intent(user_query)

    if intent == "CURRENT_DATA":
        parsed["intent"] = "query_current"

    latest_all = db_service.get_latest_operational_data()
    global_context = {r.unit.code: {"throughput": r.throughput, "pressure": r.pressure, "temperature": r.temperature, "flow_rate": r.flow_rate, "downtime": r.downtime, "yield": r.yield_, "energy_consumption": r.energy_consumption, "timestamp": getattr(r, 'timestamp', None)} for r in latest_all if r.unit}

    llm_called = False
    system_response = ""
    db_records = []

    # ── OPERATIONAL IMPACT ───────────────────────────────────────────────
    if intent == INTENT_OPERATIONAL_IMPACT:
        # Identify unit and threshold from query
        unit = 'CDU'
        if 'fcc' in q_lower or 'catalytic cracking' in q_lower:
            unit = 'FCC'
        elif 'vdu' in q_lower or 'vacuum distillation' in q_lower:
            unit = 'VDU'
        elif 'hydro' in q_lower or 'treating' in q_lower:
            unit = 'Hydrotreater'
        elif 'storage' in q_lower or 'terminal' in q_lower:
            unit = 'Storage Terminal'

        u_obj = db_service.get_unit_by_code(unit)
        current_values = {}
        db_records = []
        if u_obj:
            latest = db_service.get_latest_operational_data(u_obj.id)
            if latest:
                current_values = {
                    'throughput': latest.throughput,
                    'temperature': latest.temperature,
                    'pressure': latest.pressure,
                    'flow_rate': latest.flow_rate,
                    'yield': latest.yield_,
                    'energy_consumption': latest.energy_consumption,
                }
                db_records = [latest.to_dict()]

        # Extract threshold value from query
        nums = re.findall(r'\b\d+(?:\.\d+)?\b', q_lower)
        threshold_val = float(nums[0]) if nums else None

        # Determine what parameter is being asked about
        param = "temperature"
        if "pressure" in q_lower:
            param = "pressure"
        elif "throughput" in q_lower or "bpd" in q_lower:
            param = "throughput"
        elif "yield" in q_lower:
            param = "yield"

        # Run simulation with threshold
        changes = {}
        if threshold_val:
            if param == "temperature":
                changes['temperature_target_f'] = threshold_val
            elif param == "pressure":
                changes['pressure_target_psi'] = threshold_val
            elif param == "throughput":
                changes['throughput_bpd'] = threshold_val
        
        if changes:
            estimates = estimate_parameters(unit, changes, current_values)
        else:
            # Default: simulate a 20% increase
            changes = {'throughput_bpd': current_values.get('throughput', 80000) * 1.2}
            estimates = estimate_parameters(unit, changes, current_values)

        # Get unit-specific engineering knowledge
        unit_eng = UNIT_ENGINEERING.get(unit, {})
        unit_expert = UNIT_EXPERT_ANALYSIS.get(unit, {})

        # Determine which expert template to use
        expert = unit_expert.get("default", {})
        if param == "temperature" and threshold_val:
            temp_limit = unit_eng.get("safety_limits", {}).get("temp_max", 1000)
            if threshold_val >= temp_limit * 0.95:
                expert = unit_expert.get("high_temperature", unit_expert.get("default", {}))
            elif threshold_val >= temp_limit * 0.85:
                expert = unit_expert.get("high_throughput", unit_expert.get("default", {}))
        elif param == "pressure" and threshold_val:
            press_limit = unit_eng.get("safety_limits", {}).get("press_max", 2000)
            if threshold_val >= press_limit * 0.95:
                expert = unit_expert.get("high_pressure", unit_expert.get("default", {}))
        elif param == "throughput" and threshold_val:
            tp_limit = 40000 if unit == "FCC" else (100000 if unit == "CDU" else 30000)
            if threshold_val >= tp_limit * 0.95:
                expert = unit_expert.get("high_throughput", unit_expert.get("default", {}))

        lines = []
        lines.append(f"Operational Impact Analysis: {unit_eng.get('name', unit)} at {param.upper()} = {threshold_val}")
        lines.append("")
        lines.append("Current Conditions")
        lines.append(f"Throughput: {current_values.get('throughput', 'N/A')} BPD")
        lines.append(f"Temperature: {current_values.get('temperature', 'N/A')}°F")
        lines.append(f"Pressure: {current_values.get('pressure', 'N/A')} psi")
        lines.append(f"Yield: {current_values.get('yield', 'N/A')}%")
        lines.append("")
        lines.append("Critical Risk Assessment")
        
        # Check if threshold exceeds safety limits
        if param == "temperature" and threshold_val:
            temp_limit = unit_eng.get("safety_limits", {}).get("temp_max", 1000)
            if threshold_val >= temp_limit:
                lines.append(f"CRITICAL: Temperature {threshold_val}°F EXCEEDS maximum safety limit ({temp_limit}°F)")
                lines.append("Immediate shutdown required to prevent metallurgical failure.")
            elif threshold_val >= temp_limit * 0.95:
                lines.append(f"HIGH RISK: Temperature {threshold_val}°F at {threshold_val/temp_limit*100:.0f}% of maximum safety limit ({temp_limit}°F)")
                lines.append("Approaching critical threshold. Close monitoring required.")
            else:
                lines.append(f"Temperature {threshold_val}°F is within operating limits (max: {temp_limit}°F)")
        elif param == "pressure" and threshold_val:
            press_limit = unit_eng.get("safety_limits", {}).get("press_max", 2000)
            if threshold_val >= press_limit:
                lines.append(f"CRITICAL: Pressure {threshold_val} psi EXCEEDS maximum safety limit ({press_limit} psi)")
                lines.append("Immediate shutdown required to prevent vessel rupture.")
            elif threshold_val >= press_limit * 0.95:
                lines.append(f"HIGH RISK: Pressure {threshold_val} psi at {threshold_val/press_limit*100:.0f}% of maximum safety limit ({press_limit} psi)")
            else:
                lines.append(f"Pressure {threshold_val} psi is within operating limits (max: {press_limit} psi)")
        
        lines.append("")
        lines.append("Engineering Analysis")
        lines.append(f"Most Likely Cause: {expert.get('causes', ['Process upset'])[0]}")
        lines.append("")
        lines.append("Operational Impact")
        for impact in expert.get('impacts', ['Potential process instability'])[:3]:
            lines.append(f"- {impact}")
        lines.append("")
        lines.append("Recommendations")
        for rec in expert.get('recs', ['Monitor closely'])[:3]:
            lines.append(f"- {rec}")
        lines.append("")
        lines.append("Simulation Results")
        for c in estimates.get('consequences', [])[:2]:
            lines.append(f"- {c}")
        for r in estimates.get('risks', [])[:2]:
            lines.append(f"- {r}")
        lines.append("")
        lines.append("Confidence Level: HIGH")
        lines.append("Based on engineering rules and current database values.")

        system_response = "\n".join(lines)
        llm_called = False

    # ── MIXED ────────────────────────────────────────────────────────────
    elif intent == INTENT_MIXED:
        # Extract unit from query
        unit = None
        if 'cdu' in q_lower or 'crude distillation' in q_lower:
            unit = 'CDU'
        elif 'vdu' in q_lower or 'vacuum distillation' in q_lower:
            unit = 'VDU'
        elif 'fcc' in q_lower or 'catalytic cracking' in q_lower:
            unit = 'FCC'
        elif 'hydro' in q_lower or 'treating' in q_lower:
            unit = 'Hydrotreater'
        elif 'storage' in q_lower or 'terminal' in q_lower:
            unit = 'Storage Terminal'

        # Get current database values
        db_header = ""
        if unit:
            db_header = get_unit_db_values_header(unit)
        
        # Get knowledge facts
        facts = retrieve_facts(user_query)
        facts_context = ""
        if facts:
            facts_context = "Technical Facts:\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n"
        
        # Build combined response
        prompt = (
            f"{db_header}\n"
            f"{facts_context}\n"
            f"Question: {user_query}\n\n"
            "Provide a combined explanation that includes:\n"
            "1. Current database values for the unit\n"
            "2. Technical definition and explanation\n"
            "3. How the current values relate to the technical explanation\n"
            "Format: Direct answer with bullet points. Max 150 words."
        )
        system_response = slm_service.query(prompt, context_data=None)
        llm_called = True

    # ── KNOWLEDGE ────────────────────────────────────────────────────────
    elif intent == INTENT_KNOWLEDGE:
        facts = retrieve_facts(user_query)
        facts_context = ""
        if facts:
            facts_context = "Ground Truth Facts (Use these facts to ensure technical accuracy, do NOT contradict them):\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n"
        
        prompt = (
            f"{facts_context}"
            f"Question: {user_query}\n\n"
            "You are a Senior Refinery Process Engineer. Answer using professional refinery terminology.\n"
            "Rules:\n"
            "- Give direct answer first (one short sentence).\n"
            "- Use bullet points for details (max 4 bullets).\n"
            "- Focus on operational decisions, not textbook theory.\n"
            "- Never invent SQLite values.\n"
            "- Never calculate engineering values independently.\n"
            "- Use engineer-style short operational language.\n"
            "- Max 100 words.\n"
            "- No AI-style introductions or disclaimers.\n"
        )
        system_response = slm_service.query(prompt, context_data=None)
        llm_called = True

    # ── CURRENT_DATA ─────────────────────────────────────────────────────
    elif intent == INTENT_CURRENT:
        db_data, db_desc, db_records = execute_db_query(parsed)
        if parsed.get('intent') in ['query_average', 'query_extreme']:
            system_response = db_desc or "No data found."
        elif db_records:
            lines = []
            for rec in db_records:
                ts = rec.get('timestamp') or rec.get('time') or ''
                code = rec.get('unit_code') or rec.get('unit') or ''
                if parsed.get('parameter'):
                    params = parsed['parameter'] if isinstance(parsed['parameter'], list) else [parsed['parameter']]
                    if len(params) == 1:
                        p = params[0]
                        val = rec.get(p)
                        param_name = p.replace('_', ' ').title()
                        unit_str = ""
                        if "throughput" in p: unit_str = " BPD"
                        elif "flow" in p: unit_str = " BPH"
                        elif "temperature" in p: unit_str = " °F"
                        elif "pressure" in p: unit_str = " psi"
                        elif "yield" in p: unit_str = "%"
                        elif "energy" in p: unit_str = " MMBtu/hr"
                        elif "downtime" in p: unit_str = " hours"
                        lines.append(f"{code} Current {param_name}:\nValue: {val}{unit_str}\nTimestamp: {ts}")
                    else:
                        param_lines = []
                        for p in params:
                            val = rec.get(p)
                            param_name = p.replace('_', ' ').title()
                            unit_str = ""
                            if "throughput" in p: unit_str = " BPD"
                            elif "flow" in p: unit_str = " BPH"
                            elif "temperature" in p: unit_str = " °F"
                            elif "pressure" in p: unit_str = " psi"
                            elif "yield" in p: unit_str = "%"
                            elif "energy" in p: unit_str = " MMBtu/hr"
                            elif "downtime" in p: unit_str = " hours"
                            param_lines.append(f"{param_name}: {val}{unit_str}")
                        lines.append(f"Current Database Values for {code}:\n" + "\n".join(param_lines) + f"\nTimestamp: {ts}")
                else:
                    lines.append(
                        f"Current Database Values for {code}:\n"
                        f"Throughput: {rec.get('throughput')} BPD\n"
                        f"Flow Rate: {rec.get('flow_rate')} BPH\n"
                        f"Temperature: {rec.get('temperature')} °F\n"
                        f"Pressure: {rec.get('pressure')} psi\n"
                        f"Yield: {rec.get('yield') or rec.get('yield_')}%\n"
                        f"Energy Consumption: {rec.get('energy_consumption')} MMBtu/hr\n"
                        f"Timestamp: {ts}"
                    )
            system_response = "Current Plant Data\n\n" + "\n\n".join(lines)
        else:
            system_response = db_desc or "No current data found."

    # ── ANALYSIS ─────────────────────────────────────────────────────────
    elif intent == INTENT_ANALYSIS:
        db_data, db_desc, db_records = execute_db_query(parsed)
        if not db_records:
            target_unit = parsed.get("unit_code")
            if not target_unit:
                for code in ["CDU", "VDU", "FCC", "Hydrotreater", "Storage Terminal"]:
                    if code.lower() in user_query.lower():
                        target_unit = code
                        break
            if target_unit:
                u_obj = db_service.get_unit_by_code(target_unit)
                if u_obj:
                    latest = db_service.get_latest_operational_data(u_obj.id)
                    if latest:
                        db_records = [latest.to_dict()]
            if not db_records:
                latest_all = db_service.get_latest_operational_data()
                db_records = [r.to_dict() for r in latest_all]

        if not db_records:
            system_response = db_desc or "Data insufficient for analysis. Specify unit and parameter."
        else:
            from engineering_analyzer import analyze_parameter
            compact = {}
            concerns = []
            
            target_unit = parsed.get("unit_code")
            if not target_unit:
                target_unit = 'CDU'
                for code in ["CDU", "VDU", "FCC", "Hydrotreater", "Storage Terminal"]:
                    if code.lower() in user_query.lower():
                        target_unit = code
                        break

            for r in db_records:
                unit = r.get('unit_code') or r.get('unit') or target_unit or 'UNKNOWN'
                metrics_to_check = {
                    "throughput": r.get('throughput'),
                    "flow_rate": r.get('flow_rate'),
                    "temperature": r.get('temperature'),
                    "pressure": r.get('pressure'),
                    "yield": r.get('yield') or r.get('yield_')
                }
                compact[unit] = metrics_to_check
                for k, v in metrics_to_check.items():
                    if v is not None:
                        audit_res = analyze_parameter(target_unit, k, v)
                        if audit_res.get("status") in ["WARNING", "CRITICAL"] and audit_res.get("concern"):
                            concerns.append(f"- {audit_res['concern']} Status: {audit_res['status']}")

            # Get unit-specific expert analysis
            unit_expert = UNIT_EXPERT_ANALYSIS.get(target_unit, {})
            expert = unit_expert.get("default", {})

            # Check for specific conditions to select expert template
            target_metrics = compact.get(target_unit, {})
            if target_metrics.get("temperature"):
                temp_limit = UNIT_ENGINEERING.get(target_unit, {}).get("safety_limits", {}).get("temp_max", 1000)
                if target_metrics["temperature"] > temp_limit * 0.9:
                    expert = unit_expert.get("high_temperature", expert)
            if target_metrics.get("pressure"):
                press_limit = UNIT_ENGINEERING.get(target_unit, {}).get("safety_limits", {}).get("press_max", 2000)
                if target_metrics["pressure"] > press_limit * 0.9:
                    expert = unit_expert.get("high_pressure", expert)
            if target_metrics.get("throughput"):
                tp_limit = 40000 if target_unit == "FCC" else (100000 if target_unit == "CDU" else 30000)
                if target_metrics["throughput"] > tp_limit * 0.9:
                    expert = unit_expert.get("high_throughput", expert)

            confidence = "HIGH"
            confidence_reason = "Consistent historical operating data available in database."

            concerns_str = "\n".join(concerns) if concerns else "- None immediate detected."
            
            formatted_values = []
            for unit_name, metrics in compact.items():
                metrics_lines = [f"{k}: {v}" for k, v in metrics.items() if v is not None]
                formatted_values.append(f"- {unit_name}: {', '.join(metrics_lines)}")
            formatted_values_str = "\n".join(formatted_values)

            prompt = (
                f"Perform a professional engineering analysis for query: \"{user_query}\"\n\n"
                "CRITICAL RULES:\n"
                "- Use ONLY the exact numeric values provided below. Do NOT invent, estimate, or hallucinate any values.\n"
                "- Every number in your response MUST come from the Input Data Facts below.\n"
                "- If a value is not provided, do NOT guess — state 'not available'.\n\n"
                "Input Data Facts:\n"
                f"- Current Values:\n{formatted_values_str}\n"
                f"- Observed Concerns:\n{concerns_str}\n"
                f"- Most Likely Cause: {expert.get('causes', ['Process upset'])[0]}\n"
                f"- Other Possible Causes: {', '.join(expert.get('causes', ['Unknown'])[1:])}\n"
                f"- Operational Impact: {', '.join(expert.get('impacts', ['Potential instability']))}\n"
                f"- Recommendations: {', '.join(expert.get('recs', ['Monitor closely']))}\n"
                f"- Confidence: {confidence} (Reason: {confidence_reason})\n\n"
                "Output Format Checklist:\n"
                "Start with a single direct engineering conclusion sentence. Then output these exact sections:\n\n"
                "Current Values\n"
                f"{formatted_values_str}\n\n"
                "Observed Concerns\n"
                f"{concerns_str}\n\n"
                "Possible Causes\n"
                "Most Likely Cause:\n"
                f"- {expert.get('causes', ['Process upset'])[0]}\n"
                "Other Possible Causes:\n" + "\n".join([f"- {c}" for c in expert.get('causes', ['Unknown'])[1:]]) + "\n\n"
                "Operational Impact\n" + "\n".join([f"- {i}" for i in expert.get('impacts', ['Potential instability'])]) + "\n\n"
                "Recommendations\n" + "\n".join([f"- {r}" for r in expert.get('recs', ['Monitor closely'])]) + "\n\n"
                f"Confidence Level\n- {confidence}\nReason: {confidence_reason}\n\n"
                "Format rules:\n"
                "- Start with a single direct process-engineering conclusion sentence.\n"
                "- Write the exact section headers: Current Values, Observed Concerns, Possible Causes, Operational Impact, Recommendations, Confidence Level.\n"
                "- Be concise and keep the response under 130 words.\n"
                "- REMINDER: Use ONLY the exact numbers from Input Data Facts. Do NOT hallucinate values.\n"
            )
            system_response = slm_service.query(prompt, context_data=None)
            llm_called = True

    # ── SIMULATION ───────────────────────────────────────────────────────
    elif intent == INTENT_SIMULATION:
        unit = 'CDU'
        if 'fcc' in q_lower or 'catalytic cracking' in q_lower:
            unit = 'FCC'
        elif 'vdu' in q_lower or 'vacuum distillation' in q_lower:
            unit = 'VDU'
        elif 'hydro' in q_lower or 'treating' in q_lower:
            unit = 'Hydrotreater'
        elif 'storage' in q_lower or 'terminal' in q_lower or 'logistics' in q_lower:
            unit = 'Storage Terminal'

        u_obj = db_service.get_unit_by_code(unit)
        current_values = None
        db_records = []
        if u_obj:
            latest = db_service.get_latest_operational_data(u_obj.id)
            if latest:
                current_values = {
                    'throughput': latest.throughput,
                    'temperature': latest.temperature,
                    'pressure': latest.pressure,
                    'flow_rate': latest.flow_rate,
                    'yield': latest.yield_,
                    'energy_consumption': latest.energy_consumption,
                    'downtime': latest.downtime,
                }
                db_records = [latest.to_dict()]

        num_pattern = r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b|\b\d+(?:\.\d+)?\b'
        raw_matches = list(re.finditer(num_pattern, user_query))
        matches = []
        nums = []
        for m in raw_matches:
            val_extracted = float(m.group(0).replace(',', ''))
            end_chars = user_query[m.end():m.end()+2]
            pre_chars = user_query[max(0, m.start()-5):m.start()]
            is_list_marker = False
            if end_chars and end_chars[0] == '.':
                if len(end_chars) > 1 and end_chars[1] in [' ', '\n', '\r']:
                    if not pre_chars.strip() or '\n' in pre_chars or '\r' in pre_chars:
                        is_list_marker = True
            if not is_list_marker:
                matches.append(m)
                nums.append(val_extracted)

        changes = {}
        is_percent = '%' in user_query or 'percent' in user_query or 'percentage' in user_query
        is_increase = any(k in q_lower for k in ['increase', 'increases', 'increasing', 'rise', 'rises', 'rising', 'up', 'higher', 'grow', 'grows', 'growing'])
        is_decrease = any(k in q_lower for k in ['decrease', 'decreases', 'decreasing', 'drop', 'drops', 'dropping', 'down', 'lower', 'halves', 'leak', 'reduce', 'reducing', 'reduced'])
        
        base_throughput = current_values.get('throughput', 3200.0) if current_values else 3200.0
        base_flow_rate = current_values.get('flow_rate', 133.0) if current_values else 133.0

        current_val = None
        target_val = None
        if len(matches) == 1:
            target_val = float(matches[0].group(0).replace(',', ''))
        elif len(matches) >= 2:
            for m in matches:
                raw_val = m.group(0)
                val_extracted = float(raw_val.replace(',', ''))
                start_idx = m.start()
                context = q_lower[max(0, start_idx - 40):start_idx]
                words = re.findall(r'\b\w+\b', context)
                if any(phrase in context for phrase in ['increases to', 'decreases to', 'increase to', 'decrease to']) or any(kw in words for kw in ['target', 'to', 'reach', 'become', 'becomes', 'new']):
                    target_val = val_extracted
                elif any(kw in words for kw in ['current', 'currently', 'now', 'is', 'from', 'baseline', 'start']):
                    current_val = val_extracted
            if target_val is None and current_val is None:
                current_val = float(matches[0].group(0).replace(',', ''))
                target_val = float(matches[1].group(0).replace(',', ''))
            elif target_val is None:
                for m in matches:
                    val_extracted = float(m.group(0).replace(',', ''))
                    if val_extracted != current_val:
                        target_val = val_extracted
                        break
            elif current_val is None:
                for m in matches:
                    val_extracted = float(m.group(0).replace(',', ''))
                    if val_extracted != target_val:
                        current_val = val_extracted
                        break

        val = target_val if target_val is not None else (nums[0] if nums else None)
        
        is_flow_rate_query = any(k in q_lower for k in ['flow rate', 'flowrate']) or ('flow' in q_lower and 'throughput' not in q_lower)
        is_throughput_query = 'throughput' in q_lower or any(k in q_lower for k in ['feed', 'charge', 'capacity', 'crude charge'])
        is_flow_query = is_flow_rate_query or is_throughput_query
        
        if is_flow_query:
            if 'halves' in q_lower:
                if is_flow_rate_query:
                    changes['flow_rate_bph'] = base_flow_rate * 0.5
                else:
                    changes['throughput_bpd'] = base_throughput * 0.5
            elif val is not None:
                if 'bph' in q_lower:
                    changes['flow_rate_bph'] = val
                elif 'bpd' in q_lower and not is_flow_rate_query:
                    changes['throughput_bpd'] = val
                elif 'by' in q_lower and (is_increase or is_decrease):
                    sign = -1.0 if is_decrease else 1.0
                    if is_flow_rate_query:
                        changes['flow_rate_bph'] = base_flow_rate + sign * val
                    else:
                        changes['throughput_bpd'] = base_throughput + sign * val
                else:
                    if is_flow_rate_query:
                        changes['flow_rate_bph'] = val
                    else:
                        changes['throughput_bpd'] = val

        if any(k in q_lower for k in ['temperature', 'temp', 'reactor_temp']):
            if nums:
                t_val = target_val if target_val is not None else (nums[-1] if len(nums) > 1 and is_flow_query else nums[0])
                is_target = False
                to_match = re.search(r'\bto\s+(\d+(?:\.\d+)?)\b', q_lower)
                if to_match and float(to_match.group(1)) == t_val:
                    is_target = True
                is_celsius = 'c' in q_lower or 'celsius' in q_lower
                is_fahrenheit = 'f' in q_lower or 'fahrenheit' in q_lower
                if is_target:
                    if is_celsius:
                        changes['temperature_target_c'] = t_val
                    elif is_fahrenheit:
                        changes['temperature_target_f'] = t_val
                    else:
                        if t_val > 500:
                            changes['temperature_target_f'] = t_val
                        else:
                            changes['temperature_target_c'] = t_val
                else:
                    sign = -1.0 if is_decrease else 1.0
                    if is_fahrenheit:
                        changes['temperature_F_delta'] = sign * t_val
                    else:
                        changes['temperature_C_delta'] = sign * t_val

        if any(k in q_lower for k in ['pressure', 'vacuum']):
            if nums:
                p_val = target_val if target_val is not None else (nums[-1] if len(nums) > 1 and is_flow_query else nums[0])
                is_target = False
                to_match = re.search(r'\bto\s+(\d+(?:\.\d+)?)\b', q_lower)
                if to_match and float(to_match.group(1)) == p_val:
                    is_target = True
                is_psi = 'psi' in q_lower
                is_bar = 'bar' in q_lower
                if is_target:
                    if is_bar:
                        changes['pressure_target_bar'] = p_val
                    elif is_psi:
                        changes['pressure_target_psi'] = p_val
                    else:
                        if p_val > 100:
                            changes['pressure_target_psi'] = p_val
                        else:
                            if unit == 'Hydrotreater':
                                changes['pressure_target_psi'] = p_val
                            else:
                                changes['pressure_target_bar'] = p_val
                else:
                    if is_percent:
                        changes['pressure_pct'] = -p_val if is_decrease else p_val
                    else:
                        sign = -1.0 if is_decrease else 1.0
                        if is_psi:
                            changes['pressure_psi_delta'] = sign * p_val
                        elif is_bar:
                            changes['pressure_bar_delta'] = sign * p_val
                        else:
                            if p_val < 5:
                                changes['pressure_bar_delta'] = sign * p_val
                            else:
                                changes['pressure_psi_delta'] = sign * p_val
            elif 'rises' in q_lower or 'rising' in q_lower or 'increase' in q_lower:
                changes['pressure_pct'] = 15.0
            elif 'drops' in q_lower or 'dropping' in q_lower or 'decrease' in q_lower:
                changes['pressure_pct'] = -15.0

        if 'sulfur' in q_lower:
            if 'double' in q_lower or 'doubles' in q_lower:
                changes['sulfur_feed_mult'] = 2.0
            elif nums:
                changes['sulfur_feed_mult'] = 1.0 + (nums[0] / 100.0) if is_percent else nums[0]
            else:
                changes['sulfur_feed_mult'] = 2.0

        if any(k in q_lower for k in ['utilization', 'utilize', 'utilized', 'capacity']):
            if nums:
                changes['tank_utilization_pct'] = nums[0]

        if 'catalyst' in q_lower and ('activity' in q_lower or 'ratio' in q_lower):
            if nums:
                changes['catalyst_activity_pct_change'] = -nums[0] if is_decrease else nums[0]

        if 'duty' in q_lower or 'heater' in q_lower:
            if nums:
                changes['heater_duty_pct_change'] = -nums[0] if is_decrease else nums[0]

        if 'api' in q_lower:
            if nums:
                changes['api_gravity_delta'] = -nums[0] if is_decrease else nums[0]

        estimates = estimate_parameters(unit, changes, current_values)
        system_response = _format_simulation_response(unit, current_values, changes, estimates)
        llm_called = False

    else:
        prompt = f"{user_query}\nAnswer concisely in bullets, direct answer first."
        system_response = slm_service.query(prompt, context_data=None)
        llm_called = True

    db_service.log_chatbot_query(
        user_query=user_query,
        system_response=system_response,
        retrieved_data_used=(db_records if 'db_records' in locals() else []),
        llm_called=llm_called
    )

    return {
        "response": system_response,
        "db_data": (db_records if 'db_records' in locals() else []),
        "parsed_intent": parsed,
        "llm_called": llm_called,
        "detected_intent": intent
    }
