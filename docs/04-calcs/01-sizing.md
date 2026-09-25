---
doc_id: HLT-CAL-001
title: HelioLite sizing calculations
project: HelioLite
doc_type: Calculation
version: "0.1"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: First issue for TRL 3 (optics, hourly energy at reference sites, stiffness, pointing and calibration, wind and drives, stow reserve, mass, power, cost)
---

# HelioLite sizing calculations

On paper, HelioLite meets eight of its fifteen requirements, misses two and has four at risk; one cannot be verified at TRL 3. The optics work: at the design point the mirror delivers about 211 W to the outside of the glazing and 159 W (about 15,000 lm) into the room, and a reference site at 45° N receives 0.50 kWh through the glazing on the winter solstice and 1.0 kWh on 1 February. The misses are stowed wind survival (R9), where the assumed stowed hinge moment of 24 N·m at 35 m/s exceeds the gearbox's listed 22 N·m maximum, and mass on the mast top (R13), about 12.5 kg against 10 kg. Pointing (R4) is at risk because it relies on four-point calibration and on preloaded drives. Every number in this note is printed by `docs/04-calcs/sizing.py`; the tag in brackets, for example [D5], is the line of that script's output that carries it.

> **Safety:** These calculations concern a reflected beam of nearly one sun, a glass mirror 2.2 m above the ground, worm drives with high output torque, and a mast in storm winds. They are first-principles estimates for a paper proof of concept and are not a substitute for datasheets, a structural review or test. See HLT-PRC-001, Safety.

## Scope and method

The note checks every requirement in HLT-REQ-001 v0.3 against the design in HLT-PRC-001 v0.3 and the parametric model `cad/src/model.py`. The script imports the model's `PARAMS` and `derived()` values, so mast, yoke, mirror and clearance dimensions are the ones in the STEP files and in drawing HLT-DWG-001. It reads the BOM total from `bom/bom.csv`. Run it from the repo root with `python docs/04-calcs/sizing.py` (about 20 s, most of it the calibration simulation).

## Assumptions

*Table 1. Main assumptions.*

