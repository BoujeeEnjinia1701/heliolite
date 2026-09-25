---
doc_id: HLT-PRC-001
title: HelioLite design precis
project: HelioLite
doc_type: Design precis
version: "0.2"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-24'
  author: Amish Chadha
  change: Initial scaffold
- version: "0.2"
  date: '2026-09-25'
  author: Amish Chadha
  change: Populate to TRL 2 (architecture, first-order numbers, pointing and wind budgets, safety, media)
---

# HelioLite design precis

HelioLite is a 600 x 600 mm glass mirror on a two-axis, worm-driven gimbal at the top of a 60.3 mm steel mast. An ESP32 computes the sun's position from a real-time clock and the site location, and turns the mirror so its normal bisects the directions to the sun and to a fixed target window. First-order numbers suggest about 160 W of sunlight and a mean of about 500 lx extra light in a 12 m² room at the design point, about 0.7 kWh through the glazing on a clear winter day, and a pointing error budget of about 0.34° against a 0.5° target, for about $391 in parts against the $400 budget. The concept does not yet meet the wind-survival (R9) and safe-on-power-loss (R10) requirements.

![Hero render](../media/hero.png)

*Figure 1. HelioLite on its mast with a 1.75 m person for scale. The house wall and target window are context and are drawn closer than a real site so the heliostat stays legible.*

## How it works

