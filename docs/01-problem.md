---
doc_id: HLT-PRB-001
title: HelioLite problem statement
project: HelioLite
doc_type: Problem statement
version: "0.4"
status: Draft
date: '2026-09-26'
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
  change: Populate to TRL 2 (users, context, siting, constraints, out of scope, cited prior work)
- version: "0.3"
  date: '2026-09-25'
  author: Amish Chadha
  change: TRL 3 update; budget $430 and no-sun-sensor constraint as decided by Amish (HLT-DDR-001); siting findings from HLT-CAL-001; open items listed; EN 17037 sunlight citation corrected
- version: "0.4"
  date: '2026-09-26'
  author: Amish Chadha
  change: Stronger sources
---

# HelioLite problem statement

Rooms that face away from the equator (north-facing in the Northern Hemisphere) and the shaded back of many greenhouses never receive direct sun in winter, so they stay dim and cold while sunlight falls a few meters away. A small two-axis mirror that follows the sun can send that sunlight through a chosen window all day, but the heliostats on the market are either large power-plant or civic installations or discontinued consumer products. HelioLite aims to be a garage-buildable, open design at about $455 in parts.

## The problem

In the Northern Hemisphere a north-facing window sees only diffuse skylight. At 45° N the noon sun stands only about 21.6° above the horizon at the winter solstice (90° minus latitude minus 23.44°), so neighboring buildings, trees and the house itself also shade many south, east and west openings for much of the winter. The result is:

