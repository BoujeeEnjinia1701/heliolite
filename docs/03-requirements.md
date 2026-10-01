---
doc_id: HLT-REQ-001
title: HelioLite requirements
project: HelioLite
doc_type: Requirements
version: "0.6"
status: Draft
date: '2026-10-01'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-24'
  author: Amish Chadha
  change: Initial scaffold
- version: "0.2"
  date: '2026-09-25'
  author: Amish Chadha
  change: First measurable requirements for TRL 2, with status against the concept estimates
- version: "0.3"
  date: '2026-09-25'
  author: Amish Chadha
  change: R15 budget raised to $430 (HLT-DDR-001 D4); R5 allows the decided anemometer (D2); status column replaced by the TRL 3 results of HLT-CAL-001
- version: "0.4"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
- version: "0.5"
  date: '2026-09-26'
  author: Amish Chadha
  change: Budget top-up approved by Amish
- version: "0.6"
  date: '2026-10-01'
  author: Amish Chadha
  change: Status from HLT-CAL-001 v0.4 for the constructable design (HLT-DDR-003); R15 reported against the value-engineering target
---

# HelioLite requirements

These are the requirements for the concept, checked by calculation at TRL 3 in HLT-CAL-001 v0.4, for the constructable design of HLT-DDR-003. Targets are proposals, not yet validated with users. "Met" means met on paper only. On 2026-09-25 Amish decided to raise the budget to $430 (HLT-DDR-001, D4), so R15 reads $430, and R5 names the weather anemometer decided in D2 as allowed. Later the same day he accepted the TRL 3 recommendations (HLT-DDR-002): R13 is relaxed from 10 kg to 13 kg (N3), R7 now counts hands-on time spread over one clear day (N4), and R10 now allows the beam to move only downward during a stow (N5). On 2026-09-26 Amish approved a budget top-up to $455 (HLT-DDR-002 v0.2, P1), so R15 read $455. On 2026-10-01 Amish set budgets as hypothetical value-engineering targets ("the budgets are a hypothethical control target to ensure we are thinking along a value engineering lens"), so R15 now names the $455 value-engineering target and its status is reported against it. No other target has changed.

The **design point** used throughout is a clear winter day at 45° N, DNI 800 W/m², a mirror-to-target distance of 10 m and an angle of incidence on the mirror of about 32° (cosine factor 0.85).

Table 1. Requirements and TRL 3 status (tags refer to lines printed by `docs/04-calcs/sizing.py`).

