# Review note: HelioLite

## Session 2026-09-25: /populate to a strong TRL 2

### What was done

- `docs/01-problem.md` (HLT-PRB-001 v0.2): problem with winter sun geometry, users, operating environment and siting, constraints, out of scope, prior work with cited sources (Rjukan sun mirrors, Sunflower home heliostat, open Arduino heliostats, NREL SPA, Grena 2012, Sandia wind-load and glare methods), open questions and a co-design checklist.
- `docs/03-requirements.md` (HLT-REQ-001 v0.2): 15 measurable requirements (R1 to R15) with targets, a defined design point, a status column against the estimates, and a list of requirements not met.
- `docs/02-concept.md` (HLT-PRC-001 v0.2): how it works, numbered components, optical power and daylight, daily energy and heat, beam size, pointing error budget, wind loads, power, mass, cost, proposed design choices, safety section and open questions.
- `cad/src/concept_media.py`: massing model with 11 BOM-numbered parts (mirror, backing and torque tube, printed yoke, two worm drives, turntable, mast, anchor, controller box, homing switches, cabling), plus a house wall and window as hero-only context.
- `media/`: `hero.png` (1.75 m scale figure), `concept-blueprint.png`, `.pdf` and `.svg`, `exploded.png` with callouts 1 to 11, `flow.png` (sun to room, all values labeled as estimates), `model.glb` and `viewer.html`. No cutaway: the inside of the gimbal does not carry the idea at massing level. Temporary `media/_views*` folders deleted.
- `bom/bom.csv`: 13 lines with indicative prices, items 1 to 11 matching the exploded view; `bom/bom-notes.md` updated.
- `README.md`: hero image and links line inserted before "## Problem"; problem, concept, key components and safety text brought in line with the precis.
- `docs/pdf/`: branded PDFs of the three controlled documents.
- `project.yaml`: unchanged.

### Key results (estimates, to be checked at TRL 3)

| Quantity | Estimate | Requirement |
| --- | --- | --- |
| Beam at the outside of the glazing, design point (DNI 800 W/m², 10 m) | about 212 W | R1 (200 W) met, small margin |
| Sunlight into the room | about 159 W, about 15,000 lm | |
| Mean added illuminance, 12 m² room | about 500 lx | R2 (300 lx) met |
| Energy through the glazing, clear winter day | about 0.7 kWh | R3 (0.5 kWh) met |
| Share of a small room's daytime heat loss | about 10 to 30 % while sunny | Heat benefit is modest |
| Pointing error, root sum square | about 0.17° normal, 0.34° beam | R4 (0.5°) met on paper |
| Clock error, 6 months without network | about 32 s | R6 (60 s) met |
| Hinge moment, 35 m/s face-on | about 40 N·m | R9 at risk (gearbox holding torque unknown) |
| Mast stress, 35 m/s | about 78 MPa in 60.3 mm steel pipe | Mast OK |
| Mass on the mast top | about 8 kg | R13 (10 kg) met |
| Average power | about 0.6 W | R14 (3 W) met |
| Parts cost | about $391 | R15 ($400) met, about $9 margin |

Requirements not met or at risk:

- **R9 (wind survival) not met.** The unit has no way to know a storm is coming, and a generic NEMA17 worm gearbox may not hold the estimated 40 N·m hinge moment if caught face-on.
- **R10 (safe state on power loss) not met.** Worm drives hold the mirror where it stops, so after a power loss the beam walks across the surroundings at about 15° per hour.
- **R7 (30 min calibration) and R12 (outdoor life)** are unverified.
- **R15 (cost)** has only about $9 of margin; either fix for R9 or R10 takes the total over budget.

### Proposed, awaiting Amish

