from models import db

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    format = db.Column(db.String(20), nullable=False) # PDF, CSV
    file_path = db.Column(db.String(255), nullable=False)
    run_id = db.Column(db.Integer, db.ForeignKey('simulation_runs.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    run = db.relationship('SimulationRun')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "format": self.format,
            "file_path": self.file_path,
            "run_id": self.run_id,
            "scenario_name": self.run.scenario.name if (self.run and self.run.scenario) else "None",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
