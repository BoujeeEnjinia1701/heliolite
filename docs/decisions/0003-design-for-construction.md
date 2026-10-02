---
doc_id: HLT-DDR-003
title: HelioLite design for construction
project: HelioLite
doc_type: Design decision record
version: "0.2"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-10-01'
  author: Amish Chadha
  change: Changes that make the concept physically buildable, with the reason for each; made under Amish's 2026-09-30 instruction to make the design physically buildable; open for his review
- version: "0.2"
  date: '2026-10-02'
  author: Amish Chadha
  change: "Table 3 items decided by Amish on 2026-10-02: A1 aluminum latch bracket (changed), A2 two-lift head fitting from a platform (changed), A3 renders updated; Table 1 acceptance still to be put to Amish"
---

# 0003: Design for construction

- **Date:** 2026-10-01
- **Status:** draft. The changes in Table 1 were made under Amish's 2026-09-30 instruction to make the design physically buildable. The items in Table 3 were decided by Amish on 2026-10-02 ("i approve your recommendations for all 555 open decisions."), A1 and A2 on changed recommendations, and are recorded in the design decisions register (`docs/06-design-decisions.md`, HLT-DEC-001). Acceptance of Table 1 as a whole was not among the open decisions and is still to be put to Amish.

## Context

On 2026-09-30 Amish asked for a build plan that shows how each component is made and how it fits the next, with pictures, and wrote: "If you are realising that the design cannot be built as per concept - fix the design assumptions to match and be physically feasible as you draw the illustrations." The TRL 3 model of HLT-DDR-002 showed what HelioLite does, but it was a massing model: some parts overlapped, some floated with no fixing, one could not be made by its stated process, and the trunnion could not be fitted once the mirror was in the yoke. Checking the model with build123d (intersections, distances and an elevation sweep from stow to face-up) found the fourteen problems in Table 1.

The changes keep what HelioLite does: the same 600 x 600 mm mirror, elevation axis 2.2 m up, arm spacing and mirror clearances, the same drives, mast, anchor, controller, anemometer, preload springs and stow latch, the same face-down stow and the same pitch. Nothing here changes the safety case. Every change is in `cad/src/model.py`, which now builds each part separately and runs 1,583 constructability checks (`python cad/src/model.py --check`): parts that must touch do touch, parts that must stay apart keep their stated gap, no two parts overlap, and the mirror, tube and lug clear the yoke and latch at every elevation from -90 to +90 degrees in 15 degree steps. All pass.

## Decision

*Table 1. Changes made to the model, the BOM and the calculations.*

