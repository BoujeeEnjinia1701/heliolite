---
doc_id: HLT-DDR-001
title: HelioLite TRL 2 review decisions
project: HelioLite
doc_type: Design decision record
version: "0.2"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Record Amish's decisions on the TRL 2 review items and the items that remain open
- version: "0.2"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
---

# 0001: TRL 2 review decisions

- **Date:** 2026-09-25
- **Status:** accepted for items D1 to D10; item O4 decided in HLT-DDR-002; items O1 to O3 remain proposed

## Context

The TRL 2 review note (`docs/REVIEW.md`, session 2026-09-25, /populate) listed eleven items as "Proposed, awaiting Amish". Ten carried a recommendation. On 2026-09-25 Amish reviewed the review points for every portfolio repo and wrote: "proceed with all of your recommendations across all batches. Make sure we don't proceed to TRL 4 on any of them." Every item that carried a recommendation is therefore decided in favor of that recommendation. Items without a recommendation stay open.

The same instruction approved portfolio-wide decisions on the SwapCell interface (a wake method for hosts without CAN, a charge-while-discharging mode and a latch vibration rating) and on pricing shared SwapCell packs once. HelioLite runs from a listed indoor 12 V adapter and uses no SwapCell pack, so these do not change this design. The instruction also leaves co-design partners open for community designs; HelioLite's first site and user (O1) stays open accordingly.

## Options considered

The options for each item are those listed in `docs/REVIEW.md` (TRL 2 session) and in HLT-PRC-001 v0.2, Key design choices.

## Decision

*Table 1. Decided items.*

| # | Item | Decision |
| --- | --- | --- |
| D1 | Mast | 60.3 mm (2 in) galvanized steel pipe (Option A), rather than an 80 x 80 mm extrusion or a guyed 40 x 40 mm extrusion. Decided by Amish, 2026-09-25: go with recommendation. |
| D2 | Storm awareness (R9) | Wi-Fi wind forecast plus a low-cost cup anemometer (Options A and B), with the anemometer counted as a weather sensor, not a tracking sensor, and costed in the BOM. Decided by Amish, 2026-09-25: go with recommendation. |
| D3 | Safe state on power loss (R10) | Supercapacitor stow reserve that finishes a face-down stow (Option A). Decided by Amish, 2026-09-25: go with recommendation. |
| D4 | Budget | Raise `budget_usd` from $400 to $430 (option a), because the fixes for R9 and R10 are safety items. Decided by Amish, 2026-09-25: go with recommendation. |
| D5 | Pitch wording | Change "with no sensors" to "with no sun sensors". Decided by Amish, 2026-09-25: go with recommendation. |
| D6 | Stow attitude | Face-down stow at night, on faults and before storms, rather than face-up or edge-on. Decided by Amish, 2026-09-25: go with recommendation. |
| D7 | Calibration | Jog the sun spot onto the target at three or more times of day and fit the mount model, rather than a compass, inclinometer or GPS survey. Decided by Amish, 2026-09-25: go with recommendation. |
| D8 | Sun-position algorithm | Grena algorithm 5 at 30 s updates, NREL SPA as an alternative, with weekly network time when Wi-Fi is available. Decided by Amish, 2026-09-25: go with recommendation. |
| D9 | Power supply | Listed indoor 12 V adapter with only SELV cable outdoors, rather than a solar panel and battery on the mast. Decided by Amish, 2026-09-25: go with recommendation. |
| D10 | Mirror | Glass mirror with a safety backing film, rather than acrylic or aluminum-film mirror. Decided by Amish, 2026-09-25: go with recommendation. |

Notes on the decided items:

- **D4.** `project.yaml` now carries `budget_usd: 430`, and requirement R15 reads "$430 or less". The TRL 3 BOM totals $425 (HLT-CAL-001, section J).
- **D5.** Applied to `project.yaml` and `README.md`. The design uses two axis homing Hall switches and, after D2, an anemometer; neither senses the sun.
- **D7.** HLT-CAL-001 (section D) finds that three points over about 3 h leave a 95th percentile residual of about 0.45° on the mirror normal, and four points over about 4 h about 0.23°. The decision allows "three or more"; four points over about 4 h are used in the pointing budget.

*Table 2. Items that remained open after this record (O1 to O3 still Proposed, awaiting Amish).*

| # | Item | Why it stays open |
| --- | --- | --- |
| O1 | First site and user for the co-design checklist (house, greenhouse or school) | No recommendation was made; needs Amish. Co-design partners stay open by Amish's instruction |
| O2 | Local rules on glare and structures at the first site | Depends on O1 |
| O3 | Siting survey of real yards (how often a mirror can see both the winter sun and a north window) | Listed as an open question with no recommendation |
| O4 | New TRL 3 proposals: stowed wind survival (R9), mass limit (R13), drive preload (R4), calibration time wording (R7), transient beam path in a stow (R10), calibration points | Decided by Amish, 2026-09-25: go with recommendation. Recorded in HLT-DDR-002 (N1 to N6) |

## Consequences

- The BOM gains an anemometer (line 14) and a supercapacitor stow reserve (line 15); the drives become NEMA17 motors on NMRV030-class 50:1 worm gearboxes with a listed rating, so the holding torque question in R9 can be checked.
- HLT-PRB-001, HLT-PRC-001 and HLT-REQ-001 move to v0.3 with these choices recorded as decided.
- TRL 4 work stays on hold by Amish's instruction.
