#!/usr/bin/env python
"""Quick endpoint test script for RDIS."""
import json
import sys

try:
    from app import app
    print("✓ App loaded OK")
except Exception as e:
    print(f"✗ App import failed: {e}")
    sys.exit(1)

with app.test_client() as client:
    endpoints = [
        ("GET", "/"),
        ("GET", "/dashboard"),
        ("GET", "/api/analytics"),
        ("GET", "/units"),
        ("GET", "/units/CDU"),
        ("GET", "/units/VDU"),
        ("GET", "/units/FCC"),
        ("GET", "/units/Hydrotreater"),
        ("GET", "/units/Storage Terminal"),
        ("GET", "/history"),
        ("GET", "/chatbot"),
        ("GET", "/scenarios"),
        ("GET", "/reports"),
        ("GET", "/settings"),
    ]
    
    all_pass = True
    for method, path in endpoints:
        r = client.get(path)
        status = "✓" if r.status_code == 200 else "✗"
        if r.status_code != 200:
            all_pass = False
        print(f"  {status} {method} {path} => {r.status_code}")
    
    # Test chatbot API
    r = client.post('/chatbot/query', json={'query': 'What is CDU throughput?'})
    status = "✓" if r.status_code == 200 else "✗"
    if r.status_code != 200:
        all_pass = False
    print(f"  {status} POST /chatbot/query => {r.status_code}")
    if r.status_code == 200:
        cdata = json.loads(r.data)
        print(f"    Response keys: {list(cdata.keys())}")
    
    # Check analytics data integrity
    r = client.get('/api/analytics')
    data = json.loads(r.data)
    trends = data.get("trends", {})
    print(f"\n--- Analytics Data ---")
    print(f"  Trend unit codes: {list(trends.keys())}")
    for code in trends:
        t = trends[code]
        print(f"  {code}: {len(t.get('timestamps',[]))} timestamps, {len(t.get('throughput',[]))} throughput points")
    print(f"  Scenario distribution: {data.get('scenario_distribution', {})}")
    
    # Check dataset rendering - the history page
    r = client.get('/history')
    html = r.data.decode('utf-8')
    has_records = 'No historical records' not in html
    print(f"\n--- Dataset Rendering ---")
    print(f"  History page has records: {has_records}")
    
    # Check units page renders data
    r = client.get('/units')
    html = r.data.decode('utf-8')
    has_cdu = 'CDU' in html
    has_vdu = 'VDU' in html
    print(f"  Units page has CDU: {has_cdu}")
    print(f"  Units page has VDU: {has_vdu}")
    
    # Check dashboard renders
    r = client.get('/')
    html = r.data.decode('utf-8')
    has_throughput_chart = 'throughputChart' in html
    has_yield_chart = 'yieldChart' in html
    print(f"  Dashboard has throughputChart: {has_throughput_chart}")
    print(f"  Dashboard has yieldChart: {has_yield_chart}")
    
    print(f"\n{'='*50}")
    print(f"ALL ENDPOINTS PASS: {all_pass}")
