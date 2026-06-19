import sys
import os
import pytest

# Add the project root to python path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from chatbot.hybrid_retriever import get_hybrid_chatbot_response

@pytest.fixture(scope="module", autouse=True)
def app_context():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SLM_PROVIDER': 'mock'
    })
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()



class DummySLM:
    def __init__(self):
        self.last_prompt = None
    def query(self, prompt, context_data=None):
        self.last_prompt = prompt
        return "- Direct answer\n- Support 1\n- Support 2"


class DummyDBService:
    def __init__(self, monkeypatch):
        import services.db_service as dbs
        self._orig_get_latest = dbs.get_latest_operational_data
        self._orig_get_all = dbs.get_all_units
        def fake_latest(*args, **kwargs):
            class R:
                unit = type('U',(object,),{'code':'CDU'})
                throughput = 12000
                pressure = 40
                temperature = 700
                flow_rate = 300
                downtime = 0
                yield_ = 90
            return [R()]
        def fake_units(*args, **kwargs):
            class U:
                id = 1
                code = 'CDU'
                name = 'Crude Distillation Unit'
                throughput_capacity = 50000
            return [U()]
        monkeypatch.setattr('services.db_service.get_latest_operational_data', fake_latest)
        monkeypatch.setattr('services.db_service.get_all_units', fake_units)


def test_routing_knowledge(monkeypatch):
    slm = DummySLM()
    # Knowledge: should call SLM and return a string from it
    res = get_hybrid_chatbot_response('What is FCC?', slm)
    assert isinstance(res, dict)
    assert '- Direct answer' in res['response']
    # Other knowledge examples
    res2 = get_hybrid_chatbot_response('What is CDU?', slm)
    assert '- Direct answer' in res2['response']
    res3 = get_hybrid_chatbot_response('Why is hydrotreater used?', slm)
    assert '- Direct answer' in res3['response']


def test_routing_current(monkeypatch):
    # Current data should be returned from DB path
    # Provide one sample record for current data
    class R:
        unit = type('U',(object,),{'code':'CDU'})
        throughput = 3185
        pressure = 40
        temperature = 350
        flow_rate = 0
        downtime = 0
        yield_ = 90
        energy_consumption = 120
        timestamp = '2026-06-11 12:56'
        def to_dict(self):
            return {'unit_code':'CDU','throughput':self.throughput,'pressure':self.pressure,'temperature':self.temperature,'timestamp':self.timestamp}
    def fake_latest(*a, **k):
        # If called with a unit_id arg, return a single record object; otherwise return list
        if len(a) > 0:
            return R()
        return [R()]
    monkeypatch.setattr('services.db_service.get_latest_operational_data', fake_latest)
    # Provide a unit object so execute_db_query can map unit_code -> unit id
    class U:
        id = 1
        code = 'CDU'
        name = 'Crude Distillation Unit'
        throughput_capacity = 50000
    class U2:
        id = 2
        code = 'FCC'
        name = 'Fluid Catalytic Cracking'
        throughput_capacity = 35000
    monkeypatch.setattr('services.db_service.get_all_units', lambda *a, **k: [U(), U2()])
    slm = DummySLM()
    res = get_hybrid_chatbot_response('Show CDU flow rate', slm)
    assert isinstance(res, dict)
    assert 'Current Plant Data' in res['response']
    # Additional current data examples
    res2 = get_hybrid_chatbot_response('Show FCC temperature', slm)
    assert 'Current Plant Data' in res2['response'] or 'No current data' in res2['response']
    res3 = get_hybrid_chatbot_response('Which unit has highest throughput?', slm)
    assert isinstance(res3, dict)


def test_routing_simulation(monkeypatch):
    slm = DummySLM()
    # Simulation examples
    res = get_hybrid_chatbot_response('If CDU flow becomes 6000, what should temperature be?', slm)
    assert isinstance(res, dict)
    assert 'Current Conditions' in res['response']
    res2 = get_hybrid_chatbot_response('If FCC temperature drops by 20°C', slm)
    assert 'Current Conditions' in res2['response']
    res3 = get_hybrid_chatbot_response('If VDU throughput increases by 15%', slm)
    assert 'Current Conditions' in res3['response']
    res4 = get_hybrid_chatbot_response('If hydrotreater sulfur feed doubles', slm)
    assert 'Current Conditions' in res4['response']
    res5 = get_hybrid_chatbot_response('If CDU pressure rises by 10%', slm)
    assert 'Current Conditions' in res5['response']


def teardown_module(module):
    # Clean up mock overrides from sys.modules to prevent test poisoning
    for m in ['models', 'services', 'sqlalchemy']:
        if m in sys.modules:
            del sys.modules[m]

