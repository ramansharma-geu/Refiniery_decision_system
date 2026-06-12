from models import db

class ChatbotLog(db.Model):
    __tablename__ = 'chatbot_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_query = db.Column(db.Text, nullable=False)
    system_response = db.Column(db.Text, nullable=False)
    retrieved_data_used = db.Column(db.Text, nullable=True) # Stored as JSON string
    llm_called = db.Column(db.Integer, default=0, nullable=False) # 1 if SLM was called, 0 if SQL-only
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        import json
        retrieved_data = None
        if self.retrieved_data_used:
            try:
                retrieved_data = json.loads(self.retrieved_data_used)
            except Exception:
                retrieved_data = []
        return {
            "id": self.id,
            "user_query": self.user_query,
            "system_response": self.system_response,
            "retrieved_data": retrieved_data,
            "llm_called": bool(self.llm_called),
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
        }
