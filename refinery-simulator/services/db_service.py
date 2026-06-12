from models import db, RefineryUnit, OperationalHistory, Scenario, ScenarioParameter, SimulationRun, SimulationResult, AIRecommendation, ChatbotLog, Report, User
from sqlalchemy import func
import datetime
import json

def get_all_units():
    return RefineryUnit.query.all()

def get_unit_by_code(code):
    return RefineryUnit.query.filter_by(code=code).first()

def get_latest_operational_data(unit_id=None):
    """
    Fetches the most recent operational history record for each unit or a specific unit.
    This serves as the 'Before' state in simulations.
    """
    if unit_id:
        return OperationalHistory.query.filter_by(unit_id=unit_id).order_by(OperationalHistory.timestamp.desc()).first()
    
    # Get latest record for all units
    latest_records = []
    units = get_all_units()
    for u in units:
        record = OperationalHistory.query.filter_by(unit_id=u.id).order_by(OperationalHistory.timestamp.desc()).first()
        if record:
            latest_records.append(record)
    return latest_records

def get_historical_data(unit_id, limit=30):
    return OperationalHistory.query.filter_by(unit_id=unit_id).order_by(OperationalHistory.timestamp.desc()).limit(limit).all()

def get_all_scenarios():
    return Scenario.query.all()

def get_scenario_by_id(scenario_id):
    return Scenario.query.get(scenario_id)

def get_simulation_runs(limit=10):
    return SimulationRun.query.order_by(SimulationRun.run_timestamp.desc()).limit(limit).all()

def get_simulation_run_by_id(run_id):
    return SimulationRun.query.get(run_id)

def save_simulation_run(scenario_id, risk_score, bottleneck_unit_id, user_id, results_list, recommendations_list):
    """
    Saves a simulation run, its before/after parameter state, and generated AI recommendations inside a transaction.
    """
    try:
        run = SimulationRun(
            scenario_id=scenario_id,
            user_id=user_id,
            risk_score=risk_score,
            bottleneck_unit_id=bottleneck_unit_id
        )
        db.session.add(run)
        db.session.flush() # Populate run.id

        # Save results
        for res in results_list:
            result_obj = SimulationResult(
                run_id=run.id,
                unit_id=res['unit_id'],
                parameter_name=res['parameter_name'],
                before_value=res['before_value'],
                after_value=res['after_value']
            )
            db.session.add(result_obj)

        # Save recommendations
        for rec in recommendations_list:
            rec_obj = AIRecommendation(
                run_id=run.id,
                unit_id=rec.get('unit_id'),
                recommendation_text=rec['recommendation_text'],
                priority=rec['priority']
            )
            db.session.add(rec_obj)

        db.session.commit()
        return run
    except Exception as e:
        db.session.rollback()
        raise e

def log_chatbot_query(user_query, system_response, retrieved_data_used=None, llm_called=False):
    try:
        log = ChatbotLog(
            user_query=user_query,
            system_response=system_response,
            retrieved_data_used=json.dumps(retrieved_data_used) if retrieved_data_used else None,
            llm_called=1 if llm_called else 0
        )
        db.session.add(log)
        db.session.commit()
        return log
    except Exception as e:
        db.session.rollback()
        print(f"Error logging chatbot query: {e}")
        return None

def get_chatbot_logs(limit=10):
    return ChatbotLog.query.order_by(ChatbotLog.timestamp.desc()).limit(limit).all()

def get_all_reports():
    return Report.query.order_by(Report.created_at.desc()).all()

def save_report_metadata(name, format_type, file_path, run_id=None):
    try:
        rep = Report(
            name=name,
            format=format_type,
            file_path=file_path,
            run_id=run_id
        )
        db.session.add(rep)
        db.session.commit()
        return rep
    except Exception as e:
        db.session.rollback()
        raise e

def get_dashboard_metrics():
    """
    Aggregates stats for the dashboard:
    - Total units, active units, units under maintenance
    - Total simulations run
    - Total scenarios configured
    - Recent recommendations
    """
    total_units = RefineryUnit.query.count()
    active_units = RefineryUnit.query.filter_by(status='Active').count()
    maintenance_units = RefineryUnit.query.filter_by(status='Maintenance').count()
    total_simulations = SimulationRun.query.count()
    total_scenarios = Scenario.query.count()
    
    # Recent recommendations (limit 5)
    recent_recs = AIRecommendation.query.order_by(AIRecommendation.id.desc()).limit(5).all()
    
    return {
        "total_units": total_units,
        "active_units": active_units,
        "maintenance_units": maintenance_units,
        "total_simulations": total_simulations,
        "total_scenarios": total_scenarios,
        "recent_recommendations": [r.to_dict() for r in recent_recs]
    }
