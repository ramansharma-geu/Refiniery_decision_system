from flask import Blueprint, render_template, jsonify
from services import db_service
from models import db, OperationalHistory, RefineryUnit, SimulationRun, Scenario
from sqlalchemy import func
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def index():
    stats = db_service.get_dashboard_metrics()
    recent_runs = db_service.get_simulation_runs(limit=5)
    
    return render_template(
        'dashboard.html', 
        stats=stats, 
        recent_runs=recent_runs,
        active_page='dashboard'
    )

@dashboard_bp.route('/api/analytics')
def analytics_data():
    """
    Returns data arrays for Chart.js:
    - Last 15 operational records for each unit (Throughput, Yield, Energy, Downtime).
    - Scenario distribution (Count of simulation runs per scenario).
    """
    units = db_service.get_all_units()
    analytics = {}
    
    for u in units:
        # Fetch last 15 historical points sorted in chronological order for charting
        history = OperationalHistory.query.filter_by(unit_id=u.id)\
                                           .order_by(OperationalHistory.timestamp.desc())\
                                           .limit(15).all()
        # Reverse to get chronological order (past to present)
        history.reverse()
        
        analytics[u.code] = {
            "timestamps": [h.timestamp.strftime("%m-%d") for h in history],
            "throughput": [h.throughput for h in history],
            "yield": [h.yield_ for h in history],
            "energy_consumption": [h.energy_consumption for h in history],
            "downtime": [h.downtime for h in history]
        }

    # Scenario distribution counts
    runs = db.session.query(Scenario.name, func.count(SimulationRun.id))\
                     .join(SimulationRun, Scenario.id == SimulationRun.scenario_id)\
                     .group_by(Scenario.id).all()
                     
    scenario_dist = {name: count for name, count in runs}
    
    # If no runs exist, populate default values
    if not scenario_dist:
        scenario_dist = {"FCC Shutdown": 0, "Throughput Increase (+10%)": 0, "Maintenance Delay": 0}

    return jsonify({
        "trends": analytics,
        "scenario_distribution": scenario_dist
    })
