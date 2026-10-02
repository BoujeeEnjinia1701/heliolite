---
doc_id: HLT-DEC-001
title: HelioLite design decisions register
project: HelioLite
doc_type: Design decisions register
version: "0.2"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-10-01'
  author: Amish Chadha
  change: Register opened with the constructable design (HLT-DDR-003); budget treated as a value-engineering target
- version: "0.2"
  date: '2026-10-02'
  author: Amish Chadha
  change: "Amish approved the recommendations for all open decisions 1 to 11 on 2026-10-02 (aluminum latch bracket, two-lift head fitting, edge guard, clear lid, glare check before uncovering); moved to decisions made; value engineering savings updated"
---

# HelioLite design decisions register

Every design decision still to be made, and every decision made, in one place. Each decision is argued in full in its decision record under `docs/decisions/`; this register is the index Amish works from. The build plan (`docs/05-build-plan.md`) describes the design as it stands and does not list open decisions.

## Open decisions

None. All open decisions were decided on 2026-10-02.

## To confirm when parts are bought

| # | What to confirm | Why it matters | Source |
| --- | --- | --- | --- |
| 1 | The NMRV030 gearbox's output-face hole pattern (the model assumes four M6 on a 44 mm square), its mass (1.2 kg assumed) and its listed backlash | Sets the holes in the right arm and cap plate; R13 has a 0.06 kg margin, which the aluminum latch bracket and the edge guard decided on 2026-10-02 change; R4 depends on backlash | HLT-DDR-003; HLT-CAL-001 |
| 2 | A 14 mm double output shaft is sold for the chosen azimuth gearbox, and the gearbox's permissible radial load and overturning moment on its output | The yoke's wind moment passes through the azimuth gearbox's output bearings | HLT-DDR-003 |
| 3 | The floor flange's hole circle (105 mm assumed) and that the pipe thread engages fully | Sets the tapped holes in the cap plate | HLT-DDR-003 |
| 4 | The keyed flange hub fits the 14 mm keyed shaft, has a 30 mm boss and a 40 mm screw circle | Sets the turntable disc's holes | HLT-DDR-003 |
| 5 | The release solenoid's stroke (12 mm needed), pull force with its return spring, and mass | The pawl must clear the lug fully | HLT-DDR-003 |
| 6 | The spiral springs give about 3 N·m over the axis travel and fit the 50 mm and 52.5 mm cans | The preload that R4 depends on | HLT-DDR-002, N2 |
| 7 | The ground screw socket fits 60.3 mm pipe and its overturning rating is at least 1.0 kN·m | Mast survival at 35 m/s | HLT-CAL-001 [E4] |
| 8 | A published stowed force and hinge moment coefficient for small heliostats | The latch is designed on an assumed coefficient with a factor of 2 | HLT-CAL-001 [E7] |
| 9 | The polyurethane pad's modulus (50 MPa assumed) | The pad must deflect less than the worm's free travel | HLT-CAL-001 [E8] |
| 10 | The controller box's mounting lugs | Sets the plate's box holes | HLT-DDR-003 |

## Value engineering

Value-engineering target: USD 455 (a hypothetical control target, not a limit). Estimated cost of the constructable design: USD 492 (USD 37 over the target). Main cost drivers and savings worth trying:

