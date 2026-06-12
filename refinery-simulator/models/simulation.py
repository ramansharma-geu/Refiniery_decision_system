from models import db

class SimulationRun(db.Model):
    __tablename__ = 'simulation_runs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    run_timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    risk_score = db.Column(db.Integer, nullable=False)
    bottleneck_unit_id = db.Column(db.Integer, db.ForeignKey('refinery_units.id', ondelete='SET NULL'), nullable=True)

    # Relationships
    scenario = db.relationship('Scenario', back_populates='runs')
    user = db.relationship('User')
    bottleneck_unit = db.relationship('RefineryUnit')
    results = db.relationship('SimulationResult', back_populates='run', cascade='all, delete-orphan')
    recommendations = db.relationship('AIRecommendation', back_populates='run', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario.name if self.scenario else None,
            "scenario_type": self.scenario.type if self.scenario else None,
            "user_id": self.user_id,
            "username": self.user.username if self.user else "System",
            "run_timestamp": self.run_timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.run_timestamp else None,
            "risk_score": self.risk_score,
            "bottleneck_unit_id": self.bottleneck_unit_id,
            "bottleneck_unit_code": self.bottleneck_unit.code if self.bottleneck_unit else "None",
            "results": [r.to_dict() for r in self.results],
            "recommendations": [rec.to_dict() for rec in self.recommendations]
        }

class SimulationResult(db.Model):
    __tablename__ = 'simulation_results'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    run_id = db.Column(db.Integer, db.ForeignKey('simulation_runs.id', ondelete='CASCADE'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('refinery_units.id', ondelete='CASCADE'), nullable=False)
    parameter_name = db.Column(db.String(50), nullable=False)
    before_value = db.Column(db.Float, nullable=False)
    after_value = db.Column(db.Float, nullable=False)

    # Relationships
    run = db.relationship('SimulationRun', back_populates='results')
    unit = db.relationship('RefineryUnit')

    def to_dict(self):
        return {
            "id": self.id,
            "run_id": self.run_id,
            "unit_id": self.unit_id,
            "unit_code": self.unit.code if self.unit else None,
            "parameter_name": self.parameter_name,
            "before_value": self.before_value,
            "after_value": self.after_value,
            "change": self.after_value - self.before_value,
            "pct_change": ((self.after_value - self.before_value) / self.before_value * 100.0) if self.before_value != 0 else 0.0
        }
