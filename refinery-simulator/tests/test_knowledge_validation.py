import sys
import os
import pytest

# Add the project root to python path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from chatbot.hybrid_retriever import get_hybrid_chatbot_response
from services.slm_service import SLMService

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


def test_knowledge_what_is_fcc():
    slm = SLMService(provider='mock')
    res = get_hybrid_chatbot_response("What is FCC?", slm)
    assert isinstance(res, dict)
    body = res['response']
    
    # Must contain correct facts
    assert any(term in body.lower() for term in ["crack", "catalytic", "conversion", "vgo", "fluidized bed"])
    # Must NOT contain incorrect active claims
    assert "extracts aromatics" not in body.lower()
    assert "fcc extracts" not in body.lower()
    assert "removes water" not in body.lower()
    assert "hydrotreater removes" not in body.lower()


def test_knowledge_fcc_products():
    slm = SLMService(provider='mock')
    res = get_hybrid_chatbot_response("What are FCC products?", slm)
    assert isinstance(res, dict)
    body = res['response']
    
    # Must contain correct products
    assert any(term in body.lower() for term in ["gasoline", "lpg", "lco", "cycle oil"])
    # Must NOT contain incorrect active claims
    assert "extracts aromatics" not in body.lower()
    assert "fcc extracts" not in body.lower()


def test_knowledge_why_hydrotreater_used():
    slm = SLMService(provider='mock')
    res = get_hybrid_chatbot_response("Why is hydrotreater used?", slm)
    assert isinstance(res, dict)
    body = res['response']
    
    # Must contain correct desulfurization / impurity removal facts
    assert any(term in body.lower() for term in ["sulfur", "desulfur", "impurities", "nitrogen", "metals", "protect downstream"])
    assert "removes water" not in body.lower()
    assert "hydrotreater removes" not in body.lower()
    assert "removes water from crude oil" not in body.lower()


def test_knowledge_catalyst_deactivation():
    slm = SLMService(provider='mock')
    res = get_hybrid_chatbot_response("What causes catalyst deactivation?", slm)
    assert isinstance(res, dict)
    body = res['response']
    
    # Must contain catalyst deactivation mechanisms
    assert any(term in body.lower() for term in ["coke", "coking", "poisoning", "metal", "sintering", "fouling", "plugging"])
    # Must NOT contain unrelated errors
    assert "water from crude" not in body.lower()
    assert "extracts aromatics" not in body.lower()


def teardown_module(module):
    # Clean up mock overrides from sys.modules to prevent test poisoning
    for m in ['models', 'services', 'sqlalchemy']:
        if m in sys.modules:
            del sys.modules[m]
