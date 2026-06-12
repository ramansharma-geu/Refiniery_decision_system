from models import db

class Scenario(db.Model):
    __tablename__ = 'scenarios'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False) # FCC_SHUTDOWN, THROUGHPUT_INCREASE, MAINTENANCE_DELAY, ENERGY_REDUCTION, DEMAND_INCREASE
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    parameters = db.relationship('ScenarioParameter', back_populates='scenario', cascade='all, delete-orphan')
    runs = db.relationship('SimulationRun', back_populates='scenario', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "parameters": [p.to_dict() for p in self.parameters]
        }

class ScenarioParameter(db.Model):
    __tablename__ = 'scenario_parameters'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id', ondelete='CASCADE'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('refinery_units.id', ondelete='CASCADE'), nullable=False)
    parameter_name = db.Column(db.String(50), nullable=False) # throughput, pressure, temperature, flow_rate, downtime, yield, energy_consumption
    value_change_type = db.Column(db.String(20), nullable=False) # PERCENTAGE, ABSOLUTE
    value_change = db.Column(db.Float, nullable=False) # e.g. -1.0, 0.10, etc.

    # Relationships
    scenario = db.relationship('Scenario', back_populates='parameters')
    unit = db.relationship('RefineryUnit')

    def to_dict(self):
        return {
            "id": self.id,
            "scenario_id": self.scenario_id,
            "unit_id": self.unit_id,
            "unit_code": self.unit.code if self.unit else None,
            "parameter_name": self.parameter_name,
            "value_change_type": self.value_change_type,
            "value_change": self.value_change
        }
