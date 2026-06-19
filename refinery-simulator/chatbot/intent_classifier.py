import re

INTENT_KNOWLEDGE = "KNOWLEDGE"
INTENT_CURRENT = "CURRENT_DATA"
INTENT_ANALYSIS = "ANALYSIS"
INTENT_SIMULATION = "SIMULATION"


def detect_intent(question: str) -> str:
    q = (question or "").strip().lower()
    
    # Database-only query override (Failure 5)
    if "only database values" in q or "only database" in q or "database values" in q:
        return INTENT_CURRENT
        
    # Term difference explanation override (Failure 4)
    if "difference" in q:
        return INTENT_KNOWLEDGE
    
    # Specific knowledge overrides to prevent false grouping into SIMULATION or ANALYSIS
    if "affected" in q and ("unit" in q or "refinery" in q):
        return INTENT_KNOWLEDGE
        
    # Simulation indicators (highest priority)
    # Detect phrases: if, suppose, assume, increase, decrease, another, impact, consequence,
    # what will happen, what should happen, what changes are required, what adjustments are required,
    # target, scenario, risk, recommendation
    sim_patterns = [
        r'\bif\b',
        r'\bsuppose(s|d|ing)?\b',
        r'\bassume(s|d|ing)?\b',
        r'\bincrease(s|d)?\b',
        r'\bdecrease(s|d)?\b',
        r'\banother\b',
        r'\bimpact(s|ed)?\b',
        r'\bconsequence(s)?\b',
        r'\bwhat\s+will\s+happen\b',
        r'\bwhat\s+should\s+happen\b',
        r'\bwhat\s+changes\s+are\s+required\b',
        r'\bwhat\s+adjustments\s+are\s+required\b',
        r'\btarget(s)?\b',
        r'\bscenario(s)?\b',
        r'\brisk(s)?\b',
        r'\brecommendation(s)?\b',
        r'\brecommend(s|ed|ing)?\b'
    ]
    if any(re.search(pat, q) for pat in sim_patterns):
        return INTENT_SIMULATION
        
    # Specific knowledge overrides to prevent false grouping into ANALYSIS
    if any(k in q for k in ["catalyst deactivation", "debottlenecking", "heat exchanger network", "fractionating column", "catalyst regeneration"]):
        return INTENT_KNOWLEDGE
        
    # CURRENT_DATA indicators (explicit show/display/current/which unit or asking for parameters/metrics/values)
    units_keywords = ["cdu", "vdu", "fcc", "hydrotreater", "storage terminal", "storage", "refinery"]
    param_keywords = ["parameter", "parameters", "metric", "metrics", "value", "values", "flow rate", "flowrate", "temperature", "temp", "pressure", "throughput", "yield", "energy"]
    has_unit = any(u in q for u in units_keywords)
    has_param_word = any(pw in q for pw in param_keywords)

    if any(k in q for k in ["current", "today", "now", "show", "display", "which unit", "which has", "which unit has", "which has the"]) or (has_unit and has_param_word):
        # Do not classify as current data if it is clearly asking for a root-cause / analysis / explanation / simulation
        if not any(k in q for k in ["why", "reason", "cause", "explain", "analyze", "if", "suppose", "assume", "increase", "decrease", "what happens"]):
            return INTENT_CURRENT
        
    # Analysis indicators
    analysis_indicators = ["why", "reason", "caus", "cause", "decreasing", "increasing", "trend", "why is", "why are", "what is causing", "analyze", "evaluate", "evaluation", "status", "operating at", "observed", "risk", "bottleneck", "explain", "explanation", "describe", "description"]
    if any(k in q for k in analysis_indicators):
        # Treat straightforward 'why is X used' as knowledge
        if 'used' in q or 'used for' in q or 'purpose' in q:
            return INTENT_KNOWLEDGE
        return INTENT_ANALYSIS

    # Default fallback -> knowledge
    return INTENT_KNOWLEDGE


