"""HelioLite concept media (TRL 3), built from the parametric model.

Run from the repo root:  python cad/src/concept_media.py
Main dimensions and interfaces from cad/src/model.py; not for fabrication.
Figures quoted below are printed by docs/04-calcs/sizing.py (HLT-CAL-001); tags in brackets.

Coordinates in mm, Z up, ground at Z = 0. The mast stands at the origin. The mirror
turns in azimuth about the mast axis and in elevation about a horizontal torque tube
close to its center of mass (13.7 mm offset, HLT-CAL-001 [H4]). The house wall with the target window is a
context part shown only in the hero render.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".kit"))
from build123d import Box, Pos
from concept import Part, render_all

# Geometry comes from the TRL 3 parametric model (cad/src/model.py); only above-ground parts are shown.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import parts as model_parts  # noqa: E402

parts = [Part(name, shape, color, bom, explode) for bom, name, shape, color, explode in model_parts(below_ground=False)]


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


# Context for the hero render: part of a north-facing house wall with the target window,
# drawn closer than a real site (about 2.2 m from the mast) so the heliostat stays legible. Not in the BOM.
WX = -2200.0
wall = box(WX - 200, WX, -1000, 1000, 0, 2700) - box(WX - 210, WX + 10, -500, 500, 900, 2100)
window = box(WX - 120, WX - 80, -500, 500, 900, 2100) - box(WX - 130, WX - 70, -450, 450, 950, 2050)
pane = box(WX - 105, WX - 95, -450, 450, 950, 2050)
context = [Part("House wall (context)", wall, "#E7E5E4"),
           Part("Target window (context)", window + pane, "#CBD5E1")]

render_all(
    parts, project="HelioLite", title="Two-axis mini heliostat concept", dwg_no="HLT-DWG-010",
    date="2026-09-25",
    key_figures=["Mirror 600 x 600 mm (0.36 m²), center 2.2 m above ground",
                 "About 159 W of sunlight into the room at 800 W/m² DNI [A2]",
                 "0.5 kWh (21 Dec) to 1.0 kWh (1 Feb) into the room, reference site [B3]",
                 "Open loop: sun-position algorithm and RTC, no sun sensor",
                 "Beam error 0.31° typical against 0.5° with preloaded drives [D5]",
                 "Face-down stow in 23 s on a supercapacitor reserve [F1]",
                 "Parts $425 against $430 budget [J1]"],
    cut=False, context=context,
    flow={"title": "instantaneous power, sun to room at the design point, W (all values are estimates)",
          "unit": "W",
          "stages": [("DNI x mirror area", 288), ("Intercepted by mirror", 244), ("Reflected beam", 216),
                     ("Beam at window", 211), ("Into the room", 159)],
          "losses": [(0, "Cosine loss (est.)", 44), (1, "Reflectance, soiling (est.)", 28),
                     (2, "Edge, spill (est.)", 5), (3, "Glazing (est.)", 52)]},
)