| Area | Assumption | Basis |
| --- | --- | --- |
| Design point | Clear winter day at 45° N, DNI 800 W/m², 10 m to the target, 32° incidence on the mirror | HLT-REQ-001 |
| Optics | Reflectance 0.93 clean, soiling factor 0.95; 0.98 allowance for mirror edges, sun-shape tails and spill; double glazing 0.75 at normal incidence, falling with angle by Fresnel reflection at four air-glass surfaces (n = 1.52) and path length; direct sunlight 95 lm/W; utilization factor 0.4 in a 3 x 4 m room | Engineering judgment and textbook optics |
| Sun and sky | Declination by Cooper's formula, solar time (no equation of time); clear-sky DNI by the Meinel model with Kasten-Young air mass | Textbook models, adequate for daily energy |
| Reference sites | Window 1.0 x 1.2 m, center 1.5 m high, in the north wall of a house 10 m wide, 8 m deep and 5.5 m high; mirror center 2.2 m high at site A (6 m east, 8 m north of the window), B (8 m east, 5 m north) or C (15 m due north) | Illustrative siting, not a surveyed site |
| Wind | Air 1.225 kg/m³; face-on force coefficient 1.2; operating peak hinge moment coefficient 0.25 (normalized by q·A·c), in the range reported by Peterka and Derickson ([SAND92-7009](https://www.osti.gov/biblio/7105290)); stowed normal force coefficient 0.6 and stowed hinge moment coefficient 0.15, raised for a small chord because peak stow coefficients roughly double as chord halves ([Emes et al.](https://apvi.org.au/solar-research-conference/wp-content/uploads/2018/01/Matthew-Emes-Experimental-Investigation-of-the-Wind-Loads-on-Heliostats.pdf)); yaw moment coefficient 0.1; mast drag coefficient 1.2 | Rough; the stowed values are the largest uncertainty in R9 |
| Drives | NMRV030-class 50:1 worm gearbox: rated output 17 N·m and backlash 1° as listed by [StepperOnline](https://www.omc-stepperonline.com/nmrv30-worm-gearbox); maximum 22 N·m as listed for a Motovario 50:1 unit ([RS](https://my.rs-online.com/web/p/gearboxes/2166494)); mass about 1.2 kg (typical of the frame size, to confirm); worm efficiency 0.4; NEMA17 48 mm motor 0.36 kg | Supplier listings; mass assumed |
| Materials | Steel E = 200 GPa, G = 80 GPa, pipe yield 240 MPa (ASTM A53 grade B); printed ASA E = 1.8 GPa, 1.07 g/cm³ at 60 % infill; aluminum composite panel 5.5 kg/m²; glass 2,500 kg/m³ | Typical values |
| Calibration | Mount model with five unknowns: azimuth and elevation zero offsets, two base tilts and mirror cant on the torque tube. User jogs the spot to the target within 0.05° per axis (normal) at each point. True errors drawn at random: azimuth ±10°, elevation ±3°, tilts and cant with 1° and 0.3° standard deviation. 120 trials per case | Monte Carlo simulation |
| Power | Idle 0.4 W (ESP32 light sleep, RTC, drivers off); one motor at 5 W for 1 s per 30 s update; stow at 3.8 W (two coils at 1.0 A in 1.5 Ω, driver 0.3 W, ESP32 0.5 W) | Typical module data |

## A. Optics at the design point (R1, R2, R8)

The mirror intercepts 800 W/m² x 0.36 m² x 0.848 = 244 W. After reflectance and soiling 216 W leave the mirror, 211 W arrive at the outside of the glazing and 159 W enter the room [A2]. That is about 15,070 lm and a mean added illuminance of about 500 lx over 12 m² [A3]. R1 (200 W) and R2 (300 lx) are met. The beam carries 0.88 to 0.93 of the DNI; a flat mirror does not concentrate [A4].

The spot is the projected mirror outline plus the sun's 0.53° angular diameter. At 10 m it is about 0.65 m square, and a 0.5° beam error moves it 87 mm, so spot plus error on both sides is 0.82 m and fits a 1.0 m wide window. At 20 m the figure is 1.09 m and the beam spills [A5]. The largest distance at which spot plus 0.5° error fits a 1.0 m wide window is 16.8 m [A6]. R8 (3 to 20 m) is met mechanically; above about 17 m a wider target is needed.

## B. Daily energy at reference sites (R3)

The TRL 2 figure used a generic day (6 h, mean DNI 650 W/m², mean cosine 0.80) and gave 0.97 kWh at the window and 0.73 kWh through the glazing [B1]. The hourly model below replaces it with sun geometry, clear-sky DNI, shading by the house and the angle at which the beam strikes the glazing.

*Table 2. Clear-day energy through the glazing at three illustrative sites, 45° N [B2].*

| Site | Mirror position (east, north of window) | Distance | Glazing incidence (τ) | Day | Sunlit tracking | Mean cosine | At window | Into room | Peak into room |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 6 m, 8 m | 10.0 m | 37° (0.73) | 21 Dec | 4.8 h | 0.83 | 0.69 kWh | 0.50 kWh | 152 W |
| A | 6 m, 8 m | 10.0 m | 37° (0.73) | 1 Feb | 8.3 h | 0.86 | 1.38 kWh | 1.00 kWh | 166 W |
| B | 8 m, 5 m | 9.5 m | 58° (0.61) | 21 Dec | 5.5 h | 0.75 | 0.66 kWh | 0.40 kWh | 97 W |
| B | 8 m, 5 m | 9.5 m | 58° (0.61) | 1 Feb | 6.2 h | 0.73 | 0.82 kWh | 0.50 kWh | 107 W |
| C | 0 m, 15 m | 15.0 m | 3° (0.75) | 21 Dec | 8.4 h | 0.95 | 1.34 kWh | 1.00 kWh | 163 W |
| C | 0 m, 15 m | 15.0 m | 3° (0.75) | 1 Feb | 9.4 h | 0.93 | 1.64 kWh | 1.23 kWh | 177 W |

At reference site A the unit delivers 0.501 kWh on the solstice and 1.004 kWh on 1 February [B3]. R3 (0.5 kWh on a clear winter day) is **at risk**: site A meets it with no margin on the shortest day, and site B, where the beam strikes the glazing at 58°, misses it. The best result comes from a mirror standing well out from the house on the window's axis (site C, 1.23 kWh on 1 February [B4]), where the house does not shade the mirror and the beam meets the glazing square on, but that site is 15 m away and close to the spill limit in section A. Siting matters more than any hardware choice; the siting survey (HLT-DDR-001, O3) should use this model.

## C. Mast and yoke stiffness (R4)

The 60.3 x 3.9 mm pipe has I = 276,079 mm⁴ and EI = 5.52 x 10¹⁰ N·mm² [C1]. At 8 m/s face-on the mirror force is 16.9 N, and the mast top tilts 0.040° [C2]. The same load on a 2.2 m 40 x 40 mm extrusion would tilt it 0.37° [C3], which confirms decision D1.

The printed yoke arms carry the wind force and react the hinge moment through the elevation gearbox. With the TRL 2 scaffold's 30 x 50 mm section, 382 mm long, the arm slope at 8 m/s would be 0.145°, three times the 0.05° allowed in the TRL 2 budget. The model therefore uses 40 x 70 mm arms, which give 0.040° [C4]. Mast twist from an assumed yaw moment of 0.85 N·m is 0.002° [C5].

## D. Pointing error budget and calibration (R4, R6, R7)

A DS3231 at ±2 ppm drifts 31.5 s in 6 months, during which the sun moves 0.131°; that is 0.066° as a mirror-normal equivalent [D1]. R6 (60 s) is met. The drive resolves 0.0023° per microstep at the output [D2].

*Table 3. Calibration simulation: worst mirror-normal error from 09:00 to 15:00 at site A on 21 December [D3].*

| Calibration points | Median | 95th percentile |
| --- | --- | --- |
| 3 points over 30 min | 9.8° | 38.7° |
| 3 points over 3 h | 0.18° | 0.45° |
| 4 points over 4 h | 0.12° | 0.23° |

Points taken within half an hour cannot separate the five mount errors, and the fit is unusable. Three points over 3 h are adequate on average but leave a long tail. Four points over about 4 h are used below.

*Table 4. Pointing error budget, mirror normal [D4, D5].*

| Source | Normal error | Basis |
| --- | --- | --- |
| Sun-position algorithm (Grena 5) | 0.001° | Half of 0.0027° |
| Clock, 6 months without network time | 0.066° | [D1] |
| Mount model residual, 4 points over 4 h | 0.116° | Median of [D3] |
| Worm backlash with preload | 0.050° | Assumed lost motion with the teeth held on one flank |
| Step resolution | 0.002° | [D2] |
| Mast bending, 8 m/s | 0.040° | [C2] |
| Yoke arm flex, 8 m/s | 0.040° | [C4] |
| **Root sum square** | **0.153°** | **0.31° beam against 0.5°** |

With the 95th percentile calibration residual (0.23°) the beam error is 0.50°, exactly at the limit [D5]. The budget also depends on a preload: the listed backlash of the gearbox is 1°, and if the wind reverses the load, half of it can appear at the mirror, giving 1.04° beam error [D6]. The mirror's center of mass sits 13.7 mm in front of the elevation axis, a gravity moment of up to 0.80 N·m [H4], so a preload of more than 2.9 N·m (operating hinge moment 2.1 N·m plus imbalance) is needed at 8 m/s [H5]. A 3 N·m torsion spring on each axis would need about 0.30 N·m at the motor with wind and imbalance [H5], within a 48 mm NEMA17's holding torque but with little margin at speed. R4 is **at risk**; the preload is proposed, awaiting Amish.

Calibration hands-on time by task analysis is 19 min for four points (5 min setup, 3 min per point, 2 min to fit and save) [G1], within 30 min, but the points must span about 4 h of elapsed time [G2]. R7 as worded ("in 30 min or less") is therefore **at risk**; a rewording to hands-on time is proposed, awaiting Amish.

## E. Wind, drives, mast and anchor (R9)

*Table 5. Wind loads [E1].*

| Wind | Pose | q | Mirror force | Hinge moment | Mast base moment | Mast stress |
| --- | --- | --- | --- | --- | --- | --- |
| 8 m/s | Tracking | 39 Pa | 17 N | 2.1 N·m | 41 N·m | 5 MPa |
| 15 m/s | Tracking (stow trigger) | 138 Pa | 60 N | 7.4 N·m | 146 N·m | 16 MPa |
| 20 m/s | Tracking | 245 Pa | 106 N | 13.2 N·m | 259 N·m | 28 MPa |
| 35 m/s | Stowed face-down | 750 Pa | 162 N | 24.3 N·m | 436 N·m | 48 MPa |
| 35 m/s | Caught face-on | 750 Pa | 324 N | 40.5 N·m | 793 N·m | 87 MPa |

The mast is adequate in every case: caught face-on at 35 m/s it reaches 87 MPa against 240 MPa yield, a factor of 2.8, and the anchor must resist 0.79 kN·m [E4]. The BOM asks for an anchor rated at 1.0 kN·m or more.

The weak link remains the elevation gearbox. With the decided storm awareness (D2), the controller stows when the anemometer sees a 15 m/s gust or the forecast predicts one; the hinge moment at the trigger is 7.4 N·m, within the 17 N·m rating [E5]. In stow, the assumed stowed hinge moment at 35 m/s is 24.3 N·m, above both the 17 N·m rating and the 22 N·m listed maximum [E2]; the rating is reached at a 29 m/s gust [E3]. R9 is **not met** on the assumed stowed coefficient. The static strength of a self-locking worm is usually higher than its running rating, but this is not listed and cannot be counted on. Options (proposed, awaiting Amish): a larger NMRV040-class gearbox on the elevation axis (more mass, see R13); rubber stow stops on the yoke that take the stowed hinge moment in both directions; or a published stowed coefficient for small heliostats that justifies a lower load.

## F. Stow on power loss (R10)

A worst-case stow turns the elevation axis 180° at 10°/s in 18 s, plus 5 s to detect the loss, and uses 87 J at 3.8 W [F1]. Five 2.7 V, 25 F supercapacitors in series (5 F) charged to 11.7 V and used down to 7.0 V hold 187 J after 85 % conversion, a margin of 2.1, with 2.34 V per cell against the 2.7 V rating [F2]. The stow always turns the normal downward. From site A at 11:00 on 21 December the beam starts 4.0° below the horizon and never rises above it; the reflection ends after 7.7 s, and for about 2.8 s the beam crosses the ground between the target and a point 3 m from the mast [F4]. The stow finishes in 23 s, within 60 s, but R10 as worded allows the beam only on the target or the ground within 3 m, so it is **at risk** on that transient. Clarifying R10 to allow a downward sweep during a stow is proposed, awaiting Amish.

## G. Calibration time (R7)

See section D and [G1], [G2].

## H. Mass and balance (R13)

The mirror assembly weighs 5.98 kg: glass 2.70, panel 1.98, torque tube 0.32, ribs 0.50, trunnions 0.29, adhesive and film 0.20 [H1]. The yoke, printed at 60 % infill from the model's 4.23 L, weighs 2.72 kg; each drive 1.66 kg (gearbox 1.2 kg assumed); the turntable 0.5 kg [H2]. The total on the mast top is 12.5 kg against 10 kg [H3], so R13 is **not met**. The TRL 2 estimate of about 8 kg assumed small generic NEMA17 worm gearboxes without a rating and a 0.8 kg yoke; the rated NMRV030-class gearboxes and the stiffer arms of section C add about 4.5 kg. The mast pipe adds 9.2 kg and the cap plate 1.6 kg. Installation in 4 h by two people is not verifiable at TRL 3.

## I. Power (R14)

Average draw is 0.60 W: idle 0.4 W, moves 0.17 W and 0.029 W in the stow reserve's balancing resistors, about 14 Wh a day [I1]. R14 (3 W) is met.

## J. Cost (R15)

The BOM has 15 lines, all priced, totaling $425.00 against the $430 budget decided on 2026-09-25, a margin of $5.00 [J1]. R15 is met, thinly. Preload springs (about $6, proposed), tools, printer time and shipping are not included [J2].

## K. Results

The yoke sweeps: at site A the normal stays within 46° of the target direction on the solstice, inside the ±135° range; the mirror clears the arms by 20 mm and the crossbar by 46 mm, so a face-down stow clears the yoke [K1].

*Table 6. Requirement status, not met first [K2, K3].*

| ID | Requirement | Value | Target | Status |
| --- | --- | --- | --- | --- |
| R9 | Wind | Stowed hinge moment 24 N·m at 35 m/s against 17 N·m rated and 22 N·m maximum; rating reached at 29 m/s; mast 87 MPa worst case | Hold R4 to 8 m/s; survive 35 m/s in stow | **Not met** |
| R13 | Mass and install | 12.5 kg on the mast top | 10 kg or less; two people, hand tools, 4 h | **Not met** |
| R3 | Daily energy | 0.50 kWh (21 Dec) and 1.00 kWh (1 Feb) at site A; 0.40 kWh at site B on 21 Dec | 0.5 kWh or more on a clear winter day | At risk |
| R4 | Pointing | 0.31° beam typical, 0.50° at the 95th percentile, with preloaded drives; 1.04° without preload | 0.5° beam up to 8 m/s | At risk |
| R7 | Calibration | 19 min hands-on, about 4 h elapsed between first and last point | 30 min or less, no survey instrument | At risk |
| R10 | Safe beam | Stow in 23 s on stored energy (margin 2.1); beam moves only downward, crossing the ground beyond 3 m for about 2.8 s | Target or ground within 3 m; stow within 60 s | At risk |
| R12 | Outdoor life | ASA, galvanized steel, glass with backing film, by selection | -20 to +45 °C, UV, corrosion, 10 years | Not verifiable at TRL 3 |
| R1 | Redirected sunlight | 211 W at the glazing | 200 W or more | Met |
| R2 | Daylight | 502 lx mean added (utilization 0.4 assumed) | 300 lx or more | Met |
| R5 | Sensorless tracking | Time, location and target only; Hall switches for homing, anemometer for weather | No sun sensor or camera | Met |
| R6 | Timekeeping | 32 s after 6 months | 60 s or less | Met |
| R8 | Working range | Mechanical range met; spot plus error fits a 1.0 m window up to 17 m | 3 to 20 m; ±135°; -90 to +90° | Met |
| R11 | Electrical safety | 12 V SELV outdoors, IP65 box, listed indoor adapter | SELV, IP65, listed adapter | Met |
| R14 | Standby power | 0.60 W average | 3 W or less | Met |
| R15 | Cost | $425, margin $5 | $430 or less | Met |

Totals: 2 not met, 4 at risk, 1 not verifiable at TRL 3, 8 met [K3].

## Checks against earlier figures

- **Optical chain.** TRL 2 quoted 245 W intercepted and about 212 W at the glazing; the script gives 244 W and 211 W [A2]. HLT-PRC-001 and the flow diagram now use the script's values.
- **Spill distance.** TRL 2 said spill rises above about 15 m; with 0.5° error and a 1.0 m window the limit is 16.8 m [A6].
- **Daily energy.** TRL 2 quoted about 0.7 kWh from a generic day; the generic day reproduces 0.73 kWh [B1], but the hourly site model gives 0.50 kWh at site A on the solstice [B3]. Documents now quote the site figures.
- **Clock.** TRL 2 quoted about 32 s; the script gives 31.5 s [D1].
- **Pointing.** TRL 2 quoted 0.17° normal and 0.34° beam with a 0.10° calibration residual, 0.10° backlash and 0.05° yoke flex. The new budget is 0.153° normal and 0.31° beam [D5], but only with four-point calibration, preloaded drives and 40 x 70 mm arms.
- **Wind.** The face-on figures match TRL 2 (40 N·m hinge moment; mast stress now 87 MPa including drag on the pipe, up from 78 MPa). Stowed loads were not estimated at TRL 2 and are new.
- **Mass.** TRL 2 quoted about 8 kg on the mast top; now 12.5 kg [H3].
- **Power.** 0.6 W, unchanged [I1].
- **Cost.** TRL 2 quoted $391 against $400; the BOM is now $425 against the decided $430 [J1].
