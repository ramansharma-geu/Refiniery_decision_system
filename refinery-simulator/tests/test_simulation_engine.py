import simulation_engine.engine  # Force package load to prevent module shadowing in pytest cache
from simulation_engine import estimate_parameters


def test_estimate_parameters_cdu_throughput():
    res = estimate_parameters('CDU', {'throughput_bpd': 6000})
    assert 'Recommended Parameters' in res
    assert 'Temperature_F' in res['Recommended Parameters']


def test_estimate_parameters_temp_delta():
    res = estimate_parameters('FCC', {'temperature_C_delta': -20})
    assert 'Recommended Parameters' in res
    assert 'Temperature_F' in res['Recommended Parameters'] or 'Throughput_bpd' in res['Recommended Parameters']


def test_estimate_parameters_with_current_values():
    # Test that different database conditions yield different parameters
    res_low = estimate_parameters('CDU', {'throughput_bpd': 6000}, {'throughput': 3000, 'temperature': 650, 'pressure': 30})
    res_high = estimate_parameters('CDU', {'throughput_bpd': 6000}, {'throughput': 5000, 'temperature': 700, 'pressure': 40})
    
    assert res_low['Recommended Parameters'] != res_high['Recommended Parameters']

