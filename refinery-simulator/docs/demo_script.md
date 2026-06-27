# RDIS Demonstration Script: Quick 5-Minute Briefing

Welcome to the **Refinery Decision Intelligence System (RDIS)**. This script guide is structured for refinery managers and supervisors to grasp the project context, technical architecture, and live simulation capabilities within 5 minutes.

---

## 1. Project Overview
The **Refinery Decision Intelligence System (RDIS)** is a domain-specific decision support proof-of-concept. It acts as an experienced **Refinery Process Engineer Assistant** rather than a generic database search tool. Using local Small Language Models (SLMs) and a rule-based scaling simulation engine, it helps process operators and refinery managers perform quick what-if assessments before committing to plant changes.

## 2. Problem Statement
Refinery managers and operators often need to evaluate how upstream modifications (like changing CDU throughput or crude API gravity) propagate through downline units (VDU, FCC, Hydrotreater, Storage) and affect yields, pressures, utility energy, and safety margins. Traditional models are heavy and slow. Generic LLMs lack mathematical database bounds and hallucinate. RDIS solves this by bridging SQLite process history with an engineering rules simulation engine and a local SLM.

## 3. Architecture Overview
```text
                    +--------------------------------+
                    |           User Query           |
                    +--------------------------------+
                                    |
                                    v
                    +--------------------------------+
                    |       Intent Classifier        |
                    +--------------------------------+
                                    |
            +-----------------------+-----------------------+
            |                       |                       |
            v                       v                       v
     [ KNOWLEDGE ]           [ CURRENT DATA ]         [ SIMULATION ]
            |                       |                 [  & ANALYSIS  ]
            |                       |                       |
            v                       v                       v
     +------------+          +------------+          +--------------+
     | Ollama SLM |          | SQLite DB  |          | Sim V2 Engine|
     | (Domain KB)|          | (Query SQL)|          | (Scale Rules)|
     +------------+          +------------+          +--------------+
            |                       |                       |
            |                       |                       v
            |                       |                +--------------+
            |                       |                |  Ollama SLM  |
            |                       |                |  (Synthesis) |
            |                       |                +--------------+
            +-----------------------+-----------------------+
                                    |
                                    v
                    +--------------------------------+
                    |       Response Validator       |
                    |   (Forbidden Phrase / Words)   |
                    +--------------------------------+
                                    |
                                    v
                    +--------------------------------+
                    |        Chatbot Output          |
                    +--------------------------------+
```

## 4. Supported Question Types
RDIS supports exactly four process engineering intents:
1. **Knowledge Questions (Type 1):** Queries answered from the SLM's chemical engineering training only (no DB query).
2. **Current Data Questions (Type 2):** Returns actual, direct operational records straight from the SQLite database.
3. **Analysis Questions (Type 3):** Combines SQLite recent values with SLM diagnostic reasoning to suggest causes and recommendations.
4. **What-If Simulations (Type 4):** Evaluates hypothetical adjustments by combining SQLite current conditions, engineering rules bounds, and scaling formulas.

---

## 5. Live Demo Questions
Here are four questions to execute in the live chatbot to demonstrate its capabilities:
1. *Knowledge:* **"What is FCC?"**
2. *Current Data:* **"Show CDU flow rate."**
3. *Analysis:* **"Why is FCC yield decreasing?"**
4. *Simulation:* **"If CDU flow becomes 6000 BPD, what should temperature be?"**

---

## 6. Sample Chatbot Outputs

### Live Example 1: Knowledge Query
* **User:** "What is VDU?"
* **Response:** 
  > The Vacuum Distillation Unit (VDU) processes the heavy Atmospheric Residue from the CDU. By operating under deep vacuum (0.5 to 1.5 psi absolute), it lowers boiling points and separates high-boiling heavy hydrocarbons into Vacuum Gas Oils (VGO) and Vacuum Residue without causing thermal cracking.
  > 
  > • Operates at sub-atmospheric pressure.
  > • Avoids thermal degradation of heavy hydrocarbons.
  > • Produces feedstock for the FCC reactor.

### Live Example 2: Current Data Query
* **User:** "Show FCC temperature."
* **Response:**
  > **Current Plant Data**
  >
  > FCC
  > • Reactor Temperature: 1005.2 °F
  > • Pressure: 31.4 psi
  > • Throughput: 27,842.1 BPD
  > • Timestamp: 2026-06-18 12:00:00

---

## 7. Simulation Examples (The Core Feature)
* **User Query:** "If CDU flow becomes 6000 BPD, what are the recommended parameters?"
* **Response:**
  > CDU operating throughput is estimated at 6000 BPD with a confidence score of 0.95 (High).
  >
  > **Current Conditions**
  > • Flow Rate: 3200.0 BPD
  > • Temperature: 680.0 °F
  > • Pressure: 35.0 psi
  > • Timestamp: 2026-06-18 12:00:00
  >
  > **Recommended Parameters**
  > • Temperature: 689.7 - 717.9 °F
  > • Pressure: 36.7 - 38.2 psi
  > • Throughput: 5880.0 - 6120.0 BPD
  > • Yield: 87.9 - 91.5 %
  > • Confidence: 0.95 (High)
  >
  > **Expected Changes**
  > • Energy consumption change: +109.4%
  > • Res residence time decreases yield by -1.1%
  >
  > **Operational Risks**
  > • Column flooding and furnace duty limits when throughput rises.
  >
  > **Recommendations**
  > • Increase charge rate gradually in 5% steps and monitor tray differential pressures.

---

## 8. Benefits for Refinery Supervisors
- **Digital Twin Sandbox:** Safely models plant reactions before making mechanical adjustments.
- **Dynamic Context awareness:** Calculations adapt to the active database state, ensuring realistic estimations.
- **Strict Compliance Safety:** Validator strips out AI fluff, disclaimers, or generic explanations, matching senior engineer language.
- **Local & Offline Execution:** Ollama runs completely locally, protecting proprietary refinery operational metrics.

## 9. Current Limitations
- **POC Scenarios:** Models relationships only for the five main process units.
- **Empirical Formulas:** Formulas represent generic scaling dynamics, not high-fidelity physical kinetics.

## 10. Future Scope
- **Real-time Sensor Integration:** Bridge with real OPC-UA / SCADA historian pipelines.
- **Machine Learning Integration:** Replace scaling formulas with neural-net surrogates trained on live plant data.
