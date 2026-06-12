# RDIS Testing Guide

This document describes how to execute the RDIS automated test suite and check system integrations.

## 1. Automated Test Suite
RDIS contains a comprehensive unittest suite located in `tests/test_refinery.py`. It runs in isolation using an in-memory SQLite database, verifying:
- Database structures, models, and CRUD operations.
- Simulation engine logic (verifying parameter calculations and bottleneck detection).
- Chatbot parser (ensuring natural language triggers map to the correct intents).
- Hybrid retriever (testing correct SQL query translations and SLM routing).
- Report services (validating that PDF/CSV generations write correct files).

### Running Automated Tests
Navigate to the project root and run:

```bash
python3 -m unittest discover -s tests -p "test_refinery.py"
```

### Expected Output
The test discovery will execute all test cases and return a clean success status:

```text
.....
----------------------------------------------------------------------
Ran 5 tests in 0.064s

OK
```

---

## 2. Manual Verification Checklist

Follow this checklist to manually verify the system behaves as expected on the frontend:

### Checklist Item A: Dashboard Check
- Open the dashboard at [http://127.0.0.1:5001](http://127.0.0.1:5001).
- Confirm that the KPI cards show:
  - Total Units: `5`
  - Active Units: `5`
  - In Maintenance: `0`
- Confirm that the line graphs display historical data points for the 5 units.

### Checklist Item B: Run Scenario Simulation
- Navigate to **Scenarios & Runs** page.
- Locate the **FCC Shutdown** template card and click **Execute Simulation & Analysis**.
- You will be redirected to the **Simulation Results** page.
- Verify:
  - Operational Risk Index shows `85 / 100` (Red warning).
  - Detected Bottleneck shows `Fluid Catalytic Cracking Unit (FCC)`.
  - In the VDU table, verify Throughput has dropped (40% drop).
  - AI Recommendations card lists priority actions for the VDU and FCC.

### Checklist Item C: PDF Compilation
- On the **Simulation Results** page, click the **Generate PDF Report** button.
- You will be redirected to the **Reports & Exports Manager** showing a confirmation banner.
- Under **Generated Reports Log**, verify that a new PDF report record is listed.
- Click **Download** to open the PDF file and verify formatting.

### Checklist Item D: Chatbot Hybrid Query
- Navigate to **Hybrid AI Chatbot**.
- Click the quick-query button: **"What is current FCC throughput?"**
  - Verify that a database context table appears displaying the current FCC data point.
- Click **"What is FCC and why is it important?"** (Hybrid)
  - Verify that the response includes both the current FCC data point and an explanation of FCC conversion.
