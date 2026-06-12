from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models to ensure they are registered with SQLAlchemy
from models.user import User
from models.unit import RefineryUnit
from models.operational_history import OperationalHistory
from models.scenario import Scenario, ScenarioParameter
from models.simulation import SimulationRun, SimulationResult
from models.recommendation import AIRecommendation
from models.chatbot import ChatbotLog
from models.report import Report
