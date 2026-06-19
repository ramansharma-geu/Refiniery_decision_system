# Unit Audit Report: Flow Rate vs. Throughput

This report documents the semantic definitions, storage representations, display formats, and conversion formulas for flow rates and throughput metrics in the Refinery Decision Intelligence System (RDIS).

---

## 1. Parameter Definitions

| Parameter | Engineering Definition | Operational Scope |
| :--- | :--- | :--- |
| **FLOW_RATE** | The instantaneous volumetric velocity of feedstock or process intermediate fluid passing through a given cross-section per unit time. | Used by control room operators and process engineers to monitor hydraulic loading, column velocities, and pump stresses. |
| **THROUGHPUT** | The cumulative volume of feedstock or intermediate material charged (processed) in a refinery unit over a standard 24-hour operating day. | Used for planning, scheduling, scheduling capacity margins, and tracking daily production volume targets. |

---

## 2. Storage vs. Display Specifications

| Parameter | Database Column | Storage Unit | Display Unit | Resolution / Constraints |
| :--- | :--- | :--- | :--- | :--- |
| **Flow Rate** | `operational_history.flow_rate` | **BPH** (Barrels Per Hour) | **BPH** (Barrels Per Hour) | Must not exceed mechanical safety design limits (e.g. 4,200 BPH for CDU). |
| **Throughput** | `operational_history.throughput` | **BPD** (Barrels Per Day) | **BPD** (Barrels Per Day) | Must align with unit capacity limits (e.g. 100,000 BPD for CDU). |

---

## 3. Conversion Formulas

The mathematical relationship between instantaneous flow rate ($F_{BPH}$) and daily throughput ($T_{BPD}$) assumes continuous, steady-state operations over a 24-hour period:

$$\text{Throughput (BPD)} = \text{Flow Rate (BPH)} \times 24.0$$

$$\text{Flow Rate (BPH)} = \frac{\text{Throughput (BPD)}}{24.0}$$

### Scaling & Safety Clamping Rules
1. **Flow Ratio Calculation:** When simulating throughput adjustments, the scaling ratio is computed based on daily throughput:
   $$\text{flow\_ratio} = \frac{T_{\text{target, BPD}}}{T_{\text{current, BPD}}}$$
2. **Display Clamping:** The requested target conditions are displayed as entered by the user (up to design limits or physical bounds), but actual safety estimations and thermodynamic outputs are calculated using clamped capacity inputs to prevent unrealistic extrapolations.
