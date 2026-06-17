import unittest
import os
import sys
import datetime

# Add the project root to python path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, User, RefineryUnit, OperationalHistory, Scenario, SimulationRun, ChatbotLog
from services import db_service
from services.slm_service import SLMService
from simulation_engine.engine import run_simulation
from chatbot.parser import parse_query
from chatbot.hybrid_retriever import get_hybrid_chatbot_response
from services.report_service import generate_pdf_report
from services.export_service import export_units_to_csv

class TestRefinerySystem(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Configure app for testing with in-memory database
        cls.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SLM_PROVIDER': 'mock'
        })
        cls.client = cls.app.test_client()
        
        # Initialize context and create tables
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
        cls.seed_test_data()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    @classmethod
    def seed_test_data(cls):
        # 1. Seed default user
        user = User(username="test_admin", role="Operator")
        db.session.add(user)
        
        # 2. Seed 5 refinery units
        units_data = [
            ("Crude Distillation Unit", "CDU", 100000.0),
            ("Vacuum Distillation Unit", "VDU", 45000.0),
            ("Fluid Catalytic Cracking Unit", "FCC", 35000.0),
            ("Hydrotreater Unit", "Hydrotreater", 25000.0),
            ("Storage & Logistics Terminal", "Storage Terminal", 1000000.0)
        ]
        units = []
        for name, code, cap in units_data:
            u = RefineryUnit(name=name, code=code, throughput_capacity=cap, status="Active")
            db.session.add(u)
            units.append(u)
        db.session.flush()

        # 3. Seed historical records (5 per unit for simple tests)
        for u in units:
            for d in range(5):
                oh = OperationalHistory(
                    unit_id=u.id,
                    throughput=u.throughput_capacity * 0.8,
                    pressure=40.0,
                    temperature=400.0,
                    flow_rate=1500.0,
                    downtime=0.0,
                    yield_=90.0,
                    energy_consumption=120.0,
                    timestamp=datetime.datetime.now() - datetime.timedelta(days=d)
                )
                db.session.add(oh)

        # 4. Seed a test scenario (FCC Shutdown)
        sc = Scenario(name="FCC Shutdown Test", type="FCC_SHUTDOWN", description="Test fcc outage")
        db.session.add(sc)
        
        db.session.commit()

    def test_database_connections(self):
        """Verifies units and historical records exist in database."""
        units = db_service.get_all_units()
        self.assertEqual(len(units), 5)
        
        cdu = db_service.get_unit_by_code("CDU")
        self.assertIsNotNone(cdu)
        self.assertEqual(cdu.throughput_capacity, 100000.0)
        
        history = db_service.get_latest_operational_data(cdu.id)
        self.assertIsNotNone(history)
        self.assertEqual(history.throughput, 80000.0)

    def test_simulation_engine(self):
        """Verifies simulation run executes and records results in DB."""
        # Query the seeded scenario
        sc = Scenario.query.filter_by(type="FCC_SHUTDOWN").first()
        self.assertIsNotNone(sc)
        
        # Execute run
        run = run_simulation(sc.id, user_id=1)
        self.assertIsNotNone(run)
        self.assertEqual(run.risk_score, 85)
        self.assertEqual(run.bottleneck_unit.code, "FCC")
        
        # Verify result parameters
        fcc_tp_result = next(r for r in run.results if r.unit.code == "FCC" and r.parameter_name == "throughput")
        self.assertEqual(fcc_tp_result.after_value, 0.0)
        
        vdu_tp_result = next(r for r in run.results if r.unit.code == "VDU" and r.parameter_name == "throughput")
        # VDU throughput drops by 40% (80% before * 0.6 = 48% after, i.e., 36000 * 0.6 = 21600 bbl/d)
        # Seeded before throughput was VDU capacity (45000) * 0.8 = 36000. 36000 * 0.6 = 21600.
        self.assertEqual(vdu_tp_result.after_value, 21600.0)

    def test_chatbot_parser(self):
        """Tests intent parsing matching rules."""
        p1 = parse_query("What is current FCC throughput?")
        self.assertEqual(p1["intent"], "query_current")
        self.assertEqual(p1["unit_code"], "FCC")
        self.assertEqual(p1["parameter"], "throughput")

        p2 = parse_query("Show Hydrotreater temperature history last 10 days")
        self.assertEqual(p2["intent"], "query_history")
        self.assertEqual(p2["unit_code"], "Hydrotreater")
        self.assertEqual(p2["parameter"], "temperature")
        self.assertEqual(p2["limit"], 10)

        p3 = parse_query("Which unit has highest energy consumption?")
        self.assertEqual(p3["intent"], "query_extreme")
        self.assertEqual(p3["parameter"], "energy_consumption")
        self.assertEqual(p3["extreme_type"], "MAX")

        p4 = parse_query("What is FCC?")
        self.assertEqual(p4["intent"], "general")

    def test_hybrid_chatbot_retriever(self):
        """Verifies chatbot queries fetch SQLite records and route to SLM."""
        slm = SLMService(provider='mock')
        
        # Factual query
        res = get_hybrid_chatbot_response("What is current FCC throughput?", slm)
        self.assertIn("response", res)
        self.assertTrue(len(res["db_data"]) > 0)
        self.assertEqual(res["db_data"][0]["unit_code"], "FCC")
        self.assertEqual(res["db_data"][0]["throughput"], 28000.0) # VDU seeded at 35000*0.8=28000

        # General concept query
        res_general = get_hybrid_chatbot_response("What is FCC?", slm)
        self.assertIn("response", res_general)
        self.assertIn("Fluid Catalytic Cracking", res_general["response"])
        self.assertEqual(len(res_general["db_data"]), 0)

        # Pressure financial impact query (new feature)
        res_pressure_financial = get_hybrid_chatbot_response(
            "what if the pressure is increased in fcc unit by 100 what are the profit and loss this unit will face.",
            slm
        )
        self.assertIn("response", res_pressure_financial)
        self.assertIn("Net Loss of", res_pressure_financial["response"])
        self.assertIn("Automatic Emergency Shutdown", res_pressure_financial["response"])
        self.assertIn("Required Parameters", res_pressure_financial["response"])
        self.assertFalse(res_pressure_financial["llm_called"])

        # Sulfur content query (new constraint check)
        res_sulfur = get_hybrid_chatbot_response(
            "If crude sulfur content suddenly increases by 30%, what refinery units are most likely to be affected?",
            slm
        )
        self.assertIn("response", res_sulfur)
        self.assertIn("Hydrotreater (HDS Unit)", res_sulfur["response"])
        self.assertIn("Storage Terminal (STA Unit)", res_sulfur["response"])
        self.assertIn("FCC Unit", res_sulfur["response"])
        self.assertIn("CDU / VDU", res_sulfur["response"])
        self.assertTrue(res_sulfur["response"].startswith("-"))
        bullet_points = [line for line in res_sulfur["response"].split("\n") if line.strip().startswith("-")]
        self.assertTrue(1 <= len(bullet_points) <= 8)

    def test_report_compiling(self):
        """Tests report service outputs files successfully."""
        sc = Scenario.query.filter_by(type="FCC_SHUTDOWN").first()
        run = run_simulation(sc.id, user_id=1)
        
        # Test PDF Generation
        pdf_path = generate_pdf_report(run)
        self.assertTrue(os.path.exists(pdf_path))
        
        # Clean up temporary test report
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        # Test CSV Export
        units = db_service.get_all_units()
        csv_path = export_units_to_csv(units)
        self.assertTrue(os.path.exists(csv_path))
        
        # Clean up temporary test export
        if os.path.exists(csv_path):
            os.remove(csv_path)

if __name__ == '__main__':
    unittest.main()
