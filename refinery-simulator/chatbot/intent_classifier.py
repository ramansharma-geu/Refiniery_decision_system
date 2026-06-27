import re

INTENT_KNOWLEDGE = "KNOWLEDGE"
INTENT_CURRENT = "CURRENT_DATA"
INTENT_ANALYSIS = "ANALYSIS"
INTENT_SIMULATION = "SIMULATION"
INTENT_MIXED = "MIXED"
INTENT_OPERATIONAL_IMPACT = "OPERATIONAL_IMPACT"
INTENT_SEVERITY_RANKING = "SEVERITY_RANKING"


def detect_intent(question: str) -> str:
    q = (question or "").strip().lower()
    
    if not q or len(q.strip()) == 0:
        return INTENT_KNOWLEDGE
    
    # ── SEVERITY RANKING (highest priority) ─────────────────────────────
    severity_patterns = [
        r'which\s+(unit|refinery|plant)\s+(requires|needs|demands)\s+.*?(attention|priority|focus)',
        r'rank\s+(all\s+)?(units?|refinery|plant)\s+(by|based\s+on)',
        r'which\s+unit\s+has\s+(the\s+)?(highest|most|greatest|worst)\s+(risk|severity|danger|problem)',
        r'severity\s+ranking',
        r'priority\s+ranking',
        r'most\s+operator\s+attention',
        r'which\s+unit\s+is\s+(most|worst|critical|dangerous)',
    ]
    if any(re.search(pat, q) for pat in severity_patterns):
        return INTENT_SEVERITY_RANKING
    
    # ── OPERATIONAL IMPACT (critical threshold questions) ────────────────
    impact_patterns = [
        r'operational\s+impact',
        r'what\s+are\s+the\s+risks?\s+of\s+operating\s+at',
    ]
    if any(re.search(pat, q) for pat in impact_patterns):
        return INTENT_OPERATIONAL_IMPACT
    
    # ── MIXED (knowledge + current data) ────────────────────────────────
    mixed_patterns = [
        r'explain\s+.*?\s+using\s+(current|database|actual)\s+(values?|data|records?)',
        r'what\s+is\s+\w+\s+and\s+what\s+(are|is)\s+(its|the)\s+current',
        r'compare\s+\w+\s+and\s+\w+\s+with\s+(current|database)',
        r'difference\s+between\s+.*?\s+using\s+(current|database)',
        r'what\s+is\s+.*?\s+and\s+what\s+is\s+(the\s+)?current',
        r'current\s+.*?\s+is\s+\d+.*?explain',
        r'current\s+.*?\s+is\s+\d+.*?is\s+this\s+normal',
        r'current\s+.*?\s+is\s+\d+.*?is\s+this\s+(within|efficient|normal|ok)',
        r'current\s+.*?\s+is\s+\d+.*?explain',
        r'what\s+is\s+.*?\s+and\s+what\s+is\s+the\s+current',
        r'show\s+current\s+.*?\s+and\s+explain',
        r'display\s+current\s+.*?\s+and\s+explain',
        r'what\s+is\s+.*?\s+and\s+what\s+are\s+the\s+current',
        r'current\s+.*?\s+explain',
    ]
    if any(re.search(pat, q) for pat in mixed_patterns):
        return INTENT_MIXED
    
    # ── DATABASE-ONLY override ──────────────────────────────────────────
    if "only database values" in q or "only database" in q or "database values" in q:
        return INTENT_CURRENT
    
    # ── Simulation indicators (HIGHEST PRIORITY) ───────────────────────
    sim_patterns = [
        r'\bif\b',
        r'\bsuppose(s|d|ing)?\b',
        r'\bassume(s|d|ing)?\b',
        r'\b(increase|decrease|drop|rise|set|adjust)\s+(.*?\s+)?(by|to)\s+\d+',
        r'\bwhat\s+will\s+happen\b',
        r'\bwhat\s+should\s+happen\b',
        r'\bwhat\s+changes\s+are\s+required\b',
        r'\bwhat\s+adjustments\s+are\s+required\b',
        r'\btarget(s)?\s+(throughput|temperature|pressure|yield)',
        r'\bscenario(s)?\b',
        r'\bsimulate\b',
        r'\bimpact\s+of\s+(increasing|decreasing|changing)',
        r'what\s+happens?\s+(when|if)\s+.*?\s+(increase|decrease|rises?|drops?|reaches?)',
        r'what\s+are\s+the\s+(effects?|consequences?|risks?)\s+of',
        r'what\s+happens?\s+if\s+.*?\s+\d+',
    ]
    if any(re.search(pat, q) for pat in sim_patterns):
        return INTENT_SIMULATION
    
    # ── Knowledge definitions (HIGH PRIORITY for "how does", "what is", "explain") ──
    knowledge_how_what = [
        r'how\s+does\s+.*?\s+work',
        r'what\s+is\s+the\s+(purpose|function|role|difference)',
        r'what\s+is\s+the\s+meaning\s+of',
        r'explain\s+the\s+(role|concept|purpose|process|principle)',
        r'what\s+causes?\s+.*?\s+(in|within)\s+(a|the)',
        r'what\s+is\s+the\s+difference\s+between',
        r'why\s+is\s+.*?\s+used',
        r'why\s+does\s+.*?\s+work',
        r'what\s+is\s+.*?\s+and\s+how\s+does\s+it',
    ]
    if any(re.search(pat, q) for pat in knowledge_how_what):
        # But NOT if it's asking for current values
        if not any(k in q for k in ["current", "today", "now", "show me", "display"]):
            return INTENT_KNOWLEDGE
    
    # ── Knowledge exact matches ─────────────────────────────────────────
    knowledge_exact = [
        "what is cdu", "what is vdu", "what is fcc", "what is hydrotreater",
        "what is storage terminal", "what is throughput", "what is yield",
        "what is pressure in refinery", "what is temperature in refinery",
        "what is energy consumption", "purpose of cdu", "purpose of vdu",
        "purpose of fcc", "purpose of hydrotreater", "purpose of storage terminal",
        "why is hydrogen used", "why is hydrogen purity critical",
        "why is furnace outlet temperature important",
        "why is zeolite catalyst used", "why is catalyst important",
        "explain column flooding", "explain tray weeping",
        "explain catalyst regeneration", "explain delayed maintenance",
        "explain refinery bottlenecks", "catalyst regeneration",
        "compare cdu and vdu", "compare fcc and cdu",
        "what is catalyst deactivation", "what is refinery bottleneck",
        "how does", "what is the purpose", "what is the function",
        "what is the role", "what is the difference",
    ]
    for k in knowledge_exact:
        if k in q:
            return INTENT_KNOWLEDGE
    
    # ── Analysis indicators ─────────────────────────────────────────────
    analysis_indicators = [
        "why is", "why are", "why does", "what is causing",
        "analyze", "analyze the", "evaluate", "trend", "status",
        "root cause", "reason for", "cause of",
    ]
    if any(k in q for k in analysis_indicators):
        if not any(k in q for k in ["used for", "purpose", "what is the purpose", "what is cdu", "what is vdu", "what is fcc"]):
            return INTENT_ANALYSIS
    
    # ── CURRENT_DATA indicators ─────────────────────────────────────────
    current_explicit = ["current", "today", "now", "show me", "display", "what are the current", "what is the"]
    has_current_keyword = any(k in q for k in current_explicit)
    
    unit_keywords = ["cdu", "vdu", "fcc", "hydrotreater", "storage terminal", "storage"]
    param_keywords = ["throughput", "temperature", "pressure", "flow rate", "yield", "energy", "utilization", "inventory", "dispatch", "steam rate", "level", "rate"]
    has_unit = any(u in q for u in unit_keywords)
    has_param = any(p in q for p in param_keywords)
    
    if has_current_keyword and has_unit:
        # But NOT if it's asking for analysis or explanation
        if not any(k in q for k in ["why", "reason", "cause", "explain", "analyze", "is this", "is it", "within spec", "efficient"]):
            return INTENT_CURRENT
    
    if has_unit and has_param and not any(k in q for k in ["why", "reason", "cause", "explain", "analyze", "if ", "suppose", "assume", "what happens", "impact", "is this", "is it"]):
        return INTENT_CURRENT
    
    # ── Default fallback → knowledge ────────────────────────────────────
    return INTENT_KNOWLEDGE