1. **Too little daylight.** People in the United States spend, on average, about 90 % of their time indoors ([US EPA](https://www.epa.gov/report-environment/indoor-air-quality)), so a room without winter sun leaves its occupants with little daylight for much of the season.
2. **No passive solar gain.** Those rooms get no free winter heat, and greenhouse beds on the north side grow slowly.
3. **Electric light as the fallback.** Occupants turn on lamps during the day.

A heliostat is a mirror turned by two motors so that the reflection of the sun stays on a fixed target as the sun moves. The physics is well proven. What is missing is a small, low-cost, repairable unit that a homeowner, school or community garden can build, site and calibrate without special tools, and that is safe to run next to people.

## Users and context

| User | Need | Context |
| --- | --- | --- |
| Homeowner or tenant with a dark north room | Sunlight in a living room, kitchen or home office on clear winter days | Suburban yard or courtyard, target window 3 to 20 m away |
| Small greenhouse or community garden | Light and some heat on shaded beds in winter and spring | Hoop house or lean-to, target is a glazed end wall |
| School or makerspace | A teaching project in astronomy, optics and control that does real work | Rooftop or yard, supervised use |
| Maker who builds and maintains it | Buy common parts, print the gimbal, flash firmware, calibrate from a phone | Home workshop, hand tools, a 3D printer |

### Operating environment

- **Latitude:** 30° to 55° N (and the mirror image in the Southern Hemisphere). Winter sun elevations at noon from about 12° to 37°.
- **Sun:** direct normal irradiance (DNI) of about 700 to 900 W/m² on clear winter days; nothing useful on overcast days.
- **Weather:** outdoor all year, -20 to +45 °C ambient, rain, snow, hail, UV and wind gusts that can exceed 30 m/s (108 km/h) in storms.
- **Siting:** the mirror must see the sun during the useful hours and see the target. A unit placed directly north of a house must stand outside the house's winter shadow (about 15 m for 6 m eaves at 45° N), so many sites will use a side yard, a roof or a garage.
- **Power:** a 12 V supply fed from an indoor outlet; Wi-Fi often available but not guaranteed.
- **People:** the beam crosses gardens, paths and windows where people, pets, drivers and neighbors may look into it.

## Constraints

- Garage-buildable prototype, about $455 USD in parts (`project.yaml` budget, raised from $400 to $430 by Amish on 2026-09-25, HLT-DDR-001 D4, then to $455 by a top-up he approved on 2026-09-26, HLT-DDR-002 P1).
- Open-loop tracking from time and location (a sun-position algorithm), with no sun sensor or camera. Homing switches for the axes and a weather anemometer for storm stow are allowed (HLT-DDR-001 D2, D5).
- Only extra-low voltage (12 V DC) outdoors; the mains adapter stays indoors.
- Parts available from general hardware, electronics and 3D-printing suppliers; one mirror cut to size by a local glazier.
- Install by two people with hand tools, without a crane or permanent roof penetration.
- Must not create a hazard to people, vehicles or aircraft from the reflected beam, including when stowed or unpowered.

## Out of scope

- Concentrating sunlight for heating water, cooking or power (a flat mirror only redirects about one sun).
- Arrays of heliostats aimed at one target.
- Light pipes, fibers or daylight-redirecting films inside the building.
- Commercial product certification.

## Prior work

- **Civic heliostats.** Since 2013, three computer-driven heliostats with 51 m² of mirror in total, about 450 m above the town of Rjukan, Norway, reflect sunlight onto an ellipse of about 600 m² in the market square during the months when the valley is in shadow ([Visit Rjukan](https://visitrjukan.com/en/p/the-giant-sun-mirrors-in-rjukan/)). The project shows the social value of redirected winter sun at a scale far above a house.
- **Home heliostats.** The Sunflower home heliostat was marketed around 2012 as a self-powered unit redirecting up to about half a square meter of sunlight, described as up to 500 W, into a home ([Inhabitat](https://inhabitat.com/easy-to-use-sunflower-heliostat-provides-up-to-500-watts-of-sun-energy-for-homes/); [Solar Power World](https://www.solarpowerworldonline.com/2012/04/home-heliostats/)). It confirms the use case; it does not appear to be widely available today, and its design is not open.
- **Open maker heliostats.** Open Arduino projects compute the sun's position from a clock and drive a mirror in altitude and azimuth, for example [jremington/Arduino_heliostat](https://github.com/jremington/Arduino_heliostat) (steppers with gear reduction, about 0.1° step resolution, and a warning that the Arduino's own crystal is not accurate enough for long unattended tracking) and the Cerebral Meltdown [Open Sun Harvesting Project](https://github.com/FrodgE/sun-harvester). The [Open Source Ecology heliostat page](https://wiki.opensourceecology.org/wiki/Heliostat) collects further examples. HelioLite builds on this approach but targets an outdoor-rated, calibrated, safe unit rather than a bench model.
- **Sun-position algorithms.** NREL's Solar Position Algorithm computes the sun's position with an uncertainty of ±0.0003° for the years -2000 to 6000 ([Reda and Andreas, NREL/TP-560-34302](https://www.nrel.gov/docs/fy08osti/34302.pdf); [NREL MIDC SPA page](https://midcdmz.nrel.gov/spa/)). Grena's five lighter algorithms, valid for 2010 to 2110, have maximum errors from 0.19° down to 0.0027° and suit small microcontrollers ([Grena 2012, Solar Energy 86](https://www.sciencedirect.com/science/article/abs/pii/S0038092X12000400)). Either is far more accurate than the mechanics of a low-cost unit.
- **Heliostat wind loads.** Wind-tunnel data and design methods for ground-mounted heliostats are given in Sandia report SAND92-7009 ([Peterka and Derickson 1992](https://www.osti.gov/biblio/7105290)) and updated by the Heliostat Consortium ([NREL 2025](https://docs.nrel.gov/docs/fy25osti/96375.pdf)). HelioLite uses these only for first-order estimates.
- **Glare and eye hazard.** Sandia's analytical method for glint and glare from solar mirrors relates retinal irradiance and subtended angle to after-image and retinal burn risk ([Ho, Ghanbari and Diver 2011](https://www.sandia.gov/app/uploads/sites/167/2025/03/Methods_Ho_2011.pdf)). It is the basis for the beam-safety requirements in HLT-REQ-001.

## Open questions

- Which first site and user (a house with a north room, a greenhouse or a school)? This sets latitude, distance to target and siting. Proposed, awaiting Amish (HLT-DDR-001, O1); co-design partners stay open by Amish's instruction.
- How common is a site where the mirror can see the winter sun and the north window at the same time, without standing in the house's shadow? The hourly model in HLT-CAL-001 (section B) shows the answer matters more than any hardware choice: the same unit delivers 0.40 to 1.00 kWh on the solstice at three illustrative sites. A short siting survey of real yards is needed (O3).
- Is daylight or heat the main benefit users value? The calculations suggest daylight is substantial (about 500 lx) and heat is modest (about 150 W while sunny).
- What local rules on glare, setbacks and structures on a lot or roof apply at the first site (O2)?

## User research and co-design

This design is for households and growers the author does not know yet, so requirements should be checked with them.

- [ ] Identify two or three candidate sites (house, greenhouse, school) and their owners
- [ ] Record latitude, target size and distance, shading, and where people walk
- [ ] Ask users whether they want light, heat or both, and for how many hours
- [ ] Revise requirements (REQ) from findings before freezing the design