| # | Problem in the concept | Change made | Why this way |
| --- | --- | --- | --- |
| P1 | The two 25 x 20 mm rib tubes crossed the 25 mm torque tube in the same space: each overlapped the tube by 25 x 25 x 20 mm, so neither could be made as drawn. | Ribs are 25 x 40 x 1.5 mm aluminum tube, each with a 25.5 mm square tunnel cut at mid-length from the panel face. The torque tube slides through both tunnels and touches the panel; all three are bonded to the panel with structural silicone. | Keeps the elevation axis where the concept put it, so the mirror's balance (center of mass 12.4 mm in front of the axis, was 13.7 mm) and the preload check are unchanged in substance. A square tube in a square tunnel passes the hinge moment into the ribs by bearing, not through the silicone alone. |
| P2 | One 14 mm trunnion rod ran through the 21 mm bore of the square tube with nothing holding it, and it could not be fitted once the mirror was between the arms. | Two aluminum end blocks (21 x 21 x 60 mm, bored 14 mm) bolted into the tube ends with two M6 bolts each; two separate 14 mm keyed steel stubs (148 mm drive side, 108 mm spring side) slid in through the bushes after the mirror is in the yoke and held by a 5 mm roll pin through tube, block and stub. | The mirror can be lowered into the yoke first and the stubs fitted from outside. The pin and the square block carry the drive torque into the tube. |
| P3 | The one-piece printed ASA yoke (base plate, 720 mm crossbar and two arms about 440 mm tall) cannot be printed: the crossbar is twice the bed of common printers and the arms do not fit a 350 mm bed even diagonally. | An aluminum frame from one stock size, 60 x 40 x 2 mm rectangular tube: a 720 mm crossbar and two 397 mm arms standing on its ends, each foot clamped by two 3 mm aluminum gusset plates and four M6 bolts with crush sleeves. A printed ASA bearing plug fills the top 75 mm of each arm. The printed base plate is gone; the crossbar bolts straight to the turntable. | Buildable from stock with a saw and drill. Arm positions, the 20 mm arm gap and the mirror sweep are unchanged; the crossbar gap grows from 46 to 56 mm. The aluminum arms are stiffer (arm flex 0.006 degrees at 8 m/s, was 0.040) and the yoke is lighter (2.27 kg, was 2.72 kg). Printed parts stay where printing suits them: the plugs, spring cans and Hall post. |
| P4 | The two 14 mm bearings had no housing; the trunnion passed through a solid arm. | A flanged bronze bush 14 x 18 x 40 mm through each arm and its plug, flange on the inside. The torque tube ends rest against the flanges, which locate the mirror sideways. | A bush suits a slow, oscillating axis and fits a reamed 18 mm hole; the flange gives end float control for free. |
| P5 | The elevation gearbox hung beside the +X arm with no fixing. | Its output face bolts flat to the arm's outer side with four M6 bolts through the arm and plug into the gearbox's tapped holes; the keyed drive stub runs through its hollow bore. | The gearbox body is held against its own reaction torque, and the plug stops the bolts crushing the tube. |
| P6 | The elevation spring can stood 5 mm off the -X arm and the trunnion stopped short of it. | The printed can screws to the arm's outer side with three M4 screws; the spring stub reaches into it, and the spiral spring's inner end sits in a slot across the stub's end. | The spring now acts between the arm and the mirror, as the preload decision (HLT-DDR-002 N2) needs. |
| P7 | The turntable sat directly on the azimuth gearbox with no shaft, no bearing and no fixing; the azimuth spring can inside the mast had nothing to turn it. | A bought double output shaft (14 mm, keyed) passes through the gearbox and the cap plate into the spring can in the pipe. On top: a bronze thrust washer, a keyed aluminum flange hub and a 120 x 10 mm aluminum disc (was a 150 x 20 mm disc), held by four countersunk M5 screws. The crossbar bolts to the disc with four M6 bolts. | Every part in the stack is now fixed and the stack height is unchanged (20 mm), so the elevation axis stays at 2.2 m. The smaller disc saves mass for P1 to P9. |
| P8 | The cap plate was "welded or bolted to a pipe socket", with neither shown. | A bought 2 in threaded floor flange screws onto the threaded pipe top; four M8 screws go up through the flange into tapped holes in the 8 mm cap. The gearbox is held by four countersunk M6 screws from under the cap, fitted before the cap goes on the flange. | No welding. The cap's top stays flat under the gearbox, so no screw head clashes with it. |
| P9 | The stow latch could not work as drawn: the lug floated 2.5 mm off the tube with no fixing; the pawl lifted upward but sat inside the lug's swing, so lifting it could never let the lug out; the bracket reached 55 mm past the arm's front face with 10 mm on the arm and nothing under the stop pad; its back wall stood inside the swing of the lug's corners (76 mm radius); the solenoid floated 2 mm from it. | Lug: an 8 mm steel collar that slides on the tube's left end with an M5 set screw, and its tongue. Bracket: 4 mm steel bent into a leg and a flange, clear of the turning tube end by a 21 mm radius bite and of the lug's corners (flange 79 mm from the axis), held to the arm and plug by two M6 countersunk screws; a steel stop block screwed under the pad. Pawl: a 12 x 8 mm steel bar that slides sideways 12 mm in a slot in the leg, pushed out by the solenoid's return spring and pulled back by the coil; its chamfered tip lets the lug push it aside on the way into stow. Solenoid: on a strap screwed to the leg's outer face, beside the arm. | Keeps the decided function (HLT-DDR-002 N1): the lug is trapped between the pad and the pawl in both directions, the latch engages with no power and the solenoid releases it. A sideways pawl can leave the lug's swing; a lifting one cannot. Pawl bending 90 MPa and bracket screw load 1.2 kN at the 48.6 N·m design moment (HLT-CAL-001 [E8]). |
| P10 | The homing switches sensed nothing: the azimuth switch sat 48 mm under the turntable, and the elevation switch sat 190 mm from the axis, where no moving part passes. | Azimuth: the switch on a printed post on the cap, 4 mm under a magnet set in the disc. Elevation: the switch on the left arm's inner side, 6 mm from a magnet set in the lug's tongue. Home is azimuth zero and elevation zero (mirror upright). | Each switch now sees a magnet once per turn of its axis. |
| P11 | The controller box floated 5 mm off the mast with no fixing. | A 3 mm aluminum plate on the box's back and two 2 in U-bolts round the mast; the box stands 3 mm off the pipe. | Standard pole mounting; no holes in the mast. |
| P12 | The anemometer arm touched the mast at a single point. | A bought right-angle pipe clamp (60.3 mm to 20 mm) holds the 20 mm arm to the mast. | Standard part; the height and reach stay at 1.5 m and 550 mm. |
| P13 | The cable ran through the anchor flange and, after P8, through the floor flange; no cable reached the turning yoke, which carries the elevation motor, Hall switch and solenoid. | The feed leaves the mast 30 mm above the anchor flange; the riser steps out round the floor flange and cap; a service loop runs from beside the azimuth motor to the crossbar and along its top. | The loop takes the decided azimuth travel of plus or minus 135 degrees without a slip ring. |
| P14 | The mast pipe sat loose in the anchor socket. | Two M10 set bolts through the socket wall. | Usual practice with ground screw sockets; makes the mast plumb and stops it turning. |