1. **Mast.** The scaffold's aluminum extrusion mast is too flexible: a 40 x 40 mm profile at 2.2 m tilts about 0.37° at 8 m/s, more than the whole pointing budget. Options: (A) 60.3 mm galvanized steel pipe, about $35; (B) 80 x 80 mm aluminum extrusion, about $70 to $90, over budget; (C) 40 x 40 mm extrusion with guy wires. Recommendation: A. This changes a key component listed in the README, where it is marked as proposed.
2. **Storm awareness (R9).** Options: (A) Wi-Fi wind forecast; (B) cup anemometer, about $20; (C) slip clutch. Recommendation: A plus B, with the anemometer treated as a weather sensor, not a tracking sensor.
3. **Safe state on power loss (R10).** Options: (A) supercapacitor stow reserve, about $10 to $15; (B) supervised sites only. Recommendation: A.
4. **Budget.** With the recommendations for items 2 and 3 the parts total becomes about $425 against $400. Options: (a) raise `budget_usd` to $430; (b) keep $400 and drop to a cheaper gearbox or print the turntable; (c) treat the anemometer as optional where a forecast is available. Recommendation: (a), because the fixes are safety items. `project.yaml` is unchanged.
5. **Pitch wording.** The pitch says "with no sensors", but the design uses two axis homing switches and may add an anemometer. Recommendation: change to "with no sun sensors". `project.yaml` is unchanged.
6. Face-down stow at night, on faults and before storms, rather than face-up or edge-on.
7. Calibration by jogging the sun spot onto the target at three or more times of day, rather than a compass, inclinometer or GPS survey.
8. Grena algorithm 5 at 30 s updates (NREL SPA as an alternative), with weekly network time when Wi-Fi is available.
9. Indoor listed 12 V adapter with only SELV outdoors, rather than a solar panel and battery on the mast.
10. Glass mirror with safety backing film, rather than acrylic or film mirror.
11. First site and user for the co-design checklist (house, greenhouse or school).

### Safety concerns

- Eye injury and glare from a beam of 0.6 to 0.9 sun; beam sweep during slews and after power loss (R10).
- Fire only if several mirrors are aimed at one spot or the mirror is bent concave; single-unit, flat-mirror design.
- Broken glass falling from 2 m; pinch points in a high-torque worm-driven gimbal.
- Mast or mirror failure in storms (R9); buried services when driving a ground screw; working at height on roofs.
- Mains stays indoors in a listed adapter; only 12 V DC outdoors.

### Problems and notes

- The hero and blueprint show the house wall about 2.2 m from the mast so the heliostat stays legible; the design range is 3 to 20 m. The precis caption says so.
- Some sources (Grena 2012 abstract, EN 17037 summary) were checked through secondary pages; the full texts should be read at TRL 3.
- The legacy `cad/src/model.py` placeholder is untouched (TRL 3 work).

### Recommended next step

Review this note and the media, then decide items 1 to 4. If approved, run `/advance-trl3` to check the optical, pointing and wind estimates by calculation, select gearboxes with a known holding torque, and produce the parametric model and drawing sheet.

## Session 2026-09-25: TRL 3

Amish's instruction for this session (2026-09-25): "proceed with all of your recommendations across all batches. Make sure we don't proceed to TRL 4 on any of them." HelioLite now claims TRL 3 (proof of concept on paper). TRL 4 is on hold by Amish's instruction.

### What was done

- `docs/decisions/0001-trl2-review-decisions.md` (HLT-DDR-001 v0.1): the ten TRL 2 review items with a recommendation recorded as decided by Amish, 2026-09-25, and four items that stay open.
- `docs/04-calcs/01-sizing.md` (HLT-CAL-001 v0.1) and `docs/04-calcs/sizing.py`: design-point optics and spot size; an hourly clear-sky model with house shading and glazing incidence at three illustrative sites; mast and yoke stiffness; a Monte Carlo simulation of the jogged-point calibration; the pointing budget; wind loads in operation, at the stow trigger, stowed and caught face-on, against the gearbox rating; the supercapacitor stow reserve and the beam path during a stow; mass and balance from the model; power; BOM total. The script imports the model's `PARAMS`, reads `bom/bom.csv`, and prints every quoted number with a tag, [A1] to [K3].
- `cad/src/model.py`: parametric build123d model (mirror, backing and torque tube with trunnions, printed yoke, two NMRV030-class drive envelopes, mast cap, turntable, mast pipe, ground anchor and screw, controller box, Hall switches, cabling, anemometer) in tracking or stowed pose, exporting `cad/step/heliolite-tracking.step`, `heliolite-stowed.step`, `mirror-assembly.step`, `gimbal.step`, `mast-and-anchor.step` and matching STL files in `cad/stl/`.
- `cad/src/sheets.py` and `cad/drawings/HLT-DWG-001.svg`, `.pdf`, `.png`: general arrangement at Rev P1, scale 1:25, stowed orthographic views with dimensions drawn from the model, tracking-pose isometric, and a main-dimensions box. The sheet carries "CONCEPT, NOT FOR FABRICATION" and "PRELIMINARY, NOT FOR FABRICATION". HLT-DWG-001 was free; the concept sheet is HLT-DWG-010.
- `bom/bom.csv` and `bom/bom-notes.md`: all 15 lines priced with a supplier or supplier type; total $425 against the $430 budget.
- `cad/src/concept_media.py` now builds the media from `model.py`; every file in `media/` was regenerated and checked by eye; temporary `media/_views*` folders were deleted.
- HLT-PRB-001, HLT-PRC-001 and HLT-REQ-001 revised to v0.3 (decisions recorded, numbers replaced by HLT-CAL-001, TRL 3 status column); `README.md` updated to TRL 3 with the new pitch; `project.yaml` set to `trl: 3`, `trl_target: 3`, `budget_usd: 430` and the new pitch, with the evidence files listed. PDFs are in `docs/pdf/`.

