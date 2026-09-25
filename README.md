# HelioLite

![TRL 2](https://img.shields.io/badge/TRL-2%20of%209-0F766E) ![Hardware: CERN-OHL-S-2.0](https://img.shields.io/badge/hardware-CERN--OHL--S--2.0-111827) ![Software: MIT](https://img.shields.io/badge/software-MIT-111827)

**Area:** CleanTech · **TRL:** 2 of 9 (concept formulated) · **Prototype budget:** about $400 USD · **Difficulty:** 3 of 5

Two-axis mini heliostat on a mast that redirects sunlight to a fixed target, using a sun-position algorithm with no sensors.

![HelioLite concept](media/hero.png)

[Interactive 3D model](media/viewer.html) · [Concept blueprint (PDF)](media/concept-blueprint.pdf) · [Review note](docs/REVIEW.md)

## Problem

North-facing rooms and greenhouses lack daylight and solar heat. On a clear winter day a 0.36 m² mirror can send about 160 W of sunlight (about 15,000 lm) through a window, enough to add roughly 500 lx to a small room, while its heat contribution is modest (estimates in the [problem statement](docs/01-problem.md) and [precis](docs/02-concept.md)).

## Concept

Two-axis mini heliostat on a mast that redirects sunlight to a fixed target, using a sun-position algorithm with no sensors.

An ESP32 computes the sun's position from a real-time clock and the site location every 30 s, and two worm-driven steppers turn the mirror so its normal bisects the directions to the sun and to the target. A phone-based calibration fits the mount alignment, and the mirror stows face-down at night.

Full design precis: [docs/02-concept.md](docs/02-concept.md)

## Key components

- Glass mirror 60 x 60 cm
- NEMA17 steppers with worm gears (2)
- ESP32 with RTC
- Mast: aluminum extrusion in the scaffold; a 60.3 mm steel pipe is proposed for stiffness (awaiting Amish)
- Printed gimbal

The working bill of materials is in [bom/bom.csv](bom/bom.csv).

## Safety

> **Safety:** The reflected beam is nearly as bright as the sun and can cause eye injury; several mirrors aimed at one spot can start a fire. Never aim at people, vehicles or aircraft. The gimbal moves with high torque, the mirror is glass 2 m above the ground, and the mast must be anchored and stowed before storms. Only 12 V DC runs outdoors. See the safety section of the [precis](docs/02-concept.md).

## Repository layout

| Folder | Contents |
| --- | --- |
| `docs/` | Problem, concept, requirements, calculations and design decisions |
| `cad/src/` | build123d Python source, the source of truth for all geometry |
| `cad/step/`, `cad/stl/` | Exported models for FreeCAD, other CAD tools and printing |
| `cad/drawings/` | 2D sketches and dimensioned drawings |
| `bom/` | Bill of materials |
| `electronics/` | KiCad schematics and PCB layouts |
| `firmware/` | Microcontroller code |
| `media/` | Renders, perspectives and photos |
| `build-log/` | Dated prototyping notes |

## Documentation

Controlled documents follow the portfolio [documentation standard](.kit/STANDARDS.md). Each carries a document ID (HLT-PRC-001 for the precis), a version and a revision history. Branded PDFs are built with `python .kit/render.py` and attached to GitHub Releases when a document is tagged, for example `HLT-PRC-001/v1.0`.

## Licenses

- **Hardware** (CAD, drawings, BOM, electronics): [CERN-OHL-S v2](LICENSE)
- **Software** (firmware, scripts, notebooks): [MIT](LICENSE-SOFTWARE)

Part of the open hardware portfolio at [amishchadha.com](https://amishchadha.com).