*Table 2. Knock-on changes.*

| Item | Change | Reason |
| --- | --- | --- |
| Mass | 12.94 kg on the mast top against the 13 kg limit of R13 (0.06 kg margin, was 0.05 kg) [H3]. Mirror assembly 6.18 kg, yoke 2.27 kg, turntable stack 0.51 kg, latch 0.43 kg. | P1 to P14 add ribs, end blocks, bushes, bolts, a shaft and a hub; the aluminum yoke, the smaller disc, an aluminum hub and compact gussets take it back. |
| Pointing | Arm flex 0.006 degrees (was 0.040); root sum square 0.148 degrees on the normal and 0.30 degrees on the beam (was 0.153 and 0.31); 0.50 degrees at the 95th percentile of calibration, unchanged [C4, D5]. R4 stays at risk. | P3. |
| Wind and latch | Unchanged loads; the pawl and bracket screws checked at the 48.6 N·m design moment [E8]. | P9. |
| Cost | BOM lines 2, 3, 5, 6, 9, 13, 14 and 17 repriced. Value-engineering target: USD 455. Estimated cost of the constructable design: USD 492 (USD 37 over the target) [J1]. | Parts added for construction. `budget_usd` is a hypothetical control target and is unchanged; the design decisions register lists the cost drivers and savings worth trying. |
| Drawing | HLT-DWG-001 Rev P4; making sketches HLT-DWG-101 to 115 added. | Follows the model. |
| Documents | HLT-CAL-001 v0.4, HLT-PRC-001 v0.6, HLT-REQ-001 v0.6. R13 stays met (0.06 kg margin); R15 is reported against the value-engineering target, USD 37 over it. | Follows the model. |

*Table 3. Proposed, then decided by Amish on 2026-10-02.*

| # | Question | Options | Recommendation |
| --- | --- | --- | --- |
| A1 | The R13 mass margin is now 0.06 kg, on an assumed gearbox mass of 1.2 kg each. | (a) accept and weigh the parts at TRL 4; (b) look for more mass now (for example an aluminum latch bracket, about 0.1 kg). | (a). Decided 2026-10-02 on a changed recommendation: (b), the aluminum latch bracket now (about 0.1 kg), with the parts weighed at TRL 4; the EPDM edge guard decided the same day uses up most of the saving. |
| A2 | How the head goes on the mast. The plan builds the head (yoke, mirror, drive and latch, about 11 kg with the turntable disc) on the bench and lifts it onto the azimuth shaft at 1.8 m. | (a) two people on stable steps lift the head on, glass covered; (b) fit the yoke at height and lower the mirror assembly into it there; (c) a hinged mast base so the head is fitted at waist height. | (a) for the prototype, with the mirror covered; (c) is worth a look before any second build. Decided 2026-10-02 on a changed recommendation: (b) for the prototype, the yoke and drive fitted at height first and the mirror assembly (about 6.2 kg) lowered into it, glass covered, from a stable platform rather than steps; (c) looked at before any second build. |
| A3 | The appearance model (`cad/src/product_model.py`) and the photoreal renders still show the printed yoke, the concept latch and two bolted torque tube saddles (render item 4 of 2026-09-26), which P1 replaces. | (a) update the appearance model to the constructable design on Amish's Mac; (b) keep the concept renders as they are. | (a), and drop the saddles. Decided 2026-10-02. |

## Consequences

- `design_state: constructable` in `project.yaml`. The build plan HLT-BLD-001 shows every component and step in pictures generated from the model (`cad/src/build_plan_media.py`).
- Requirement status: none not met, R15 over the value-engineering target by USD 37, 2 at risk (R3, R4), 11 met on paper, 1 not verifiable at TRL 3 (HLT-CAL-001 v0.4).
- The photoreal renders (`media/render-*.png`), `media/card.png` and `media/social-preview.png` still show the concept yoke and latch; they are stale until regenerated on Amish's Mac, where Blender is.
- The gearbox bolt pattern, the double output shaft, the floor flange holes, the solenoid stroke and the spring torque are chosen when parts are bought (TRL 4); the design decisions register lists what to confirm then.
- With A1 and A2 decided, the latch bracket becomes aluminum and the head goes on the mast in two lifts from a stable platform; the model, the latch making sketch, the build plan steps 10 to 17 and their pictures, the BOM and the mass estimate are still to be changed to match (follow-up actions in `docs/REVIEW.md`, 2026-10-02).
- TRL 4 work (building and testing) stays on hold by Amish's instruction.
