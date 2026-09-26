---
doc_id: HLT-DDR-002
title: HelioLite recommendations accepted
project: HelioLite
doc_type: Design decision record
version: "0.2"
status: Draft
date: '2026-09-26'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002); record the TRL 3 review items now decided, what changed in the repo and the items still open
- version: "0.2"
  date: '2026-09-26'
  author: Amish Chadha
  change: Budget top-up to $455 decided by Amish (P1)
---

# 0002: Recommendations accepted

- **Date:** 2026-09-25
- **Status:** accepted for items N1 to N6; items O1 to O3 and P1 remain proposed

## Context

The TRL 3 review (`docs/REVIEW.md`, session 2026-09-25: TRL 3, and HLT-DDR-001, item O4) listed six new items as "Proposed, awaiting Amish", each with a recommendation. On 2026-09-25 Amish wrote: "i accept all your recommendations, go with them across all repos." Every item with a recommendation is therefore decided in favor of that recommendation; where a recommendation named one of several options, that option is the decision. Items without a recommendation stay open. TRL 4 work stays on hold by Amish's instruction, and HelioLite stays at `trl: 3`, `trl_target: 3`.

The ten TRL 2 items (D1 to D10) were already decided in HLT-DDR-001 and are unchanged.

## Decision

*Table 1. Items decided by Amish, 2026-09-25: go with recommendation.*

| # | Item | Decision | What changed in the repo |
| --- | --- | --- | --- |
| N1 | Stowed wind survival (R9) | Option B: stow stops on the yoke that carry the stowed hinge moment in both directions, checked against option C (published stowed coefficients), rather than a larger NMRV040-class gearbox (A) | Because a fixed stop can resist only one direction on an axis that turns into the stow, the stops are a polyurethane stop pad below a steel lug on the torque tube and a sprung latch pawl above it, on a steel bracket on the -X arm, with a 12 V pull solenoid to release the pawl. Designed for twice the assumed stowed moment (48.6 N·m, a coefficient up to 0.30), which is the check against C. Added to `cad/src/model.py` (part 17), BOM line 17 ($20), HLT-PRC-001, HLT-CAL-001 [E7, E8] and drawing HLT-DWG-001 Rev P2. R9 moves from not met (24.3 N·m on a gearbox with a 22 N·m listed maximum) to met on paper |
| N2 | Drive preload (R4) | A spiral preload spring of about 3 N·m on each axis, about $6 for both | Model part 16 (spring cans on the -X trunnion and inside the mast top), BOM line 16 ($6), pointing budget now counts on it. The elevation spring biases the mirror toward stow. R4 stays at risk (0.31° typical, 0.50° at the 95th percentile of calibration) |
| N3 | Mass limit (R13) | Option (a): relax R13 from 10 kg to 13 kg, rather than lighter drives (b) or aluminum arms (c) | HLT-REQ-001 R13 reads 13 kg. With N1 and N2 the mast-top mass is 12.95 kg, so R13 moves from not met (12.5 kg against 10 kg) to met with 0.05 kg margin on assumed masses |
| N4 | R7 wording | "30 min or less of hands-on time, spread over one clear day" | HLT-REQ-001 R7 reworded; R7 moves from at risk to met (19 min hands-on over about 4 h) |
| N5 | R10 wording | During a stow the beam may move only downward, toward the ground | HLT-REQ-001 R10 reworded; R10 moves from at risk to met (stow in 23 s, beam never above -4°) |
| N6 | Calibration points | Four points over about 4 h as the default, within D7's "three or more" | HLT-PRC-001 and HLT-CAL-001 use four points over about 4 h as the default (95th percentile residual 0.23° on the normal) |

Consequences for the budget: the recommendations for N1 and N2 carried no budget figure. Lines 16 and 17 take the BOM from $425 to $451 against the $430 in `project.yaml`, so R15 moves from met to **not met**. `budget_usd` stayed at $430 until P1 below was decided.

Budget top-up to $455: decided by Amish, 2026-09-26 (P1, option a). `budget_usd` $430 to $455; HLT-REQ-001 v0.5 and HLT-CAL-001 v0.3: R15 moves from not met to met ($451, $4 margin).

*Table 2. Items still open (Proposed, awaiting Amish).*

| # | Item | Why it stays open |
| --- | --- | --- |
| O1 | First site and user for the co-design checklist (house, greenhouse or school) | No recommendation was made; co-design partners stay open by Amish's instruction |
| O2 | Local rules on glare and structures at the first site | Depends on O1 |
| O3 | Siting survey of real yards | No recommendation was made |
| P1 | Budget for the $451 BOM (R15) | New. Options: (a) raise `budget_usd` to $455; (b) keep $430 and cut cost elsewhere, for example print the turntable and source a cheaper anemometer; (c) treat the anemometer as optional where a reliable forecast is available. Recommendation: (a), because both additions are safety or accuracy items, as with D4. **Decided by Amish, 2026-09-26: budget top-up to $455 (option a)** |

## Consequences

- HLT-PRB-001 is unchanged. HLT-PRC-001 and HLT-REQ-001 move to v0.4, HLT-CAL-001 to v0.2, drawing HLT-DWG-001 to Rev P2; the model, STEP, STL and media were regenerated.
- Requirement status: 11 met, 1 not met (R15), 2 at risk (R3, R4), 1 not verifiable at TRL 3 (R12). After the 2026-09-26 budget top-up (P1): 12 met, 0 not met, 2 at risk, 1 not verifiable.
- No cross-repo action arises from these items.
- The latch, springs and solenoid are paper design only. Building and testing them (holding moment, pad compliance, latch engagement on a power-loss stow) is TRL 4 work and stays on hold by Amish's instruction.
