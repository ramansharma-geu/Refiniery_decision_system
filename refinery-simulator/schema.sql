-- SQLite Database Schema for Refinery Decision Intelligence System (RDIS)

PRAGMA foreign_keys = ON;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL DEFAULT 'Operator',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Refinery Units Table
CREATE TABLE IF NOT EXISTS refinery_units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    code TEXT UNIQUE NOT NULL,
    description TEXT,
    throughput_capacity REAL NOT NULL, -- Design limit
    status TEXT NOT NULL DEFAULT 'Active', -- Active, Maintenance, Shutdown
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Operational History Table (minimum 1000 records, 200 per unit)
CREATE TABLE IF NOT EXISTS operational_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    throughput REAL NOT NULL,
    pressure REAL NOT NULL,
    temperature REAL NOT NULL,
    flow_rate REAL NOT NULL,
    downtime REAL NOT NULL DEFAULT 0.0, -- cumulative hours in that time interval
    yield REAL NOT NULL, -- yield percentage (e.g. 85.5)
    energy_consumption REAL NOT NULL, -- MWh or similar
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES refinery_units(id) ON DELETE CASCADE
);

-- Scenarios Table
CREATE TABLE IF NOT EXISTS scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- FCC_SHUTDOWN, THROUGHPUT_INCREASE, MAINTENANCE_DELAY, ENERGY_REDUCTION, DEMAND_INCREASE
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Scenario Parameters Table (defining delta rules)
CREATE TABLE IF NOT EXISTS scenario_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,
    parameter_name TEXT NOT NULL, -- throughput, pressure, temperature, flow_rate, downtime, yield, energy_consumption
    value_change_type TEXT NOT NULL, -- PERCENTAGE, ABSOLUTE
    value_change REAL NOT NULL, -- e.g. -1.0 (for shutdown), 0.10 (for 10% increase)
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES refinery_units(id) ON DELETE CASCADE
);

-- Simulation Runs Table
CREATE TABLE IF NOT EXISTS simulation_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    user_id INTEGER,
    run_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    risk_score INTEGER NOT NULL CHECK(risk_score >= 0 AND risk_score <= 100),
    bottleneck_unit_id INTEGER,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (bottleneck_unit_id) REFERENCES refinery_units(id) ON DELETE SET NULL
);

-- Simulation Results Table
CREATE TABLE IF NOT EXISTS simulation_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,
    parameter_name TEXT NOT NULL,
    before_value REAL NOT NULL,
    after_value REAL NOT NULL,
    FOREIGN KEY (run_id) REFERENCES simulation_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES refinery_units(id) ON DELETE CASCADE
);

-- AI Recommendations Table
CREATE TABLE IF NOT EXISTS ai_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    unit_id INTEGER, -- target unit for recommendation (NULL for global)
    recommendation_text TEXT NOT NULL,
    priority TEXT NOT NULL CHECK(priority IN ('High', 'Medium', 'Low')),
    FOREIGN KEY (run_id) REFERENCES simulation_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES refinery_units(id) ON DELETE SET NULL
);

-- Chatbot Logs Table
CREATE TABLE IF NOT EXISTS chatbot_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_query TEXT NOT NULL,
    system_response TEXT NOT NULL,
    retrieved_data_used TEXT, -- JSON serialization of SQL records retrieved
    llm_called INTEGER NOT NULL DEFAULT 0, -- boolean 0 or 1
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Reports Table
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    format TEXT NOT NULL, -- PDF, CSV
    file_path TEXT NOT NULL,
    run_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES simulation_runs(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_history_unit_time ON operational_history(unit_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_simulation_runs_scenario ON simulation_runs(scenario_id);
CREATE INDEX IF NOT EXISTS idx_simulation_results_run ON simulation_results(run_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_run ON ai_recommendations(run_id);
