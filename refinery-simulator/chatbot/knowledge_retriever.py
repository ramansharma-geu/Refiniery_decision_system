import os
import json
from pathlib import Path

_knowledge_cache = None

def load_knowledge():
    global _knowledge_cache
    if _knowledge_cache is not None:
        return _knowledge_cache
    
    # Locate refinery_knowledge.json relative to this file
    json_path = Path(__file__).resolve().parent.parent / "refinery_knowledge.json"
    if not json_path.exists():
        # Fallback check current working directory
        json_path = Path("refinery_knowledge.json")
        
    if json_path.exists():
        try:
            with open(json_path, "r") as f:
                _knowledge_cache = json.load(f)
        except Exception as e:
            print(f"Error loading refinery_knowledge.json: {e}")
            _knowledge_cache = {}
    else:
        print(f"Warning: refinery_knowledge.json not found at {json_path}")
        _knowledge_cache = {}
    return _knowledge_cache

def retrieve_facts(query: str) -> list:
    """
    Scans the query for keywords matching CDU, VDU, FCC, Hydrotreater,
    Storage Terminal, or Catalyst Deactivation, and retrieves ground truth facts.
    """
    knowledge = load_knowledge()
    if not knowledge:
        return []
    
    q = (query or "").strip().lower()
    retrieved = []
    matched_keys = set()

    # Define keyword matching rules
    rules = {
        "CDU": ["cdu", "crude distillation", "atmospheric distillation"],
        "VDU": ["vdu", "vacuum distillation"],
        "FCC": ["fcc", "fluid catalytic cracking", "catalytic cracking"],
        "Hydrotreater": ["hydrotreater", "hydrotreating", "desulfur", "hds"],
        "Storage Terminal": ["storage", "terminal", "tank farm", "tank"],
        "Catalyst Deactivation": ["catalyst", "deactivation", "poisoning", "sintering", "coking", "coke deposit"]
    }

    for key, keywords in rules.items():
        if any(kw in q for kw in keywords):
            matched_keys.add(key)

    # Collect facts for matched keys
    for key in matched_keys:
        if key in knowledge:
            unit_info = knowledge[key]
            if "facts" in unit_info:
                for fact in unit_info["facts"]:
                    if fact not in retrieved:
                        retrieved.append(fact)
                        
    return retrieved
