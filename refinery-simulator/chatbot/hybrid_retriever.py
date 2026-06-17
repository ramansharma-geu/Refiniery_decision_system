# Hybrid Retriever & Query Executor for RDIS Chatbot
from services import db_service
from chatbot.parser import parse_query
from models import db, RefineryUnit, OperationalHistory
from sqlalchemy import func
import json

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

def get_hybrid_chatbot_response(user_query, slm_service):
    """
    Routines query logic:
    - Checks for unit pressure financial impact queries first to provide direct calculations without theory.
    - Parses query.
    - If database question: executes SQL, passes context to SLM to synthesize response.
    - If general: queries SLM with background context.
    - Logs session.
    """
    q_lower = user_query.lower()
    if "pressure" in q_lower and any(k in q_lower for k in ["profit", "loss", "margin", "cost", "economic"]):
        # Identify unit
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
            import re
            nums = re.findall(r'\b\d+(?:\.\d+)?\b', q_lower)
            delta_val = float(nums[0]) if nums else 100.0

            is_increase = True
            if any(k in q_lower for k in ["decrease", "down", "lower", "drop", "reduction", "reduced"]):
                is_increase = False

            # Fetch latest metrics
            units = db_service.get_all_units()
            unit_map = {u.code: u for u in units}
            u_obj = unit_map.get(unit_code)
            if u_obj:
                latest = db_service.get_latest_operational_data(u_obj.id)
                if latest:
                    # Unit specific constants
                    # (max_design_pressure, normal_min_pressure, normal_max_pressure, opt_pressure, product_margin_per_bbl, normal_min_temp, normal_max_temp, opt_temp)
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
                    elif unit_code == "VDU" and new_pressure > max_press:
                        is_shutdown = True
                        shutdown_reason = f"VDU operating pressure ({new_pressure:.2f} psi) exceeds vacuum safety threshold, initiating emergency shutdown."

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

                    # Log chatbot query
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

    # 1. Parse
    parsed = parse_query(user_query)

    # 2. Load latest metrics as a global background context
    latest_all = db_service.get_latest_operational_data()
    global_context = {r.unit.code: {
        "throughput": r.throughput,
        "pressure": r.pressure,
        "temperature": r.temperature,
        "flow_rate": r.flow_rate,
        "downtime": r.downtime,
        "yield": r.yield_,
        "energy_consumption": r.energy_consumption
    } for r in latest_all if r.unit}

    # 3. Execute DB Query
    db_data, db_desc, db_records = execute_db_query(parsed)

    # 4. Formulate Prompt for SLM
    llm_called = False
    system_response = ""

    if parsed["intent"] == "general":
        # General refinery concept
        prompt = (
            f"The user is asking: '{user_query}'. Respond directly using your refinery engineering knowledge.\n"
            f"Requirements:\n"
            f"- Answer in at most 7-8 bullet points.\n"
            f"- Output only content directly answering the question. Avoid any preambles, introductory definitions, general theory, or concluding summaries.\n"
            f"- Keep and state all relevant numbers, figures, or calculations for the unit or plant if asked or required."
        )
        system_response = slm_service.query(prompt, context_data=global_context)
        llm_called = True
    else:
        # Database question or hybrid
        if db_desc:
            prompt = (
                f"The user is asking: '{user_query}'.\n"
                f"Operational data from database: {db_desc}.\n"
                f"Explain the operational significance of this data.\n"
                f"Requirements:\n"
                f"- Answer in at most 7-8 bullet points.\n"
                f"- Output only content directly answering the question. Avoid any preambles, introductory definitions, general theory, or concluding summaries.\n"
                f"- Keep and state all relevant numbers, figures, or calculations for the unit or plant if asked or required."
            )
            system_response = slm_service.query(prompt, context_data=global_context)
            llm_called = True
        else:
            system_response = "I couldn't locate specific data in the refinery database matching that question. Please try asking about a specific unit (CDU, VDU, FCC, Hydrotreater) and parameter (throughput, yield, pressure, temperature)."

    # 5. Log chatbot query
    db_service.log_chatbot_query(
        user_query=user_query,
        system_response=system_response,
        retrieved_data_used=db_records,
        llm_called=llm_called
    )

    return {
        "response": system_response,
        "db_data": db_records,
        "parsed_intent": parsed,
        "llm_called": llm_called
    }
