-- RDIS Boss Demonstration SQL Queries
-- Purpose: Quick inspections to demonstrate the SQLite relational storage schema to supervisors.
-- All queries are tested against the RDIS database.

-- =====================================================================
-- SECTION 1: UNIT OVERVIEW
-- =====================================================================

-- Query 1.1: Show all refinery units
-- Lists the name, code, design throughput capacity, and active status.
SELECT id, name, code, throughput_capacity, status 
FROM refinery_units;

-- Query 1.2: Show unit details
-- Fetches full details for a specific unit (e.g. Crude Distillation Unit).
SELECT * 
FROM refinery_units 
WHERE code = 'CDU';


-- =====================================================================
-- SECTION 2: OPERATIONAL DATA
-- =====================================================================

-- Query 2.1: Latest operational records
-- Pulls the single most recent data entry from operational history for each unit.
SELECT u.code, oh.throughput, oh.pressure, oh.temperature, oh.yield, oh.downtime, oh.energy_consumption, oh.timestamp
FROM operational_history oh
JOIN refinery_units u ON oh.unit_id = u.id
WHERE oh.id IN (SELECT MAX(id) FROM operational_history GROUP BY unit_id);

-- Query 2.2: Top 5 throughput values (surges)
-- Returns the highest loading periods recorded in the refinery.
SELECT u.code, oh.throughput, oh.timestamp 
FROM operational_history oh
JOIN refinery_units u ON oh.unit_id = u.id
ORDER BY oh.throughput DESC 
LIMIT 5;

-- Query 2.3: Highest temperature records
-- Audit query for thermal stress records.
SELECT u.code, oh.temperature, oh.timestamp 
FROM operational_history oh
JOIN refinery_units u ON oh.unit_id = u.id
ORDER BY oh.temperature DESC 
LIMIT 5;

-- Query 2.4: Highest energy consumption
-- Identify periods with the highest utility overhead.
SELECT u.code, oh.energy_consumption, oh.timestamp 
FROM operational_history oh
JOIN refinery_units u ON oh.unit_id = u.id
ORDER BY oh.energy_consumption DESC 
LIMIT 5;

-- Query 2.5: Downtime analysis
-- Calculates cumulative offline hours and total shutdown occurrences.
SELECT u.code, 
       ROUND(SUM(oh.downtime), 1) as total_downtime_hours, 
       COUNT(CASE WHEN oh.downtime > 0 THEN 1 END) as downtime_occurrences
FROM operational_history oh
JOIN refinery_units u ON oh.unit_id = u.id
GROUP BY oh.unit_id;


-- =====================================================================
-- SECTION 3: ANALYTICS
-- =====================================================================

-- Query 3.1: Average throughput by unit
-- Average charge rate compared to the design capacity limit.
SELECT u.code, 
       ROUND(AVG(oh.throughput), 1) as avg_throughput, 
       u.throughput_capacity as design_limit,
       ROUND((AVG(oh.throughput) / u.throughput_capacity) * 100, 1) as avg_utilization_pct
FROM operational_history oh
JOIN refinery_units u ON oh.unit_id = u.id
GROUP BY oh.unit_id;

-- Query 3.2: Average yield by unit
-- Returns average distillation and cracking efficiencies.
SELECT u.code, 
       ROUND(AVG(oh.yield), 2) as avg_yield_pct
FROM operational_history oh
JOIN refinery_units u ON oh.unit_id = u.id
GROUP BY oh.unit_id;

-- Query 3.3: Average energy consumption
-- Shows the utility footprint for heaters and pumps.
SELECT u.code, 
       ROUND(AVG(oh.energy_consumption), 2) as avg_hourly_energy
FROM operational_history oh
JOIN refinery_units u ON oh.unit_id = u.id
GROUP BY oh.unit_id;

-- Query 3.4: Performance comparison matrix
-- Aggregates min, mean, max parameters side-by-side.
SELECT u.code,
       ROUND(MIN(oh.throughput), 1) as min_throughput,
       ROUND(AVG(oh.throughput), 1) as avg_throughput,
       ROUND(MAX(oh.throughput), 1) as max_throughput,
       ROUND(AVG(oh.yield), 2) as avg_yield_pct,
       ROUND(AVG(oh.energy_consumption), 2) as avg_energy
FROM operational_history oh
JOIN refinery_units u ON oh.unit_id = u.id
GROUP BY oh.unit_id;


-- =====================================================================
-- SECTION 4: SIMULATION DATA
-- =====================================================================

-- Query 4.1: All scenarios
-- Lists configured templates.
SELECT * FROM scenarios;

-- Query 4.2: Recent simulation runs
-- Lists simulation histories, risk values, and detected bottlenecks.
SELECT sr.id as run_id, 
       s.name as scenario_name, 
       sr.run_timestamp, 
       sr.risk_score, 
       COALESCE(u.code, 'None') as bottleneck_unit
FROM simulation_runs sr
JOIN scenarios s ON sr.scenario_id = s.id
LEFT JOIN refinery_units u ON sr.bottleneck_unit_id = u.id
ORDER BY sr.run_timestamp DESC;

-- Query 4.3: Parameter changes count
-- Count of unit parameters modified in previous simulations (identifies unit impact frequency).
SELECT u.code, 
       COUNT(r.id) as parameter_change_records
FROM simulation_results r
JOIN refinery_units u ON r.unit_id = u.id
WHERE r.before_value != r.after_value
GROUP BY r.unit_id
ORDER BY parameter_change_records DESC;

-- Query 4.4: High risk simulations
-- Displays simulations carrying a risk index >= 70.
SELECT sr.id as run_id, 
       s.name as scenario_name, 
       sr.risk_score, 
       sr.run_timestamp
FROM simulation_runs sr
JOIN scenarios s ON sr.scenario_id = s.id
WHERE sr.risk_score >= 70
ORDER BY sr.risk_score DESC;


-- =====================================================================
-- SECTION 5: AI RECOMMENDATIONS
-- =====================================================================

-- Query 5.1: Latest AI recommendations
-- Retrieves generated advice associated with simulation run templates.
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

-- Query 5.2: Count of recommendations by severity
-- Group warnings by severity levels (High, Medium, Low).
SELECT priority, 
       COUNT(*) as recommendation_count
FROM ai_recommendations
GROUP BY priority
ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;


-- =====================================================================
-- SECTION 6: CHATBOT LOGS
-- =====================================================================

-- Query 6.1: Recent chatbot questions
-- Inspects the conversation history log.
SELECT id, user_query, system_response, llm_called, timestamp 
FROM chatbot_logs 
ORDER BY timestamp DESC 
LIMIT 5;

-- Query 6.2: Chatbot database retrieval queries
-- Lists chatbot queries that used data-first retrieval (retrieved SQLite context).
SELECT user_query, retrieved_data_used, timestamp 
FROM chatbot_logs 
WHERE retrieved_data_used IS NOT NULL AND retrieved_data_used != '[]'
ORDER BY timestamp DESC 
LIMIT 5;
