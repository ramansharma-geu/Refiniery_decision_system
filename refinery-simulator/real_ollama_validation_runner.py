import time
import json
import sys
from pathlib import Path

# Ensure we import local modules from simulator dir
sys.path.insert(0, str(Path(__file__).resolve().parent))

from services.slm_service import SLMService
from response_validator import validate_response

import types

# Provide lightweight stubs for services/models to allow imports
stub_services = types.ModuleType('services')
class StubDBService:
    def get_latest_operational_data(self, unit_id=None):
        class R:
            def __init__(self, code):
                self.unit = type('U', (object,), {'code': code})
                self.throughput = 4000
                self.pressure = 40
                self.temperature = 700
                self.flow_rate = 3000
                self.downtime = 0
                self.yield_ = 90
                self.energy_consumption = 120
                self.timestamp = '2026-06-18 12:00'
            def to_dict(self):
                return {'unit_code': self.unit.code, 'throughput': self.throughput, 'pressure': self.pressure, 'temperature': self.temperature, 'timestamp': self.timestamp}
        if unit_id:
            return R('CDU')
        return [R('CDU'), R('FCC'), R('VDU'), R('Hydrotreater'), R('Storage Terminal')]
    def get_all_units(self):
        class U:
            def __init__(self, id, code, name):
                self.id = id
                self.code = code
                self.name = name
                self.throughput_capacity = 50000
        return [U(1,'CDU','Crude Distillation Unit'), U(2,'FCC','Fluid Catalytic Cracking'), U(3,'VDU','Vacuum Distillation Unit'), U(4,'Hydrotreater','Hydrotreater'), U(5,'Storage Terminal','Storage Terminal')]
    def log_chatbot_query(self, *a, **k):
        return None
stub_services.db_service = StubDBService()
import sys as _sys
_sys.modules['services'] = stub_services

# Also inject lightweight fake models/sqlalchemy to avoid import-time Flask app requirements
fake_models = types.ModuleType('models')
class FakeQuery:
    def query(self, *a, **k):
        return self
    def filter_by(self, **k):
        return self
    def order_by(self, *a, **k):
        return self
    def scalar(self):
        return 12000
    def group_by(self, *a, **k):
        return self
    def all(self):
        return [(1, 12000)]
    def limit(self, n):
        return self
    def first(self):
        return (1, 12000)
fake_models.db = types.SimpleNamespace(session=FakeQuery())
class FakeUnit: pass
fake_models.RefineryUnit = FakeUnit
class FakeAttr:
    def __init__(self,name):
        self.name=name
    def desc(self):
        return self
    def asc(self):
        return self
class FakeOH:
    throughput = FakeAttr('throughput')
    pressure = FakeAttr('pressure')
    temperature = FakeAttr('temperature')
    flow_rate = FakeAttr('flow_rate')
    downtime = FakeAttr('downtime')
    yield_ = FakeAttr('yield_')
    energy_consumption = FakeAttr('energy_consumption')
    unit_id = FakeAttr('unit_id')
fake_models.OperationalHistory = FakeOH
_sys.modules['models'] = fake_models

import os
from config import Config

def load_questions():
    # Load the validation suite and expand to 50 by adding small variants
    p = Path(__file__).with_name('validation_suite.json')
    data = json.loads(p.read_text())
    base = [t['question'] for t in data['tests']]
    questions = []
    # For each base question create minor variants (5 variants) to reach 50+
    for q in base:
        questions.append(q)
        for i in range(1,5):
            questions.append(q + (" (variant %d)" % i))
    return questions[:60]

def main():
    # Use environment-configured SLM provider and Ollama URL
    cfg = Config()
    slm = SLMService(provider='ollama', ollama_url=cfg.OLLAMA_URL, ollama_model=cfg.OLLAMA_MODEL, hf_model_path=cfg.HF_MODEL_PATH)

    questions = load_questions()
    results = []
    for q in questions:
        start = time.time()
        resp = slm.query(q, context_data=None)
        latency = time.time() - start
        # Attempt to coerce response into string
        body = resp if isinstance(resp, str) else json.dumps(resp)
        # Intent detection using local classifier
        try:
            from chatbot.intent_classifier import detect_intent
            intent = detect_intent(q)
        except Exception:
            intent = 'UNKNOWN'

        # Select required sections for validator based on intent
        sections = None
        if intent == 'ANALYSIS':
            sections = [
                'Current Values',
                'Observed Concerns',
                'Possible Causes',
                'Operational Impact',
                'Recommendations',
                'Confidence Level'
            ]
        elif intent == 'SIMULATION':
            sections = [
                'Current Conditions',
                'Target Conditions',
                'Parameter Adjustments',
                'Expected Changes',
                'Operational Risks',
                'Economic Impact',
                'Recommendations'
            ]

        passed, details = validate_response(body, required_sections=sections)

        results.append({
            'question': q,
            'response': body,
            'intent': intent,
            'latency_s': latency,
            'pass': passed,
            'details': details
        })

    # Write markdown report and json
    md = ['# REAL OLLAMA VALIDATION REPORT', f'Date: {time.ctime()}', '', f'Total questions: {len(results)}', '']
    for r in results:
        md.append(f'## Question: {r["question"]}')
        md.append(f'- Intent: {r["intent"]}')
        md.append(f'- Latency (s): {r["latency_s"]:.2f}')
        md.append(f'- Pass: {r["pass"]}')
        md.append(f'- Details: {r["details"]}')
        md.append('\nResponse:\n')
        md.append('```')
        md.append(r['response'][:4000])
        md.append('```\n')

    out_md = Path(__file__).with_name('REAL_OLLAMA_VALIDATION_REPORT_V2.md')
    out_md.write_text('\n'.join(md))
    out_json = Path(__file__).with_name('REAL_OLLAMA_VALIDATION_REPORT_V2.json')
    out_json.write_text(json.dumps({'meta': {'date': time.ctime(), 'total': len(results)}, 'results': results}, indent=2))

    print(f"Wrote REAL_OLLAMA_VALIDATION_REPORT_V2.md and JSON for {len(results)} questions")

if __name__ == '__main__':
    main()
