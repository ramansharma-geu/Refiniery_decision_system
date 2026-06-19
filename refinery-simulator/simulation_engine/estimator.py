"""
Wrapper to delegate parameter estimation to the root simulation_engine.py module.
Ensures single source of truth and avoids namespace collisions.
"""
import importlib.util
import os
from pathlib import Path
from typing import Dict, Any

# Dynamic loader for root simulation_engine.py
_ROOT_DIR = Path(__file__).resolve().parent.parent
_ENGINE_PATH = _ROOT_DIR / "simulation_engine.py"

if _ENGINE_PATH.exists():
    spec = importlib.util.spec_from_file_location("simulation_engine_root", str(_ENGINE_PATH))
    _sim_root = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_sim_root)
    _estimate_parameters = _sim_root.estimate_parameters
else:
    raise ImportError(f"Could not locate root simulation_engine.py at {_ENGINE_PATH}")


def estimate_parameters(unit: str, changes: Dict[str, float], current_values: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Delegates to the root simulation_engine.py implementation.
    """
    return _estimate_parameters(unit, changes, current_values)

