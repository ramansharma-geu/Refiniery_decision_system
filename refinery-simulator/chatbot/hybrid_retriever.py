# Hybrid Retriever & Query Executor for RDIS Chatbot
from services import db_service
from chatbot.parser import parse_query
from chatbot.intent_classifier import detect_intent, INTENT_KNOWLEDGE, INTENT_CURRENT, INTENT_ANALYSIS, INTENT_SIMULATION
from chatbot.knowledge_retriever import retrieve_facts
from simulation_engine import estimate_parameters
from models import db, RefineryUnit, OperationalHistory
from sqlalchemy import func
import json
import re

# ── Unit conversion helpers (display) ────────────────────────────────────
def _f_to_c(f):
    """Fahrenheit to Celsius for display."""
    return round((float(f) - 32) * 5.0 / 9.0, 1)

def _psi_to_bar(psi):
    """PSI to bar for display."""
    return round(float(psi) * 0.0689476, 2)

def _bph_to_bpd(bph):
    """Barrels per hour to barrels per day."""
    return round(float(bph) * 24.0, 1)


def execute_db_query(parsed):
    """
    Executes a structured database query based on the parsed intent.
    Returns:
        tuple: (data_list, formatted_string, record_dicts)
    """
    intent = parsed["intent"]
    unit_code = parsed["unit_code"]
    parameter = parsed["parameter"]
    limit = parsed["limit"]
    extreme_type = parsed["extreme_type"]

    # 1. Handle GENERAL questions (no DB queries needed)
    if intent == "general" and not unit_code and not parameter:
        return None, "", []

    # Get units lookup map
    units = db_service.get_all_units()
    unit_map = {u.code: u for u in units}
    unit_id_map = {u.id: u.code for u in units}

    # Helper mapping for column fields
    col_attr = {
        "throughput": OperationalHistory.throughput,
        "pressure": OperationalHistory.pressure,
        "temperature": OperationalHistory.temperature,
        "flow_rate": OperationalHistory.flow_rate,
        "downtime": OperationalHistory.downtime,
        "yield": OperationalHistory.yield_,
        "energy_consumption": OperationalHistory.energy_consumption
    }

    # 2. Query CURRENT State
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
            # Query parameter for all units
            latest_all = db_service.get_latest_operational_data()
            records = [r.to_dict() for r in latest_all]
            results = []
            for r in records:
                results.append(f"{r['unit_code']}: {r.get(parameter)}")
            desc = f"Current {parameter} across units: " + ", ".join(results)
            return records, desc, records

    # 3. Query HISTORY State
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

    # 4. Query AVERAGE Aggregation
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
            # Average for all units
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

    # 5. Query EXTREME (MAX or MIN)
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
            # Query across all units to find global max/min record
            query = db.session.query(OperationalHistory.unit_id, attr).order_by(attr.desc() if extreme_type == "MAX" else attr.asc()).limit(1).first()
            if query:
                uid, val = query
                code = unit_id_map.get(uid, f"Unit {uid}")
                desc = f"The {word} {parameter} was recorded at {code} with a value of {val}."
                return [{"unit_code": code, "parameter": parameter, "extreme": val}], desc, []

    return None, "Intent matched, but query execution returned no data.", []