- The largest lines are the two drives (azimuth with cap and flange USD 68, elevation USD 52), the controller with its mounting plate (USD 51), the gimbal yoke (USD 38), the backing panel, ribs, tube and trunnions (USD 36), the mast and the ground anchor (USD 35 each), and the turntable stack (USD 28).
- Making the design constructable repriced lines 2, 3, 5, 6, 9, 13, 14 and 17, from USD 451 to USD 492: the floor flange and tapped cap (USD 8), the shaft, hub and thrust washer (USD 13), the controller plate and U-bolts (USD 6), the anemometer clamp (USD 4), more fixings (USD 4), the rib, end block and stub parts (USD 6) and the latch detail (USD 2), partly offset by the aluminum yoke costing less than the printed one (USD 2 less).
- Savings worth trying: buy both gearboxes and motors as one kit (often USD 10 to 15 less than two singles); print the turntable disc in ASA instead of aluminum if a stiffness check allows (about USD 6); a forecast-only storm stow where the forecast is reliable, making the anemometer optional (USD 24, but it weakens R9's backup). The cheaper box without a clear lid is no longer a saving: the clear lid was decided on 2026-10-02. The EPDM edge guard decided the same day adds a few dollars and is not yet priced.

## Decisions made

| Date | Decision | Decided by | Record |
| --- | --- | --- | --- |
| 2026-09-25 | TRL 2 review items D1 to D10: 60.3 mm galvanized steel pipe mast; forecast plus cup anemometer; supercapacitor stow reserve; budget $430; pitch "with no sun sensors"; face-down stow; calibration by jogged spot points; Grena algorithm 5 with weekly network time; listed indoor 12 V adapter; glass mirror with safety backing film | Amish: "proceed with all of your recommendations across all batches. Make sure we don't proceed to TRL 4 on any of them." | HLT-DDR-001 |
| 2026-09-25 | TRL 3 review items N1 to N6: stow stop and latch carrying the stowed moment; spiral preload springs on both axes; R13 relaxed to 13 kg; R7 and R10 reworded; four calibration points over about 4 h | Amish: "i accept all your recommendations, go with them across all repos." | HLT-DDR-002 |
| 2026-09-26 | Budget top-up to $455 for the $451 BOM (P1, option a) | Amish: "I am ok with the budget top ups" | HLT-DDR-002 v0.2 |
| 2026-09-30 | Make the design physically buildable while drawing the build plan | Amish: "If you are realising that the design cannot be built as per concept - fix the design assumptions to match and be physically feasible as you draw the illustrations." | HLT-DDR-003 (its Table 3 items were decided on 2026-10-02, below) |
| 2026-10-01 | `budget_usd` is a hypothetical value-engineering target, not a limit | Amish: "the budgets are a hypothethical control target to ensure we are thinking along a value engineering lens. its ok to ensure wording reflects that the hypothesis budget was x - the real cost being accrued is y" | This register, Value engineering |
| 2026-10-02 | First site and user: a house first, owned by a contributor or someone in the team's network, chosen by the siting check of decision 3 (one mirror spot sees both the winter sun and a north window); schools only after glare safety is shown | Amish: "i approve your recommendations for all 555 open decisions." | HLT-DDR-001, O1 |
| 2026-10-02 | Local rules and glare: before the mirror is uncovered, check the local building and planning rules and do a simple glare study of where the beam can go (neighbours, roads, sky); the beam stays inside the property in every state | Amish: "i approve your recommendations for all 555 open decisions." | HLT-DDR-001, O2 |
| 2026-10-02 | Siting survey: a desk survey of 20 to 30 real yards using satellite images and a sun-path check, scored on whether one mirror spot sees the winter sun and a north window within range, then a visit to the first build site | Amish: "i approve your recommendations for all 555 open decisions." | HLT-DDR-001, O3 |
| 2026-10-02 | Benefit: public copy leads with daylight and treats heat as a bonus until co-design shows otherwise; both questions are asked at the co-design sessions | Amish: "i approve your recommendations for all 555 open decisions." | HLT-PRC-001, open questions |
| 2026-10-02 | R13 mass margin (option b, changed from a): the latch bracket is made in aluminum now (about 0.1 kg saved), and the parts are weighed at TRL 4 | Amish: "i approve your recommendations for all 555 open decisions." | HLT-DDR-003, A1 |
| 2026-10-02 | Head on the mast (option b, changed from a): for the prototype the yoke and drive are fitted at height first and the mirror assembly (about 6.2 kg) is lowered into it, glass covered, from a stable platform rather than steps; a hinged mast base (option c) is looked at before any second build | Amish: "i approve your recommendations for all 555 open decisions." | HLT-DDR-003, A2 |
| 2026-10-02 | Appearance model and renders: updated to the aluminum yoke, the new latch and the rib tunnels, dropping the torque tube saddles | Amish: "i approve your recommendations for all 555 open decisions." | HLT-DDR-003, A3; `docs/REVIEW.md`, 2026-09-26, item 4 |
| 2026-10-02 | Target distance in the product render: the wall stays 1.0 m from the mast as a render-only layout, with the caption saying so | Amish: "i approve your recommendations for all 555 open decisions." | `docs/REVIEW.md`, 2026-09-26, item 1 |
| 2026-10-02 | Mirror edge guard: a black EPDM edge channel round the glass and panel edges is added to the BOM, paired with the aluminum latch bracket of decision 5; if the weighed head still exceeds 13 kg, R13 is relaxed slightly rather than the guard dropped | Amish: "i approve your recommendations for all 555 open decisions." | `docs/REVIEW.md`, 2026-09-26, item 2 |
| 2026-10-02 | Controller lid: an IP65 box with a clear lid is specified on BOM line 9 | Amish: "i approve your recommendations for all 555 open decisions." | `docs/REVIEW.md`, 2026-09-26, item 3 |
| 2026-10-02 | Product finish set (option a), with the yoke in natural aluminum: teal turntable and name plate, silver-grey gearboxes, black motors, galvanized mast and cap, dark anchor | Amish: "i approve your recommendations for all 555 open decisions." | `docs/REVIEW.md`, 2026-09-26, item 5 |
