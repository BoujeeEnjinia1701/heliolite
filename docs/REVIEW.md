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

1. **Mast.** The scaffold's aluminum extrusion mast is too flexible: a 40 x 40 mm profile at 2.2 m tilts about 0.37° at 8 m/s, more than the whole pointing budget. Options: (A) 60.3 mm galvanized steel pipe, about $35; (B) 80 x 80 mm aluminum extrusion, about $70 to $90, over budget; (C) 40 x 40 mm extrusion with guy wires. Recommendation: A. This changes a key component listed in the README, where it is marked as proposed. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-001 D1).
2. **Storm awareness (R9).** Options: (A) Wi-Fi wind forecast; (B) cup anemometer, about $20; (C) slip clutch. Recommendation: A plus B, with the anemometer treated as a weather sensor, not a tracking sensor. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-001 D2).
3. **Safe state on power loss (R10).** Options: (A) supercapacitor stow reserve, about $10 to $15; (B) supervised sites only. Recommendation: A. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-001 D3).
4. **Budget.** With the recommendations for items 2 and 3 the parts total becomes about $425 against $400. Options: (a) raise `budget_usd` to $430; (b) keep $400 and drop to a cheaper gearbox or print the turntable; (c) treat the anemometer as optional where a forecast is available. Recommendation: (a), because the fixes are safety items. `project.yaml` is unchanged. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-001 D4).
5. **Pitch wording.** The pitch says "with no sensors", but the design uses two axis homing switches and may add an anemometer. Recommendation: change to "with no sun sensors". `project.yaml` is unchanged. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-001 D5).
6. Face-down stow at night, on faults and before storms, rather than face-up or edge-on. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-001 D6).
7. Calibration by jogging the sun spot onto the target at three or more times of day, rather than a compass, inclinometer or GPS survey. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-001 D7).
8. Grena algorithm 5 at 30 s updates (NREL SPA as an alternative), with weekly network time when Wi-Fi is available. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-001 D8).
9. Indoor listed 12 V adapter with only SELV outdoors, rather than a solar panel and battery on the mast. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-001 D9).
10. Glass mirror with safety backing film, rather than acrylic or film mirror. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-001 D10).
11. First site and user for the co-design checklist (house, greenhouse or school). No recommendation; stays Proposed, awaiting Amish.

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

