# Core Simulation Engine for RDIS

from services import db_service
from simulation_engine.rules import get_rule_executor
from ai_engine.recommender import generate_recommendations

def run_simulation(scenario_id, user_id=None):
    """
    Retrieves the scenario, gets the current state of refinery units,
    applies the scenario formulas, generates recommendations, and persists the run in SQLite.
    """
    # 1. Retrieve the scenario
    scenario = db_service.get_scenario_by_id(scenario_id)
    if not scenario:
        raise ValueError(f"Scenario with ID {scenario_id} not found.")

    # 2. Retrieve current operational state of all units
    units = db_service.get_all_units()
    units_by_code = {u.code: u for u in units}
    
    before_state = {}
    for u in units:
        latest = db_service.get_latest_operational_data(u.id)
        if latest:
            before_state[u.code] = {
                "throughput": latest.throughput,
                "pressure": latest.pressure,
                "temperature": latest.temperature,
                "flow_rate": latest.flow_rate,
                "downtime": latest.downtime,
                "yield": latest.yield_,
                "energy_consumption": latest.energy_consumption
            }
        else:
            # Fallback default values if no history exists (safety)
            before_state[u.code] = {
                "throughput": u.throughput_capacity * 0.8,
                "pressure": 50.0,
                "temperature": 100.0,
                "flow_rate": 1000.0,
                "downtime": 0.0,
                "yield": 90.0,
                "energy_consumption": 100.0
            }

    # 3. Apply scenario rules
    executor = get_rule_executor(scenario.type)
    if not executor:
        raise ValueError(f"No rule executor defined for scenario type: {scenario.type}")
        
    after_state, risk_score, bottleneck_unit_code = executor(before_state)

    # 4. Resolve Bottleneck Unit ID
    bottleneck_unit_id = None
    if bottleneck_unit_code and bottleneck_unit_code != "None":
        bu = units_by_code.get(bottleneck_unit_code)
        if bu:
            bottleneck_unit_id = bu.id

    # 5. Format results before/after
    results_list = []
    parameters = ["throughput", "pressure", "temperature", "flow_rate", "downtime", "yield", "energy_consumption"]
    for code, after in after_state.items():
        unit_obj = units_by_code[code]
        before = before_state[code]
        for p in parameters:
            results_list.append({
                "unit_id": unit_obj.id,
                "parameter_name": p,
                "before_value": before[p],
                "after_value": after[p]
            })

    # 6. Generate AI recommendations
    recs_list = generate_recommendations(before_state, after_state, risk_score, bottleneck_unit_code, units_by_code)

    # 7. Save Simulation Run to Database
    run = db_service.save_simulation_run(
        scenario_id=scenario.id,
        risk_score=risk_score,
        bottleneck_unit_id=bottleneck_unit_id,
        user_id=user_id,
        results_list=results_list,
        recommendations_list=recs_list
    )

    return run
