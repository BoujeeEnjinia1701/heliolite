"""HelioLite parametric model (build123d), TRL 3, massing-plus level of detail.
Revised 2026-09-25 for HLT-DDR-002: stow stop and latch (R9) and drive preload springs (R4) added.

Run from the repo root:  python cad/src/model.py
Exports STEP and STL into cad/step and cad/stl:
    heliolite-tracking.step / .stl   whole unit, mirror in the tracking pose shown in the media
    heliolite-stowed.step / .stl     whole unit, mirror face-down (night, fault, storm)
    mirror-assembly.step, gimbal.step, mast-and-anchor.step (and .stl)

Axes: Z up, ground at Z = 0, mast on the Z axis. In the yoke frame the elevation axis
(torque tube) lies along X at Z = axis_z; the mirror normal is -Y at elevation 0, +Z
at +90 degrees and -Z (face-down stow) at -90 degrees. The yoke turns about Z for azimuth.
Main dimensions and interfaces only (mirror, torque tube and trunnions, yoke arm spacing,
NMRV030-class worm gearbox envelopes, mast pipe, cap plate, anchor, enclosures, stow stop and
latch, preload spring cans). Gearbox and spring envelopes
envelopes are estimates to confirm against the chosen part's drawing. Not for fabrication.
The same PARAMS feed docs/04-calcs/sizing.py (HLT-CAL-001).
"""
from pathlib import Path

# Top-level parameters (mm, degrees). Edit these, not the geometry below.
PARAMS = {
    # mirror and backing (decided 2026-09-25: glass mirror with safety backing film)
    "mirror": 600.0,          # square mirror side
    "glass_t": 3.0,           # silvered float glass
    "back_t": 4.0,            # aluminum composite panel
    "tube": 25.0,             # square aluminum torque tube, 2 mm wall, elevation axis
    "tube_wall": 2.0,
    "rib": (25.0, 20.0),      # two aluminum rib tubes under the panel (width, depth)
    "trunnion_d": 14.0,       # trunnion shaft, fits the 14 mm hollow bore of the gearbox
    # gimbal
    "arm_x": 340.0,           # yoke arm centerline from the mirror center, clear of the mirror sweep
    "arm_t": 40.0,            # printed arm section (X), sized in HLT-CAL-001 section C
    "arm_w": 70.0,            # printed arm section (Y)
    "base_t": 15.0,           # printed base plate on the turntable
    "cross_h": 35.0,          # crossbar depth; sits on the base plate
    "axis_z": 2200.0,         # elevation axis height above ground (mirror center)
    # drives: NEMA17 stepper on an NMRV030-class 50:1 worm gearbox, via an adapter plate
    "gb": (80.0, 97.0, 63.0), # gearbox envelope: along worm, across, along output bore
    "motor": 42.3,            # NEMA17 frame
    "motor_l": 48.0,
    "adapter_t": 10.0,
    # turntable and mast (decided 2026-09-25: 60.3 mm galvanized steel pipe)
    "turntable_d": 150.0, "turntable_t": 20.0,
    "cap": 160.0, "cap_t": 8.0,             # mast cap plate carrying the azimuth gearbox
    "mast_od": 60.3, "mast_wall": 3.9,
    "mast_len": 1700.0,                     # pipe length above the anchor flange
    "flange_d": 220.0, "flange_t": 12.0,    # ground screw head flange
    "sleeve_d": 84.0, "sleeve_h": 140.0,    # socket that takes the pipe
    "screw_d": 76.0, "screw_len": 800.0,    # ground screw below ground
    # controller and weather sensor (decided 2026-09-25: anemometer and stow reserve)
    "ctrl": (180.0, 80.0, 180.0), "ctrl_z": 1100.0,
    "anemo_z": 1500.0, "anemo_reach": 550.0,
    # stow stop and latch (decided 2026-09-25, HLT-DDR-002: carries the stowed hinge moment in both directions)
    "lug_r0": 15.0, "lug_r1": 75.0,         # steel stow lug on the torque tube, radial extent from the elevation axis
    "lug_w": 25.0, "lug_t": 8.0,            # lug width (in the direction of rotation) and thickness (X)
    "lug_x": -307.0,                        # lug mid-plane, between the mirror edge (-300) and the -X arm (-320)
    "stop_r": 55.0,                         # contact radius of the stop pad and latch pawl
    "pad_t": 3.0,                           # polyurethane (90A) stop pad thickness
    # drive preload springs (decided 2026-09-25, HLT-DDR-002: about 3 N m each, biasing toward stow)
    "spring_d": 50.0, "spring_l": 30.0,     # spiral spring can envelope
    # poses shown
    "track_el": 25.0,         # mirror normal elevation in the tracking pose
    "track_az": -36.9,        # yoke rotation about Z in the tracking pose
}


