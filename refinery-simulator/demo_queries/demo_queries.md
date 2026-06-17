# Boss Demonstration SQL Queries Walkthrough

This document compiles the SQL queries located in [demo_queries.sql](file:///Users/shivam/Desktop/refinery_decision_system/refinery-simulator/demo_queries/demo_queries.sql), describing what each query does and showing sample output tables to assist in demonstrating the database backend to supervisors.

To execute any query, open the SQLite shell:
```bash
sqlite3 refinery.db
```

---

## 1. Unit Overview Queries

### Query 1.1: Show All Refinery Units
- **Purpose:** Demonstrates the core refinery assets registered in the database, displaying unit names, codes, throughput capacities, and statuses.
- **SQL Code:**
  ```sql
  SELECT id, name, code, throughput_capacity, status FROM refinery_units;
  ```
- **Sample Output:**
  | ID | Name | Code | Throughput Capacity (bbl/day) | Status |
  |---|---|---|---|---|
  | 1 | Crude Distillation Unit | CDU | 100000.0 | Active |
  | 2 | Vacuum Distillation Unit | VDU | 45000.0 | Active |
  | 3 | Fluid Catalytic Cracking Unit | FCC | 35000.0 | Active |
  | 4 | Hydrotreater Unit | Hydrotreater | 25000.0 | Active |
  | 5 | Storage & Logistics Terminal | Storage Terminal | 1000000.0 | Active |

---

## 2. Operational Data Queries

### Query 2.1: Latest Operational Records
- **Purpose:** Fetches the most recent entry from the operational logs for each unit. This acts as the default "Before State" for simulations.
- **SQL Code:**
  ```sql
  SELECT u.code, oh.throughput, oh.pressure, oh.temperature, oh.yield, oh.downtime, oh.energy_consumption, oh.timestamp
  FROM operational_history oh
  JOIN refinery_units u ON oh.unit_id = u.id
  WHERE oh.id IN (SELECT MAX(id) FROM operational_history GROUP BY unit_id);
  ```

### Query 2.2: Downtime Analysis
- **Purpose:** Sums cumulative downtime hours and counts outage events per unit, helping evaluate reliability.
- **SQL Code:**
  ```sql
  SELECT u.code, 
         ROUND(SUM(oh.downtime), 1) as total_downtime_hours, 
         COUNT(CASE WHEN oh.downtime > 0 THEN 1 END) as downtime_occurrences
  FROM operational_history oh
  JOIN refinery_units u ON oh.unit_id = u.id
  GROUP BY oh.unit_id;
  ```

---

## 3. Analytics Queries

### Query 3.1: Average Throughput & Utilization
- **Purpose:** Shows average throughput rates over the historical period, and compares it to hydraulic limits to output a utilization index.
- **SQL Code:**
  ```sql
  SELECT u.code, 
         ROUND(AVG(oh.throughput), 1) as avg_throughput, 
         u.throughput_capacity as design_limit,
         ROUND((AVG(oh.throughput) / u.throughput_capacity) * 100, 1) as avg_utilization_pct
  FROM operational_history oh
  JOIN refinery_units u ON oh.unit_id = u.id
  GROUP BY oh.unit_id;
  ```
- **Sample Output:**
  | Code | Avg Throughput | Design Limit | Avg Utilization % |
  |---|---|---|---|
  | CDU | 82340.5 | 100000.0 | 82.3% |
  | VDU | 35890.2 | 45000.0 | 79.8% |
  | FCC | 27610.9 | 35000.0 | 78.9% |
  | Hydrotreater | 19450.4 | 25000.0 | 77.8% |

---

## 4. Simulation Data Queries

### Query 4.2: Recent Simulation Runs
- **Purpose:** Audits completed simulations, including the scenario name, timestamp, risk score, and diagnosed bottlenecks.
- **SQL Code:**
  ```sql
  SELECT sr.id as run_id, 
         s.name as scenario_name, 
         sr.run_timestamp, 
         sr.risk_score, 
         COALESCE(u.code, 'None') as bottleneck_unit
  FROM simulation_runs sr
  JOIN scenarios s ON sr.scenario_id = s.id
  LEFT JOIN refinery_units u ON sr.bottleneck_unit_id = u.id
  ORDER BY sr.run_timestamp DESC;
  ```

---

## 5. AI Recommendations Queries

### Query 5.1: Latest AI Recommendations
- **Purpose:** Displays recommendations generated from simulation runs, their target units, and severity.
- **SQL Code:**
  ```sql
  SELECT rec.id, 
         s.name as scenario_name, 
         COALESCE(u.code, 'Global') as target_unit, 
         rec.recommendation_text, 
         rec.priority
  FROM ai_recommendations rec
  JOIN simulation_runs sr ON rec.run_id = sr.id
  JOIN scenarios s ON sr.scenario_id = s.id
  LEFT JOIN refinery_units u ON rec.unit_id = u.id
  ORDER BY rec.id DESC 
  LIMIT 10;
  ```

---

## 6. Chatbot Logs Queries

### Query 6.1: Recent Chatbot Questions
- **Purpose:** Inspects chatbot requests to audit system utility.
- **SQL Code:**
  ```sql
  SELECT id, user_query, system_response, llm_called, timestamp 
  FROM chatbot_logs 
  ORDER BY timestamp DESC 
  LIMIT 5;
  ```


































sqlite3 refinery.db
.headers on
.mode box


--Purpose: Displays the core refinery units, their model codes, operational statuses, and maximum throughput design capacities.


SELECT id, name, code, throughput_capacity, status FROM refinery_units;


--Purpose: Calculates the average real-world throughput of each unit from historical logs and compares it against design capacity to show an efficiency percentage.


SELECT u.code, 
       ROUND(AVG(oh.throughput), 1) AS avg_throughput, 
       u.throughput_capacity AS design_limit,
       ROUND((AVG(oh.throughput) / u.throughput_capacity) * 100, 1) AS avg_utilization_pct
FROM operational_history oh
JOIN refinery_units u ON oh.unit_id = u.id
GROUP BY oh.unit_id;



--Purpose: Showcases how the system captures scenario simulations, calculates safety/operational risk scores (0-100), and auto-diagnoses unit bottlenecks.


SELECT sr.id AS run_id, 
       s.name AS scenario_name, 
       sr.run_timestamp, 
       sr.risk_score, 
       COALESCE(u.code, 'None') AS bottleneck_unit
FROM simulation_runs sr
JOIN scenarios s ON sr.scenario_id = s.id
LEFT JOIN refinery_units u ON sr.bottleneck_unit_id = u.id
ORDER BY sr.run_timestamp DESC
LIMIT 5;




--Purpose: Shows that the chatbot records queries, responses, and whether it pulled database facts to formulate answers.


SELECT id, user_query, llm_called, timestamp 
FROM chatbot_logs 
ORDER BY timestamp DESC 
LIMIT 5;


.exit




Database Storage File:
Path: 

refinery.db
What it is: The actual binary SQLite database containing all records (refinery units, 1,000+ operational logs, simulation runs, parameters, chatbot logs, and PDF records).


Path: 

schema.sql
What it is: The query script containing all the DDL (CREATE TABLE, indexes) that defines the tables, column types (like throughput REAL, status TEXT), constraints, and relationships (foreign keys).


Path: 

seed_data.sql
What it is: The raw SQL script that inserts initial setup parameters and populates the database tables with baseline values and historical timelines.




Path: 

generate_seed_data.py
What it is: The Python script that programmatically models normal operational variables (under bounds of physical ranges) and writes the seed_data.sql file.


Path: 

demo_queries.sql
 (Raw queries)
Path: 

demo_queries.md
 (Step-by-step review with pre-computed outputs)