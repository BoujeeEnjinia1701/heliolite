---
doc_id: HLT-CAL-001
title: HelioLite sizing calculations
project: HelioLite
doc_type: Calculation
version: "0.5"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: First issue for TRL 3 (optics, hourly energy at reference sites, stiffness, pointing and calibration, wind and drives, stow reserve, mass, power, cost)
- version: "0.2"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
- version: "0.3"
  date: '2026-09-26'
  author: Amish Chadha
  change: "Budget top-up approved by Amish: R15 target $455, script re-run"
- version: "0.4"
  date: '2026-10-01'
  author: Amish Chadha
  change: Design made constructable (HLT-DDR-003); aluminum tube yoke, masses from the model's parts; budget treated as a value-engineering target
- version: "0.5"
  date: '2026-10-02'
  author: Amish Chadha
  change: "Decisions of 2026-10-02 carried in: aluminum latch bracket (bending rechecked, E9), EPDM edge channel (mass and clear aperture), two-lift fitting masses, BOM lines 1, 9 and 17; script re-run"
---

# HelioLite sizing calculations

On paper, HelioLite meets eleven of its fifteen requirements, has two at risk and is over its value-engineering target on cost; one cannot be verified at TRL 3. Version 0.4 follows the constructable design of HLT-DDR-003 (aluminum tube yoke, rib tunnels, trunnion end blocks and stubs, detailed latch, mast top and fixings): the yoke arms are stiffer and the masses now come from the model's separate parts. Version 0.5 carries in the decisions of 2026-10-02: the latch bracket is 6 mm aluminum angle, a black EPDM edge channel guards the glass and panel edges (its 3 mm front lip trims the clear aperture by 2 %), and the head goes on the mast in two lifts; the estimated cost is USD 499 against the USD 455 value-engineering target, USD 44 over. This version applies the decisions Amish took on 2026-09-25 (HLT-DDR-002): a stow stop and latch that carries the stowed hinge moment, preload springs on both drives, R13 relaxed to 13 kg, R7 and R10 reworded, and four calibration points over about 4 h as the default. The optics work: at the design point the mirror delivers about 207 W to the outside of the glazing and 155 W (about 14,800 lm) into the room, and a reference site at 45° N receives 0.49 kWh through the glazing on the winter solstice and 0.98 kWh on 1 February. Stowed wind survival (R9) is now met on paper, because the latch rather than the gearbox carries the stowed moment, with a factor of 2 on the assumed coefficient. Version 0.3 recorded a budget of $455, a top-up Amish approved on 2026-09-26 (HLT-DDR-002 v0.2); on 2026-10-01 Amish set budgets as hypothetical value-engineering targets, so R15 is now reported against that target. Pointing (R4) stays at risk at the 95th percentile of calibration, and daily energy (R3) depends on siting. Every number in this note is printed by `docs/04-calcs/sizing.py`; the tag in brackets, for example [D5], is the line of that script's output that carries it.

> **Safety:** These calculations concern a reflected beam of nearly one sun, a glass mirror 2.2 m above the ground, worm drives with high output torque, and a mast in storm winds. They are first-principles estimates for a paper proof of concept and are not a substitute for datasheets, a structural review or test. See HLT-PRC-001, Safety.

## Scope and method

The note checks every requirement in HLT-REQ-001 v0.8 against the design in HLT-PRC-001 v0.8 and the parametric model `cad/src/model.py`. The script imports the model's `PARAMS` and `derived()` values, so mast, yoke, mirror and clearance dimensions are the ones in the STEP files and in drawing HLT-DWG-001. It reads the BOM total from `bom/bom.csv`. Run it from the repo root with `python docs/04-calcs/sizing.py` (about 20 s, most of it the calibration simulation).

## Assumptions

*Table 1. Main assumptions.*