def derived(P=PARAMS):
    """Heights and clearances that follow from PARAMS (used by the calc note and the sheet)."""
    gx, gy, gz = P["gb"]
    mast_top = P["flange_t"] + P["mast_len"]
    gb_top = mast_top + P["cap_t"] + gz
    tt_top = gb_top + P["turntable_t"]
    yoke_base = tt_top
    h = P["mirror"] / 2
    back = P["tube"] / 2
    front = back + P["back_t"] + P["glass_t"]
    sweep_r = (h ** 2 + front ** 2) ** 0.5            # mirror edge sweep radius about the elevation axis
    return {
        "mast_top": mast_top, "gb_top": gb_top, "tt_top": tt_top, "yoke_base": yoke_base,
        "lever": P["axis_z"],                           # wind lever arm from ground to mirror center
        "sweep_r": sweep_r,
        "arm_gap": P["arm_x"] - P["arm_t"] / 2 - h,      # mirror edge to inside of arm
        "cross_top": yoke_base + P["base_t"] + P["cross_h"],
        "cross_gap": P["axis_z"] - (yoke_base + P["base_t"] + P["cross_h"]) - sweep_r,  # mirror sweep to crossbar
        "arm_len": P["axis_z"] - yoke_base,              # yoke base to elevation axis
        "front_z": front,                                # mirror front face above the axis (mirror frame)
    }


def _box(x0, x1, y0, y1, z0, z1):
    from build123d import Box, Pos
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def _rod(a, b, r):
    from build123d import Solid, Plane, Vector
    a = Vector(*a); b = Vector(*b); d = b - a
    return Solid.make_cylinder(r, d.length, Plane(origin=a, z_dir=d.normalized()))


def _cyl(r, z0, z1, x=0.0, y=0.0):
    from build123d import Cylinder, Pos
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(r, z1 - z0)


