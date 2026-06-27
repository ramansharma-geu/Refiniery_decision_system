from datetime import datetime, timezone
from flask import Flask, render_template, jsonify
from config import Config
from models import db
from routes.dashboard import dashboard_bp
from routes.units import units_bp
from routes.scenarios import scenarios_bp
from routes.chatbot import chatbot_bp
from routes.reports import reports_bp
from routes.settings import settings_bp

def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    # Initialize SQLAlchemy database with Flask
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(units_bp)
    app.register_blueprint(scenarios_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    # Context processors to inject global context to templates
    @app.context_processor
    def inject_global_variables():
        from models import RefineryUnit
        try:
            # Safe database load for navbar links
            units = RefineryUnit.query.all()
            return {
                "global_units": units,
                "current_year": 2026
            }
        except Exception:
            return {
                "global_units": [],
                "current_year": 2026
            }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors.html', code=404, message=str(e.description)), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors.html', code=500, message="An internal server error occurred. Please verify database availability."), 500

    # Health Check Endpoint
    @app.route('/api/health')
    def health_check():
        try:
            db.session.execute(db.text('SELECT 1'))
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"

        return jsonify({
            "status": "healthy" if db_status == "connected" else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": db_status,
            "version": "1.0.0"
        })

    # Status Endpoint
    @app.route('/api/status')
    def system_status():
        from models import RefineryUnit, OperationalHistory, SimulationRun, Scenario
        try:
            unit_count = RefineryUnit.query.count()
            history_count = OperationalHistory.query.count()
            run_count = SimulationRun.query.count()
            scenario_count = Scenario.query.count()
            db_ok = True
        except Exception as e:
            unit_count = history_count = run_count = scenario_count = 0
            db_ok = False

        return jsonify({
            "status": "operational" if db_ok else "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": {
                "status": "connected" if db_ok else "error",
                "refinery_units": unit_count,
                "operational_history_rows": history_count,
                "simulation_runs": run_count,
                "scenarios": scenario_count
            },
            "slm_provider": app.config.get("SLM_PROVIDER", "mock"),
            "version": "1.0.0"
        })

    return app

app = create_app()

if __name__ == '__main__':
    # Build database tables if they do not exist
    with app.app_context():
        db.create_all()
        
    app.run(host='0.0.0.0', port=5001, debug=True)
