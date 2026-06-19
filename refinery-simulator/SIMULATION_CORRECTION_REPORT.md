# SIMULATION CORRECTION REPORT

**Total Tests:** 100
**Passed:** 0
**Failed:** 100
**Pass Rate:** 0.0%

## Results by Unit

| Unit | Passed | Failed | Pass Rate |
|------|--------|--------|-----------|
| CDU | 0 | 20 | 0% |
| FCC | 0 | 20 | 0% |
| VDU | 0 | 20 | 0% |
| Hydrotreater | 0 | 20 | 0% |
| Storage Terminal | 0 | 20 | 0% |

## Validation Criteria

1. ✅ Response contains required sections: Current Conditions, Target Conditions, Parameter Adjustments, Expected Changes, Operational Risks, Recommendations
2. ✅ Response does NOT contain forbidden sections: Analysis:, Economic Impact, Confidence Level
3. ✅ Response under 150 words
4. ✅ Uses correct units: °C (temperature), bar (pressure), BPD (flow rate)
5. ✅ No unrealistic values (energy change capped at ±50%)
6. ✅ Uses bullet points for operational items

## Sample Correct Outputs

## Failed Tests Detail

### CDU

- **Query:** If CDU flow rate increases from current value to 6000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if CDU throughput increases by 10%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If CDU temperature rises by 20 degrees
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if CDU pressure increases by 5 psi
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If CDU throughput drops to 70000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if CDU flow rate decreases by 20%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If CDU feed rate doubles
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if CDU throughput increases to 90000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If CDU flow halves what adjustments needed
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if CDU crude charge increases by 15%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If CDU pressure drops by 10 psi what are the risks
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if CDU temperature increases to 750 F
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If CDU throughput increases by 5000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if CDU flow rate goes to 4000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If CDU pressure rises by 20%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What adjustments if CDU feed increases by 8%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If CDU throughput reduces to 60000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if CDU temperature decreases by 30 degrees
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If CDU flow rate increases to 5000 BPD what risks
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if CDU API gravity decreases by 3
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))

### FCC

- **Query:** If FCC throughput increases by 10%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if FCC catalyst activity drops by 15%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If FCC flow rate increases to 35000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if FCC temperature rises by 30 degrees
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If FCC throughput decreases to 20000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if FCC pressure increases by 10%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If FCC catalyst ratio increases
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if FCC feed rate drops by 25%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If FCC throughput goes to 30000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if FCC temperature increases by 15%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If FCC flow rate decreases by 5000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if FCC sulfur in feed doubles
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If FCC throughput increases by 20%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if FCC catalyst activity increases by 10%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If FCC pressure drops by 5 psi
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What adjustments if FCC feed increases to 32000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If FCC reactor temperature increases by 25 degrees
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if FCC throughput drops to 22000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If FCC flow rate increases by 15%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if FCC heater duty increases by 10%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))

### VDU

- **Query:** If VDU throughput increases by 10%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if VDU pressure increases by 20%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If VDU flow rate goes to 40000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if VDU temperature rises by 25 degrees
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If VDU throughput decreases to 30000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if VDU vacuum drops
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If VDU feed rate increases by 5000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if VDU throughput increases to 43000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If VDU pressure rises what are the risks
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if VDU flow rate decreases by 15%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If VDU temperature increases to 800 F
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if VDU throughput drops by 20%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If VDU flow increases by 8%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if VDU pressure increases by 0.5 psi
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If VDU heater duty increases by 12%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What adjustments if VDU feed increases by 10%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If VDU throughput goes to 35000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if VDU temperature decreases by 20 degrees
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If VDU flow rate increases to 1800 BPD what risks
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if VDU throughput increases by 25%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))

### Hydrotreater

- **Query:** If Hydrotreater throughput increases by 10%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if Hydrotreater sulfur feed doubles
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Hydrotreater flow rate goes to 25000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if Hydrotreater temperature rises by 15 degrees
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Hydrotreater throughput decreases to 12000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if Hydrotreater pressure increases by 10%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Hydrotreater feed rate increases by 20%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if Hydrotreater throughput increases to 22000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Hydrotreater pressure drops what are the risks
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if Hydrotreater flow rate decreases by 15%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Hydrotreater temperature increases by 25 degrees
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if Hydrotreater throughput drops by 30%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Hydrotreater sulfur in feed increases by 50%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if Hydrotreater pressure rises by 100 psi
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Hydrotreater heater duty increases by 8%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What adjustments if Hydrotreater feed increases by 15%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Hydrotreater throughput goes to 20000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if Hydrotreater temperature decreases by 10 degrees
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Hydrotreater flow rate increases by 10% what risks
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if Hydrotreater throughput increases by 5000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))

### Storage Terminal

- **Query:** If Storage Terminal throughput increases by 10%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if Storage Terminal utilization reaches 92%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Storage Terminal flow rate goes to 130000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if Storage Terminal capacity increases by 20%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Storage Terminal throughput decreases to 90000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if Storage Terminal utilization drops to 50%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Storage Terminal flow rate increases by 15%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if Storage Terminal throughput increases to 140000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Storage Terminal utilization reaches 95% what are the risks
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if Storage Terminal flow rate decreases by 20%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Storage Terminal throughput drops by 25%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if Storage Terminal utilization increases to 88%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Storage Terminal flow rate increases by 10000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if Storage Terminal throughput increases by 8%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Storage Terminal utilization goes to 70%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What adjustments if Storage Terminal feed increases by 12%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Storage Terminal throughput goes to 120000 BPD
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What if Storage Terminal capacity reduces by 10%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** If Storage Terminal flow rate increases to 6000 BPD what risks
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))
- **Query:** What happens if Storage Terminal throughput increases by 20%
  - ⚠ Exception: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /chatbot/query (Caused by NewConnectionError("HTTPConnection(host='localhost', port=5001): Failed to establish a new connection: [Errno 1] Operation not permitted"))

## Changes Made

### Files Modified

1. **engineering_rules.json** — Updated CDU throughput bounds (60k→100k), VDU (30k→45k), added flow_rate_bph bounds for all units
2. **simulation_engine.py** — Complete rewrite (V3): Fixed throughput/flow_rate confusion, added °F→°C and psi→bar conversion, sanity clamping (flow_ratio 0.1–3.0, energy ±50%), fixed Storage Terminal NameError
3. **chatbot/hybrid_retriever.py** — New _format_simulation_response() for engineer-style output, fixed parameter parsing heuristics, removed Economic Impact from default
4. **services/slm_service.py** — Updated prompt templates and validation sections, lowered word limit to 120
5. **response_validator.py** — Added FORBIDDEN_DEFAULT_SECTIONS, lowered default max_words to 120

### Root Causes Fixed

| Root Cause | Fix Applied |
|------------|------------|
| throughput (BPD) confused with flow_rate (BPH) | Separate handling; heuristic detection of user intent |
| engineering_rules.json CDU max=60k vs actual 95k | Updated to 100k to match design capacity |
| Storage Terminal NameError (c_utilization) | Fixed to use current_values.get('yield') |
| Response shows Economic Impact/Confidence Level | Removed from default; only when explicitly asked |
| No sanity checks on flow_ratio | Clamped to 0.1–3.0 range |
| Energy % unlimited scaling | Capped at ±50% |
| Labels 'Flow' but shows throughput | Correct field labels with proper units |