def _format_simulation_response(unit, current_values, changes, estimates):
    """
    Format simulation response in engineer-style format.
    Uses °C for temperature, bar for pressure.
    Throughput in BPD, Flow Rate in BPH.
    
    Returns a formatted string under 120 words.
    """
    cd = estimates['current_display']
    td = estimates['target_display']
    adj = estimates['adjustments']
    
    lines = []
    
    # Current Conditions (from actual DB values)
    lines.append("Current Conditions")
    lines.append(f"• Throughput: {cd['throughput_bpd']} BPD")
    lines.append(f"• Flow Rate: {cd['flow_rate_bph']} BPH")
    lines.append(f"• Temperature: {cd['temperature_c']}°C")
    lines.append(f"• Pressure: {cd['pressure_bar']} bar")
    
    # Target Conditions
    lines.append("")
    lines.append("Target Conditions")
    # Show what the user asked to change
    if 'throughput_bpd' in changes or 'flow_rate_bpd' in changes:
        lines.append(f"• Throughput: {td['throughput_bpd']} BPD")
        lines.append(f"• Flow Rate: {td['flow_rate_bph']} BPH")
    if 'temperature_C_delta' in changes:
        target_temp_c = _f_to_c(estimates['internal']['t_temp_f'])
        lines.append(f"• Temperature: {target_temp_c}°C")
    if 'pressure_pct' in changes:
        target_press_bar = _psi_to_bar(estimates['internal']['t_press_psi'])
        lines.append(f"• Pressure: {target_press_bar} bar")
    if not any(k in changes for k in ['throughput_bpd', 'flow_rate_bpd', 'temperature_C_delta', 'pressure_pct']):
        lines.append(f"• Throughput: {td['throughput_bpd']} BPD")
        lines.append(f"• Flow Rate: {td['flow_rate_bph']} BPH")
    
    # Parameter Adjustments
    lines.append("")
    lines.append("Parameter Adjustments")
    lines.append(f"• Temperature: {adj['temperature_range_c']}")
    lines.append(f"• Pressure: {adj['pressure_range_bar']}")
    
    # Expected Changes
    lines.append("")
    lines.append("Expected Changes")
    for c in estimates['consequences'][:3]:
        lines.append(f"• {c}")
    
    # Operational Risks
    lines.append("")
    lines.append("Operational Risks")
    for r in estimates['risks'][:3]:
        lines.append(f"• {r}")
    
    # Recommendations
    lines.append("")
    lines.append("Recommendations")
    for r in estimates['recommendations'][:3]:
        lines.append(f"• {r}")
    
    return "\n".join(lines)


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
        f"• Throughput: {rec.get('throughput')} BPD",
        f"• Flow Rate: {rec.get('flow_rate')} BPH",
        f"• Temperature: {rec.get('temperature')} °F",
        f"• Pressure: {rec.get('pressure')} psi",
        f"• Yield: {rec.get('yield') or rec.get('yield_')}%",
        f"• Energy Consumption: {rec.get('energy_consumption')} MMBtu/hr",
        f"• Timestamp: {ts}"
    ]
    return "\n".join(lines) + "\n\n"


