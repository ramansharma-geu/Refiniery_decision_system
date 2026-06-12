from models import db

class AIRecommendation(db.Model):
    __tablename__ = 'ai_recommendations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    run_id = db.Column(db.Integer, db.ForeignKey('simulation_runs.id', ondelete='CASCADE'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('refinery_units.id', ondelete='SET NULL'), nullable=True)
    recommendation_text = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False) # High, Medium, Low

    # Relationships
    run = db.relationship('SimulationRun', back_populates='recommendations')
    unit = db.relationship('RefineryUnit')

    def to_dict(self):
        return {
            "id": self.id,
            "run_id": self.run_id,
            "unit_id": self.unit_id,
            "unit_code": self.unit.code if self.unit else "Global",
            "recommendation_text": self.recommendation_text,
            "priority": self.priority
        }