| Area | Assumption | Basis |
| --- | --- | --- |
| Design point | Clear winter day at 45° N, DNI 800 W/m², 10 m to the target, 32° incidence on the mirror | HLT-REQ-001 |
| Optics | Clear aperture 594 x 594 mm inside the edge channel's 3 mm front lip (0.353 m²; the full 0.36 m² is used for wind and mass); reflectance 0.93 clean, soiling factor 0.95; 0.98 allowance for mirror edges, sun-shape tails and spill; double glazing 0.75 at normal incidence, falling with angle by Fresnel reflection at four air-glass surfaces (n = 1.52) and path length; direct sunlight 95 lm/W; utilization factor 0.4 in a 3 x 4 m room | Engineering judgment and textbook optics |
| Sun and sky | Declination by Cooper's formula, solar time (no equation of time); clear-sky DNI by the Meinel model with Kasten-Young air mass | Textbook models, adequate for daily energy |
| Reference sites | Window 1.0 x 1.2 m, center 1.5 m high, in the north wall of a house 10 m wide, 8 m deep and 5.5 m high; mirror center 2.2 m high at site A (6 m east, 8 m north of the window), B (8 m east, 5 m north) or C (15 m due north) | Illustrative siting, not a surveyed site |
| Wind | Air 1.225 kg/m³; face-on force coefficient 1.2; operating peak hinge moment coefficient 0.25 (normalized by q·A·c), in the range reported by Peterka and Derickson ([SAND92-7009](https://www.osti.gov/biblio/7105290)); stowed normal force coefficient 0.6 and stowed hinge moment coefficient 0.15, raised for a small chord because peak stow coefficients roughly double as chord halves ([Emes et al.](https://apvi.org.au/solar-research-conference/wp-content/uploads/2018/01/Matthew-Emes-Experimental-Investigation-of-the-Wind-Loads-on-Heliostats.pdf)); yaw moment coefficient 0.1; mast drag coefficient 1.2 | Rough; the stowed values are the largest uncertainty in R9 |
| Stow latch | Stowed moment carried by a steel lug trapped between a 3 mm polyurethane (90A) stop pad and a sprung steel latch pawl at 55 mm from the elevation axis; design factor 2 on the stowed moment; polyurethane E = 50 MPa (assumed); bracket and stop block 6 mm aluminum angle and bar, 6063-T6, 170 MPa minimum yield (decided 2026-10-02); solenoid 0.06 kg and each spiral preload spring 0.08 kg (assumed) | HLT-DDR-002 N1, N2; HLT-DEC-001; engineering judgment |
| Drives | NMRV030-class 50:1 worm gearbox: rated output 17 N·m and backlash 1° as listed by [StepperOnline](https://www.omc-stepperonline.com/nmrv30-worm-gearbox); maximum 22 N·m as listed for a Motovario 50:1 unit ([RS](https://my.rs-online.com/web/p/gearboxes/2166494)); mass about 1.2 kg (typical of the frame size, to confirm); worm efficiency 0.4; NEMA17 48 mm motor 0.36 kg | Supplier listings; mass assumed |
| Materials | Steel E = 200 GPa, G = 80 GPa, pipe yield 240 MPa (ASTM A53 grade B); printed ASA E = 1.8 GPa, 1.07 g/cm³ at 60 % infill; aluminum E = 69 GPa, 2.7 g/cm³; bronze 8.8 g/cm³; aluminum composite panel 5.5 kg/m²; glass 2,500 kg/m³; EPDM edge channel 1.3 g/cm³ (assumed) | Typical values |
| Calibration | Mount model with five unknowns: azimuth and elevation zero offsets, two base tilts and mirror cant on the torque tube. User jogs the spot to the target within 0.05° per axis (normal) at each point. True errors drawn at random: azimuth ±10°, elevation ±3°, tilts and cant with 1° and 0.3° standard deviation. 120 trials per case | Monte Carlo simulation |
| Power | Idle 0.4 W (ESP32 light sleep, RTC, drivers off); one motor at 5 W for 1 s per 30 s update; stow at 3.8 W (two coils at 1.0 A in 1.5 Ω, driver 0.3 W, ESP32 0.5 W) | Typical module data |

## A. Optics at the design point (R1, R2, R8)

The edge channel's front lip covers 3 mm of the glass all round, leaving a clear aperture of 0.353 m² [A1]. The mirror intercepts 800 W/m² x 0.353 m² x 0.848 = 239 W. After reflectance and soiling 211 W leave the mirror, 207 W arrive at the outside of the glazing and 155 W enter the room [A2]. That is about 14,770 lm and a mean added illuminance of about 490 lx over 12 m² [A3]. R1 (200 W) and R2 (300 lx) are met. The beam carries 0.88 to 0.93 of the DNI; a flat mirror does not concentrate [A4].

The spot is the projected mirror outline plus the sun's 0.53° angular diameter. At 10 m it is about 0.64 m square, and a 0.5° beam error moves it 87 mm, so spot plus error on both sides is 0.81 m and fits a 1.0 m wide window. At 20 m the figure is 1.08 m and the beam spills [A5]. The largest distance at which spot plus 0.5° error fits a 1.0 m wide window is 17.0 m [A6]. R8 (3 to 20 m) is met mechanically; above about 17 m a wider target is needed.

## B. Daily energy at reference sites (R3)

The TRL 2 figure used a generic day (6 h, mean DNI 650 W/m², mean cosine 0.80) and gives 0.95 kWh at the window and 0.71 kWh through the glazing with the clear aperture [B1]. The hourly model below replaces it with sun geometry, clear-sky DNI, shading by the house and the angle at which the beam strikes the glazing.

*Table 2. Clear-day energy through the glazing at three illustrative sites, 45° N [B2].*

| Site | Mirror position (east, north of window) | Distance | Glazing incidence (τ) | Day | Sunlit tracking | Mean cosine | At window | Into room | Peak into room |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 6 m, 8 m | 10.0 m | 37° (0.73) | 21 Dec | 4.8 h | 0.83 | 0.67 kWh | 0.49 kWh | 149 W |
| A | 6 m, 8 m | 10.0 m | 37° (0.73) | 1 Feb | 8.3 h | 0.86 | 1.35 kWh | 0.98 kWh | 163 W |
| B | 8 m, 5 m | 9.5 m | 58° (0.61) | 21 Dec | 5.5 h | 0.75 | 0.65 kWh | 0.40 kWh | 96 W |
| B | 8 m, 5 m | 9.5 m | 58° (0.61) | 1 Feb | 6.2 h | 0.73 | 0.81 kWh | 0.50 kWh | 106 W |
| C | 0 m, 15 m | 15.0 m | 3° (0.75) | 21 Dec | 8.4 h | 0.95 | 1.31 kWh | 0.98 kWh | 159 W |
| C | 0 m, 15 m | 15.0 m | 3° (0.75) | 1 Feb | 9.4 h | 0.93 | 1.61 kWh | 1.21 kWh | 173 W |

At reference site A the unit delivers 0.491 kWh on the solstice and 0.984 kWh on 1 February [B3]. R3 (0.5 kWh on a clear winter day) is **at risk**: site A now falls 2 % short on the shortest day (it met the target with no margin before the edge channel's front lip) and meets it from about mid-January, and site B, where the beam strikes the glazing at 58°, misses it. The best result comes from a mirror standing well out from the house on the window's axis (site C, 1.21 kWh on 1 February [B4]), where the house does not shade the mirror and the beam meets the glazing square on, but that site is 15 m away and close to the spill limit in section A. Siting matters more than any hardware choice; the siting survey (HLT-DDR-001, O3) should use this model.

## C. Mast and yoke stiffness (R4)

The 60.3 x 3.9 mm pipe has I = 276,079 mm⁴ and EI = 5.52 x 10¹⁰ N·mm² [C1]. At 8 m/s face-on the mirror force is 16.9 N, and the mast top tilts 0.040° [C2]. The same load on a 2.2 m 40 x 40 mm extrusion would tilt it 0.37° [C3], which confirms decision D1.

The yoke arms carry the wind force and react the hinge moment through the elevation gearbox. Version 0.3 used solid printed ASA arms 40 x 70 mm; that yoke cannot be printed in one piece, and HLT-DDR-003 replaced it with aluminum rectangular tube 40 x 60 x 2 mm, 357 mm from the crossbar top to the axis. Its slope at 8 m/s is 0.006°, against 0.036° for the printed arm over the same length [C4]. Mast twist from an assumed yaw moment of 0.85 N·m is 0.002° [C5].

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
| Yoke arm flex, 8 m/s | 0.006° | [C4] |
| **Root sum square** | **0.148°** | **0.30° beam against 0.5°** |

With the 95th percentile calibration residual (0.23°) the beam error is 0.50°, exactly at the limit [D5]. The budget also depends on a preload: the listed backlash of the gearbox is 1°, and if the wind reverses the load, half of it can appear at the mirror, giving 1.04° beam error [D6]. The mirror's center of mass sits 12.5 mm in front of the elevation axis, a gravity moment of up to 0.78 N·m [H4], so a preload of more than 2.9 N·m (operating hinge moment 2.1 N·m plus imbalance) is needed at 8 m/s [H5]. The decided spiral preload spring of about 3 N·m on each axis (HLT-DDR-002 N2, BOM line 16) needs about 0.29 N·m at the motor with wind and imbalance [H5], within a 48 mm NEMA17's holding torque but with little margin at speed. The elevation spring biases the mirror toward stow, so it never opposes a stow. R4 remains **at risk**: the typical beam error is 0.30°, but the 95th percentile of calibration sits at the 0.5° limit.

Calibration hands-on time by task analysis is 19 min for four points (5 min setup, 3 min per point, 2 min to fit and save) [G1], and the points span about 4 h of one day [G2]. Four points over about 4 h are now the default (HLT-DDR-002 N6), and R7 now reads "30 min or less of hands-on time, spread over one clear day" (N4), so R7 is **met**.

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

The weak link remains the elevation gearbox. With the decided storm awareness (D2), the controller stows when the anemometer sees a 15 m/s gust or the forecast predicts one; the hinge moment at the trigger is 7.4 N·m, within the 17 N·m rating [E5]. In stow, the assumed stowed hinge moment at 35 m/s is 24.3 N·m, above both the 17 N·m rating and the 22 N·m listed maximum [E2]; the rating is reached at a 29 m/s gust [E3]. Without a stow latch R9 would not be met: the gearbox would carry 2.3 N·m more than its listed maximum [E6] (the v0.1 result). On 2026-09-25 Amish decided on stow stops on the yoke that carry the stowed hinge moment in both directions (HLT-DDR-002 N1). A fixed stop can only resist one direction on an axis that must turn into the stow, so the design uses a stop and a latch together:

- A steel lug on the -X end of the torque tube, between the mirror edge and the -X arm, lies along -Y when the mirror is face-down.
- An aluminum bracket (6 mm angle, decided 2026-10-02) on the -X arm carries a 3 mm polyurethane (90A) pad on a stop block below the stowed lug, which takes the moment in the stowing direction, and a sliding steel pawl above it (HLT-DDR-003), which the lug pushes aside on the way into stow and which then takes the moment in the other direction. The latch engages without power, so a power-loss stow on the supercapacitor reserve also latches.
- A 12 V pull solenoid pulls the pawl back out of the lug's path for a few seconds when the unit leaves stow; its return spring pushes the pawl out again; it draws no standby power.
- After latching, the firmware backs the elevation worm off to the middle of its 1° backlash, so the worm teeth do not touch while the pad compresses.

The latch is designed for 48.6 N·m, twice the assumed stowed moment, which covers a stowed hinge moment coefficient up to 0.30 [E7]. This is the check against option C: a published stowed coefficient for small heliostats would have to exceed twice the value assumed here before the latch is overloaded. At that load the contact force is 884 N, the pad stress 4.6 MPa and its deflection 0.28 mm, less than the 0.48 mm the lug can move before the worm teeth touch, the sliding 12 x 8 mm pawl sees 90 MPa in bending against a 275 MPa yield, and each of the two M6 bracket screws carries up to 1.23 kN in shear [E8]. The pawl's moment, 11.5 N·m at the design load, bends the aluminum bracket leg across its 53 mm section at the pawl slot to 36 MPa, a factor of 4.7 on the 170 MPa minimum yield of 6063-T6; at 6 mm the leg is 1.16 times as stiff in bending as the 4 mm steel bracket it replaces, so the pad, not the bracket, sets how far the lug moves [E9]. The gearbox therefore carries no stowed moment, and R9 is **met** on paper. The stowed coefficient and the polyurethane modulus are still assumptions, and the case of a unit caught face-on (40.5 N·m) still exceeds the gearbox, so the stow must not fail.

## F. Stow on power loss (R10)

A worst-case stow turns the elevation axis 180° at 10°/s in 18 s, plus 5 s to detect the loss, and uses 87 J at 3.8 W [F1]. Five 2.7 V, 25 F supercapacitors in series (5 F) charged to 11.7 V and used down to 7.0 V hold 187 J after 85 % conversion, a margin of 2.1, with 2.34 V per cell against the 2.7 V rating [F2]. The stow always turns the normal downward. From site A at 11:00 on 21 December the beam starts 4.0° below the horizon and never rises above it; the reflection ends after 7.7 s, and for about 2.8 s the beam crosses the ground between the target and a point 3 m from the mast [F4]. The stow finishes in 23 s, within 60 s, and the latch engages without power. R10 now allows the beam to move only downward, toward the ground, during a stow (HLT-DDR-002 N5), so R10 is **met**.

## G. Calibration time (R7)

See section D and [G1], [G2].

## H. Mass and balance (R13)

Masses come from the volumes of the model's separate parts (HLT-DDR-003). The mirror assembly weighs 6.34 kg: glass 2.70, panel 1.98, torque tube 0.31, ribs 0.55, trunnion end blocks, stubs and bolts 0.44, adhesive and film 0.20, and the EPDM edge channel decided on 2026-10-02, 0.16 kg for about 2.2 m fitted [H1]. The aluminum tube yoke with its gussets, bolts, printed plugs and bushes weighs 2.27 kg (the printed yoke of v0.3 was 2.72 kg); each drive 1.69 kg (gearbox 1.2 kg assumed); the turntable disc, hub, shaft and thrust washer 0.51 kg [H2]. The stow stop and latch add 0.33 kg, with the bracket and stop block in aluminum (0.09 kg, about 0.08 kg less than the same parts in steel, a little under the 0.1 kg expected when it was decided), and the two preload springs 0.16 kg [H3]. The total on the mast top is 12.99 kg against the 13 kg limit decided on 2026-09-25 (HLT-DDR-002 N3), a margin of 0.01 kg [H3], so R13 is **met**, very thinly and on assumed gearbox, spring and solenoid masses: the edge channel uses up more than the aluminum bracket saves. Decided on 2026-10-02: if the weighed head at TRL 4 exceeds 13 kg, R13 is relaxed slightly rather than the guard dropped. The head now goes on the mast in two lifts from a platform: the yoke with its elevation drive, latch, disc and hub, 4.48 kg, then the mirror assembly, 6.34 kg [H3]. The TRL 2 estimate of about 8 kg assumed small generic NEMA17 worm gearboxes without a rating and a 0.8 kg yoke; the rated NMRV030-class gearboxes and the stiffer arms of section C add about 4.5 kg. The mast pipe adds 9.2 kg and the cap plate 1.6 kg. Installation in 4 h by two people is not verifiable at TRL 3.

## I. Power (R14)

Average draw is 0.60 W: idle 0.4 W, moves 0.17 W and 0.029 W in the stow reserve's balancing resistors, about 14 Wh a day [I1]. R14 (3 W) is met.

## J. Cost (R15)

Value-engineering target: USD 455 (`budget_usd`, a hypothetical control target, not a limit). Estimated cost of the constructable design: USD 499 (USD 44 over the target) [J1]. The BOM has 17 lines, all priced. The parts added to make the design constructable (HLT-DDR-003) repriced lines 2, 3, 5, 6, 9, 13, 14 and 17, from USD 451 to USD 492; the decisions of 2026-10-02 add the edge channel to line 1 (USD 6), the clear lid to line 9 (no change) and the aluminum bracket to line 17 (USD 1), to USD 499 [J2]. R15 is reported as over the value-engineering target; the cost drivers and savings worth trying are in the design decisions register (HLT-DEC-001). Tools, printer time and shipping are not included.

## K. Results

The yoke sweeps: at site A the normal stays within 46° of the target direction on the solstice, inside the ±135° range; the mirror clears the arms by 20 mm and the crossbar by 56 mm, so a face-down stow clears the yoke (the edge channel, 2.5 mm proud of the glass edge, still clears the crossbar by more than 40 mm in the model check); the stow lug runs 3 mm outside the mirror edge and 9 mm inside the -X arm [K1].

*Table 6. Requirement status, not met and over the target first [K2, K3].*

| ID | Requirement | Value | Target | Status |
| --- | --- | --- | --- | --- |
| R3 | Daily energy | 0.49 kWh (21 Dec) and 0.98 kWh (1 Feb) at site A; 0.40 kWh at site B on 21 Dec | 0.5 kWh or more on a clear winter day | At risk |
| R15 | Cost | USD 499 estimated, USD 44 over the target | USD 455 value-engineering target (a hypothetical control target) | Over the value-engineering target |
| R4 | Pointing | 0.30° beam typical, 0.50° at the 95th percentile, with the decided preload springs; 1.04° without preload | 0.5° beam up to 8 m/s | At risk |
| R12 | Outdoor life | ASA, galvanized steel, glass with backing film, by selection | -20 to +45 °C, UV, corrosion, 10 years | Not verifiable at TRL 3 |
| R1 | Redirected sunlight | 207 W at the glazing | 200 W or more | Met |
| R2 | Daylight | 492 lx mean added (utilization 0.4 assumed) | 300 lx or more | Met |
| R5 | Sensorless tracking | Time, location and target only; Hall switches for homing, anemometer for weather | No sun sensor or camera | Met |
| R6 | Timekeeping | 32 s after 6 months | 60 s or less | Met |
| R7 | Calibration | 19 min hands-on for four points over about 4 h of one day | 30 min or less of hands-on time, over one clear day; no survey instrument | Met |
| R8 | Working range | Mechanical range met; spot plus error fits a 1.0 m window up to 17 m | 3 to 20 m; ±135°; -90 to +90° | Met |
| R9 | Wind | Stowed moment 24 N·m at 35 m/s carried by the stow stop and latch (designed for 49 N·m), not the gearbox; 7.4 N·m at the stow trigger; mast 87 MPa worst case | Hold R4 to 8 m/s; survive 35 m/s in stow | Met |
| R10 | Safe beam | Stow in 23 s on stored energy (margin 2.1); beam moves only downward; latch engages without power | Target or ground within 3 m when stowed; only downward during a stow; stow within 60 s | Met |
| R11 | Electrical safety | 12 V SELV outdoors, IP65 box, listed indoor adapter | SELV, IP65, listed adapter | Met |
| R13 | Mass and install | 12.99 kg on the mast top, 0.01 kg margin; heaviest lift 6.34 kg | 13 kg or less; two people, hand tools, 4 h | Met (install time not verifiable at TRL 3) |
| R14 | Standby power | 0.60 W average | 3 W or less | Met |

Totals: 0 not met, 1 over the value-engineering target, 2 at risk, 1 not verifiable at TRL 3, 11 met [K3].

## Checks against earlier figures

- **Optical chain.** TRL 2 quoted 245 W intercepted and about 212 W at the glazing; the script gives 244 W and 211 W [A2]. HLT-PRC-001 and the flow diagram now use the script's values.
- **Spill distance.** TRL 2 said spill rises above about 15 m; with 0.5° error and a 1.0 m window the limit is 16.8 m [A6].
- **Daily energy.** TRL 2 quoted about 0.7 kWh from a generic day; the generic day reproduces 0.73 kWh [B1], but the hourly site model gives 0.50 kWh at site A on the solstice [B3]. Documents now quote the site figures.
- **Clock.** TRL 2 quoted about 32 s; the script gives 31.5 s [D1].
- **Pointing.** TRL 2 quoted 0.17° normal and 0.34° beam with a 0.10° calibration residual, 0.10° backlash and 0.05° yoke flex. The budget in v0.3 was 0.153° normal and 0.31° beam with printed 40 x 70 mm arms; with the aluminum tube arms of HLT-DDR-003 it is 0.148° normal and 0.30° beam [D5], still only with four-point calibration and preloaded drives.
- **Wind.** The face-on figures match TRL 2 (40 N·m hinge moment; mast stress now 87 MPa including drag on the pipe, up from 78 MPa). Stowed loads were not estimated at TRL 2 and are new.
- **Mass.** TRL 2 quoted about 8 kg on the mast top; now 12.5 kg [H3].
- **Power.** 0.6 W, unchanged [I1].
- **Cost.** TRL 2 quoted $391 against $400; v0.1 of this note gave $425 against the decided $430; with lines 16 and 17 it is now $451, against $455 after the 2026-09-26 top-up [J1].
- **Changes in v0.2 (HLT-DDR-002).** R9 moved from not met (24.3 N·m on the gearbox against 22 N·m maximum) to met (moment carried by the stow latch); R13 moved from not met (12.5 kg against 10 kg) to met (12.95 kg against 13 kg); R7 and R10 moved from at risk to met after rewording; R15 moved from met ($425) to not met ($451 against $430). R3, R4 and R12 are unchanged.
- **Changes in v0.3 (budget top-up).** `BUDGET` in `sizing.py` is $455; R15 moves from not met ($451 against $430) to met ($451 against $455). No other figure changes.
- **Changes in v0.4 (design for construction, HLT-DDR-003).** Arm flex 0.040° to 0.006° [C4]; root sum square 0.153° to 0.148° (beam 0.31° to 0.30°) [D5]; center of mass 13.7 to 12.4 mm in front of the axis [H4]; mast-top mass 12.95 to 12.94 kg [H3]; crossbar clearance 46 to 56 mm [K1]; latch pawl and bracket screws checked [E8]; cost USD 451 to USD 492, now reported against the USD 455 value-engineering target [J1]. No requirement moved between met, at risk and not met; R15 moved from met to over the value-engineering target.
- **Changes in v0.5 (decisions of 2026-10-02).** Clear aperture 0.36 to 0.353 m² inside the edge channel's front lip [A1]; at the glazing 211 to 207 W and into the room 159 to 155 W [A2]; site A on 21 Dec 0.501 to 0.491 kWh [B3]; spill limit 16.8 to 17.0 m [A6]; latch bracket bending checked in aluminum [E9]; mirror assembly 6.18 to 6.34 kg [H1]; latch 0.43 to 0.33 kg and mast-top mass 12.94 to 12.99 kg [H3]; center of mass 12.4 to 12.5 mm [H4]; cost USD 492 to USD 499 [J1]. No requirement changed status; R3 stays at risk but site A now misses the target on the solstice, and R13 stays met with a 0.01 kg margin.
