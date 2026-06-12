from models import db

class OperationalHistory(db.Model):
    __tablename__ = 'operational_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('refinery_units.id', ondelete='CASCADE'), nullable=False)
    throughput = db.Column(db.Float, nullable=False)
    pressure = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    flow_rate = db.Column(db.Float, nullable=False)
    downtime = db.Column(db.Float, default=0.0, nullable=False)
    yield_ = db.Column('yield', db.Float, nullable=False) # Yield is a SQL reserved word, mapping as yield_
    energy_consumption = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    # Relationships
    unit = db.relationship('RefineryUnit', back_populates='history')

    def to_dict(self):
        return {
            "id": self.id,
            "unit_id": self.unit_id,
            "unit_code": self.unit.code if self.unit else None,
            "unit_name": self.unit.name if self.unit else None,
            "throughput": self.throughput,
            "pressure": self.pressure,
            "temperature": self.temperature,
            "flow_rate": self.flow_rate,
            "downtime": self.downtime,
            "yield": self.yield_,
            "energy_consumption": self.energy_consumption,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
        }
