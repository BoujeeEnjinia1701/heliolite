# HelioLite

**Area:** CleanTech · **Status:** Concept · **Prototype budget:** about $400 USD · **Difficulty:** 3 of 5

Two-axis mini heliostat on a mast that redirects sunlight to a fixed target, using a sun-position algorithm with no sensors.

## Problem

North-facing rooms and greenhouses lack daylight and solar heat.

## Concept

Two-axis mini heliostat on a mast that redirects sunlight to a fixed target, using a sun-position algorithm with no sensors.

Full design precis: [docs/02-concept.md](docs/02-concept.md)

## Key components

- Glass mirror 60 x 60 cm
- NEMA17 steppers with worm gears (2)
- ESP32 with RTC
- Aluminum extrusion mast
- Printed gimbal

The working bill of materials is in [bom/bom.csv](bom/bom.csv).

## Safety

> Concentrated sunlight can cause eye injury and fire. Never aim at people, vehicles or aircraft.

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

## Licenses

- **Hardware** (CAD, drawings, BOM, electronics): [CERN-OHL-S v2](LICENSE)
- **Software** (firmware, scripts, notebooks): [MIT](LICENSE-SOFTWARE)

Part of the open hardware portfolio at [amishchadha.com](https://amishchadha.com).
