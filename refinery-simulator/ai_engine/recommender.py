# AI Recommendation Engine for RDIS

def generate_recommendations(before_state, after_state, risk_score, bottleneck_unit_code, units_by_code):
    """
    Analyzes simulated parameter deltas to generate context-specific operational recommendations.
    Returns a list of dicts: [{'unit_id': int or None, 'recommendation_text': str, 'priority': str}]
    """
    recs = []
    
    # 1. Look up unit DB IDs by code for mapping
    unit_ids = {code: u.id for code, u in units_by_code.items()}
    
    # 2. General Risk-Based Recommendations
    if risk_score >= 80:
        recs.append({
            "unit_id": None,
            "recommendation_text": f"Refinery-wide operational risk is CRITICAL ({risk_score}/100). Initiate emergency planning meetings and review emergency shutdown valves (ESVs).",
            "priority": "High"
        })
    elif risk_score >= 55:
        recs.append({
            "unit_id": None,
            "recommendation_text": f"Refinery operational risk is ELEVATED ({risk_score}/100). Implement shift-level monitoring on stressed parameters.",
            "priority": "Medium"
        })

    # 3. Unit-Specific Rules based on parameter changes
    for code, after in after_state.items():
        before = before_state[code]
        u_id = unit_ids.get(code)
        
        # Check for extreme throughput drops (Shutdowns)
        if before["throughput"] > 0 and after["throughput"] == 0:
            recs.append({
                "unit_id": u_id,
                "recommendation_text": f"{code} throughput has dropped to zero (Complete Outage). Isolate process lines, open nitrogen purging lines, and adjust inventory routing.",
                "priority": "High"
            })
            continue

        # Check for bottlenecks
        if code == bottleneck_unit_code:
            recs.append({
                "unit_id": u_id,
                "recommendation_text": f"{code} identified as active processing bottleneck. Limit upstream feed rates immediately to prevent pressure build-up and safety reliefs.",
                "priority": "High"
            })
            
        # Check capacity stressors
        if code == "CDU" and after["throughput"] > before["throughput"]:
            pct_increase = ((after["throughput"] - before["throughput"]) / before["throughput"]) * 100.0
            if pct_increase >= 8.0:
                recs.append({
                    "unit_id": u_id,
                    "recommendation_text": f"CDU crude charge rate surged by {pct_increase:.1f}%. Furnace coil temperatures must be monitored closely to prevent localized coking in radiant tubes.",
                    "priority": "Medium"
                })
                
        if code == "Hydrotreater":
            if after["throughput"] > before["throughput"]:
                recs.append({
                    "unit_id": u_id,
                    "recommendation_text": "Hydrotreater throughput surged. High pressure hydrogen make-up compressor must be checked for capacity limits; monitor bed delta temperatures to prevent thermal runaway.",
                    "priority": "High"
                })
            if after["pressure"] > before["pressure"] and after["pressure"] > 900:
                recs.append({
                    "unit_id": u_id,
                    "recommendation_text": f"Hydrotreater reactor operating at elevated pressure ({after['pressure']} psi). Catalytic bed channeling hazard; restrict hydrogen flow adjustments.",
                    "priority": "High"
                })

        if code == "VDU" and after["throughput"] < before["throughput"]:
            pct_drop = ((before["throughput"] - after["throughput"]) / before["throughput"]) * 100.0
            if pct_drop >= 30.0:
                recs.append({
                    "unit_id": u_id,
                    "recommendation_text": f"VDU running at a reduced rate (-{pct_drop:.1f}%). Divert heavy vacuum gas oil (HVGO) stream to storage buffer tanks immediately.",
                    "priority": "Medium"
                })

        if code == "Storage Terminal":
            if after["throughput"] > before["throughput"]:
                recs.append({
                    "unit_id": u_id,
                    "recommendation_text": "Storage Terminal loading throughput increased. Coordinate pipeline receipt logs and ship charter laytimes to avoid terminal demurrage fees.",
                    "priority": "Medium"
                })
            if after["downtime"] > before["downtime"]:
                recs.append({
                    "unit_id": u_id,
                    "recommendation_text": "Logistics terminal experiencing downtime. Reroute finished products to emergency external buffer tanks if run-down lines start backing up.",
                    "priority": "High"
                })
                
        # Check energy stress
        if after["energy_consumption"] > before["energy_consumption"] * 1.10:
            recs.append({
                "unit_id": u_id,
                "recommendation_text": f"{code} energy consumption increased by over 10%. Verify efficiency of heat exchanger preheat trains and optimize fuel gas fuel-air ratio.",
                "priority": "Low"
            })
            
        # Check high downtime
        if after["downtime"] > before["downtime"] + 5.0:
            recs.append({
                "unit_id": u_id,
                "recommendation_text": f"Delayed maintenance on {code} raises downtime risk. Perform non-destructive testing (NDT) checks and check vibration signals of rotating machinery.",
                "priority": "High"
            })

    # Default general recommendation if list is empty
    if not recs:
        recs.append({
            "unit_id": None,
            "recommendation_text": "Refinery operations normal. Continue routine inspections and maintain scheduled product distributions.",
            "priority": "Low"
        })

    return recs