def parts(el=None, az=None, P=PARAMS, below_ground=True):
    """Return a list of (bom_no, name, shape, color, explode) for the given pose."""
    from build123d import Pos, Rot
    D = derived(P)
    el = P["track_el"] if el is None else el
    az = P["track_az"] if az is None else az
    h = P["mirror"] / 2
    t = P["tube"]
    gx, gy, gz = P["gb"]

    def on_yoke(s):
        return Pos(0, 0, P["axis_z"]) * Rot(0, 0, az) * s

    def on_mirror(s):
        return on_yoke(Rot(90 - el, 0, 0) * s)

    # 1 Mirror
    zb = t / 2
    glass = on_mirror(_box(-h, h, -h, h, zb + P["back_t"], zb + P["back_t"] + P["glass_t"]))
    # 2 Backing panel, ribs, torque tube and trunnions
    rw, rd = P["rib"]
    ax_in = P["arm_x"] - P["arm_t"] / 2 - 2
    tube = _box(-ax_in, ax_in, -t / 2, t / 2, -t / 2, t / 2) - _box(-ax_in - 1, ax_in + 1, -t / 2 + P["tube_wall"],
                                                                      t / 2 - P["tube_wall"], -t / 2 + P["tube_wall"], t / 2 - P["tube_wall"])
    trun = _rod((-P["arm_x"] - P["arm_t"] / 2 - 5, 0, 0), (P["arm_x"] + P["arm_t"] / 2 + gx / 2, 0, 0), P["trunnion_d"] / 2)
    back = (_box(-h, h, -h, h, zb, zb + P["back_t"])
            + _box(-h + 60, -h + 60 + rw, -h + 20, h - 20, zb - rd, zb)
            + _box(h - 60 - rw, h - 60, -h + 20, h - 20, zb - rd, zb)
            + tube + trun)
    back = on_mirror(back)
    # 3 Printed yoke: base plate, crossbar, two arms (ASA)
    yb = D["yoke_base"] - P["axis_z"]
    ax_, at, aw = P["arm_x"], P["arm_t"], P["arm_w"]
    cz = D["cross_top"] - P["axis_z"]
    yoke = (_cyl(80, yb, yb + P["base_t"])
            + _box(-ax_ - at / 2, ax_ + at / 2, -aw / 2, aw / 2, cz - P["cross_h"], cz)
            + _box(-ax_ - at / 2, -ax_ + at / 2, -aw / 2, aw / 2, cz - P["cross_h"], 40)
            + _box(ax_ - at / 2, ax_ + at / 2, -aw / 2, aw / 2, cz - P["cross_h"], 40))
    yoke = on_yoke(yoke)
    # 4 Elevation drive: gearbox outboard of the +X arm, bore on the trunnion, motor hanging below
    x0 = ax_ + at / 2
    el_gb = _box(x0, x0 + gz, -gx / 2, gx / 2, -gy / 3, gy * 2 / 3)
    m = P["motor"]
    el_mot = (_box(x0 + gz / 2 - m / 2, x0 + gz / 2 + m / 2, -m / 2, m / 2, -gy / 3 - P["adapter_t"] - P["motor_l"], -gy / 3 - P["adapter_t"])
              + _box(x0 + gz / 2 - 30, x0 + gz / 2 + 30, -30, 30, -gy / 3 - P["adapter_t"], -gy / 3))
    el_drive = on_yoke(el_gb + el_mot)
    # 5 Azimuth drive: gearbox on the mast cap plate, bore vertical, motor to the side
    z0 = D["mast_top"] + P["cap_t"]
    az_gb = _box(-gx / 2, gx / 2, -gy / 3, gy * 2 / 3, z0, z0 + gz)
    zc = z0 + gz / 2
    az_mot = (_box(-30, 30, -gy / 3 - P["adapter_t"], -gy / 3, zc - 30, zc + 30)
              + _box(-m / 2, m / 2, -gy / 3 - P["adapter_t"] - P["motor_l"], -gy / 3 - P["adapter_t"], zc - m / 2, zc + m / 2))
    cap = _box(-P["cap"] / 2, P["cap"] / 2, -P["cap"] / 2, P["cap"] / 2, D["mast_top"], D["mast_top"] + P["cap_t"])
    az_drive = az_gb + az_mot + cap
    # 6 Turntable with thrust bearing
    turntable = _cyl(P["turntable_d"] / 2, D["gb_top"], D["tt_top"])
    # 7 Mast pipe
    ro, ri = P["mast_od"] / 2, P["mast_od"] / 2 - P["mast_wall"]
    mast = _cyl(ro, P["flange_t"], D["mast_top"]) - _cyl(ri, P["flange_t"] - 1, D["mast_top"] + 1)
    # 8 Ground anchor: flange and socket above ground, screw below
    anchor = _cyl(P["flange_d"] / 2, 0, P["flange_t"]) + (_cyl(P["sleeve_d"] / 2, P["flange_t"], P["flange_t"] + P["sleeve_h"])
                                                          - _cyl(ro + 0.5, P["flange_t"], P["flange_t"] + P["sleeve_h"] + 1))
    if below_ground:
        from build123d import Cone
        anchor = anchor + _cyl(P["screw_d"] / 2, -P["screw_len"] + 150, 0) + Pos(0, 0, -P["screw_len"] + 75) * Cone(10, P["screw_d"] / 2, 150)
    # 9 Controller box (ESP32, RTC, drivers, supercapacitor stow reserve), IP65
    cx, cy, cz_ = P["ctrl"]
    ctrl = _box(-cx / 2, cx / 2, -ro - 5 - cy, -ro - 5, P["ctrl_z"], P["ctrl_z"] + cz_)
    # 10 Homing Hall switches (azimuth on the cap plate, elevation on the -X arm)
    homing = (_box(-P["cap"] / 2 + 5, -P["cap"] / 2 + 25, -10, 10, D["mast_top"] + P["cap_t"], D["mast_top"] + P["cap_t"] + 15)
              + on_yoke(_box(-ax_ + at / 2, -ax_ + at / 2 + 15, -12, 12, -200, -180)))
    # 11 Cabling: controller up the mast, feed down to the ground and away toward the house
    cyy = -ro - 12
    cable = (_rod((-40, cyy, P["ctrl_z"] + cz_), (-40, cyy, D["mast_top"] - 5), 4)
             + _rod((40, cyy, P["ctrl_z"]), (40, cyy, 60), 4)
             + _rod((40, cyy, 60), (-150, cyy, 8), 4)
             + _rod((-150, cyy, 8), (-500, cyy, 8), 4))
    # 14 Anemometer on a side arm (weather sensor, not a sun sensor)
    ar = P["anemo_reach"]; za = P["anemo_z"]
    anemo = (_rod((0, ro, za), (0, ar, za), 10) + _cyl(8, za, za + 60, 0, ar) + _cyl(18, za + 60, za + 100, 0, ar)
             + _rod((0, ar, za + 90), (70, ar, za + 90), 3) + _rod((0, ar, za + 90), (-35, ar + 61, za + 90), 3)
             + _rod((0, ar, za + 90), (-35, ar - 61, za + 90), 3))
    for dx, dy in [(70, 0), (-35, 61), (-35, -61)]:
        anemo = anemo + _cyl(20, za + 78, za + 102, dx, ar + dy)
    # 16 Drive preload springs: elevation spiral spring can on the -X trunnion outboard of the -X arm;
    # azimuth spring can inside the mast top on the turntable shaft (envelopes only)
    xo = -ax_ - at / 2
    sp_el = on_yoke(_rod((xo - 5, 0, 0), (xo - 5 - P["spring_l"], 0, 0), P["spring_d"] / 2))
    sp_az = _cyl(ri - 1, D["mast_top"] - P["spring_l"] - 20, D["mast_top"] - 20)
    springs = sp_el + sp_az
    # 17 Stow stop and latch: steel lug on the torque tube (turns with the mirror); on the -X arm a steel bracket
    # carrying a polyurethane stop pad below the stowed lug, a sprung latch pawl above it and a 12 V pull solenoid
    lx, lt = P["lug_x"], P["lug_t"]
    lug = _box(lx - lt / 2, lx + lt / 2, P["lug_r0"], P["lug_r1"], -P["lug_w"] / 2, P["lug_w"] / 2)
    lug = on_yoke(Rot(90 - el, 0, 0) * lug)          # mirror frame: lug along +Y, so it lies along -Y when stowed
    wlo, whi = -(P["lug_r1"] + 10), -35.0                       # bracket extent in Y (yoke frame), stowed lug along -Y
    xa_in = -ax_ + at / 2                                          # inner face of the -X arm
    hw = P["lug_w"] / 2
    bracket = (_box(xa_in, xa_in + 4, wlo, whi + 15, -hw - P["pad_t"] - 12, hw + 22)
               + _box(xa_in + 4, lx + lt / 2 + 2, wlo, wlo + 10, -hw - P["pad_t"] - 12, hw + 22))
    pad = _box(xa_in + 4, lx + lt / 2 + 2, -P["stop_r"] - 12, -P["stop_r"] + 12, -hw - P["pad_t"] - 0.5, -hw - 0.5)
    pawl = _box(xa_in + 4, lx + lt / 2 + 2, -P["stop_r"] - 12, -P["stop_r"] + 12, hw + 0.5, hw + 8)
    sol = _box(xa_in - 30, xa_in - 2, wlo, wlo + 22, hw + 8, hw + 34)
    latch = lug + on_yoke(bracket + pad + pawl + sol)
    return [
        (1, "Glass mirror, 600 x 600 mm", glass, "#A9C7DA", (-250, -200, 700)),
        (2, "Backing panel and torque tube", back, "#6B7280", (-100, -100, 420)),
        (3, "Printed gimbal yoke (ASA)", yoke, "#D4A017", (0, 0, 170)),
        (4, "Elevation drive, NEMA17 on NMRV030", el_drive, "#1F2937", (420, 0, 220)),
        (5, "Azimuth drive and mast cap", az_drive, "#374151", (380, 0, -40)),
        (6, "Azimuth turntable and bearing", turntable, "#0F766E", (0, 0, 70)),
        (7, "Mast, 60.3 mm steel pipe", mast, "#9CA3AF", (0, 0, -160)),
        (8, "Ground anchor and flange", anchor, "#57534E", (0, 0, -300)),
        (9, "Controller box with stow reserve", ctrl, "#15803D", (0, -450, 0)),
        (10, "Homing Hall switches (2)", homing, "#C2410C", (-380, -300, 120)),
        (11, "Cabling, 12 V and motor leads", cable, "#111827", (-250, -650, -100)),
        (14, "Cup anemometer on side arm", anemo, "#7C3AED", (0, 450, 0)),
        (16, "Drive preload springs (2)", springs, "#BE185D", (-520, 0, 360)),
        (17, "Stow stop and latch", latch, "#B91C1C", (-300, -520, 380)),
    ]


