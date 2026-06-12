from flask import Blueprint, render_template, request, abort
from services import db_service
from models import RefineryUnit, OperationalHistory

units_bp = Blueprint('units', __name__)

@units_bp.route('/units')
def list_units():
    units = db_service.get_all_units()
    latest_data = db_service.get_latest_operational_data()
    
    # Map latest parameters by unit ID for display
    latest_map = {r.unit_id: r.to_dict() for r in latest_data}
    
    return render_template(
        'units.html',
        units=units,
        latest_map=latest_map,
        active_page='units'
    )

@units_bp.route('/units/<string:code>')
def unit_details(code):
    unit = db_service.get_unit_by_code(code)
    if not unit:
        abort(404, description=f"Refinery unit {code} not found.")
        
    history = db_service.get_historical_data(unit.id, limit=30)
    latest = db_service.get_latest_operational_data(unit.id)
    
    return render_template(
        'unit_details.html',
        unit=unit,
        latest=latest.to_dict() if latest else None,
        history=[h.to_dict() for h in history],
        active_page='units'
    )

@units_bp.route('/history')
def operational_history():
    selected_unit_id = request.args.get('unit_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    units = db_service.get_all_units()
    
    # Query operational history with pagination
    query = OperationalHistory.query.order_by(OperationalHistory.timestamp.desc())
    if selected_unit_id:
        query = query.filter_by(unit_id=selected_unit_id)
        
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items
    
    return render_template(
        'history.html',
        records=[r.to_dict() for r in records],
        pagination=pagination,
        units=units,
        selected_unit_id=selected_unit_id,
        active_page='history'
    )