def get_hybrid_chatbot_response(user_query, slm_service):
    """
    Main query orchestrator:
    - Parses query
    - Routes to KNOWLEDGE / CURRENT_DATA / ANALYSIS / SIMULATION
    - Returns formatted response
    """
    q_lower = user_query.lower()

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
                            f"<b>Unit:</b> {u_obj.name} ({unit_code})<br>"
                            f"<b>Pressure Change:</b> {'+' if is_increase else '-'}{delta_val:.1f} psi (Current: {latest.pressure:.2f} psi -> Target: {new_pressure:.2f} psi)<br>"
                            f"<b>Financial Impact:</b> Net Loss of <b>${loss_amount:,.2f}/day</b> (100% loss of daily operating margin due to safety shutdown).<br>"
                            f"<b>Safety Status:</b> <span style='color: var(--semantic-error); font-weight: bold;'>CRITICAL</span> - Automatic Emergency Shutdown triggered. {shutdown_reason}<br><br>"
                            f"<b>Required Parameters for Safe & Profitable Operation:</b><br>"
                            f"• <b>Operating Pressure:</b> Maintain between <b>{min_norm_press:.1f} and {max_norm_press:.1f} psi</b> (Optimum: {opt_press:.1f} psi). Max mechanical safety limit: <b>{max_press:.1f} psi</b>.<br>"
                            f"• <b>Throughput:</b> Keep within <b>{latest.throughput:,.1f} bbl/day</b> (Max capacity: {u_obj.throughput_capacity:,.1f} bbl/day).<br>"
                            f"• <b>Operating Temperature:</b> Maintain between <b>{min_temp:.1f}°F and {max_temp:.1f}°F</b> (Optimum: {opt_temp:.1f}°F)."
                        )
                    else:
                        pressure_deviation = abs(new_pressure - opt_press)
                        yield_impact = -0.1 * pressure_deviation
                        new_yield = max(50.0, min(100.0, latest.yield_ + yield_impact))
                        new_profit = latest.throughput * (new_yield / 100.0) * margin_per_bbl
                        profit_diff = new_profit - baseline_profit

                        if profit_diff < 0:
                            impact_str = f"Net Loss of <b>${abs(profit_diff):,.2f}/day</b> (Yield dropped from {latest.yield_:.2f}% to {new_yield:.2f}%)"
                        else:
                            impact_str = f"Net Profit of <b>${profit_diff:,.2f}/day</b> (Yield changed to {new_yield:.2f}%)"

                        response = (
                            f"<b>Unit:</b> {u_obj.name} ({unit_code})<br>"
                            f"<b>Pressure Change:</b> {'+' if is_increase else '-'}{delta_val:.1f} psi (Current: {latest.pressure:.2f} psi -> Target: {new_pressure:.2f} psi)<br>"
                            f"<b>Financial Impact:</b> {impact_str}.<br>"
                            f"<b>Safety Status:</b> Operating within safe nominal bounds.<br><br>"
                            f"<b>Required Parameters for Safe & Profitable Operation:</b><br>"
                            f"• <b>Operating Pressure:</b> Maintain between <b>{min_norm_press:.1f} and {max_norm_press:.1f} psi</b> (Optimum: {opt_press:.1f} psi).<br>"
                            f"• <b>Throughput:</b> Keep within <b>{latest.throughput:,.1f} bbl/day</b> (Max capacity: {u_obj.throughput_capacity:,.1f} bbl/day).<br>"
                            f"• <b>Operating Temperature:</b> Maintain between <b>{min_temp:.1f}°F and {max_temp:.1f}°F</b> (Optimum: {opt_temp:.1f}°F)."
                        )

                    db_records = [latest.to_dict()]
                    db_service.log_chatbot_query(
                        user_query=user_query,
                        system_response=response,
                        retrieved_data_used=db_records,
                        llm_called=False
                    )

                    return {
                        "response": response,
                        "db_data": db_records,
                        "parsed_intent": {
                            "intent": "query_current",
                            "unit_code": unit_code,
                            "parameter": "pressure",
                            "limit": 5,
                            "extreme_type": None
                        },
                        "llm_called": False
                    }

    # ── 1. Parse using existing parser for DB queries ────────────────────
    parsed = parse_query(user_query)

    # ── 2. Detect higher-level intent ────────────────────────────────────
    intent = detect_intent(user_query)

    if intent == "CURRENT_DATA":
        parsed["intent"] = "query_current"

    # Pre-check for parameter explanation query (Bug 4)
    is_explanation_query = any(k in q_lower for k in ["explain", "explanation", "describe", "description"]) and not ("only database values" in q_lower or "database values" in q_lower or "only database" in q_lower)
    exp_unit = None
    if "cdu" in q_lower or "crude distillation" in q_lower:
        exp_unit = "CDU"
    elif "vdu" in q_lower or "vacuum distillation" in q_lower:
        exp_unit = "VDU"
    elif "fcc" in q_lower or "catalytic cracking" in q_lower:
        exp_unit = "FCC"
    elif "hydro" in q_lower or "treating" in q_lower:
        exp_unit = "Hydrotreater"
    elif "storage" in q_lower or "terminal" in q_lower:
        exp_unit = "Storage Terminal"

    db_header = ""
    if is_explanation_query and exp_unit:
        db_header = get_unit_db_values_header(exp_unit)

    # Prepare background metrics for DB-backed workflows
    latest_all = db_service.get_latest_operational_data()
    global_context = {r.unit.code: {
        "throughput": r.throughput,
        "pressure": r.pressure,
        "temperature": r.temperature,
        "flow_rate": r.flow_rate,
        "downtime": r.downtime,
        "yield": r.yield_,
        "energy_consumption": r.energy_consumption,
        "timestamp": getattr(r, 'timestamp', None)
    } for r in latest_all if r.unit}

    llm_called = False
    system_response = ""
    db_records = []

    # ── KNOWLEDGE ────────────────────────────────────────────────────────
    if intent == INTENT_KNOWLEDGE:
        facts = retrieve_facts(user_query)
        facts_context = ""
        if facts:
            facts_context = "Ground Truth Facts (Use these facts to ensure technical accuracy, do NOT contradict them):\n" + "\n".join([f"- {f}" for f in facts]) + "\n\n"
        
        prompt = (
            f"{facts_context}"
            f"Question: {user_query}\n\n"
            "Format required:\n"
            "<Direct answer sentence>\n\n"
            "• Bullet 1\n"
            "• Bullet 2\n"
            "(Max 5 bullets)\n"
            "Only include practical operational points; no introductions or theory.\n"
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
                        lines.append(f"{code} Current {param_name}:\n• Value: {val}{unit_str}\n• Timestamp: {ts}")
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
                            param_lines.append(f"• {param_name}: {val}{unit_str}")
                        lines.append(f"Current Database Values for {code}:\n" + "\n".join(param_lines) + f"\n• Timestamp: {ts}")
                else:
                    lines.append(
                        f"Current Database Values for {code}:\n"
                        f"• Throughput: {rec.get('throughput')} BPD\n"
                        f"• Flow Rate: {rec.get('flow_rate')} BPH\n"
                        f"• Temperature: {rec.get('temperature')} °F\n"
                        f"• Pressure: {rec.get('pressure')} psi\n"
                        f"• Yield: {rec.get('yield') or rec.get('yield_')}%\n"
                        f"• Energy Consumption: {rec.get('energy_consumption')} MMBtu/hr\n"
                        f"• Timestamp: {ts}"
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
                standard_unit = unit
                if unit == "Storage Terminal" or unit == "STA":
                    standard_unit = "Storage Terminal"
                
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
                        audit_res = analyze_parameter(standard_unit, k, v)
                        if audit_res.get("status") in ["WARNING", "CRITICAL"] and audit_res.get("concern"):
                            concerns.append(f"• {audit_res['concern']} Status: {audit_res['status']}")

            # Unit-specific expert knowledge
            expert_causes = [
                "Catalyst thermal fatigue or chemical deactivation.",
                "Feedstock quality or composition shift.",
                "Instrument calibration error or sensor drift."
            ]
            expert_impacts = [
                "Degraded high-value product selectivity.",
                "Increased coke or heavy residue yield.",
                "Higher utility and fuel gas costs."
            ]
            expert_recs = [
                "Audit local field instrumentation and sensors.",
                "Review laboratory product quality logs.",
                "Adjust reflux/recycle flow rates to stabilize process."
            ]
            
            confidence = "HIGH"
            confidence_reason = "Consistent historical operating data available in database."
            
            if target_unit == "FCC":
                fcc_temp = compact.get("FCC", {}).get("temperature") or 0
                fcc_yield = compact.get("FCC", {}).get("yield") or 0
                if fcc_temp >= 1000 or "temperature" in user_query.lower():
                    expert_causes = ["Excessive riser temperature causing overcracking.", "Regenerator air grid issue.", "Catalyst bypass flow."]
                    expert_impacts = ["Riser thermal runaway coking risk.", "High dry gas yield and reduced gasoline selectivity.", "Catalyst thermal damage."]
                    expert_recs = ["Check riser quench injection.", "Inspect catalyst circulation slides.", "Calibrate temperature thermocouples."]
                elif fcc_yield < 75 or "yield" in user_query.lower():
                    expert_causes = ["Catalyst deactivation or poison carryover.", "Feedstock heavy metal poisoning.", "Stripper steam blockages."]
                    expert_impacts = ["Reduced conversion gasoline yield.", "Coke buildup in cyclone grids.", "Increased catalyst replacement rate."]
                    expert_recs = ["Increase catalyst fresh make-up rate.", "Audit catalyst activity logs.", "Check feed sulfur levels."]
                    confidence = "MEDIUM"
                    confidence_reason = "Reduced conversion is likely catalyst deactivation but requires metals verification."
            elif target_unit == "CDU":
                cdu_tp = compact.get("CDU", {}).get("throughput") or 0
                cdu_press = compact.get("CDU", {}).get("pressure") or 0
                if cdu_tp > 90000 or "flow" in user_query.lower() or "throughput" in user_query.lower():
                    expert_causes = ["High liquid load exceeding tray design throughput.", "Over-firing in the main heater furnace.", "Flooding in wash zone trays."]
                    expert_impacts = ["Main column trays flooding and entrainment.", "Extreme furnace tube skin temperatures (hot spots).", "Poor fractionation quality."]
                    expert_recs = ["Check column delta pressure differential.", "Inspect furnace tube skins.", "Decrease feed rate gradually."]
                elif cdu_press > 50 or "pressure" in user_query.lower():
                    expert_causes = ["Overhead condenser fouling.", "Accumulated non-condensable gas lock.", "Reflux accumulator vent valve failure."]
                    expert_impacts = ["Overhead relief valve lifting hazard.", "Loss of light naphtha distillation cut separation.", "Tray mechanical deflection."]
                    expert_recs = ["Monitor overhead condenser inlet/outlet delta temperature.", "Check non-condensable accumulator purge vents.", "Slowly trim furnace firing."]
            elif target_unit == "Hydrotreater":
                ht_tp = compact.get("Hydrotreater", {}).get("throughput") or 0
                ht_press = compact.get("Hydrotreater", {}).get("pressure") or 0
                if ht_tp > 24000 or "flow" in user_query.lower() or "throughput" in user_query.lower():
                    expert_causes = ["Space velocity exceeding design desulfurization kinetics.", "Hydrogen recycle compressor bottleneck.", "Reactor temperature runaway hazard."]
                    expert_impacts = ["Hydrogen deficiency in catalyst bed.", "Sulfur breakthrough in ULSD pool.", "High bed pressure drops."]
                    expert_recs = ["Increase recycle gas rate.", "Activate emergency reactor cold quench lines.", "Adjust feed rate to design capacity."]
                elif ht_press > 1050 or "pressure" in user_query.lower():
                    expert_causes = ["Catalyst bed particulate plugging or bed compaction.", "Preheat exchanger train fouling.", "Hydrogen feed gas compressor surge."]
                    expert_impacts = ["Pressure drop exceeds catalyst bed collapse limits.", "Feed pump motor high-amperage trip.", "Catalyst poisoning."]
                    expert_recs = ["Perform reactor pressure drop audit.", "Verify hydrogen feed rate.", "Prepare catalyst skimming maintenance schedule."]
            elif target_unit == "Storage Terminal":
                st_util = compact.get("Storage Terminal", {}).get("yield") or 0
                if st_util > 85 or "utilization" in user_query.lower():
                    expert_causes = ["Feed import flow rate exceeding outgoing export shipping volumes.", "Demurrage delay at shipping docks.", "Buffer tank maintenance lockouts."]
                    expert_impacts = ["Tank overflow and containment hazard.", "Downstream CDU throughput runback bottleneck.", "Demurrage penalty accumulation."]
                    expert_recs = ["Expedite cargo export pump dispatch.", "Segregate high-utilization tanks.", "Prepare pipeline transfer bypass routing."]

            concerns_str = "\n".join(concerns) if concerns else "• None immediate detected."
            
            formatted_values = []
            for unit_name, metrics in compact.items():
                metrics_lines = [f"{k}: {v}" for k, v in metrics.items() if v is not None]
                formatted_values.append(f"• {unit_name}: {', '.join(metrics_lines)}")
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
                f"- Most Likely Cause: {expert_causes[0]}\n"
                f"- Other Possible Causes: {', '.join(expert_causes[1:])}\n"
                f"- Operational Impact: {', '.join(expert_impacts)}\n"
                f"- Recommendations: {', '.join(expert_recs)}\n"
                f"- Confidence: {confidence} (Reason: {confidence_reason})\n\n"
                "Output Format Checklist:\n"
                "Start with a single direct engineering conclusion sentence. Then output these exact sections on their own lines:\n\n"
                "Current Values\n"
                f"{formatted_values_str}\n\n"
                "Observed Concerns\n"
                f"{concerns_str}\n\n"
                "Possible Causes\n"
                "Most Likely Cause:\n"
                f"• {expert_causes[0]}\n"
                "Other Possible Causes:\n" + "\n".join([f"• {c}" for c in expert_causes[1:]]) + "\n\n"
                "Operational Impact\n" + "\n".join([f"• {i}" for i in expert_impacts]) + "\n\n"
                "Recommendations\n" + "\n".join([f"• {r}" for r in expert_recs]) + "\n\n"
                f"Confidence Level\n• {confidence}\nReason: {confidence_reason}\n\n"
                "Format rules:\n"
                "- Start with a single direct process-engineering conclusion sentence.\n"
                "- Write the exact section headers: Current Values, Observed Concerns, Possible Causes, Operational Impact, Recommendations, Confidence Level.\n"
                "- Possible Causes header MUST list 'Most Likely Cause' and 'Other Possible Causes' subheadings.\n"
                "- Be concise and keep the response under 130 words.\n"
                "- REMINDER: Use ONLY the exact numbers from Input Data Facts. Do NOT hallucinate values.\n"
            )
            system_response = slm_service.query(prompt, context_data=None)
            llm_called = True

    # ── SIMULATION ───────────────────────────────────────────────────────
    elif intent == INTENT_SIMULATION:
        # 1. Identify unit
        unit = 'CDU'
        if 'fcc' in q_lower or 'catalytic cracking' in q_lower:
            unit = 'FCC'
        elif 'vdu' in q_lower or 'vacuum distillation' in q_lower:
            unit = 'VDU'
        elif 'hydro' in q_lower or 'treating' in q_lower:
            unit = 'Hydrotreater'
        elif 'storage' in q_lower or 'terminal' in q_lower or 'logistics' in q_lower:
            unit = 'Storage Terminal'

        # 2. Fetch latest values from SQLite
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

        # 3. Parse numeric changes from user query
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

        # Robust current/target extraction (Failure 6)
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
            # Fallback if not assigned
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

        # Main numeric value to parse
        val = target_val if target_val is not None else (nums[0] if nums else None)
        
        # ── Throughput / Flow rate parsing (Failure 2 & 3 Decoupling) ────────────────────────────────
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

        # ── Temperature ──────────────────────────────────────────────────
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

        # ── Pressure / Vacuum ────────────────────────────────────────────
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

        # ── Sulfur feed ──────────────────────────────────────────────────
        if 'sulfur' in q_lower:
            if 'double' in q_lower or 'doubles' in q_lower:
                changes['sulfur_feed_mult'] = 2.0
            elif nums:
                changes['sulfur_feed_mult'] = 1.0 + (nums[0] / 100.0) if is_percent else nums[0]
            else:
                changes['sulfur_feed_mult'] = 2.0

        # ── Tank Utilization ─────────────────────────────────────────────
        if any(k in q_lower for k in ['utilization', 'utilize', 'utilized', 'capacity']):
            if nums:
                changes['tank_utilization_pct'] = nums[0]

        # ── Catalyst activity ────────────────────────────────────────────
        if 'catalyst' in q_lower and ('activity' in q_lower or 'ratio' in q_lower):
            if nums:
                changes['catalyst_activity_pct_change'] = -nums[0] if is_decrease else nums[0]

        # ── Heater duty ──────────────────────────────────────────────────
        if 'duty' in q_lower or 'heater' in q_lower:
            if nums:
                changes['heater_duty_pct_change'] = -nums[0] if is_decrease else nums[0]

        # ── API gravity ──────────────────────────────────────────────────
        if 'api' in q_lower:
            if nums:
                changes['api_gravity_delta'] = -nums[0] if is_decrease else nums[0]

        # 4. Run simulation engine
        estimates = estimate_parameters(unit, changes, current_values)

        # 5. Build response
        system_response = _format_simulation_response(unit, current_values, changes, estimates)
        llm_called = False

    else:
        # Default fallback — use SLM
        prompt = f"{user_query}\nAnswer concisely in bullets, direct answer first."
        system_response = slm_service.query(prompt, context_data=None)
        llm_called = True

    if db_header:
        system_response = db_header + "Explanation:\n" + system_response

    # ── Log chatbot query ────────────────────────────────────────────────
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
