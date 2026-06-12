from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from services import db_service
from models import db, Scenario, ScenarioParameter, RefineryUnit
from simulation_engine.engine import run_simulation

scenarios_bp = Blueprint('scenarios', __name__)

@scenarios_bp.route('/scenarios')
def list_scenarios():
    scenarios = db_service.get_all_scenarios()
    recent_runs = db_service.get_simulation_runs(limit=10)
    return render_template(
        'scenarios.html',
        scenarios=scenarios,
        recent_runs=recent_runs,
        active_page='scenarios'
    )

@scenarios_bp.route('/scenarios/create', methods=['GET', 'POST'])
def create_scenario():
    units = db_service.get_all_units()
    
    if request.method == 'POST':
        name = request.form.get('name')
        type_code = request.form.get('type')
        description = request.form.get('description')
        
        if not name or not type_code:
            flash("Scenario Name and Type are required.", "error")
            return redirect(url_for('scenarios.create_scenario'))
            
        try:
            scenario = Scenario(name=name, type=type_code, description=description)
            db.session.add(scenario)
            db.session.commit()
            
            flash(f"Scenario '{name}' created successfully.", "success")
            return redirect(url_for('scenarios.list_scenarios'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating scenario: {e}", "error")
            
    return render_template(
        'scenario_form.html',
        scenario=None,
        units=units,
        active_page='scenarios'
    )

@scenarios_bp.route('/scenarios/<int:scenario_id>/edit', methods=['GET', 'POST'])
def edit_scenario(scenario_id):
    scenario = db_service.get_scenario_by_id(scenario_id)
    if not scenario:
        abort(404, description="Scenario not found.")
        
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash("Scenario Name is required.", "error")
            return redirect(url_for('scenarios.edit_scenario', scenario_id=scenario_id))
            
        try:
            scenario.name = name
            scenario.description = description
            db.session.commit()
            flash("Scenario updated successfully.", "success")
            return redirect(url_for('scenarios.list_scenarios'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating scenario: {e}", "error")
            
    return render_template(
        'scenario_form.html',
        scenario=scenario,
        active_page='scenarios'
    )

@scenarios_bp.route('/scenarios/<int:scenario_id>/delete', methods=['POST'])
def delete_scenario(scenario_id):
    scenario = db_service.get_scenario_by_id(scenario_id)
    if not scenario:
        abort(404, description="Scenario not found.")
        
    try:
        db.session.delete(scenario)
        db.session.commit()
        flash("Scenario deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting scenario: {e}", "error")
        
    return redirect(url_for('scenarios.list_scenarios'))

@scenarios_bp.route('/scenarios/<int:scenario_id>/run', methods=['POST'])
def run_scenario_sim(scenario_id):
    try:
        # We run the simulation. User ID is mocked as 1 (admin) or NULL
        run = run_simulation(scenario_id, user_id=1)
        flash("Simulation run completed successfully.", "success")
        return redirect(url_for('scenarios.simulation_results', run_id=run.id))
    except Exception as e:
        flash(f"Error running simulation: {e}", "error")
        return redirect(url_for('scenarios.list_scenarios'))

@scenarios_bp.route('/simulation/results/<int:run_id>')
def simulation_results(run_id):
    run = db_service.get_simulation_run_by_id(run_id)
    if not run:
        abort(404, description="Simulation run results not found.")
        
    # Group results by unit code for easy template rendering
    grouped_results = {}
    for r in run.results:
        code = r.unit.code
        if code not in grouped_results:
            grouped_results[code] = []
        grouped_results[code].append(r.to_dict())
        
    return render_template(
        'simulation_results.html',
        run=run,
        grouped_results=grouped_results,
        active_page='scenarios'
    )
