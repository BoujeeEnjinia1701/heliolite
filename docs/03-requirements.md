---
doc_id: HLT-REQ-001
title: HelioLite requirements
project: HelioLite
doc_type: Requirements
version: "0.2"
status: Draft
date: '2026-09-25'
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
---

# HelioLite requirements

These are first-pass requirements for the concept. Targets are proposals for review, not yet validated with users, and will be checked by calculation at TRL 3. The status column compares each target with the first-order estimates in HLT-PRC-001; "met" means met on paper only.

The **design point** used throughout is a clear winter day at 45° N, DNI 800 W/m², a mirror-to-target distance of 10 m and an angle of incidence on the mirror of about 32° (cosine factor 0.85).

Table 1. Requirements.

| ID | Requirement | Target | Status (estimate) | Verification (TRL 3 or later) |
| --- | --- | --- | --- | --- |
| R1 | Redirected sunlight at the target | 200 W or more arriving at the outside of the target glazing at the design point | Met: about 212 W | Optical calculation |
| R2 | Useful daylight in the room | Raise the mean illuminance of a 12 m² room by 300 lx or more at the design point | Met: about 500 lx (utilization 0.4 assumed) | Illuminance calculation |
| R3 | Daily energy delivered | 0.5 kWh or more through the glazing on a clear winter day | Met: about 0.7 kWh | Hourly sun-path calculation |
| R4 | Pointing accuracy | Beam center within 0.5° of the target center (about 90 mm at 10 m), with winds up to 8 m/s | Met on paper: about 0.34° error budget | Error budget; later spot log |
| R5 | Sensorless tracking | Sun position from time and location only; no sun sensor or camera; axis homing switches allowed | Met by design | Design review |
| R6 | Timekeeping | Clock error 60 s or less after 6 months without a network time source | Met: about 32 s (DS3231, ±2 ppm) | Datasheet check |
| R7 | Calibration | One person sets up and calibrates from a phone in 30 min or less, with no survey instrument | Unverified | Procedure review at TRL 3 |
| R8 | Working range | Target distance 3 to 20 m; mirror normal azimuth ±135° about the target direction; elevation of the normal -90° (face-down stow) to +90° | Met by design; spill rises above 15 m (see HLT-PRC-001) | Geometry check |
| R9 | Wind | Hold R4 up to 8 m/s; survive 35 m/s (126 km/h) gusts in stow without damage | **Not met:** the worm gearboxes' holding torque is unknown and may be below the estimated 40 N·m hinge moment if a storm arrives unstowed | Wind load calculation; gearbox data |
| R10 | Safe beam when stowed, faulted or unpowered | Beam directed only at the target or the ground within 3 m of the mast; stow face-down within 60 s of a fault or power loss | **Not met:** baseline has no stored energy to stow on power loss; a stopped mirror sweeps the beam at about 15°/h | Design review; later fault test |
| R11 | Electrical safety | Only 12 V DC (SELV) outdoors; electronics enclosure IP65; mains adapter indoors and listed | Met by design | Design review |
| R12 | Outdoor life | Operate from -20 to +45 °C; UV-stable plastics (ASA or better); corrosion-resistant mast; 10-year mirror life with cleaning | Unverified | Materials review |
| R13 | Mass and install | 10 kg or less on the mast top; installed by two people with hand tools in 4 h or less | Met: about 8 kg on the mast top | Mass estimate |
| R14 | Standby power | 3 W or less average from the 12 V supply | Met: about 0.6 W | Power budget |
| R15 | Cost | Parts $400 or less | Met, thin margin: about $391 | Priced BOM (`bom/bom.csv`) |

## Requirements not met or at risk

- **R9 (wind survival) not met.** The concept relies on stowing before storms. Without a wind sensor or a network forecast the unit cannot know a storm is coming, and a small NEMA17 worm gearbox may not hold the estimated hinge moment. Options are in HLT-PRC-001.
- **R10 (safe state on power loss) not met.** Worm drives hold the mirror where it stops, and the reflected beam then walks across the surroundings as the sun moves. A small energy store to finish a stow, or a passive cover, is needed.
- **R7 (calibration time) and R12 (outdoor life) unverified.**
- **R15 (cost)** is met with only about $9 of margin.

## Assumptions

- Mirror area 0.36 m² (600 x 600 mm), solar-weighted reflectance about 0.93 when clean and 0.95 soiling factor (combined 0.88).
- Double glazing transmits about 75 % of the beam.
- Luminous efficacy of direct sunlight about 95 lm/W; a utilization factor of 0.4 for sunlight bounced from a light ceiling or a diffuser into a 3 x 4 m room.
- Six useful tracking hours on a clear winter day at a mean DNI of 650 W/m² and a mean cosine factor of 0.80.
