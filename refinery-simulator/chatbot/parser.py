# Chatbot Query Parser for RDIS
import re

def parse_query(query_text):
    """
    Parses natural language query text to extract intent, unit, parameter, and aggregation types.
    Returns:
        dict: {
            "intent": "general" | "query_current" | "query_history" | "query_extreme" | "query_average",
            "unit_code": str or None,
            "parameter": str or None,
            "limit": int,
            "extreme_type": "MAX" | "MIN" | None
        }
    """
    q = query_text.lower().strip()
    
    # 1. Map Units
    unit_code = None
    if "cdu" in q or "crude distillation" in q:
        unit_code = "CDU"
    elif "vdu" in q or "vacuum distillation" in q:
        unit_code = "VDU"
    elif "fcc" in q or "catalytic cracking" in q:
        unit_code = "FCC"
    elif "hydrotreater" in q or "treating" in q:
        unit_code = "Hydrotreater"
    elif "storage" in q or "terminal" in q or "logistics" in q:
        unit_code = "Storage Terminal"

    # 2. Map Parameters
    matched_params = []
    if "throughput" in q or "charge" in q or "feed" in q:
        matched_params.append("throughput")
    if "pressure" in q or "psi" in q or "bar" in q:
        matched_params.append("pressure")
    if "temperature" in q or "heat" in q or "temp" in q or "farenheit" in q:
        matched_params.append("temperature")
    if "flow rate" in q or "flowrate" in q or "flow" in q:
        matched_params.append("flow_rate")
    if "downtime" in q or "offline" in q:
        matched_params.append("downtime")
    if "yield" in q or "efficiency" in q or "utilization" in q:
        matched_params.append("yield")
    if "energy" in q or "power" in q or "electricity" in q or "consumption" in q or "fuel" in q:
        matched_params.append("energy_consumption")

    parameter = None
    if len(matched_params) == 1:
        parameter = matched_params[0]
    elif len(matched_params) > 1:
        parameter = matched_params

    # 3. Determine Intent & Modifiers
    intent = "general"
    extreme_type = None
    limit = 5 # Default limit for history queries

    # Keywords for historical trends
    history_keywords = ["history", "historical", "past", "trend", "days", "weeks", "records", "timeseries"]
    is_history = any(re.search(rf'\b{kw}\b', q) for kw in history_keywords)

    # Keywords for averages
    average_keywords = ["average", "avg", "mean", "summary"]
    is_average = any(re.search(rf'\b{kw}\b', q) for kw in average_keywords)

    # Keywords for extremes (max/min)
    max_keywords = ["highest", "maximum", "max", "peak", "most"]
    min_keywords = ["lowest", "minimum", "min", "least"]
    is_max = any(re.search(rf'\b{kw}\b', q) for kw in max_keywords)
    is_min = any(re.search(rf'\b{kw}\b', q) for kw in min_keywords)

    # Resolve limit numbers if present (e.g. "past 10 records" or "last 15 days")
    num_match = re.search(r'\b(last|past)\s+(\d+)\b', q)
    if num_match:
        limit = int(num_match.group(2))

    if is_average:
        intent = "query_average"
    elif is_max or is_min:
        intent = "query_extreme"
        extreme_type = "MAX" if is_max else "MIN"
    elif is_history:
        intent = "query_history"
    elif unit_code and parameter:
        intent = "query_current"
    elif (unit_code or parameter) and not any(kw in q for kw in ["what is", "why", "explain", "define", "describe"]):
        intent = "query_current"

    return {
        "intent": intent,
        "unit_code": unit_code,
        "parameter": parameter,
        "limit": limit,
        "extreme_type": extreme_type
    }