3. **Stowed wind survival (R9).** Options: (A) NMRV040-class elevation gearbox (more mass and cost); (B) rubber stow stops on the yoke that carry the stowed hinge moment in both directions; (C) find published stowed coefficients for small heliostats that justify a lower load. Recommendation: B, checked against C. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-002 N1).
4. **Drive preload (R4).** A torsion spring of about 3 N·m on each axis (about $6 for two, not yet in the BOM or model). Recommendation: adopt. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-002 N2).
5. **Mass limit (R13).** Options: (a) relax R13 to 13 kg; (b) lighter drives, which conflicts with R9; (c) aluminum yoke arms. Recommendation: (a). **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-002 N3).
6. **R7 wording.** "30 min or less of hands-on time, spread over one clear day". Recommendation: adopt. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-002 N4).
7. **R10 wording.** Allow the beam to move only downward, toward the ground, during a stow. Recommendation: adopt. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-002 N5).
8. **Calibration points.** Use four points over about 4 h as the default (within decision D7's "three or more"). Recommendation: adopt. **Decided by Amish, 2026-09-25: go with recommendation** (HLT-DDR-002 N6).

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

## Session 2026-09-25: recommendations accepted

Amish's instruction (2026-09-25, in chat): "i accept all your recommendations, go with them across all repos." Every open item with a recommendation is now decided by Amish, 2026-09-25: go with recommendation. Items without a recommendation stay open. TRL 4 remains on hold.

### Decisions applied and what changed

Recorded in `docs/decisions/0002-recommendations-accepted.md` (HLT-DDR-002 v0.1). HLT-DDR-001 moves to v0.2 (O4 marked decided).

| # | Decision | Before | After |
| --- | --- | --- | --- |
| N1 | Stow stops on the yoke carrying the stowed moment in both directions (option B, checked against C) | R9 not met: 24.3 N·m stowed moment on a gearbox rated 17 N·m, 22 N·m listed maximum | Steel lug on the torque tube trapped between a 3 mm polyurethane stop pad and a sprung latch pawl on the -X arm, released by a 12 V pull solenoid; designed for 48.6 N·m (2x, a coefficient up to 0.30); pad deflection 0.28 mm against 0.48 mm free travel at mid-backlash, so the gearbox carries no stowed moment. R9 met on paper. BOM line 17, $20 |
| N2 | Spiral preload spring of about 3 N·m on each axis | Not in BOM or model | BOM line 16, $6 for two; model part 16; elevation spring biases toward stow. R4 still at risk (0.31° typical, 0.50° at the 95th percentile) |
| N3 | Relax R13 to 13 kg | 12.5 kg against 10 kg, not met | 12.95 kg against 13 kg, met with 0.05 kg margin on assumed masses |
| N4 | R7: 30 min hands-on, spread over one clear day | At risk (19 min hands-on, 4 h elapsed) | Met |
| N5 | R10: beam may move only downward during a stow | At risk (2.8 s sweep beyond 3 m) | Met |
| N6 | Four calibration points over about 4 h as the default | Used in the budget, not decided | Default in HLT-PRC-001 and HLT-CAL-001 |

Files changed: `cad/src/model.py` (parts 16 and 17, STEP and STL re-exported); `cad/src/sheets.py` and `cad/drawings/HLT-DWG-001.*` (Rev P1 to P2, new notes, same drawing number); `cad/src/concept_media.py` and all of `media/` (regenerated and checked by eye; `media/_views*` deleted); `bom/bom.csv` (17 lines, $425 to $451) and `bom/bom-notes.md`; `docs/04-calcs/sizing.py` and `01-sizing.md` (HLT-CAL-001 v0.1 to v0.2, new tags [E6] to [E8], results table rebuilt); HLT-REQ-001 and HLT-PRC-001 v0.3 to v0.4; `project.yaml` (DDR-002 added to the TRL evidence; `budget_usd` stays 430, `trl: 3`, `trl_target: 3`); `README.md` (status, components, and the new sections Concept rationale, Burning platform, Where it could be used and What sparked the idea). HLT-PRB-001 did not attribute the idea to a brainstorm and is unchanged. All PDFs in `docs/pdf/`, the drawing and the media were regenerated so no generated file still shows the old personal domain.

### Budget

No accepted recommendation carried a budget figure, so `budget_usd` stays at $430. The two added lines take the BOM to $451, $21 over, and R15 moves from met to **not met**.

### Requirement status (HLT-CAL-001 v0.2, Table 6)

11 met, 1 not met, 2 at risk, 1 not verifiable at TRL 3.

| ID | Status | Value against target |
| --- | --- | --- |
| R15 | **Not met** | $451 against $430 |
| R3 | At risk | 0.50 kWh (21 Dec) and 1.00 kWh (1 Feb) at site A; 0.40 kWh at site B |
| R4 | At risk | 0.31° beam typical, 0.50° at the 95th percentile of calibration |
| R12 | Not verifiable at TRL 3 | Materials chosen for outdoor life |
| R1, R2, R5, R6, R7, R8, R9, R10, R11, R13, R14 | Met | R9 via the stow latch; R13 with 0.05 kg margin; R7 and R10 as reworded |

### Still awaiting Amish

1. First site and user for the co-design checklist (O1); co-design partners stay open.
2. Local rules on glare and structures at that site (O2) and a siting survey of real yards (O3).
3. **New: budget for the $451 BOM (P1).** Options: (a) raise `budget_usd` to $455; (b) keep $430 and cut cost elsewhere (printed turntable, cheaper anemometer); (c) make the anemometer optional where a reliable forecast exists. Recommendation: (a), because both additions are safety or accuracy items. **Decided by Amish, 2026-09-26: budget top-up to $455 (option a), applied in the session below.**

### Cross-repo actions

None. No decision here needs another repo to change.

### Safety concerns

- New pinch point between the stow lug and the latch bracket (3 to 9 mm); the latch pawl snaps shut under spring force; the preload springs store energy with the drives off and pull the mirror toward stow if a drive is disconnected.
- The latch is sized on an assumed stowed coefficient and an assumed polyurethane modulus; until tested, remove the mirror if gusts above about 29 m/s are forecast. A failed stow (caught face-on, 40.5 N·m) still exceeds the gearbox.
- Earlier concerns (beam and glare, stow sweep, glass at height, supercapacitor energy, mast and anchor) are unchanged.

### Notes

- The recommendation "stops in both directions" needed a latch in practice, because a fixed stop can only resist the direction the axis turns into; the latch engages passively so a power-loss stow still latches, and the solenoid is used only to leave stow. This is recorded in HLT-DDR-002 N1 for Amish to see.
- Solenoid, spring and bracket masses and prices are estimates; R13 margin (0.05 kg) is inside their uncertainty.

### TRL 4

TRL 4 remains on hold by Amish's instruction. Building and testing the latch (holding moment, pad compliance, engagement on a power-loss stow), the springs and the drives are TRL 4 work and were not started.

## Session 2026-09-26: sources strengthened

### Sources replaced

Every link in "Concept rationale", "Burning platform", "Where it could be used" and "What sparked the idea" was fetched and checked against its sentence. Kept and confirmed: US EPA (about 90 % of time indoors), IEA (lighting about 8 % of global electricity, about 2,200 TWh, 2024), WHO Housing and Health Guidelines (18 °C), Hong, Wang and Zhang 2024 (Chinese sunlight rules), World Bank 2018 (Ulaanbaatar ger districts).

| Where | Old source | New source |
| --- | --- | --- |
| What sparked the idea | Viganella, Italy (Vice) | Rjukan, Norway, sun mirrors first used in 2013 ([NPR, 2013](https://www.npr.org/2013/11/03/242789411/as-mirrors-beam-light-to-town-norwegians-share-patch-of-sun)). No BBC, Times or CBC account of Viganella could be opened (blocked or refused), and the municipal tourism page supports only the 83 sunless days, so the inspiration was changed. INSPIRATIONS.md line replaced |
| Concept rationale | No citation | NPR, 2013 (civic mirrors); jremington/Arduino_heliostat (clock-driven open heliostat) |
| Region row: United Kingdom and northern Europe | ClimateStudio and SageGlass (vendor pages on EN 17037) | Replaced by a European Union row: Eurostat, 2 February 2026 (9.2 % could not keep their home adequately warm in 2024; 19.0 % in Bulgaria and Greece) |
| Region row: Canada and the northern United States | No citation | Replaced by a United States row: US EIA "Use of energy in homes" (heating and cooling 52 % of household energy in 2020; higher use in the Northeast and Midwest) |
| Region row: Chile and Argentina | No citation | Replaced by a Chile row: UNEP "Chile takes action on air pollution" (firewood up to 94 % of PM2.5 emissions in some cities) |
| Region row: Norway | NPR, 2013 | Removed, because Rjukan is now the inspiration; the rows cover North America, Europe, East Asia, Central Asia and South America |
| HLT-PRB-001 v0.4, "The problem" item 1 | ClimateStudio and SageGlass (EN 17037 targets) | US EPA (about 90 % of time indoors). The EN 17037 figures were removed because the standard is paywalled and no primary summary could be opened |

Not changed and still weak, outside the README sections in scope: HLT-PRB-001 "Prior work" cites Inhabitat and Solar Power World for the Sunflower home heliostat, and Visit Rjukan for the mirror details.

### Budget

- P1 decided by Amish, 2026-09-26 ("I am ok with the budget top ups"): `budget_usd` $430 to $455 in `project.yaml`.
- `docs/04-calcs/sizing.py` hard-codes the budget; `BUDGET` is now 455.0 and the script was re-run: [J1] "total $451.00 against $455 budget; margin $4.00"; [K3] 0 not met, 2 at risk, 1 not verifiable, 12 met.
- R15 not met to met. Documents revised: HLT-REQ-001 v0.5, HLT-CAL-001 v0.3, HLT-DDR-002 v0.2, HLT-PRC-001 v0.5, HLT-PRB-001 v0.4 (sources and budget); `README.md` budget line and status; `bom/bom-notes.md`.
- Concept media: the blueprint key figure in `cad/src/concept_media.py` now reads "Parts $451 against $455 budget, R15 met"; all of `media/` was regenerated and the temporary `_views` folders deleted.
- Still awaiting Amish: O1, O2 and O3.

## Session 2026-09-26: product appearance model and photoreal renders

Amish chose this repo for the first batch of product renders on 2026-09-26.

### What was added

`cad/src/product_model.py` exposes `product_parts()` (70 parts: 36 shell, 25 internal, 1 accessory, 8 context), `TITLE` and `RENDER_VIEWS` (hero, exploded and a detail view of the two-axis drive with the mirror removed). It reuses PARAMS, derived() and parts() from `cad/src/model.py`; the tracking pose (mirror normal 25° up, yoke turned -36.9°), the 2.2 m axis height, the yoke arm spacing, the gearbox, motor, turntable, cap plate, mast, anchor, controller, anemometer, spring can and stow latch envelopes and positions are as model.py. It adds:

- Mirror assembly: glass with a seamed edge over a thin silvered layer, a rubber edge guard, the painted backing panel, aluminum rib tubes with end plugs, the torque tube with clamp saddles and the steel trunnion stubs.
- Yoke: filleted ASA base plate and crossbar, arms with rounded heads around the trunnion and shallow face pockets, flanged bearings and M6 bolts.
- Drives: NMRV030-class gearbox bodies with fillets, output bosses, fins and cover detail; adapter plates with screws; NEMA17 motors with chamfered bodies, aluminum end caps and connectors; the teal turntable with a bearing seam; the galvanized cap plate with bolts; both homing switches.
- Stow stop and latch: lug, bracket with bolts, orange polyurethane stop pad, pawl with pivot pin and the pull solenoid with plunger; the ribbed elevation spring can.
- Controller: IP65 box with side ribs and a parting line, a lid with a clear window over the board (ESP32 module, RTC and coin cell, two stepper drivers with heat sinks, buck converter, terminal block and the five supercapacitors of the stow reserve), lid screws, a lit green status light, cable glands and vent, a teal name plate with the HelioLite wordmark, and mast straps.
- Cabling with stand-off clips on the mast; cup anemometer with hemispherical cups, hub, spokes, body and mast clamp; anchor flange and socket with bolts and set screws; the indoor 12 V power adapter as an accessory in the exploded view.
- Context (not in the BOM): a compact ground patch with a paver pad, a short section of house wall with the target window, sill and a dark room behind the glazing, and the outdoor feed cable running to a wall entry.

`README.md` now shows `media/render-hero.png` and links `media/render-exploded.png`; the orchestrator produces both files.

### Differences from model.py (Proposed, awaiting Amish)

1. **Target distance in the render.** The concept media place the house wall 2.2 m from the mast, itself closer than a real site. The appearance model puts the wall face 1.0 m from the mast, with a 920 mm wide wall section and an 800 x 1,000 mm window, so the heliostat fills the product render. Proposed, awaiting Amish. Recommendation: keep this as a render-only layout; the hero note says the window is drawn closer than a real site.
2. **Mirror edge guard.** BOM line 1 specifies seamed edges and a safety backing film but no edge protection. The appearance model adds a black EPDM U-channel around the glass and panel edges (10 mm lip), which protects hands during fitting and the glass edge against chipping. Proposed, awaiting Amish. Recommendation: adopt it and add it to BOM line 1 or 13 at the next BOM revision (a few dollars, within the $4 margin but to be checked); the BOM was not edited.
3. **Clear window in the controller lid.** BOM line 9 specifies an IP65 box without saying whether the lid is clear. The appearance model uses a lid with a clear polycarbonate window so the board and stow reserve show. Proposed, awaiting Amish. Recommendation: adopt a clear-lid IP65 box (common and similar in price) and add "clear lid" to BOM line 9 at the next revision.
4. **Torque tube saddles.** model.py joins the torque tube directly to the underside of the backing panel, and BOM line 2 lists structural silicone. The appearance model shows two bolted steel saddles clamping the tube to the panel near the ribs. Proposed, awaiting Amish. Recommendation: keep the saddles as the mechanical attachment, with silicone as the bond, and confirm at TRL 4 design review.
5. **Finishes.** model.py colours identify parts only. The appearance model uses off-white ASA for the yoke, a teal painted turntable and name plate, silver-grey gearboxes, black motors, galvanized mast and cap plate and a dark painted anchor. Proposed, awaiting Amish. Recommendation: accept as the product finish set.
6. **Glass layering and small hardware.** The 3 mm glass is split into a 0.4 mm silvered layer and 2.6 mm of glass for rendering; the total thickness is unchanged. Bolts, clips, straps, glands and the name plate are appearance detail under BOM lines 11 and 13; no new BOM lines are implied beyond items 2 and 3.

### Status

This is an appearance model only: no tolerances, no fabrication detail, nothing past TRL 3. `trl: 3` and `trl_target: 3` are unchanged, and TRL 4 remains on hold. model.py, the BOM and the other documents were not edited.

## Session 2026-09-27: kit 1.5.0 and image quality

- Kit 1.5.0 synced: STANDARDS v1.5 (sections 12 to 15: product renders, storefront images and image quality, public release, authorship and signing), `.kit/cards.py`, `.kit/image_qc.py`, `.kit/release_gate.py`, issue templates, and the `/render-product` and `/release` commands. `CLAUDE.md` now matches `.kit/CLAUDE.md`.
- Every `media/render-*.png` recaptioned from its original render with the new layout: the title, concept label and repository sit in a band above the render and the view note in a band below it, each line wrapped to the image width, so no text overlaps other text or the render or runs off the image. `media/card.png` and `media/social-preview.png` regenerated with the same rules.
- `python .kit/image_qc.py` and `python .kit/release_gate.py` pass. trl stays 3.

## Session 2026-10-01: design for construction and prototype build plan (kit 1.7.0)

Under Amish's 2026-09-30 instruction ("If you are realising that the design cannot be built as per concept - fix the design assumptions to match and be physically feasible as you draw the illustrations") and his approval of the build plan format, HelioLite was brought to the approved standard. TRL stays 3; TRL 4 remains on hold.

### What was done

- Kit 1.7.0 installed (`.kit/`, `.claude/commands/`); `CLAUDE.md` matches `.kit/CLAUDE.md`.
- `cad/src/model.py` rebuilt as separate made and bought parts with bolt holes, and a constructability check (`python cad/src/model.py --check`): 1,583 checks of contacts, clearances, overlaps and the elevation sweep from stow to face-up, all passing. STEP and STL re-exported.
- `docs/decisions/0003-design-for-construction.md` (HLT-DDR-003 v0.1, Draft): every change, with its reason; made under Amish's 2026-09-30 instruction to make the design physically buildable; open for his review.
- `cad/src/build_plan_media.py`: overview, 15 making sketches (`cad/drawings/HLT-DWG-101` to `115`), 8 joint close-ups, 18 assembly step pictures and a block-level wiring diagram in `docs/05-build-plan/`.
- `docs/05-build-plan.md` (HLT-BLD-001 v0.1) and `docs/06-design-decisions.md` (HLT-DEC-001 v0.1), both added to `trl_evidence`; `design_state: constructable` in `project.yaml`.
- HLT-CAL-001 v0.4 (`sizing.py` re-run), HLT-PRC-001 v0.6, HLT-REQ-001 v0.6, `bom/bom.csv`, `bom/bom-notes.md`, `README.md` (links line, "Building the prototype" section, key components, value-engineering wording); general arrangement HLT-DWG-001 Rev P4; concept media regenerated.

### Design changes made for construction (HLT-DDR-003)

1. Ribs crossed the torque tube in the same space: ribs are now 25 x 40 mm with a square tunnel the tube runs through.
2. The trunnion rod was loose in the tube and could not be fitted with the mirror in the yoke: aluminum end blocks bolted in the tube ends and two keyed stubs pinned in after the mirror is in place.
3. The one-piece printed yoke could not be printed: an aluminum 60 x 40 x 2 mm tube crossbar and arms with gusset plates, printed bearing plugs; the printed base plate is gone.
4. Bearings had no housing: flanged bronze bushes through arm and plug; the flanges locate the tube.
5. Elevation gearbox had no fixing: bolted flat to the right arm.
6. Elevation spring can floated off the arm: screwed to the left arm, spring stub into it.
7. Turntable sat loose on the gearbox with no shaft: double output shaft, thrust washer, keyed hub and a 120 x 10 mm disc; the shaft drives the azimuth spring in the mast.
8. Cap plate to mast undefined: threaded floor flange on the pipe, cap screwed to it from below.
9. Stow latch could not release (pawl lifted inside the lug's swing) and was poorly supported: lug on a square collar, sliding pawl, bent bracket with a stop block, solenoid on a strap.
10. Homing switches sensed nothing: azimuth switch on a post under a magnet in the disc; elevation switch beside a magnet in the lug.
11. Controller box floating: plate and two U-bolts.
12. Anemometer arm touching the mast at a point: right-angle clamp.
13. Cable ran through the anchor flange and missed the turning yoke: rerouted, with a service loop to the crossbar.
14. Mast loose in its socket: two set bolts.

### Key results

- Requirements (HLT-CAL-001 v0.4): 11 met on paper, 2 at risk (R3, R4), 1 not verifiable at TRL 3 (R12), none not met; R15 over the value-engineering target by $37.
- Value-engineering target: USD 455. Estimated cost of the constructable design: USD 492 (USD 37 over the target).
- Mast-top mass 12.94 kg against 13 kg (0.06 kg margin, on an assumed 1.2 kg gearbox); arm flex 0.040 to 0.006 degrees; pointing 0.30 degrees beam typical, 0.50 degrees at the 95th percentile; crossbar clearance 46 to 56 mm.

### Proposed, awaiting Amish

All open items are in `docs/06-design-decisions.md`. New this session: the R13 mass margin (A1), how the head goes on the mast (A2) and updating the appearance model and renders (A3), each with a recommendation; and ten items to confirm when parts are bought.

### Stale until regenerated on Amish's Mac

The photoreal renders `media/render-*.png` (made on Amish's Mac; not in this cloud copy), `media/card.png` and `media/social-preview.png` show the printed yoke, the concept latch and the torque tube saddles; the design changed visibly. `cad/src/product_model.py` was not updated.

### Safety concerns

Unchanged in kind: the beam (glass kept covered from bonding until calibration), glass handling, high-torque drives and wound preload springs, the stow reserve's stored energy, and lifting the 11 kg head onto the mast at 1.8 m (two people, stable steps, mirror latched and covered). The build plan's safety stops S1 to S8 cover each.

### Recommended next step

Amish reviews HLT-DDR-003 and the register. TRL 4 (building and testing to the plan) stays on hold.

## Session 2026-10-02: open decisions decided

On 2026-10-02 Amish approved the recommendations for every open decision: "i approve your recommendations for all 555 open decisions." The 11 open decisions of the design decisions register are now in its Decisions made table, dated 2026-10-02.

HLT-DDR-003 Table 3 items A1 to A3 are decided (A1 and A2 on changed recommendations: an aluminum latch bracket now, and fitting the head in two lifts from a stable platform). The acceptance of HLT-DDR-003 Table 1 as a whole was never among the open decisions and is still to be put to Amish. The value engineering savings no longer list the box without a clear lid. Review flag 3 (a forecast-only stow weakening the storm-stow backup) was not part of any decision and that saving is still listed with its caveat.

### Documents changed

- `docs/06-design-decisions.md` (HLT-DEC-001 v0.2)
- `docs/decisions/0003-design-for-construction.md` (HLT-DDR-003 v0.2)
- `docs/01-problem.md` (HLT-PRB-001 v0.5)
- `docs/02-concept.md` (HLT-PRC-001 v0.7)
- `docs/03-requirements.md` (HLT-REQ-001 v0.7)
- `docs/05-build-plan.md` (HLT-BLD-001 v0.2)
- `bom/bom-notes.md` (not a controlled document)
- `README.md` (not a controlled document)

### Follow-up actions to carry approved decisions into the design

1. Decision 5: Model and drawings: make the latch bracket aluminum in `cad/src/model.py` and on making sketch HLT-DWG-110, rechecking its bending under the stowed load.
2. Decision 5: BOM and calculations: change line 17's latch bracket to aluminum with its price, and take about 0.1 kg off the mast-top mass (HLT-CAL-001, H3).
3. Decision 6: Build plan and pictures: redraw steps 10 to 17 so the yoke and drive go on the mast first and the mirror assembly (about 6.2 kg) is lowered into it from a stable platform; regenerate the step pictures.
4. Decision 6: Model: add the platform-height fitting sequence to `cad/src/build_plan_media.py` and check the mirror assembly can be lowered into the yoke with the trunnions fitted.
5. Decision 7: Appearance model and renders: update `cad/src/product_model.py` and the photoreal renders on Amish's Mac to the aluminum yoke, the new latch and the rib tunnels, dropping the torque tube saddles; finish set of item 11 and caption of item 8 with them.
6. Decision 9: BOM: add about 2.4 m of black EPDM edge channel with its price (line 1 or 13).
7. Decision 9: Model and calculations: add the edge channel to the mirror assembly and the mast-top mass (about 0.15 to 0.25 kg); if the weighed head exceeds 13 kg, propose a slight R13 relaxation.
8. Decision 9: Build plan pictures: show the edge channel in step 5 after bonding.
9. Decision 10: BOM: change line 9's specification to an IP65 box with a clear lid.
10. Decision 3: Run the desk siting survey of 20 to 30 yards and record it (HLT-CAL-001, section B, or a new note).

### Points found in the review

1. Item 9's edge guard would use up the 0.06 kg R13 margin (item 5) by itself; the two items must be decided together.
2. A saving in Value engineering (a box without a clear lid) contradicts the recommendation in item 10.
3. A saving in Value engineering (forecast-only stow, making the anemometer optional) weakens the storm-stow backup in the safety case and should not be counted as a saving.
4. REVIEW 2026-09-26 item 2 says the edge guard fits 'within the $4 margin'; the estimate is now USD 37 over its target, so that wording is stale.

No CAD model, BOM quantity or price, calculation result or picture was changed. TRL stays at 3; TRL 4 remains on hold.
