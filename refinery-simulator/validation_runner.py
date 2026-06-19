import json
import sys
from pathlib import Path

# Ensure local package imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))


class DummySLM:
    def __init__(self):
        self.last_prompt = None
    def query(self, prompt, context_data=None):
        self.last_prompt = prompt
        # Return a compact, direct-style answer for manual review
        return "Direct answer.\n• Item 1\n• Item 2"

# Lightweight DB/service stubs to avoid importing full SQLAlchemy for the runner.
# Note: This runner aims to check structural properties, not numeric correctness.
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

    def get_unit_by_code(self, code):
        for u in self.get_all_units():
            if u.code == code:
                return u
        return None

    def log_chatbot_query(self, *a, **k):
        return None

# monkeypatch module imports used by hybrid_retriever
import types
import importlib

# Inject stub services module
stub_services = types.ModuleType('services')
stub_services.db_service = StubDBService()
import sys as _sys
_sys.modules['services'] = stub_services

# Inject lightweight fake 'models' module to avoid Flask/SQLAlchemy app context requirements
fake_models = types.ModuleType('models')

class FakeQuery:
    def __init__(self, *a, **k):
        pass
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

class FakeUnit:
    pass

fake_models.RefineryUnit = FakeUnit

class FakeAttr:
    def __init__(self, name):
        self.name = name
    def desc(self):
        return self
    def asc(self):
        return self
    def __repr__(self):
        return f"FakeAttr({self.name})"

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

# Inject lightweight sqlalchemy.func stub
fake_sqlalchemy = types.ModuleType('sqlalchemy')
fake_sqlalchemy.func = types.SimpleNamespace(max=lambda x: x, min=lambda x: x, avg=lambda x: x)
_sys.modules['sqlalchemy'] = fake_sqlalchemy

# Now import hybrid_retriever after stubs are set up
from chatbot.hybrid_retriever import get_hybrid_chatbot_response

# Now load the validation suite
suite_path = Path(__file__).with_name('validation_suite.json')
with open(suite_path, 'r') as f:
    suite = json.load(f)

slm = DummySLM()

results = []
for t in suite['tests']:
    q = t['question']
    try:
        res = get_hybrid_chatbot_response(q, slm)
    except Exception as e:
        results.append({'id': t['id'], 'question': q, 'status': 'ERROR', 'error': str(e)})
        continue
    # Extract response string
    if isinstance(res, dict):
        body = res.get('response', '')
    else:
        body = str(res)

    # Basic checks
    forbidden = [p.lower() for p in suite['global_quality']['forbidden_phrases']]
    found_forbidden = [p for p in forbidden if p in body.lower()]
    word_count = len(body.split())

    status = 'PASS'
    notes = []
    if found_forbidden:
        status = 'FAIL'
        notes.append('Forbidden phrases: ' + ', '.join(found_forbidden))
    if 'db_only' in t.get('expect', {}) and t['expect']['db_only']:
        # Check that we did not call the LLM for current-data intent (llm_called flag in response)
        if isinstance(res, dict) and res.get('llm_called'):
            status = 'FAIL'
            notes.append('LLM called for db_only test')
    if word_count > suite['global_quality']['max_words']:
        status = 'WARN'
        notes.append(f'Word count {word_count} > {suite["global_quality"]["max_words"]}')

    results.append({'id': t['id'], 'question': q, 'status': status, 'notes': notes, 'response_preview': body[:300]})

# Print a short summary
pass_count = sum(1 for r in results if r['status'] == 'PASS')
fail_count = sum(1 for r in results if r['status'] == 'FAIL')
warn_count = sum(1 for r in results if r['status'] == 'WARN')
error_count = sum(1 for r in results if r['status'] == 'ERROR')

print(f"Validation run: {len(results)} tests — PASS: {pass_count}, WARN: {warn_count}, FAIL: {fail_count}, ERROR: {error_count}\n")
for r in results:
    print(f"{r['id']} {r['status']} — {r['question']}\n  Notes: {r.get('notes')}\n  Resp: {r.get('response_preview')}\n")

# Also save a report
with open(Path(__file__).with_name('validation_report.json'), 'w') as out:
    json.dump({'meta': suite['meta'], 'results': results}, out, indent=2)

print('Report written to validation_report.json')
