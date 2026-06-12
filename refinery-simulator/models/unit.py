from models import db

class RefineryUnit(db.Model):
    __tablename__ = 'refinery_units'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False) # e.g. CDU, FCC
    description = db.Column(db.Text)
    throughput_capacity = db.Column(db.Float, nullable=False) # design limit in bbl/day
    status = db.Column(db.String(30), default='Active', nullable=False) # Active, Maintenance, Shutdown
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    history = db.relationship('OperationalHistory', back_populates='unit', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "throughput_capacity": self.throughput_capacity,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