def build(stowed=False, P=PARAMS, below_ground=True):
    from build123d import Compound
    el = -90.0 if stowed else P["track_el"]
    return Compound(children=[p[2] for p in parts(el=el, P=P, below_ground=below_ground)])


if __name__ == "__main__":
    from build123d import export_step, export_stl, Compound
    out = Path(__file__).resolve().parents[1]
    (out / "step").mkdir(exist_ok=True); (out / "stl").mkdir(exist_ok=True)
    groups = {
        "heliolite-tracking": build(stowed=False),
        "heliolite-stowed": build(stowed=True),
    }
    ps = {p[0]: p[2] for p in parts()}
    groups["mirror-assembly"] = Compound(children=[ps[1], ps[2]])
    groups["gimbal"] = Compound(children=[ps[3], ps[4], ps[5], ps[6], ps[10], ps[16], ps[17]])
    groups["mast-and-anchor"] = Compound(children=[ps[7], ps[8], ps[9], ps[14]])
    for name, shape in groups.items():
        export_step(shape, str(out / "step" / f"{name}.step"))
        export_stl(shape, str(out / "stl" / f"{name}.stl"))
        bb = shape.bounding_box()
        print(f"{name}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")
    D = derived()
    print("derived:", {k: round(v, 1) for k, v in D.items()})