1. **Know the time and place.** A DS3231 real-time clock (±2 ppm from 0 to 40 °C, about ±1 min per year ([Adafruit DS3231 guide](https://learn.adafruit.com/adafruit-ds3231-precision-rtc-breakout/overview))) keeps UTC. When Wi-Fi is available the ESP32 corrects it by network time once a week. Latitude, longitude and the target direction are entered once at setup.
2. **Compute the sun.** Every 30 s the ESP32 runs a published sun-position algorithm, Grena's algorithm 5 (maximum error 0.0027° for 2010 to 2110 ([Grena 2012](https://www.sciencedirect.com/science/article/abs/pii/S0038092X12000400))) or NREL SPA (±0.0003° ([Reda and Andreas](https://www.nrel.gov/docs/fy08osti/34302.pdf))), to get the unit vector **s** toward the sun. There is no sun sensor.
3. **Aim the mirror.** The required mirror normal is **n** = (**s** + **t**) / |**s** + **t**|, where **t** is the unit vector from the mirror to the target. A small mount model (north offset, mast tilt in two directions and the two axis zero offsets) converts **n** into azimuth and elevation steps.
4. **Move.** Two NEMA17 steppers on worm gearboxes turn the yoke in azimuth and the mirror in elevation. The worms are self-locking, so the drivers switch off between moves. Hall switches home each axis at start-up.
5. **Calibrate.** At setup the user opens a web page served by the ESP32, jogs the sun spot onto the target center at three or more times of day, and the firmware fits the mount model to those points. No survey instrument is needed.
6. **Stow.** At night, on a fault, or when a storm is expected, the mirror turns face-down. This sends no reflection anywhere, protects the glass from hail and dust, and presents the lowest wind load.

The sun moves about 15° per hour, so between 30 s updates it moves about 0.125° and the mirror normal needs about half of that. The mirror is balanced about the elevation axis, so the drives only overcome friction and wind.

![Energy flow](../media/flow.png)

*Figure 2. Instantaneous power from the sun to the room at the design point (DNI 800 W/m², 10 m to the target, 32° incidence), in W. All values are estimates.*

## Main components

Numbers match the exploded view (Figure 3) and `bom/bom.csv`.

Table 1. Main components.

| # | Component | Proposed choice | Notes |
| --- | --- | --- | --- |
| 1 | Mirror | 600 x 600 x 3 mm silvered glass, seamed edges, safety backing film | Cut by a local glazier; acrylic mirror is an option (lower optical quality) |
| 2 | Backing panel and torque tube | 4 mm aluminum composite panel bonded to the mirror, two ribs, 25 mm square aluminum torque tube with trunnions | Carries the elevation axis through the mirror's center of mass |
| 3 | Gimbal yoke | 3D-printed ASA base plate, crossbar and two arms, with heat-set inserts | Arms stand outside the mirror's sweep so it can rotate face-down |
| 4 | Elevation drive | NEMA17 stepper on a 50:1 worm gearbox | On the +X arm, drives the trunnion |
| 5 | Azimuth drive | NEMA17 stepper on a 50:1 worm gearbox, clamped to the mast top | Same part as item 4 |
| 6 | Azimuth turntable | Printed or aluminum disc on a radial and a thrust ball bearing | Carries the yoke and mirror |
| 7 | Mast | 60.3 mm (2 in) galvanized steel pipe, 1.71 m | Mirror center about 2.2 m above ground. Proposed in place of the scaffold's aluminum extrusion; see Key design choices |
| 8 | Ground anchor | Ground screw for 60 mm posts or a concrete footing, with a flange | Resists about 0.7 kN·m in a 35 m/s gust |
| 9 | Controller box | ESP32, DS3231 RTC, two TMC2209 stepper drivers, 12 V to 5 V buck, IP65 box | On the mast at about 1.2 m, reachable for service |
| 10 | Homing switches | Two Hall switches with magnets | Axis reference only; not sun sensors |
| 11 | Cabling | Motor leads, 2-core outdoor 12 V cable, cable glands | 12 V feed from indoors |

A listed indoor 12 V, 3 A power adapter and the fasteners are in the BOM without callouts.

![Exploded view](../media/exploded.png)

*Figure 3. Exploded view with numbered callouts matching the BOM.*

## First-order numbers

All values are estimates for concept review and will be checked at TRL 3.

### Optical power and daylight

Assumptions: DNI 800 W/m²; cosine factor 0.85 (incidence 32°); reflectance 0.93 clean and soiling factor 0.95; 2 % of the beam spills past a 1.0 x 1.2 m window at 10 m; double glazing transmits 75 %; direct sunlight about 95 lm/W; utilization factor 0.4 in a 3 x 4 m room.

Table 2. Power and daylight at the design point.

| Quantity | Estimate | Basis | Requirement |
| --- | --- | --- | --- |
| DNI times mirror area | 288 W | 800 W/m² x 0.36 m² | |
| Intercepted (after cosine) | 245 W | x 0.85 | |
| Reflected beam | 216 W | x 0.93 x 0.95 | |
| At the outside of the glazing | about 212 W | 2 % spill | R1 (200 W) met, small margin |
| Into the room | about 159 W | x 0.75 | |
| Luminous flux into the room | about 15,000 lm | 159 W x 95 lm/W | About ten 1,500 lm LED lamps |
| Mean added illuminance, 12 m² room | about 500 lx | 15,000 lm x 0.4 / 12 m² | R2 (300 lx) met |
| Beam irradiance at the target | about 0.6 to 0.9 sun | A flat mirror does not concentrate | See Safety |

### Daily energy and heat

On a clear winter day with six useful tracking hours, a mean DNI of 650 W/m² and a mean cosine factor of 0.80, the beam delivers about 0.97 kWh at the window and **about 0.7 kWh through the glazing** (R3 met). A small, poorly insulated room may lose 0.5 to 1 kW in cold weather, so HelioLite gives a noticeable but modest share of daytime heat, of the order of 10 to 30 % while the sun is out. Its main benefit is light. On overcast days it delivers nothing.

### Beam size and spill

A flat mirror's reflected spot is roughly the mirror's projected outline blurred by the sun's angular diameter of about 0.53° (9.3 mrad) and by pointing error. At 10 m the blur adds about 93 mm, so the spot is about 0.55 x 0.65 m and fits a 1.0 x 1.2 m window with room for pointing error. At 20 m the blur is about 190 mm and a 0.5° beam error moves the spot about 175 mm, so spill onto the wall rises and a larger target is needed.

### Pointing error budget

The target is 0.5° for the beam, which is 0.25° for the mirror normal, because a mirror tilt of x turns the beam by 2x.

Table 3. Pointing error budget for the mirror normal (estimates).

| Source | Normal error | Basis |
| --- | --- | --- |
| Sun-position algorithm | under 0.003° | Grena algorithm 5 or SPA |
| Clock, 6 months without network time | about 0.07° | ±2 ppm, about 32 s; the sun moves 0.25°/min; halved for the normal |
| Mount model residual after calibration | about 0.10° | Fit to three or more jogged points |
| Worm gear backlash | about 0.10° | Approach every move from the same side; balance keeps a light preload |
| Step resolution | about 0.002° | 1.8° step, 16 microsteps, 50:1 worm |
| Mast bending at 8 m/s wind | about 0.04° | 17 N on the mirror, steel pipe EI about 5.5 x 10¹⁰ N·mm², 2.2 m lever |
| Gimbal and yoke flex | about 0.05° | Printed ASA, to be checked |
| **Root sum square** | **about 0.17°** | **Beam about 0.34°, R4 (0.5°) met on paper** |

The same wind on a 2.2 m, 40 x 40 mm aluminum extrusion mast (I about 9 x 10⁴ mm⁴) would tilt the top by about 0.37°, more than the whole budget. This is why a stiffer mast is proposed.

### Wind loads

Assumptions: air density 1.225 kg/m³; flat plate force coefficient 1.2 when face-on; hinge moment coefficient about 0.25 of force times chord, in the range reported for heliostats ([Peterka and Derickson 1992](https://www.osti.gov/biblio/7105290)). These are rough; stowed loads are lower but are not estimated here.

Table 4. Wind loads, worst orientation (estimates).

| Wind | Dynamic pressure | Force on mirror | Hinge moment | Mast base moment | Mast stress (60.3 x 3.9 mm pipe) |
| --- | --- | --- | --- | --- | --- |
| 8 m/s (operating) | 39 Pa | 17 N | 2 N·m | 37 N·m | 4 MPa |
| 20 m/s | 245 Pa | 106 N | 13 N·m | 233 N·m | 25 MPa |
| 35 m/s (survival) | 750 Pa | 324 N | 40 N·m | 713 N·m | 78 MPa, below 235 MPa yield |

The mast and anchor can carry the survival case with margin. The weak link is the gearboxes: generic NEMA17 worm gearboxes are often rated for a few N·m to about 10 N·m at the output, so a mirror caught face-on in a storm may back-drive or strip a gear. Stowing face-down cuts the load, but the unit must know to stow (R9 not met).

### Power and mass

- **Power:** the ESP32 in light sleep, the RTC and idle drivers draw about 0.4 W; each move runs one motor at about 5 W for under 1 s every 30 s. Average about 0.6 W, about 15 Wh per day (R14 met).
- **Mass:** glass 2.7 kg, backing and torque tube 2.6 kg, yoke 0.8 kg, drives 1.2 kg, turntable 0.5 kg: about 8 kg on the mast top (R13 met). The mast adds about 9 kg.

### Cost

Parts total about $391 (see `bom/bom.csv`), within the $400 budget with about $9 of margin (R15 met, thin).

## Key design choices

Every choice below is **Proposed, awaiting Amish**.

- **Mast material.** The scaffold listed an aluminum extrusion mast.
  - Option A: 60.3 mm galvanized steel pipe (about $35). About nine times the bending stiffness of a 40 x 40 extrusion, fits standard ground screws and post sockets, and meets the pointing budget.
  - Option B: 80 x 80 mm aluminum extrusion (about $70 to $90). Also stiff enough, lighter and easy to clamp to, but costs more and would break the budget.
  - Option C: 40 x 40 mm extrusion with guy wires. Cheap, but guys take yard space and trip people.
  - Recommendation: Option A. This changes a listed key component in the README. Proposed, awaiting Amish.
- **Tracking update and algorithm.** Update every 30 s with Grena algorithm 5; NREL SPA as an alternative if the ESP32 has time to spare. Proposed, awaiting Amish.
- **Calibration by jogged spot points** rather than a compass, inclinometer or GPS survey. Proposed, awaiting Amish.
- **Face-down stow** at night, on a fault and before storms, rather than face-up (which sends the beam into the sky toward aircraft) or edge-on. Proposed, awaiting Amish.
- **Storm awareness (R9).**
  - Option A: fetch a wind forecast over Wi-Fi and stow ahead of storms. No hardware, but depends on the network.
  - Option B: add a low-cost cup anemometer (about $20). Direct and local, but adds a sensor, which the pitch's "no sensors" was meant to exclude only for sun tracking.
  - Option C: a slip clutch so the mirror can weathervane. Protects the gears but loses position until re-homed.
  - Recommendation: A plus B, with the anemometer counted as a weather sensor, not a tracking sensor, and costed against the budget. Proposed, awaiting Amish.
- **Safe state on power loss (R10).** Option A: a supercapacitor bank (about $10 to $15) that stores enough energy to finish a face-down stow. Option B: accept the risk at supervised sites only. Recommendation: A. Proposed, awaiting Amish.
- **Power supply.** A listed indoor 12 V adapter with only SELV cable outdoors, rather than a solar panel and battery on the mast. Solar self-power (about 10 W panel and a small LiFePO4 battery) is possible for about $40 more but adds lithium cells and exceeds the budget. Proposed, awaiting Amish.
- **Glass mirror** rather than acrylic or aluminum-film mirror, for flatness and life, with a safety backing film against breakage. Proposed, awaiting Amish.

## Safety

> **Safety:** HelioLite redirects sunlight, moves under motor power, carries a glass mirror 2 m above the ground and stands in the wind. Treat the beam, the moving gimbal, the glass and the mast as hazards at every stage.

- **Eye injury and glare.** Looking into the reflected beam is like looking at the sun, at 0.6 to 0.9 of its brightness. A brief glance causes an after-image; staring can cause retinal injury ([Ho, Ghanbari and Diver 2011](https://www.sandia.gov/app/uploads/sites/167/2025/03/Methods_Ho_2011.pdf)). Site the unit so the beam path crosses no path, road, neighbor's window or flight approach; mount the mirror above head height; never aim at people, vehicles or aircraft; and make the firmware refuse any target that is not the calibrated one.
- **Beam sweep.** During slews, calibration and after a power loss the beam can pass across the surroundings. Slew with the mirror turned toward the ground where possible, stow face-down, and add stored energy for a stow on power loss (R10).
- **Concentration and fire.** One flat mirror does not concentrate sunlight, but several mirrors aimed at one spot, or a mirror bent concave by its mounting, can. Do not aim more than one unit at the same spot, and check the mirror for flatness after mounting.
- **Glass.** A broken mirror has sharp edges and can fall from 2 m. Use seamed edges and a safety backing film, wear cut-resistant gloves and eye protection when handling, and keep the mirror face-down in hail.
- **Moving machinery.** The worm drives turn slowly but with high torque (several N·m) and can trap fingers between the mirror, torque tube and yoke. Disable the drives before servicing and keep the gimbal above head height.
- **Mast and wind.** A falling mast or mirror can injure people. Use a rated ground anchor, check for buried services before driving a ground screw, and stow before storms. Two people install the mirror.
- **Electrical.** Only 12 V DC runs outdoors. The mains adapter stays indoors and must be a listed product; do not run mains to the mast.
- **Working at height.** Rooftop sites need fall protection and a structural check of the roof; they are not recommended for the first build.

## Open questions for TRL 3

- Choose the mast (Option A, B or C above) and confirm the pointing budget with a deflection calculation that includes the anchor and the yoke.
- Find worm gearboxes with a stated output holding torque of 40 N·m or more within budget, or add a brake or clutch.
- Decide how the unit knows to stow before a storm (R9) and how it stows on power loss (R10).
- Calculate hourly delivered energy over a winter day for two or three real sites, including shading.
- Specify the calibration routine and check it reaches 0.10° residual with three points.
- Survey typical yards to see how often a mirror can see both the winter sun and a north window.
- Check local rules on glare and structures for the first site.

Concept media: [blueprint sheet](../media/concept-blueprint.pdf), [interactive 3D model](../media/viewer.html).