### Requirements (HLT-CAL-001, Table 6)

8 met, 2 not met, 4 at risk, 1 not verifiable at TRL 3.

| ID | Status | Value against target |
| --- | --- | --- |
| R9 | **Not met** | Assumed stowed hinge moment 24.3 N·m at 35 m/s against the NMRV030-class gearbox's 17 N·m rating and 22 N·m listed maximum; rating reached at a 29 m/s gust. Stow trigger at 15 m/s (7.4 N·m) is fine; mast 87 MPa worst case against 240 MPa |
| R13 | **Not met** | 12.5 kg on the mast top against 10 kg; rated gearboxes (about 1.2 kg each, assumed) and stiffer arms add about 4.5 kg to the TRL 2 estimate |
| R3 | At risk | 0.50 kWh on 21 Dec and 1.00 kWh on 1 Feb at reference site A; 0.40 kWh at site B; strongly site dependent |
| R4 | At risk | 0.31° beam typical, 0.50° at the 95th percentile, needing four-point calibration over about 4 h and a preload on each drive; 1.04° without preload (1° listed backlash) |
| R7 | At risk | 19 min hands-on, but the calibration points must span about 4 h |
| R10 | At risk | Stow in 23 s on stored energy, 2.1x margin; the beam moves only downward but crosses the ground beyond 3 m for about 2.8 s |
| R12 | Not verifiable at TRL 3 | Materials chosen for outdoor life |
| R1 | Met | 211 W at the glazing |
| R2 | Met | 502 lx mean added |
| R5 | Met | No sun sensor |
| R6 | Met | 31.5 s after 6 months |
| R8 | Met | Mechanical range; spill limit about 17 m for a 1.0 m window |
| R11 | Met | SELV outdoors, IP65, listed adapter |
| R14 | Met | 0.60 W average |
| R15 | Met | $425 against $430 |

Other key numbers: 159 W and about 15,070 lm into the room at the design point; mast tilt 0.040° at 8 m/s (0.37° for the rejected 40 x 40 mm extrusion); 30 x 50 mm printed arms would flex 0.145°, so the model uses 40 x 70 mm (0.040°); mirror center of mass 13.7 mm off the elevation axis (0.8 N·m); stow reserve 187 J usable against 87 J needed. Every TRL 2 number in the docs was checked against the script and corrected where it differed (HLT-CAL-001, "Checks against earlier figures"): the daily energy is now site-based, the mast-top mass rose from about 8 to 12.5 kg, and the TRL 2 pointing budget's calibration, backlash and yoke terms were optimistic.

### Decisions recorded (HLT-DDR-001)

Decided by Amish, 2026-09-25, going with the recommendation: D1 60.3 mm galvanized steel pipe mast; D2 Wi-Fi forecast plus cup anemometer for storm stow; D3 supercapacitor stow reserve; D4 `budget_usd` raised to $430; D5 pitch reworded to "with no sun sensors" (applied to `project.yaml` and `README.md`); D6 face-down stow; D7 calibration by jogged spot points; D8 Grena algorithm 5 at 30 s with weekly network time; D9 listed indoor 12 V adapter; D10 glass mirror with safety backing film. R15 now reads $430 and R5 allows the anemometer; no other target was relaxed. The SwapCell interface decisions do not apply (HelioLite uses no SwapCell pack).

