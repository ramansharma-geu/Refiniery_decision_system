# RDIS Demonstration & Presentation Guide

Use this manual to guide your presentations of the Refinery Decision Intelligence System (RDIS) to supervisors, management, or stakeholders.

---

## 1. The 5-Minute Pitch (High-Level Overview)

**Objective:** Briefly show how the web console provides visibility and instant sandbox assessments.

1. **Dashboard Overview:** Start at the homepage ([http://127.0.0.1:5001](http://127.0.0.1:5001)). Point to:
   - The top utility bar showing shift details and location variables.
   - The KPI cards indicating 5 active units and total simulations completed.
   - The interactive charts showing historical trends of throughput and energy.
2. **Execute a Sandbox Simulation:**
   - Go to **Scenarios & Runs** in the sidebar.
   - Find the card **Throughput Increase (+10%)** and click **Execute Simulation & Analysis**.
3. **Show Outage Results:**
   - On the results screen, highlight the **Operational Risk Index** (which rises to `55/100` warning state) and point to the **Detected Bottleneck** (`Hydrotreater Unit`).
   - Explain: *"By raising crude rates, we have hydraulic limits exceeded on the hydrotreater column, warning operators of catalyst bed stresses before physical actions are taken."*

---

## 2. The 10-Minute Walkthrough (Deep Operational Dive)

**Objective:** Walk through operational history logs, custom rules configuration, and hybrid chatbot queries.

1. **Refinery Unit Specs & History:**
   - Go to **Refinery Units**. Show cards detailing capacity utilization progress bars.
   - Click **View Parameter Trends & Logs** on the FCC unit. Show dual-axis history charts plotting throughput and flow rate variables side-by-side.
   - Go to **Operational History** in the sidebar. Show that the database contains a B-Tree indexed logging grid containing over 1,000 unique records.
2. **Create a Custom Scenario:**
   - Go to **Scenarios & Runs** and click **Create Custom Scenario**.
   - Input Name: `Power Curtailment Level 2`.
   - Select Rule Template: `Energy Reduction (-20% electricity cap)`.
   - Input Description: `Simulate operations under a power utility cap`.
   - Click **Create Scenario Template**.
   - Back in the list, locate your new scenario and click **Execute Simulation & Analysis**. Show that all units successfully scale back throughput to stay under the energy budget.
3. **Hybrid AI Chatbot Consultation:**
   - Go to the **Hybrid AI Chatbot** page.
   - Click **"What is FCC and why is it important?"** from the quick click panel.
   - Show how the system performs database-first retrieval to fetch actual FCC throughput values, and seamlessly combines it with SLM chemical engineering reasoning.

---

## 3. The Supervisor Demonstration Flow

Follow this exact sequence of actions to deliver a premium demonstration:

### Step 1: Open Dashboard
- Navigate to the homepage. Show the dashboard.
- Explain: *"This is RDIS, an industrial decision support command center. It monitors refinery unit capacities and logs shifts."*

### Step 2: Show Unit Data
- Click **Refinery Units** in the sidebar.
- Point out the active utilization percentages: *"All units are running at roughly 80% baseline load. Now we will simulate an operational bottleneck."*
- Click **CDU** details to show its historical variables.

### Step 3: Run Scenario
- Click **Scenarios & Runs** in the sidebar.
- Click **Execute Simulation & Analysis** on the **FCC Shutdown** scenario.

### Step 4: Show Impact Analysis
- Scroll through the results comparisons table.
- Explain: *"Our rules show that shutting down the FCC instantly reduces upstream VDU throughput by 40% because vacuum gas oil backs up. CDU throughput drops by 10% to balance product distributions."*

### Step 5: Show AI Recommendations
- Point to the **AI Recommendations & Action Plan** cards.
- Highlight the **High Priority** alerts: *"The system generates desulfurization and storage action advices immediately after running the simulation, assisting safety managers."*

### Step 6: Ask Chatbot Questions
- Go to the **Hybrid AI Chatbot** page.
- Execute three query models to show integration:
  1. *Factual:* Click **"What is current FCC throughput?"** (Shows database value of `0.0` since we just ran the shutdown simulation!).
  2. *Conceptual:* Click **"What causes refinery bottlenecks?"** (SLM domain knowledge response).
  3. *Hybrid:* Click **"What is FCC and why is it important?"** (Factual zero throughput + converter explanation).

### Step 7: Export PDF Report
- Go to **Reports & Exports Manager** in the sidebar.
- Select the recent FCC Shutdown run from the dropdown list.
- Click **Compile & Save PDF Report**.
- Under **Generated Reports Log**, click **Download** next to the compiled PDF to show the printable report card.

### Step 8: Execute SQL Queries
- Open terminal console or open [demo_queries.sql](file:///Users/shivam/Desktop/refinery_decision_system/refinery-simulator/demo_queries/demo_queries.sql).
- Run a query to show the underlying SQLite tables:
  ```bash
  sqlite3 refinery.db "SELECT u.code, ROUND(AVG(oh.throughput), 2) FROM operational_history oh JOIN refinery_units u ON oh.unit_id = u.id GROUP BY oh.unit_id;"
  ```
- Explain: *"Every action, run, query, and history logs reside in a structured SQLite database file, enabling analytics exports."*
