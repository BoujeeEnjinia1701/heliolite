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
