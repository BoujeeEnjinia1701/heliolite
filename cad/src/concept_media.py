"""HelioLite concept massing model and media (TRL 2).

Run from the repo root:  python cad/src/concept_media.py
Proportions and main parts only; not for fabrication.

Coordinates in mm, Z up, ground at Z = 0. The mast stands at the origin. The mirror
turns in azimuth about the mast axis and in elevation about a horizontal torque tube
through its center, so it is balanced. The house wall with the target window is a
context part shown only in the hero render.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".kit"))
from build123d import Box, Cylinder, Pos, Rot, Solid, Plane, Vector
from concept import Part, render_all

# ---------------- key dimensions (proposed, see HLT-PRC-001) ----------------
MIRROR = 600.0            # square mirror side
GLASS_T = 3.0             # silvered glass
BACK_T = 4.0              # aluminum composite backing panel
TUBE = 25.0               # square torque tube, carries the elevation axis
MAST_R = 30.15            # 60.3 mm OD galvanized steel pipe (proposed)
MAST_TOP = 1800.0
AXIS_Z = 2200.0           # elevation axis height (mirror center)
ARM_X = 340.0             # yoke arm centerline, clear of the mirror sweep
NORMAL_EL = 25.0          # mirror normal elevation shown in the renders, degrees
NORMAL_AZ = -36.9         # yoke rotation about Z shown in the renders, degrees


def tube3(a, b, r):
    """Round rod between two 3D points."""
    a = Vector(*a); b = Vector(*b); d = b - a
    return Solid.make_cylinder(r, d.length, Plane(origin=a, z_dir=d.normalized()))


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def on_yoke(shape):
    """Place a shape built in the yoke frame (elevation axis on X at Z = 0) onto the mast top."""
    return Pos(0, 0, AXIS_Z) * Rot(0, 0, NORMAL_AZ) * shape


def on_mirror(shape):
    """Place a shape built in the mirror frame (normal +Z, axis on X) at the shown elevation."""
    return on_yoke(Rot(90 - NORMAL_EL, 0, 0) * shape)


h = MIRROR / 2
# 1 Mirror: 3 mm silvered glass, front face above the torque tube
z_back = TUBE / 2
glass = on_mirror(box(-h, h, -h, h, z_back + BACK_T, z_back + BACK_T + GLASS_T))

# 2 Backing panel, torque tube and trunnion stubs
backing = box(-h, h, -h, h, z_back, z_back + BACK_T)
torque_tube = box(-ARM_X + 15, ARM_X - 15, -TUBE / 2, TUBE / 2, -TUBE / 2, TUBE / 2)
ribs = box(-h + 60, -h + 85, -h + 20, h - 20, -TUBE / 2, z_back) + box(h - 85, h - 60, -h + 20, h - 20, -TUBE / 2, z_back)
backing = on_mirror(backing + torque_tube + ribs)

# 3 Printed gimbal yoke: base plate, crossbar and two arms (ASA, proposed)
yb = 1820.0 - AXIS_Z                   # yoke base in the yoke frame
yoke = (box(-70, 70, -70, 70, yb, yb + 15)
        + box(-ARM_X - 15, ARM_X + 15, -25, 25, yb + 15, yb + 50)
        + box(-ARM_X - 15, -ARM_X + 15, -25, 25, yb + 15, 30)
        + box(ARM_X - 15, ARM_X + 15, -25, 25, yb + 15, 30))
yoke = on_yoke(yoke)

# 4 Elevation drive: NEMA17 stepper on a worm gearbox, on the +X arm
el_drive = (box(ARM_X + 15, ARM_X + 65, -32, 32, -32, 32)              # worm gearbox on the axis
            + box(ARM_X + 19, ARM_X + 61, -21, 21, -32 - 48, -32))     # motor below the gearbox
el_drive = on_yoke(el_drive)

# 5 Azimuth drive: worm gearbox clamped to the mast top, motor to the side
az_drive = (box(-50, 50, -50, 50, MAST_TOP - 90, MAST_TOP)
            + box(50, 98, -21, 21, MAST_TOP - 80, MAST_TOP - 10))

# 6 Azimuth turntable with two ball bearings
turntable = Pos(0, 0, MAST_TOP + 10) * Cylinder(75, 20)

# 7 Mast: 60.3 mm galvanized steel pipe
mast = Pos(0, 0, (MAST_TOP - 90) / 2) * Cylinder(MAST_R, MAST_TOP - 90)

# 8 Ground anchor with flange (ground screw or concrete footing; only the above-ground flange is shown)
anchor = Pos(0, 0, 6) * Cylinder(110, 12) + Pos(0, 0, 12 + 70) * (Cylinder(42, 140) - Cylinder(MAST_R, 142))

# 9 Controller enclosure (ESP32, DS3231 RTC, two stepper drivers), IP65, clamped to the mast
ctrl = box(-80, 80, -MAST_R - 75, -MAST_R - 5, 1100, 1260)

# 10 Homing Hall switches (azimuth on the turntable, elevation on the -X arm)
homing = (box(-100, -76, -70, -50, MAST_TOP + 2, MAST_TOP + 18)
          + on_yoke(box(-ARM_X + 15, -ARM_X + 30, -12, 12, -200, -180)))

# 11 Cabling: controller up the mast to both drives, and 12 V feed down to the ground
cy = -MAST_R - 12
cable = (tube3((-40, cy, 1260), (-40, cy, MAST_TOP - 95), 4)
         + tube3((40, cy, 1100), (40, cy, 60), 4)
         + tube3((40, cy, 60), (-150, cy, 8), 4)
         + tube3((-150, cy, 8), (-500, cy, 8), 4))

parts = [
    Part("Glass mirror, 600 x 600 mm", glass, "#A9C7DA", 1, (-250, -200, 700)),
    Part("Backing panel and torque tube", backing, "#6B7280", 2, (-100, -100, 420)),
    Part("Printed gimbal yoke (ASA)", yoke, "#D4A017", 3, (0, 0, 170)),
    Part("Elevation drive, NEMA17 and worm", el_drive, "#1F2937", 4, (420, 0, 220)),
    Part("Azimuth drive, NEMA17 and worm", az_drive, "#374151", 5, (380, 0, -40)),
    Part("Azimuth turntable and bearings", turntable, "#0F766E", 6, (0, 0, 70)),
    Part("Mast, 60.3 mm steel pipe", mast, "#9CA3AF", 7, (0, 0, -160)),
    Part("Ground anchor and flange", anchor, "#57534E", 8, (0, 0, -300)),
    Part("Controller box (ESP32, RTC)", ctrl, "#15803D", 9, (0, -450, 0)),
    Part("Homing Hall switches (2)", homing, "#C2410C", 10, (-380, -300, 120)),
    Part("Cabling, 12 V and motor leads", cable, "#111827", 11, (-250, -650, -100)),
]

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
                 "About 160 W of sunlight into the room at 800 W/m² DNI (estimate)",
                 "About 0.7 kWh through the glazing on a clear winter day (estimate)",
                 "Open loop: sun-position algorithm and RTC, no sun sensor",
                 "Beam pointing target 0.5° (about 90 mm at 10 m); face-down stow",
                 "Parts about $390 against $400 budget (indicative)"],
    cut=False, context=context,
    flow={"title": "instantaneous power, sun to room at the design point, W (all values are estimates)",
          "unit": "W",
          "stages": [("DNI x mirror area", 288), ("Intercepted by mirror", 245), ("Reflected beam", 216),
                     ("Beam at window", 212), ("Into the room", 159)],
          "losses": [(0, "Cosine loss (est.)", 43), (1, "Reflectance, soiling (est.)", 29),
                     (2, "Spill, pointing (est.)", 4), (3, "Glazing (est.)", 53)]},
)
