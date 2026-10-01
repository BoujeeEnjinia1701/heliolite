---
doc_id: HLT-DEC-001
title: HelioLite design decisions register
project: HelioLite
doc_type: Design decisions register
version: "0.1"
status: Draft
date: '2026-10-01'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-10-01'
  author: Amish Chadha
  change: Register opened with the constructable design (HLT-DDR-003); budget treated as a value-engineering target
---

# HelioLite design decisions register

Every design decision still to be made, and every decision made, in one place. Each decision is argued in full in its decision record under `docs/decisions/`; this register is the index Amish works from. The build plan (`docs/05-build-plan.md`) describes the design as it stands and does not list open decisions.

## Open decisions

| # | Decision needed | Options | Recommendation | Affects in the build | Source |
| --- | --- | --- | --- | --- | --- |
| 1 | First site and user for the co-design checklist | A house, a greenhouse or a school | None yet; co-design partners stay open by Amish's instruction | Siting, mast position and target; not the build itself | HLT-DDR-001, O1 |
| 2 | Local rules on glare and structures at that site | Depends on decision 1 | None yet | Whether a permit or a glare study is needed before the mirror is uncovered | HLT-DDR-001, O2 |
| 3 | Siting survey of real yards | How often a mirror can see both the winter sun and a north window | None yet | The site of the first build (R3 depends on siting) | HLT-DDR-001, O3 |
| 4 | Which benefit users value most | Daylight or heat | None yet; ask at the co-design sessions | Not the build; the pitch and the target room | HLT-PRC-001, open questions |
| 5 | R13 mass margin of 0.06 kg on an assumed gearbox mass | (a) accept and weigh the parts at TRL 4; (b) look for more mass now, for example an aluminum latch bracket (about 0.1 kg) | (a) | Latch bracket material | HLT-DDR-003, A1 |
| 6 | How the head goes on the mast | (a) two people on stable steps lift the bench-built head (about 11 kg) onto the shaft, glass covered; (b) fit the yoke at height and lower the mirror into it there; (c) a hinged mast base | (a) for the prototype; (c) worth a look before a second build | Build plan steps 10 to 17 | HLT-DDR-003, A2 |
| 7 | Appearance model and renders for the constructable design | (a) update `cad/src/product_model.py` and the renders on Amish's Mac to the aluminum yoke, the new latch and the rib tunnels, dropping the torque tube saddles; (b) keep the concept renders | (a) | None (renders only) | HLT-DDR-003, A3; REVIEW.md 2026-09-26, item 4 |
| 8 | Target distance in the product render | (a) keep the wall 1.0 m from the mast as a render-only layout, noted in the caption; (b) draw it at a real site distance | (a) | None (renders only) | REVIEW.md 2026-09-26, item 1 |
| 9 | Mirror edge guard | (a) add a black EPDM U-channel round the glass and panel edges (a few dollars, to BOM line 1 or 13); (b) seamed edges only | (a) | Step 5 (fitted after bonding) | REVIEW.md 2026-09-26, item 2 |
| 10 | Clear window in the controller lid | (a) an IP65 box with a clear lid, similar price; (b) an opaque lid | (a) | BOM line 9 specification | REVIEW.md 2026-09-26, item 3 |
| 11 | Product finish set | (a) off-white or natural yoke, teal turntable and name plate, silver-grey gearboxes, black motors, galvanized mast and cap, dark anchor; (b) other | (a), with the yoke now natural aluminum | Paint on the made parts | REVIEW.md 2026-09-26, item 5 |

## To confirm when parts are bought

| # | What to confirm | Why it matters | Source |
| --- | --- | --- | --- |
| 1 | The NMRV030 gearbox's output-face hole pattern (the model assumes four M6 on a 44 mm square), its mass (1.2 kg assumed) and its listed backlash | Sets the holes in the right arm and cap plate; R13 has a 0.06 kg margin; R4 depends on backlash | HLT-DDR-003; HLT-CAL-001 |
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
- Savings worth trying: buy both gearboxes and motors as one kit (often USD 10 to 15 less than two singles); print the turntable disc in ASA instead of aluminum if a stiffness check allows (about USD 6); a forecast-only storm stow where the forecast is reliable, making the anemometer optional (USD 24, but it weakens R9's backup); a cheaper IP65 box without a clear lid (a few dollars).

## Decisions made

| Date | Decision | Decided by | Record |
| --- | --- | --- | --- |
| 2026-09-25 | TRL 2 review items D1 to D10: 60.3 mm galvanized steel pipe mast; forecast plus cup anemometer; supercapacitor stow reserve; budget $430; pitch "with no sun sensors"; face-down stow; calibration by jogged spot points; Grena algorithm 5 with weekly network time; listed indoor 12 V adapter; glass mirror with safety backing film | Amish: "proceed with all of your recommendations across all batches. Make sure we don't proceed to TRL 4 on any of them." | HLT-DDR-001 |
| 2026-09-25 | TRL 3 review items N1 to N6: stow stop and latch carrying the stowed moment; spiral preload springs on both axes; R13 relaxed to 13 kg; R7 and R10 reworded; four calibration points over about 4 h | Amish: "i accept all your recommendations, go with them across all repos." | HLT-DDR-002 |
| 2026-09-26 | Budget top-up to $455 for the $451 BOM (P1, option a) | Amish: "I am ok with the budget top ups" | HLT-DDR-002 v0.2 |
| 2026-09-30 | Make the design physically buildable while drawing the build plan | Amish: "If you are realising that the design cannot be built as per concept - fix the design assumptions to match and be physically feasible as you draw the illustrations." | HLT-DDR-003 (its changes are open for Amish's review) |
| 2026-10-01 | `budget_usd` is a hypothetical value-engineering target, not a limit | Amish: "the budgets are a hypothethical control target to ensure we are thinking along a value engineering lens. its ok to ensure wording reflects that the hypothesis budget was x - the real cost being accrued is y" | This register, Value engineering |
