# UNIT MAPPING REPORT — RDIS Database Fields

## Table: `operational_history`

### CDU (Crude Distillation Unit)

| Field Name | Engineering Meaning | Stored Unit | DB Range (actual) | Expected Display | Conversion |
|------------|-------------------|-------------|-------------------|-----------------|------------|
| `throughput` | Total crude feed processed per day | BPD | 73,120 – 95,000 | BPD | None |
| `flow_rate` | Instantaneous volumetric feed flow | BPH (≈throughput/24) | 2,924 – 4,000 | BPD (×24) or BPH | ×24 for BPD |
| `temperature` | Flash zone / column operating temperature | °F | 678 – 735 | °F | None |
| `pressure` | Column operating pressure | psi | 30.0 – 48.4 | psi | None |
| `yield` | Liquid product recovery percentage | % | 90.0 – 95.0 | % | None |
| `energy_consumption` | Total energy consumed | MWh | 177 – 250 | MWh | None |
| `downtime` | Cumulative hours offline | hours | 0 – 12 | hours | None |

---

### VDU (Vacuum Distillation Unit)

| Field Name | Engineering Meaning | Stored Unit | DB Range (actual) | Expected Display | Conversion |
|------------|-------------------|-------------|-------------------|-----------------|------------|
| `throughput` | Atmospheric residue feed processed | BPD | 30,000 – 42,000 | BPD | None |
| `flow_rate` | Instantaneous volumetric feed flow | BPH | 1,200 – 1,750 | BPD (×24) or BPH | ×24 for BPD |
| `temperature` | Vacuum column heater outlet temperature | °F | 737 – 772 | °F | None |
| `pressure` | Column absolute pressure | psi | 0.5 – 1.5 | psi | None |
| `yield` | Vacuum gas oil recovery percentage | % | 85.0 – 92.0 | % | None |
| `energy_consumption` | Total energy consumed | MWh | 117 – 180 | MWh | None |
| `downtime` | Cumulative hours offline | hours | 0 – 12 | hours | None |

---

### FCC (Fluid Catalytic Cracking Unit)

| Field Name | Engineering Meaning | Stored Unit | DB Range (actual) | Expected Display | Conversion |
|------------|-------------------|-------------|-------------------|-----------------|------------|
| `throughput` | VGO feed charge rate | BPD | 22,000 – 33,000 | BPD | None |
| `flow_rate` | Instantaneous feed flow | BPH | 900 – 1,400 | BPD (×24) or BPH | ×24 for BPD |
| `temperature` | Reactor riser outlet temperature | °F | 981 – 1,020 | °F | None |
| `pressure` | Reactor operating pressure | psi | 26.1 – 40.0 | psi | None |
| `yield` | Gasoline + LPG conversion yield | % | 75.0 – 85.0 | % | None |
| `energy_consumption` | Total energy consumed | MWh | 200 – 320 | MWh | None |
| `downtime` | Cumulative hours offline | hours | 0 – 12 | hours | None |

---

### Hydrotreater

| Field Name | Engineering Meaning | Stored Unit | DB Range (actual) | Expected Display | Conversion |
|------------|-------------------|-------------|-------------------|-----------------|------------|
| `throughput` | Feed charge rate to reactor | BPD | 15,000 – 23,021 | BPD | None |
| `flow_rate` | Instantaneous feed flow | BPH | 620 – 978 | BPD (×24) or BPH | ×24 for BPD |
| `temperature` | Reactor weighted average bed temperature | °F | 644 – 700 | °F | None |
| `pressure` | Reactor operating pressure | psi | 777 – 801 | psi | None |
| `yield` | Desulfurization recovery yield | % | 97.0 – 99.5 | % | None |
| `energy_consumption` | Total energy consumed | MWh | 85 – 149 | MWh | None |
| `downtime` | Cumulative hours offline | hours | 0 – 12 | hours | None |

---

### Storage Terminal

| Field Name | Engineering Meaning | Stored Unit | DB Range (actual) | Expected Display | Conversion |
|------------|-------------------|-------------|-------------------|-----------------|------------|
| `throughput` | Total terminal transfer volume | BPD | 101,185 – 127,366 | BPD | None |
| `flow_rate` | Instantaneous transfer pump flow | BPH | 4,071 – 5,544 | BPD (×24) or BPH | ×24 for BPD |
| `temperature` | Ambient / tank temperature | °F | 60 – 90 | °F | None |
| `pressure` | Tank / line operating pressure | psi | 15 – 20 | psi | None |
| `yield` | Tank utilization (stores 100% = no loss) | % | 99.8 – 100.0 | % | None |
| `energy_consumption` | Transfer pump energy | MWh | 19 – 28 | MWh | None |
| `downtime` | Cumulative hours offline | hours | 0 – 12 | hours | None |

---

## Table: `refinery_units`

| Field Name | Engineering Meaning | Stored Unit | Notes |
|------------|-------------------|-------------|-------|
| `throughput_capacity` | Maximum design capacity | BPD | CDU=100k, VDU=45k, FCC=35k, HT=25k, ST=1M |

---

## Critical Finding: `flow_rate` vs `throughput`

```
flow_rate ≈ throughput / 24

CDU: throughput=95000 BPD, flow_rate=3767 BPH → 3767 × 24 = 90,408 (close match)
VDU: throughput=39748 BPD, flow_rate=1596 BPH → 1596 × 24 = 38,304 (close match)
FCC: throughput=27760 BPD, flow_rate=1155 BPH → 1155 × 24 = 27,729 (close match)
```

The `flow_rate` is confirmed to be in **Barrels Per Hour (BPH)**, derived as `throughput/24 ± 5%` noise.

When a user says "flow rate to 6000 BPD", they likely mean throughput of 6000 BPD (a much smaller unit than current CDU throughput of 95,000 BPD). The system must:
1. Correctly identify whether the user is specifying flow_rate (BPH) or throughput (BPD)
2. Convert between the two as needed
3. Display the correct field with correct label

---

## engineering_rules.json Bounds vs Actual DB Values

| Unit | JSON throughput_bpd max | Actual DB max | Status |
|------|------------------------|---------------|--------|
| CDU | 60,000 | 95,000 | **MISALIGNED** — bounds too low |
| VDU | 30,000 | 42,000 | **MISALIGNED** — bounds too low |
| FCC | 40,000 | 33,000 | OK |
| Hydrotreater | 30,000 | 23,021 | OK |
| Storage Terminal | 50,000 (transfer) | 127,366 (throughput) | Different metric |

> [!CAUTION]
> CDU and VDU engineering_rules.json bounds are significantly lower than actual operating data. This causes every CDU simulation to hit "Maximum Safe Limit Reached" immediately.