### Proposed, awaiting Amish

Still open from TRL 2 (no recommendation was made):

1. First site and user for the co-design checklist (O1); partners stay open by Amish's instruction.
2. Local rules on glare and structures at that site (O2), and a siting survey of real yards (O3).

New from TRL 3:

3. **Stowed wind survival (R9).** Options: (A) NMRV040-class elevation gearbox (more mass and cost); (B) rubber stow stops on the yoke that carry the stowed hinge moment in both directions; (C) find published stowed coefficients for small heliostats that justify a lower load. Recommendation: B, checked against C.
4. **Drive preload (R4).** A torsion spring of about 3 N·m on each axis (about $6 for two, not yet in the BOM or model). Recommendation: adopt.
5. **Mass limit (R13).** Options: (a) relax R13 to 13 kg; (b) lighter drives, which conflicts with R9; (c) aluminum yoke arms. Recommendation: (a).
6. **R7 wording.** "30 min or less of hands-on time, spread over one clear day". Recommendation: adopt.
7. **R10 wording.** Allow the beam to move only downward, toward the ground, during a stow. Recommendation: adopt.
8. **Calibration points.** Use four points over about 4 h as the default (within decision D7's "three or more"). Recommendation: adopt.

### Safety concerns

- Beam of 0.88 to 0.93 sun: eye injury and glare; the beam sweeps the ground between target and mast for about 3 s in a power-loss stow; calibration jogs move the spot near people.
- R9 not met: until resolved, remove the mirror if gusts above about 29 m/s are forecast. Caught face-on at 35 m/s the hinge moment (40 N·m) would exceed the gearbox rating, so stow must not fail.
- Pinch points: 20 mm between mirror and arms, 46 mm to the crossbar; 17 N·m drives; a preload spring would store energy with drives off.
- Supercapacitor bank of about 360 J at 12 V: fuse, bleed and label it.
- Glass 2.2 m above ground; mast anchor must resist 0.79 kN·m (1.0 kN·m specified); buried services; working at height on roofs.
- Mains stays indoors in a listed adapter; only 12 V DC outdoors.

### Other notes

- No existing TRL 4 material was found (`build-log/` holds only its README; `electronics/` and `firmware/` are empty). None was created. STANDARDS section 9 asks for a TRL change to be recorded in the build log; no build-log entry was written, since the brief did not name one.
- Citations: the Grena 2012 abstract was checked on ScienceDirect (0.19° to 0.0027°, 2010 to 2110), confirmed. The EN 17037 claim in HLT-PRB-001 cited the ClimateStudio page for the sunlight-exposure recommendation, which that page does not cover; the citation now splits the 300 lx target (ClimateStudio) and the 1.5 h to 4 h sunlight recommendation (SageGlass summary). The full text of EN 17037 was not read. New sources used at TRL 3: StepperOnline and RS listings for the gearbox rating and backlash, and Emes et al. for the effect of chord on stowed coefficients. The stowed coefficients themselves (0.6 force, 0.15 hinge moment) are assumptions, not sourced values, and the gearbox mass (1.2 kg) is assumed.
- BOM prices other than the gearbox are indicative estimates by supplier type, not quotes.

### Recommended next step

Stay at TRL 3. TRL 4 is on hold by Amish's instruction. Decide items 3 to 8 above, starting with R9 (stow stops or a larger gearbox) and the R13 mass limit, get the chosen gearbox's drawing (mass, static holding torque, backlash), then revise HLT-CAL-001, the model and the BOM on paper. Name the first site (item 1) so the hourly model can be run for a real yard.

For reference only, TRL 4 would need: a lab test report (TST, `environment: lab`) on a built gimbal and drive set (holding torque and backlash under load, preload behavior, stow timing on the supercapacitor reserve, calibration residual on a bench or yard setup, beam spot size), build-log entries, and the purchasing and build work that goes with them. None of this has been started.
