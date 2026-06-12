from flask import Blueprint, render_template, redirect, url_for, flash, abort, send_from_directory
from services import db_service
from services.report_service import generate_pdf_report
from services.export_service import export_units_to_csv, export_history_to_csv, export_simulation_results_to_csv
from models import db, Report, SimulationRun, RefineryUnit, OperationalHistory
import os

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
def list_reports():
    reports_list = db_service.get_all_reports()
    simulation_runs = db_service.get_simulation_runs(limit=25)
    return render_template(
        'reports.html',
        reports=reports_list,
        runs=simulation_runs,
        active_page='reports'
    )

@reports_bp.route('/reports/generate/pdf/<int:run_id>')
def generate_pdf(run_id):
    run = db_service.get_simulation_run_by_id(run_id)
    if not run:
        abort(404, description="Simulation run not found.")
        
    try:
        file_path = generate_pdf_report(run)
        filename = os.path.basename(file_path)
        
        # Save to database metadata
        db_service.save_report_metadata(
            name=f"PDF Report - Run #{run.id} ({run.scenario.name})",
            format_type="PDF",
            file_path=file_path,
            run_id=run.id
        )
        
        flash(f"PDF Report for Run #{run.id} generated successfully.", "success")
    except Exception as e:
        flash(f"Failed to generate PDF report: {e}", "error")
        
    return redirect(url_for('reports.list_reports'))

@reports_bp.route('/reports/generate/csv/units')
def generate_csv_units():
    try:
        units = db_service.get_all_units()
        file_path = export_units_to_csv(units)
        
        db_service.save_report_metadata(
            name="CSV Export - Refinery Units Configuration",
            format_type="CSV",
            file_path=file_path
        )
        flash("CSV Unit configuration sheet generated successfully.", "success")
    except Exception as e:
        flash(f"Failed to generate CSV: {e}", "error")
        
    return redirect(url_for('reports.list_reports'))

@reports_bp.route('/reports/generate/csv/history')
def generate_csv_history():
    try:
        # Export all history records
        history = OperationalHistory.query.order_by(OperationalHistory.timestamp.desc()).all()
        file_path = export_history_to_csv(history)
        
        db_service.save_report_metadata(
            name="CSV Export - Operational History Log",
            format_type="CSV",
            file_path=file_path
        )
        flash("CSV Operational History sheet generated successfully.", "success")
    except Exception as e:
        flash(f"Failed to generate CSV: {e}", "error")
        
    return redirect(url_for('reports.list_reports'))

@reports_bp.route('/reports/generate/csv/run/<int:run_id>')
def generate_csv_run(run_id):
    run = db_service.get_simulation_run_by_id(run_id)
    if not run:
        abort(404, description="Simulation run not found.")
        
    try:
        file_path = export_simulation_results_to_csv(run)
        
        db_service.save_report_metadata(
            name=f"CSV Export - Run #{run.id} Results ({run.scenario.name})",
            format_type="CSV",
            file_path=file_path,
            run_id=run.id
        )
        flash(f"CSV results sheet for Run #{run.id} generated successfully.", "success")
    except Exception as e:
        flash(f"Failed to generate CSV: {e}", "error")
        
    return redirect(url_for('reports.list_reports'))

@reports_bp.route('/reports/download/<int:report_id>')
def download_report(report_id):
    report = Report.query.get(report_id)
    if not report:
        abort(404, description="Report metadata record not found.")
        
    directory = os.path.dirname(report.file_path)
    filename = os.path.basename(report.file_path)
    
    if not os.path.exists(report.file_path):
        abort(404, description="Physical report file not found on server disk.")
        
    return send_from_directory(directory, filename, as_attachment=True)
