# RDIS Process Engineering Domain Audit Report

This audit reviews the process engineering configurations, operational ranges, scaling calculations, and safety recommendations implemented in the **Refinery Decision Intelligence System (RDIS)** compared to real-world industrial standards.

---

## 1. Unit Configuration & Boundary Review

The five simulated units (CDU, VDU, FCC, Hydrotreater, Storage Terminal) are mapped with basic operational ranges. Here is the engineering audit of those boundaries:

### 1.1. Crude Distillation Unit (CDU)
* **Rules Configuration:** Throughput `[1000, 60000]` BPD, Temperature `[600, 800]` °F, Pressure `[10, 60]` psi, Yield `[70, 95]`%.
* **Engineering Review:**
  - **Nominal Pressure Range:** Atmospheric distillation columns operate at low pressures (typically 15 to 30 psi at the flash zone). A maximum mechanical design pressure of 60 psi is realistic for safety relief valve settings, but operating at 50-60 psi in a real column would flood trays and disrupt product fractionation.
  - **Nominal Temperature Range:** 650°F to 750°F is the standard temperature range for the crude furnace outlet. Going above 750°F causes crude cracking inside furnace tubes, leading to rapid tube coking and hot spots. The warning threshold of 760°F is an appropriate safety limit.

### 1.2. Vacuum Distillation Unit (VDU)
* **Rules Configuration:** Throughput `[500, 30000]` BPD, Vacuum `[25.0, 29.5]` inHg, Pressure `[0.5, 2.0]` psi.
* **Engineering Review:**
  - **Pressure & Vacuum Units:** Distillation under vacuum is meant to lower boiling points. Standard vacuum columns operate under deep vacuum (typically 10 to 40 mmHg absolute pressure at the column top, which is approximately 0.2 to 0.8 psi). Clamping the pressure to a maximum of 2.0 psi (about 100 mmHg) is a correct mechanical boundary because operating above 2.0 psi would cause heavy hydrocarbon cracking and column upsets.

### 1.3. Fluid Catalytic Cracking (FCC) Unit
* **Rules Configuration:** Throughput `[1000, 40000]` BPD, Reactor Temperature `[950, 1050]` °F, Catalyst Ratio `[0.05, 0.20]`, Gasoline Yield `[40, 90]`%.
* **Engineering Review:**
  - **Catalyst-to-Oil Ratio Mismatch (High Severity):** The catalyst-to-oil ratio (C/O) in the rules engine is set to `[0.05, 0.20]`. In industrial FCC operations, the catalyst-to-oil ratio is a **weight ratio** representing the circulation rate of catalyst relative to crude oil feed. This ratio is typically **5.0 to 10.0** (i.e. 5 to 10 tons of catalyst circulating per ton of feed). A C/O ratio of 0.10 is the *inverse* of real operations and represents a major chemical engineering domain mismatch.
  - **Temperature range:** 950°F to 1020°F is typical for riser reactor operations. Exceeding 1040°F causes excessive thermal cracking, producing excessive dry gas (methane, ethane) and reducing gasoline yield.

### 1.4. Hydrotreater Unit
* **Rules Configuration:** Throughput `[100, 30000]` BPD, Temperature `[600, 800]` °F, Pressure `[600, 1200]` psi.
* **Engineering Review:**
  - **Operating Pressure:** High pressure (600 to 1200 psi) is chemically correct and required to maintain hydrogen solubility in the liquid hydrocarbons and prevent catalyst coking.
  - **Thermal Exotherm Runaway:** Desulfurization (HDS) is an exothermic reaction. Ramping throughput by 20% or doubling sulfur feed causes an increased reaction exotherm. The warning threshold of 720°F is critical because going above 750°F can initiate catalyst bed thermal runaways.

---

## 2. Scaling Formulas & Physical Logic Auditing

### 2.1. Throughput vs Temperature Assumption
* **File:** [simulation_engine.py](file:///Users/shivam/Desktop/refinery_decision_system/refinery-simulator/simulation_engine.py)
* **Formula Checked:** `t_temp = c_temp * (1.0 + 0.04 * (flow_ratio - 1.0))`
* **Audit Verdict:** **Unrealistic Process Logic**. In real CDU or VDU columns, the column inlet (flash zone) temperature is **controlled at a constant target** (e.g. 700°F) using a feedback loop that adjusts the fuel gas firing rate in the crude furnace. Increasing crude throughput (flow rate) requires more heat transfer duty (furnace duty, MMBtu/hr), but it does **not** raise the operating temperature of the column. In fact, if the furnace duty hits its maximum limit, the temperature will *drop*, not rise. 
* **Fix Action:** Throughput increases should scale furnace heat duty (MMBtu/hr) while column temperature should remain constant unless heating capacity is exceeded.

### 2.2. Pressure Drop vs Flow Rate
* **Formula Checked:** `t_press = c_press * (1.0 + 0.15 * (flow_ratio - 1.0))` (for Hydrotreater)
* **Audit Verdict:** **Physically Correct**. Pressure drop across a packed bed (like a hydrotreater reactor) scales quadratically/linearly with fluid velocity (Ergun Equation). Representing an increase in operating pressure as a function of feed velocity is a sound engineering approximation.

---

## 3. Review of System Recommendations

* **Unsafe Advice Flagged:**
  - *CDU Over-temperature:* If CDU temperature exceeds 780°F, the system recommends *"cleaning preheat train exchangers"*. While preheat cleaning reduces furnace load, it does not solve an active column overtemperature. The immediate operational response to an overtemperature column is to **reduce furnace firing** or **increase reflux rate** to cool the top trays and prevent cracking.
  - *Hydrotreater High Sulfur:* When sulfur load increases, the system recommends *"increasing recycle gas rate and reactor quench flows"*. This is **highly accurate** and represents standard refinery emergency procedure (quench gas cooling prevents exothermic runaway).