| ID | Requirement | Target | Status (HLT-CAL-001) | Verification |
| --- | --- | --- | --- | --- |
| R1 | Redirected sunlight at the target | 200 W or more arriving at the outside of the target glazing at the design point | Met: 211 W [A2] | Optical calculation (done) |
| R2 | Useful daylight in the room | Raise the mean illuminance of a 12 m² room by 300 lx or more at the design point | Met: 502 lx, utilization 0.4 assumed [A3] | Illuminance calculation (done) |
| R3 | Daily energy delivered | 0.5 kWh or more through the glazing on a clear winter day | **At risk:** 0.50 kWh on 21 Dec and 1.00 kWh on 1 Feb at reference site A; 0.40 kWh at site B on 21 Dec [B2, B3] | Hourly sun-path calculation (done); siting survey |
| R4 | Pointing accuracy | Beam center within 0.5° of the target center (about 90 mm at 10 m), with winds up to 8 m/s | **At risk:** 0.30° typical and 0.50° at the 95th percentile, with four-point calibration and the decided preload springs; 1.04° without preload [D5, D6] | Error budget and calibration simulation (done); later spot log |
| R5 | Sensorless tracking | Sun position from time and location only; no sun sensor or camera; axis homing switches and a weather anemometer allowed | Met by design | Design review |
| R6 | Timekeeping | Clock error 60 s or less after 6 months without a network time source | Met: 31.5 s (DS3231, ±2 ppm) [D1] | Datasheet check |
| R7 | Calibration | One person sets up and calibrates from a phone in 30 min or less of hands-on time, spread over one clear day, with no survey instrument (reworded 2026-09-25, HLT-DDR-002 N4) | Met: 19 min hands-on for four points over about 4 h [G1, G2] | Task analysis (done) |
| R8 | Working range | Target distance 3 to 20 m; mirror normal azimuth ±135° about the target direction; elevation of the normal -90° (face-down stow) to +90° | Met mechanically; spot plus 0.5° error fits a 1.0 m window up to 16.8 m [A6, K1] | Geometry check (done) |
| R9 | Wind | Hold R4 up to 8 m/s; survive 35 m/s (126 km/h) gusts in stow without damage | Met: the stowed moment (24.3 N·m, assumed coefficient) is carried by the stow stop and latch, designed for 48.6 N·m, not by the gearbox [E7, E8] | Wind load calculation (done); gearbox and pad data |
| R10 | Safe beam when stowed, faulted or unpowered | Beam directed only at the target or the ground within 3 m of the mast when stowed; during a stow the beam may move only downward, toward the ground (clarified 2026-09-25, HLT-DDR-002 N5); stow face-down within 60 s of a fault or power loss | Met: stow in 23 s on the supercapacitor reserve with 2.1x energy margin, beam moving only downward; latch engages without power [F1, F2, F4] | Calculation (done); later fault test |
| R11 | Electrical safety | Only 12 V DC (SELV) outdoors; electronics enclosure IP65; mains adapter indoors and listed | Met by design | Design review |
| R12 | Outdoor life | Operate from -20 to +45 °C; UV-stable plastics (ASA or better); corrosion-resistant mast; 10-year mirror life with cleaning | Not verifiable at TRL 3 | Materials review; later exposure test |
| R13 | Mass and install | 13 kg or less on the mast top (relaxed from 10 kg, decided by Amish 2026-09-25, HLT-DDR-002 N3); installed by two people with hand tools in 4 h or less | Met, thinly: 12.94 kg on the mast top, 0.06 kg margin on assumed masses [H3]; install time not verifiable at TRL 3 | Mass estimate (done) |
| R14 | Standby power | 3 W or less average from the 12 V supply | Met: 0.60 W [I1] | Power budget (done) |
| R15 | Cost | Parts at or under the $455 value-engineering target (a hypothetical control target; raised from $400 to $430 by Amish on 2026-09-25, then to $455 by a top-up he approved on 2026-09-26) | **Over the value-engineering target by $37:** estimated cost of the constructable design $492 [J1] | Priced BOM (`bom/bom.csv`) |

## Requirements not met, at risk or over the target

- **R15 (cost) over the value-engineering target by $37.** The parts that make the design constructable (HLT-DDR-003) take the estimate from $451 to $492; the target is unchanged, and the design decisions register lists the cost drivers and savings worth trying.

- **R3 (daily energy) at risk.** Site dependent: met at site A with no margin on the solstice, missed at site B.
- **R4 (pointing) at risk.** 0.30° typical, but the 95th percentile of four-point calibration sits at the 0.5° limit; it relies on the decided preload springs against the gearbox's 1° backlash.
- **R12 (outdoor life) not verifiable at TRL 3.**
- **R13 (mass)** is met with only 0.06 kg of margin on assumed gearbox, spring and solenoid masses.

## Assumptions

- Mirror area 0.36 m² (600 x 600 mm), solar-weighted reflectance about 0.93 when clean and 0.95 soiling factor (combined 0.88).
- Double glazing transmits about 75 % of the beam at normal incidence, less at oblique incidence (HLT-CAL-001).
- Luminous efficacy of direct sunlight about 95 lm/W; a utilization factor of 0.4 for sunlight bounced from a light ceiling or a diffuser into a 3 x 4 m room.
- R3 is checked by an hourly clear-sky model at three illustrative sites at 45° N (HLT-CAL-001, section B). The TRL 2 shortcut of six useful hours at a mean DNI of 650 W/m² and a mean cosine factor of 0.80 gives 0.73 kWh and is no longer used.
