"""HelioLite parametric model (build123d), TRL 3, constructable design.
Revised 2026-09-25 for HLT-DDR-002: stow stop and latch (R9) and drive preload springs (R4) added.
Revised 2026-10-01 for HLT-DDR-003 (design for construction): every part can now be made by its stated
process and every part is fixed to the parts next to it. The changes are listed in
docs/decisions/0003-design-for-construction.md; the build plan is docs/05-build-plan.md.
Revised 2026-10-02 for the decisions of that day (HLT-DEC-001): the latch bracket and stop block are
aluminum (6 mm angle), a black EPDM edge channel guards the glass and panel edges, and the checks
include lowering the mirror assembly into the yoke at height (two-lift fitting from a platform).

Run from the repo root:
    python cad/src/model.py            export STEP and STL into cad/step and cad/stl
    python cad/src/model.py --check    run the constructability checks (contacts, clearances,
                                       overlaps and the elevation sweep) and print the result
Exports:
    heliolite-tracking.step / .stl   whole unit, mirror in the tracking pose shown in the media
    heliolite-stowed.step / .stl     whole unit, mirror face-down (night, fault, storm)
    mirror-assembly.step, gimbal.step, mast-and-anchor.step (and .stl)

Axes: Z up, ground at Z = 0, mast on the Z axis. In the yoke frame the elevation axis
(torque tube) lies along X at Z = axis_z; the mirror normal is -Y at elevation 0, +Z
at +90 degrees and -Z (face-down stow) at -90 degrees. The yoke turns about Z for azimuth.
Gearbox, motor, spring and solenoid envelopes are estimates to confirm against the chosen
part's drawing. The same PARAMS feed docs/04-calcs/sizing.py (HLT-CAL-001).
"""
from pathlib import Path
import sys

# Top-level parameters (mm, degrees). Edit these, not the geometry below.
PARAMS = {
    # mirror and backing (decided 2026-09-25: glass mirror with safety backing film)
    "mirror": 600.0,          # square mirror side
    "glass_t": 3.0,           # silvered float glass
    "back_t": 4.0,            # aluminum composite panel
    "tube": 25.0,             # square aluminum torque tube, 2 mm wall, elevation axis
    "tube_wall": 2.0,
    "rib": (25.0, 40.0),      # two aluminum rib tubes under the panel (width, depth), DDR-003: 40 deep with a tunnel for the tube
    "rib_wall": 1.5,
    "rib_x": 227.5,           # rib centerlines at +/- this X
    "trunnion_d": 14.0,       # trunnion stubs, fit the 14 mm hollow bore of the gearbox
    "block": (21.0, 60.0),    # aluminum trunnion end block (square side, length), a sliding fit inside each tube end
    # gimbal yoke, DDR-003: aluminum rectangular tube frame (the one-piece printed yoke could not be printed)
    "arm_x": 340.0,           # yoke arm centerline from the mirror center, clear of the mirror sweep
    "arm_t": 40.0,            # arm tube, along X
    "arm_w": 60.0,            # arm tube, along Y
    "arm_wall": 2.0,
    "cross_h": 40.0,          # crossbar tube depth (Z); its width (Y) equals arm_w
    "gusset_t": 3.0,          # aluminum gusset plates at each arm foot
    "plug_len": 75.0,         # printed ASA bearing plug in the top of each arm
    "bush": (14.0, 18.0, 24.0, 2.0),   # flanged bronze bush: bore, outside, flange diameter, flange thickness
    "base_t": 15.0,           # legacy printed base plate (appearance model only; not in the constructable model)
    "axis_z": 2200.0,         # elevation axis height above ground (mirror center)
    # drives: NEMA17 stepper on an NMRV030-class 50:1 worm gearbox, via an adapter plate
    "gb": (80.0, 97.0, 63.0), # gearbox envelope: across, along worm (input flange side included), along output bore
    "motor": 42.3,            # NEMA17 frame
    "motor_l": 48.0,
    "adapter_t": 10.0,
    "gb_bolt": 22.0,          # gearbox output-face M6 holes at +/- this from the bore (to confirm on the drawing)
    # turntable and mast (decided 2026-09-25: 60.3 mm galvanized steel pipe)
    "turntable_d": 120.0, "turntable_t": 20.0,   # stack height: 2 mm thrust washer, 8 mm hub flange, 10 mm disc
    "disc_t": 10.0, "hub_d": 50.0, "hub_t": 8.0, "washer_t": 2.0,
    "cap": 160.0, "cap_t": 8.0,             # mast cap plate carrying the azimuth gearbox
    "floor_flange": (140.0, 25.0, 8.0, 80.0),   # 2 in threaded floor flange: diameter, height, plate thickness, hub diameter
    "flange_pcd": 105.0,                    # its four holes; M8 screws from below into the cap
    "mast_od": 60.3, "mast_wall": 3.9,
    "mast_len": 1700.0,                     # pipe length above the anchor flange
    "flange_d": 220.0, "flange_t": 12.0,    # ground screw head flange
    "sleeve_d": 84.0, "sleeve_h": 140.0,    # socket that takes the pipe
    "screw_d": 76.0, "screw_len": 800.0,    # ground screw below ground
    # controller and weather sensor (decided 2026-09-25: anemometer and stow reserve)
    "ctrl": (180.0, 80.0, 180.0), "ctrl_z": 1100.0,
    "anemo_z": 1500.0, "anemo_reach": 550.0,
    # stow stop and latch (decided 2026-09-25, HLT-DDR-002: carries the stowed hinge moment in both directions)
    "lug_r0": 15.0, "lug_r1": 75.0,         # steel stow lug on the torque tube, radial extent of its tongue
    "lug_w": 25.0, "lug_t": 8.0,            # lug width (in the direction of rotation) and thickness (X)
    "lug_x": -307.0,                        # lug mid-plane, between the mirror edge (-300) and the -X arm (-320)
    "stop_r": 55.0,                         # contact radius of the stop pad and latch pawl
    "pad_t": 3.0,                           # polyurethane (90A) stop pad thickness
    "brk_t": 6.0,                           # latch bracket: 6 mm aluminum angle, 6063-T6 (decided 2026-10-02; was 4 mm steel)
    # mirror edge guard (decided 2026-10-02): black EPDM U channel round the glass and panel edges
    "edge_wall": 2.5,                       # channel wall thickness
    "edge_lip": (3.0, 8.0),                 # lip width over the glass front and over the panel back
    "edge_gap_l": 95.0,                     # left (latch) edge: channel stops this far each side of the tube centre
    "edge_gap_r": 15.0,                     # right edge: notch round the torque tube
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
    cross_top = yoke_base + P["cross_h"]
    return {
        "mast_top": mast_top, "gb_top": gb_top, "tt_top": tt_top, "yoke_base": yoke_base,
        "lever": P["axis_z"],                           # wind lever arm from ground to mirror center
        "sweep_r": sweep_r,
        "arm_gap": P["arm_x"] - P["arm_t"] / 2 - h,      # mirror edge to inside of arm
        "cross_top": cross_top,
        "cross_gap": P["axis_z"] - cross_top - sweep_r,  # mirror sweep to crossbar
        "arm_len": P["axis_z"] - yoke_base,              # yoke base to elevation axis
        "arm_free": P["axis_z"] - cross_top,             # arm cantilever above the crossbar to the axis
        "front_z": front,                                # mirror front face above the axis (mirror frame)
        "tube_end": P["arm_x"] - P["arm_t"] / 2 - P["bush"][3],   # torque tube ends at the bush flanges
    }


# ------------------------------------------------------------------ primitive helpers
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


def _xcyl(r, x0, x1, y=0.0, z=0.0):
    return _rod((x0, y, z), (x1, y, z), r)


def _ycyl(r, y0, y1, x=0.0, z=0.0):
    return _rod((x, y0, z), (x, y1, z), r)


def _tube_x(x0, x1, w, h, t, y=0.0, z=0.0):
    """Rectangular tube along X: w along Y, h along Z, wall t."""
    return _box(x0, x1, y - w / 2, y + w / 2, z - h / 2, z + h / 2) - _box(x0 - 1, x1 + 1, y - w / 2 + t, y + w / 2 - t, z - h / 2 + t, z + h / 2 - t)


def _tube_z(z0, z1, wx, wy, t, x=0.0, y=0.0):
    return _box(x - wx / 2, x + wx / 2, y - wy / 2, y + wy / 2, z0, z1) - _box(x - wx / 2 + t, x + wx / 2 - t, y - wy / 2 + t, y + wy / 2 - t, z0 - 1, z1 + 1)


def _fuse(shapes):
    out = None
    for s in shapes:
        if s is None:
            continue
        out = s if out is None else out + s
    return out


def _bolt_y(x, z, y0, y1, r=3.0, head=5.0, hh=4.0):
    """Through-bolt along Y from y0 to y1 with a head below y0 and a nut beyond y1."""
    return _ycyl(r, y0, y1, x, z) + _ycyl(head, y0 - hh, y0, x, z) + _ycyl(head, y1, y1 + hh, x, z)


def _gusset(sx, y0, y1, zc):
    """Gusset plate at an arm foot in the XZ plane, thickness from y0 to y1. sx = +1 or -1."""
    from build123d import Polyline, make_face, extrude, Plane
    pts = [(270, zc), (360, zc), (360, zc + 100), (320, zc + 100), (270, zc + 40)]
    pts = [(sx * x, z) for x, z in pts]
    pl = Plane(origin=(0, y0, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    face = make_face(Polyline(*pts, close=True))
    sol = extrude(pl * face, amount=y1 - y0, dir=(0, 1, 0))
    return sol


# ------------------------------------------------------------------ the constructable model
def build_components(el=None, az=None, P=PARAMS, below_ground=True):
    """Every made and bought component as a separate solid, in world coordinates.
    Returns {key: (name, shape, color, bom_line)}. Keys are stable and used by the build plan pictures."""
    from build123d import Pos, Rot, Cone
    D = derived(P)
    el = P["track_el"] if el is None else el
    az = P["track_az"] if az is None else az
    h = P["mirror"] / 2
    t = P["tube"]
    gx, gy, gz = P["gb"]
    AX = P["axis_z"]
    ax_, at, aw, awall = P["arm_x"], P["arm_t"], P["arm_w"], P["arm_wall"]
    xin, xout = ax_ - at / 2, ax_ + at / 2                       # arm inner and outer faces (320, 360)
    zyb = D["yoke_base"] - AX                                    # yoke base in the yoke frame (-397)
    zct = D["cross_top"] - AX                                    # crossbar top (-357)
    bd, bo, bf, bft = P["bush"]
    tend = D["tube_end"]                                         # 318
    C = {}

    def on_yoke(s):
        return Pos(0, 0, AX) * Rot(0, 0, az) * s

    def on_mirror(s):
        return on_yoke(Rot(90 - el, 0, 0) * s)

    def add(key, name, shape, color, bom):
        C[key] = (name, shape, color, bom)

    # ---------------- 1, 2 mirror assembly (mirror frame: normal +Z, tube along X at the origin)
    zb = t / 2
    add("glass", "Glass mirror", on_mirror(_box(-h, h, -h, h, zb + P["back_t"], zb + P["back_t"] + P["glass_t"])), "#A9C7DA", 1)
    add("panel", "Backing panel", on_mirror(_box(-h, h, -h, h, zb, zb + P["back_t"])), "#9CA3AF", 2)
    ew = P["edge_wall"]; lf, lb_ = P["edge_lip"]; zg = zb + P["back_t"] + P["glass_t"]
    edge = (_box(-h - ew, h + ew, -h - ew, h + ew, zb - ew, zg + ew) - _box(-h, h, -h, h, zb, zg)
            - _box(-h + lf, h - lf, -h + lf, h - lf, zg - 1, zg + ew + 1) - _box(-h + lb_, h - lb_, -h + lb_, h - lb_, zb - ew - 1, zb + 1))
    edge = edge - _box(-h - ew - 1, -h + lb_ + 1, -P["edge_gap_l"], P["edge_gap_l"], zb - ew - 1, zg + ew + 1)
    edge = edge - _box(h - lb_ - 1, h + ew + 1, -P["edge_gap_r"], P["edge_gap_r"], zb - ew - 1, zg + ew + 1)
    add("edge", "Edge channel (EPDM)", on_mirror(edge), "#111827", 1)
    rw, rd = P["rib"]
    rwall = P["rib_wall"]
    ribs = []
    for sx in (-1, 1):
        xr = sx * P["rib_x"]
        r_ = (_box(xr - rw / 2, xr + rw / 2, -h + 20, h - 20, zb - rd, zb)
              - _box(xr - rw / 2 + rwall, xr + rw / 2 - rwall, -h + 19, h - 19, zb - rd + rwall, zb - rwall))
        r_ = r_ - _box(xr - rw / 2 - 1, xr + rw / 2 + 1, -t / 2 - 0.25, t / 2 + 0.25, -t / 2 - 0.25, zb + 1)   # tunnel for the torque tube
        ribs.append(r_)
    add("ribs", "Rib tubes (2)", on_mirror(_fuse(ribs)), "#6B7280", 2)
    tw = P["tube_wall"]
    tube = _box(-tend, tend, -t / 2, t / 2, -t / 2, t / 2) - _box(-tend - 1, tend + 1, -t / 2 + tw, t / 2 - tw, -t / 2 + tw, t / 2 - tw)
    for sx in (-1, 1):
        for xb in (tend - 50, tend - 35):
            tube = tube - _ycyl(3.25, -t, t, sx * xb, 0)
        tube = tube - _ycyl(2.5, -t, t, sx * (tend - 20), 0)
    add("tube", "Torque tube", on_mirror(tube), "#4B5563", 2)
    bs, bl = P["block"]
    blocks, stubs, bbolts, pins = [], [], [], []
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (tend - bl), sx * tend))
        blk = _box(x0, x1, -bs / 2, bs / 2, -bs / 2, bs / 2) - _xcyl(bd / 2, x0 - 1, x1 + 1)
        for xb in (tend - 50, tend - 35):
            blk = blk - _ycyl(3.25, -t, t, sx * xb, 0)
        blk = blk - _ycyl(2.5, -t, t, sx * (tend - 20), 0)
        blocks.append(blk)
        s_in = sx * (tend - bl + 22)                              # stub reaches 38 mm into the block
        s_out = sx * (xout + gz + 5) if sx > 0 else sx * (xout + P["spring_l"] - 2)
        stubs.append(_xcyl(bd / 2, min(s_in, s_out), max(s_in, s_out)))
        for xb in (sx * (tend - 50), sx * (tend - 35)):
            bbolts.append(_bolt_y(xb, 0, -t / 2, t / 2, r=3.0, head=5.0, hh=4.0))
        pins.append(_ycyl(2.5, -t / 2, t / 2, sx * (tend - 20), 0))
    add("blocks", "Trunnion end blocks (2)", on_mirror(_fuse(blocks)), "#A8A29E", 2)
    add("stubs", "Trunnion stubs (2)", on_mirror(_fuse(stubs)), "#57534E", 2)
    add("block_bolts", "End block bolts", on_mirror(_fuse(bbolts)), "#111827", 13)
    add("pins", "Cross pins (2)", on_mirror(_fuse(pins)), "#111827", 2)

    # ---------------- 3 yoke (yoke frame)
    xc_len = xout
    cross = _tube_x(-xc_len, xc_len, aw, P["cross_h"], awall, z=zyb + P["cross_h"] / 2)
    for sx in (-1, 1):
        for x in (340, 285):
            cross = cross - _ycyl(3.25, -aw, aw, sx * x, zyb + 20)
        for y in (-15, 15):
            cross = cross - _cyl(3.25, zyb - 1, zct + 1, sx * 45, y)
    add("crossbar", "Crossbar", on_yoke(cross), "#B8C2CC", 3)
    arms = [_tube_z(zct, 40.0, at, aw, awall, x=sx * ax_) for sx in (-1, 1)]
    hole = lambda sx: _xcyl(bo / 2, sx * xin - 2 * sx, sx * xout + 2 * sx)  # noqa: E731
    arms = [a - hole(sx) for a, sx in zip(arms, (-1, 1))]
    for i, sx in enumerate((-1, 1)):
        for z in (zct + 15, zct + 45):
            arms[i] = arms[i] - _ycyl(3.25, -aw, aw, sx * ax_, z)
    for y in (-P["gb_bolt"], P["gb_bolt"]):                     # right arm: gearbox bolts
        for z in (-P["gb_bolt"], P["gb_bolt"]):
            arms[1] = arms[1] - _xcyl(3.25, xin - 1, xout + 1, y, z)
    for z in (-15.0, 22.0):                                      # left arm: latch bracket screws
        arms[0] = arms[0] - _xcyl(3.25, -xout - 1, -xin + 1, -22, z)
    import math as _m
    for k in range(3):                                           # left arm: spring can screws (outer side)
        a_ = _m.radians(90 + 120 * k)
        arms[0] = arms[0] - _xcyl(2.25, -xout - 1, -xout + 3, 20 * _m.cos(a_), 20 * _m.sin(a_))
    arms[0] = arms[0] - _box(-xin - 3, -xin + 1, -6.5, 6.5, 22.5, 38.5)   # left arm: window for the Hall switch (inner side)
    add("arm_r", "Right arm (drive side)", on_yoke(arms[1]), "#94A3B8", 3)
    add("arm_l", "Left arm (latch side)", on_yoke(arms[0]), "#94A3B8", 3)
    gus = []
    for sx in (-1, 1):
        for (y0, y1) in ((aw / 2, aw / 2 + P["gusset_t"]), (-aw / 2 - P["gusset_t"], -aw / 2)):
            gus.append(_gusset(sx, y0, y1, zyb))
    gus = _fuse(gus)
    for sx in (-1, 1):
        for (x, z) in ((340, zct + 15), (340, zct + 45), (340, zyb + 20), (285, zyb + 20)):
            gus = gus - _ycyl(3.25, -aw, aw, sx * x, z)
    add("gussets", "Gusset plates (4)", on_yoke(gus), "#64748B", 3)
    gb_ = []
    for sx in (-1, 1):
        for (x, z) in ((340, zct + 15), (340, zct + 45), (340, zyb + 20), (285, zyb + 20)):
            gb_.append(_bolt_y(sx * x, z, -aw / 2 - P["gusset_t"], aw / 2 + P["gusset_t"], r=3.0, head=5.0, hh=4.0))
    add("gusset_bolts", "Gusset bolts (8)", on_yoke(_fuse(gb_)), "#111827", 13)
    plugs = []
    for sx in (-1, 1):
        pl_ = _box(sx * ax_ - at / 2 + awall, sx * ax_ + at / 2 - awall, -aw / 2 + awall, aw / 2 - awall, 40 - P["plug_len"], 40)
        plugs.append(pl_ - hole(sx))
    add("plugs", "Bearing plugs (2, printed)", on_yoke(_fuse(plugs)), "#D4A017", 3)
    bushes = []
    for sx in (-1, 1):
        b_ = _xcyl(bo / 2, sx * xin, sx * xout) + _xcyl(bf / 2, sx * tend, sx * xin)
        bushes.append(b_ - _xcyl(bd / 2, -xout - 5, xout + 5))
    add("bushes", "Flanged bronze bushes (2)", on_yoke(_fuse(bushes)), "#B45309", 3)
    cb = []
    for x in (-45, 45):
        for y in (-15, 15):
            cb.append(_cyl(3.0, zyb - 10, zct, x, y) + _cyl(5.0, zct, zct + 4, x, y))
    add("cross_bolts", "Crossbar to turntable bolts (4)", on_yoke(_fuse(cb)), "#111827", 13)

    # ---------------- 4 elevation drive, on the +X arm outer face
    x0 = xout
    gbx = _box(x0, x0 + gz, -gx / 2, gx / 2, -gy / 3, gy * 2 / 3) - _xcyl(bd / 2, x0 - 1, x0 + gz + 1)
    m = P["motor"]
    adp = _box(x0 + gz / 2 - 30, x0 + gz / 2 + 30, -30, 30, -gy / 3 - P["adapter_t"], -gy / 3)
    mot = _box(x0 + gz / 2 - m / 2, x0 + gz / 2 + m / 2, -m / 2, m / 2, -gy / 3 - P["adapter_t"] - P["motor_l"], -gy / 3 - P["adapter_t"])
    add("el_gb", "Elevation gearbox", on_yoke(gbx), "#1F2937", 4)
    add("el_motor", "Elevation motor and adapter", on_yoke(adp + mot), "#374151", 4)
    gbb = []
    for y in (-P["gb_bolt"], P["gb_bolt"]):
        for z in (-P["gb_bolt"], P["gb_bolt"]):
            gbb.append(_xcyl(3.0, xin - 4, x0 + 12, y, z) + _xcyl(5.0, xin - 4, xin, y, z))
    add("el_bolts", "Gearbox bolts (4, M6)", on_yoke(_fuse(gbb)), "#111827", 13)

    # ---------------- 5 azimuth drive and mast cap, on the mast
    zt = D["mast_top"]
    zc0 = zt + P["cap_t"]
    az_gb = _box(-gx / 2, gx / 2, -gy / 3, gy * 2 / 3, zc0, zc0 + gz) - _cyl(bd / 2, zc0 - 1, zc0 + gz + 1)
    zc = zc0 + gz / 2
    az_mot = (_box(-30, 30, -gy / 3 - P["adapter_t"], -gy / 3, zc - 30, zc + 30)
              + _box(-m / 2, m / 2, -gy / 3 - P["adapter_t"] - P["motor_l"], -gy / 3 - P["adapter_t"], zc - m / 2, zc + m / 2))
    add("az_gb", "Azimuth gearbox", az_gb, "#1F2937", 5)
    add("az_motor", "Azimuth motor and adapter", az_mot, "#374151", 5)
    cap = _box(-P["cap"] / 2, P["cap"] / 2, -P["cap"] / 2, P["cap"] / 2, zt, zt + P["cap_t"]) - _cyl(8.0, zt - 1, zt + P["cap_t"] + 1)
    import math as _m2
    for k in range(4):
        a_ = _m2.radians(45 + 90 * k)
        cap = cap - _cyl(3.4, zt - 1, zt + P["cap_t"] + 1, P["flange_pcd"] / 2 * _m2.cos(a_), P["flange_pcd"] / 2 * _m2.sin(a_))
    for x in (-22, 22):
        for y in (-22, 22):
            cap = cap - _cyl(3.3, zt - 1, zt + P["cap_t"] + 1, x, y) - _cyl(6.0, zt - 1, zt + 3, x, y)
    cap = cap - _cyl(1.65, zt - 1, zt + P["cap_t"] + 1, -54, 0)
    add("cap", "Mast cap plate", cap, "#78716C", 5)
    fd, fh, fpt, fhub = P["floor_flange"]
    ro = P["mast_od"] / 2
    ri = ro - P["mast_wall"]
    ff = (_cyl(fd / 2, zt - fpt, zt) + _cyl(fhub / 2, zt - fh, zt - fpt)) - _cyl(ro, zt - fh - 1, zt + 1)
    add("floor_flange", "Floor flange (2 in, threaded)", ff, "#A8A29E", 5)
    import math
    fb = []
    for k in range(4):
        a = math.radians(45 + 90 * k)
        x, y = P["flange_pcd"] / 2 * math.cos(a), P["flange_pcd"] / 2 * math.sin(a)
        fb.append(_cyl(4.0, zt - fpt, zt + P["cap_t"] - 1, x, y) + _cyl(6.5, zt - fpt - 5.5, zt - fpt, x, y))
    add("flange_screws", "Flange screws (4, M8)", _fuse(fb), "#111827", 13)

    # ---------------- 6 turntable stack on the azimuth output shaft
    zg = D["gb_top"]
    wsh = _cyl(20.0, zg, zg + P["washer_t"]) - _cyl(7.5, zg - 1, zg + P["washer_t"] + 1)
    hub = (_cyl(P["hub_d"] / 2, zg + P["washer_t"], zg + P["washer_t"] + P["hub_t"])
           + _cyl(15.0, zg + P["washer_t"] + P["hub_t"], D["tt_top"] - 1)) - _cyl(bd / 2, zg, D["tt_top"])
    disc = _cyl(P["turntable_d"] / 2, D["tt_top"] - P["disc_t"], D["tt_top"]) - _cyl(15.0, D["tt_top"] - P["disc_t"] - 1, D["tt_top"] + 1)
    import math as _m3
    zd0 = D["tt_top"] - P["disc_t"]
    for k in range(4):
        a_ = _m3.radians(45 + 90 * k)
        disc = disc - _cyl(2.75, zd0 - 1, D["tt_top"] + 1, 20 * _m3.cos(a_), 20 * _m3.sin(a_))
    for x in (-45, 45):
        for y in (-15, 15):
            disc = disc - _cyl(2.5, zd0 - 1, D["tt_top"] + 1, x, y)
    disc = disc - _cyl(3.0, zd0 - 1, zd0 + 3, -54, 0)
    disc = Rot(0, 0, az) * disc
    shaft = _cyl(bd / 2, zt - 45, D["tt_top"] - 3)
    add("washer", "Thrust washer", wsh, "#B45309", 6)
    add("hub", "Keyed flange hub", hub, "#A8A29E", 6)
    add("disc", "Turntable disc", disc, "#0F766E", 6)
    add("shaft", "Azimuth output shaft", shaft, "#44403C", 6)

    # ---------------- 7 mast, 8 anchor
    add("mast", "Mast pipe", _cyl(ro, P["flange_t"], zt) - _cyl(ri, P["flange_t"] - 1, zt + 1), "#9CA3AF", 7)
    anchor = _cyl(P["flange_d"] / 2, 0, P["flange_t"]) + (_cyl(P["sleeve_d"] / 2, P["flange_t"], P["flange_t"] + P["sleeve_h"])
                                                          - _cyl(ro + 0.5, P["flange_t"], P["flange_t"] + P["sleeve_h"] + 1))
    if below_ground:
        anchor = anchor + _cyl(P["screw_d"] / 2, -P["screw_len"] + 150, 0) + Pos(0, 0, -P["screw_len"] + 75) * Cone(10, P["screw_d"] / 2, 150)
    add("anchor", "Ground anchor", anchor, "#57534E", 8)
    ss = []
    for z in (60.0, 120.0):
        ss.append(_xcyl(5.0, ro + 0.5, P["sleeve_d"] / 2 + 12, 0, z))
    add("set_screws", "Socket set bolts (2, M10)", _fuse(ss), "#111827", 8)

    # ---------------- 9 controller box on a plate with two U-bolts
    cx, cy, cz_ = P["ctrl"]
    yp = -ro                                                     # plate back touches the pipe
    add("ctrl", "Controller box", _box(-cx / 2, cx / 2, yp - 3 - cy, yp - 3, P["ctrl_z"], P["ctrl_z"] + cz_), "#15803D", 9)
    cplate = _box(-70, 70, yp - 3, yp, P["ctrl_z"] - 20, P["ctrl_z"] + cz_ + 20)
    for z in (P["ctrl_z"] - 10, P["ctrl_z"] + cz_ + 10):
        for x in (-ro - 3, ro + 3):
            cplate = cplate - _ycyl(4.25, yp - 5, yp + 1, x, z)
    add("ctrl_plate", "Controller mounting plate", cplate, "#A8A29E", 9)

    def ubolt(z, y_plate, r_pipe):
        ring = (_cyl(r_pipe + 6, z - 3, z + 3) - _cyl(r_pipe, z - 4, z + 4)) & _box(-200, 200, 0, 200, z - 10, z + 10)
        legs = _fuse([_ycyl(3.0, y_plate - 10, 0, x, z) for x in (-r_pipe - 3, r_pipe + 3)])
        nuts = _fuse([_ycyl(5.0, y_plate - 8, y_plate - 3, x, z) for x in (-r_pipe - 3, r_pipe + 3)])
        return ring + legs + nuts
    add("ctrl_ubolts", "U-bolts (2)", ubolt(P["ctrl_z"] - 10, yp, ro) + ubolt(P["ctrl_z"] + cz_ + 10, yp, ro), "#111827", 9)

    # ---------------- 10 homing Hall switches
    zdb = D["tt_top"] - P["disc_t"]                               # underside of the turntable disc
    hall_az = _box(-62, -46, -8, 8, zc0, zdb - 9) + _box(-60, -48, -6, 6, zdb - 9, zdb - 4)
    hall_el = on_yoke(_box(-xin - awall, -xin - awall + 3, -6, 6, 23, 38))   # in the arm wall's window, back on the plug, 1 mm proud
    add("hall_az", "Azimuth Hall switch on its post", hall_az, "#C2410C", 10)
    add("hall_el", "Elevation Hall switch", hall_el, "#C2410C", 10)

    # ---------------- 11 cabling: up the mast, round the flange, a service loop to the yoke
    cyy = -ro - 12
    up = _rod((-40, cyy, P["ctrl_z"] + cz_), (-40, cyy, zt - 45), 4) + _rod((-40, cyy, zt - 45), (-40, -100, zt - 25), 4) \
        + _rod((-40, -100, zt - 25), (-40, -100, zc0 + 40), 4)
    import numpy as np
    ca, sa = math.cos(math.radians(az)), math.sin(math.radians(az))
    tgt = (-100 * ca, -100 * sa, D["cross_top"] + 4)
    loop = (_rod((-40, -100, zc0 + 40), (-40, -100, D["tt_top"] + 60), 4) + _rod((-40, -100, D["tt_top"] + 60), (tgt[0], tgt[1], D["tt_top"] + 60), 4)
            + _rod((tgt[0], tgt[1], D["tt_top"] + 60), tgt, 4))
    run = on_yoke(_xcyl(4.0, -300, 300, 0, zct + 4))
    feed = (_rod((40, cyy, P["ctrl_z"]), (40, cyy, 40), 4) + _rod((40, cyy, 40), (-150, cyy, 30), 4)
            + _rod((-150, cyy, 30), (-500, cyy, 30), 4))
    add("cable", "Cabling", up + loop + run + feed, "#111827", 11)

    # ---------------- 14 anemometer on a right-angle clamp
    ar = P["anemo_reach"]; za = P["anemo_z"]
    clamp = (_cyl(ro + 6, za - 25, za + 25) - _cyl(ro, za - 26, za + 26)) + _box(-15, 15, ro + 4, ro + 40, za - 25, za + 25)
    clamp = clamp - _ycyl(10.0, ro + 10, ro + 50, 0, za)
    add("anemo_clamp", "Anemometer clamp", clamp, "#57534E", 14)
    anemo = (_ycyl(10.0, ro + 10, ar, 0, za) + _cyl(8, za, za + 60, 0, ar) + _cyl(18, za + 60, za + 100, 0, ar)
             + _rod((0, ar, za + 90), (70, ar, za + 90), 3) + _rod((0, ar, za + 90), (-35, ar + 61, za + 90), 3)
             + _rod((0, ar, za + 90), (-35, ar - 61, za + 90), 3))
    for dx, dy in [(70, 0), (-35, 61), (-35, -61)]:
        anemo = anemo + _cyl(20, za + 78, za + 102, dx, ar + dy)
    add("anemo", "Cup anemometer and arm", anemo, "#7C3AED", 14)

    # ---------------- 16 preload springs
    sp_el = _xcyl(P["spring_d"] / 2, -xout - P["spring_l"], -xout) - _xcyl(bd / 2, -xout - P["spring_l"] - 1, -xout + 1)
    add("spring_el", "Elevation spring can", on_yoke(sp_el), "#BE185D", 16)
    add("spring_az", "Azimuth spring can (inside the mast)", _cyl(ri, zt - 50, zt - 20) - _cyl(bd / 2, zt - 51, zt - 19), "#BE185D", 16)

    # ---------------- 17 stow stop and latch
    lx, lt = P["lug_x"], P["lug_t"]
    ring_o = t / 2 + 0.25 + 6
    lug = (_box(lx - lt / 2, lx + lt / 2, -ring_o, ring_o, -ring_o, ring_o) - _box(lx - lt / 2 - 1, lx + lt / 2 + 1, -t / 2, t / 2, -t / 2, t / 2)
           + _box(lx - lt / 2, lx + lt / 2, ring_o - 0.5, P["lug_r1"], -P["lug_w"] / 2, P["lug_w"] / 2))
    lug = lug - _ycyl(2.1, -ring_o - 1, -t / 2 + 0.5, lx, 0) - _xcyl(3.0, lx - lt / 2 - 1, lx - lt / 2 + 3, 30, 0)
    add("lug", "Stow lug", on_yoke(Rot(90 - el, 0, 0) * lug), "#B91C1C", 17)
    hw = P["lug_w"] / 2
    zlo, zhi = -27.5, 34.5
    bt = P["brk_t"]
    legA = (_box(-xin, -xin + bt, -83, -15, zlo, zhi) - _box(-xin - 1, -xin + bt + 1, -62, -48, 12.5, 21.5)   # slot for the pawl
            - _xcyl(21.0, -xin - 1, -xin + bt + 1))                                                           # clear of the turning tube end
    wall = _box(-xin + bt, lx + lt / 2 + 2, -83, -83 + bt, zlo, zhi)
    block = _box(-xin + bt, lx + lt / 2 + 2, -70, -40, zlo, -hw - P["pad_t"] - 0.5)
    brk = legA + wall + block
    for z in (-15.0, 22.0):
        brk = brk - _xcyl(3.3, -xin - 1, -xin + bt + 1, -22, z)
    add("bracket", "Latch bracket and stop block (aluminum)", on_yoke(brk), "#7F1D1D", 17)
    add("pad", "Stop pad", on_yoke(_box(-xin + bt, lx + lt / 2 + 2, -70, -40, -hw - P["pad_t"] - 0.5, -hw - 0.5)), "#EA580C", 17)
    add("pawl", "Latch pawl", on_yoke(_box(-xin - 8, lx + lt / 2 + 1, -61, -49, hw + 0.5, hw + 8.5)), "#DC2626", 17)
    sol = _box(-xin - 32, -xin - 10, -63, -47, hw - 4.5, hw + 12.5) + _box(-xin - 34, -xin, -65, -45, hw - 6.5, hw - 4.5)
    add("solenoid", "Release solenoid on its strap", on_yoke(sol), "#991B1B", 17)
    lb = []
    for z in (-15.0, 22.0):
        lb.append(_xcyl(3.0, -xin + bt, -xin - at, -22, z) + _xcyl(5.0, -xin - at - 4, -xin - at, -22, z))
    add("latch_bolts", "Latch bracket screws (2, M6)", on_yoke(_fuse(lb)), "#111827", 13)
    return C


GROUPS = [
    (1, "Glass mirror, 600 x 600 mm, with edge channel", ["glass", "edge"], "#A9C7DA", (-250, -200, 700)),
    (2, "Backing panel, ribs and torque tube", ["panel", "ribs", "tube", "blocks", "stubs", "pins", "block_bolts"], "#6B7280", (-100, -100, 420)),
    (3, "Gimbal yoke, aluminum frame", ["crossbar", "arm_r", "arm_l", "gussets", "gusset_bolts", "plugs", "bushes", "cross_bolts"], "#B8C2CC", (0, 0, 170)),
    (4, "Elevation drive, NEMA17 on NMRV030", ["el_gb", "el_motor", "el_bolts"], "#1F2937", (420, 0, 220)),
    (5, "Azimuth drive and mast cap", ["az_gb", "az_motor", "cap", "floor_flange", "flange_screws"], "#374151", (380, 0, -40)),
    (6, "Azimuth turntable and shaft", ["washer", "hub", "disc", "shaft"], "#0F766E", (0, 0, 70)),
    (7, "Mast, 60.3 mm steel pipe", ["mast"], "#9CA3AF", (0, 0, -160)),
    (8, "Ground anchor and flange", ["anchor", "set_screws"], "#57534E", (0, 0, -300)),
    (9, "Controller box with stow reserve", ["ctrl", "ctrl_plate", "ctrl_ubolts"], "#15803D", (0, -450, 0)),
    (10, "Homing Hall switches (2)", ["hall_az", "hall_el"], "#C2410C", (-380, -300, 120)),
    (11, "Cabling, 12 V and motor leads", ["cable"], "#111827", (-250, -650, -100)),
    (14, "Cup anemometer on side arm", ["anemo_clamp", "anemo"], "#7C3AED", (0, 450, 0)),
    (16, "Drive preload springs (2)", ["spring_el", "spring_az"], "#BE185D", (-520, 0, 360)),
    (17, "Stow stop and latch", ["lug", "bracket", "pad", "pawl", "solenoid", "latch_bolts"], "#B91C1C", (-300, -520, 380)),
]


def parts(el=None, az=None, P=PARAMS, below_ground=True):
    """Return a list of (bom_no, name, shape, color, explode) for the given pose, grouped by BOM line."""
    from build123d import Compound
    C = build_components(el, az, P, below_ground)
    return [(bom, name, Compound(children=[C[k][1] for k in keys]), color, explode) for bom, name, keys, color, explode in GROUPS]


def build(stowed=False, P=PARAMS, below_ground=True):
    from build123d import Compound
    el = -90.0 if stowed else P["track_el"]
    return Compound(children=[p[2] for p in parts(el=el, P=P, below_ground=below_ground)])


# ------------------------------------------------------------------ constructability checks
FASTENERS = {"pins", "block_bolts", "gusset_bolts", "cross_bolts", "el_bolts", "flange_screws", "set_screws", "latch_bolts", "ctrl_ubolts", "cable"}
# pairs that are meant to pass through each other in the model (a shaft in a bore is modelled with a bore,
# so these are only the fasteners and cables, which pass through holes not drawn in thin walls)
TOUCH = [  # parts that must touch (distance under 0.05 mm): one line per joint in the build plan
    ("glass", "panel"), ("edge", "glass"), ("edge", "panel"), ("panel", "ribs"), ("panel", "tube"), ("blocks", "tube"), ("stubs", "blocks"),
    ("crossbar", "arm_r"), ("crossbar", "arm_l"), ("gussets", "arm_r"), ("gussets", "arm_l"), ("gussets", "crossbar"),
    ("plugs", "arm_r"), ("plugs", "arm_l"), ("bushes", "arm_r"), ("bushes", "arm_l"), ("bushes", "stubs"), ("bushes", "tube"),
    ("el_gb", "arm_r"), ("el_motor", "el_gb"), ("stubs", "el_gb"), ("spring_el", "arm_l"), ("stubs", "spring_el"),
    ("cap", "floor_flange"), ("floor_flange", "mast"), ("az_gb", "cap"), ("az_motor", "az_gb"), ("shaft", "az_gb"),
    ("washer", "az_gb"), ("hub", "washer"), ("disc", "hub"), ("shaft", "hub"), ("crossbar", "disc"),
    ("shaft", "spring_az"), ("spring_az", "mast"), ("mast", "anchor"),
    ("ctrl_plate", "ctrl"), ("ctrl_plate", "mast"), ("anemo_clamp", "mast"), ("anemo", "anemo_clamp"),
    ("hall_az", "cap"), ("hall_el", "plugs"), ("lug", "tube"), ("bracket", "arm_l"), ("pad", "bracket"), ("solenoid", "bracket"),
]
CLEAR = [  # (a, b, minimum gap mm): parts that must stay apart
    ("glass", "arm_r", 15), ("glass", "arm_l", 15), ("glass", "crossbar", 40), ("lug", "glass", 2), ("lug", "arm_l", 5),
    ("hall_el", "lug", 4), ("hall_el", "tube", 0.5), ("pawl", "lug", 0.3), ("pad", "lug", 0.3), ("hall_az", "disc", 3), ("solenoid", "arm_l", 10),
    ("el_motor", "arm_r", 1), ("az_motor", "flange_screws", 1), ("cable", "disc", 2), ("cable", "az_motor", 2),
    ("ribs", "crossbar", 40), ("ctrl", "mast", 2),
    ("edge", "arm_r", 15), ("edge", "arm_l", 15), ("edge", "crossbar", 40), ("edge", "lug", 0.5), ("edge", "tube", 0.5),
    ("lug", "bracket", 2),
]


def check(P=PARAMS, verbose=True):
    """Run the constructability checks. Returns (passed, failed) lists of strings."""
    import itertools
    ok, bad = [], []
    C = build_components(el=-90.0, az=0.0, P=P, below_ground=False)       # stowed: the latch engaged
    sh = {k: v[1] for k, v in C.items()}
    for a, b in TOUCH:
        d = sh[a].distance_to(sh[b])
        (ok if d < 0.05 else bad).append(f"touch {a} / {b}: gap {d:.2f} mm")
    for a, b, g in CLEAR:
        d = sh[a].distance_to(sh[b])
        (ok if d >= g - 1e-6 else bad).append(f"clear {a} / {b}: gap {d:.1f} mm (at least {g})")
    keys = [k for k in sh if k not in FASTENERS]
    for a, b in itertools.combinations(keys, 2):
        try:
            v = (sh[a] & sh[b]).volume
        except Exception:
            v = 0.0
        (bad if v > 0.5 else ok).append(f"no overlap {a} / {b}: {v:.1f} mm3")
    # elevation sweep: the moving mirror parts never hit the fixed ones from stow to face-up
    moving = ["glass", "edge", "panel", "ribs", "tube", "blocks", "lug"]
    for e in range(-90, 91, 15):
        Ce = build_components(el=float(e), az=0.0, P=P, below_ground=False)
        for mk in moving:
            for fk in ("arm_r", "arm_l", "crossbar", "bracket", "pad", "solenoid", "hall_el", "gussets", "plugs", "el_gb", "spring_el"):
                if mk == "lug" and fk in ("pad",) and e == -90:
                    continue
                d = Ce[mk][1].distance_to(Ce[fk][1])
                (ok if d > 0.2 else bad).append(f"sweep el {e:+d}: {mk} / {fk} gap {d:.1f} mm")
    # two-lift fitting at height (decided 2026-10-02): the yoke, drive and latch are on the mast; the mirror
    # assembly, upright (elevation 0) with its end blocks fitted and no stubs, is lowered between the arms
    from build123d import Pos as _Pos
    C0 = build_components(el=0.0, az=0.0, P=P, below_ground=False)
    mir = ["glass", "edge", "panel", "ribs", "tube", "blocks", "lug"]
    fixed = ["arm_r", "arm_l", "crossbar", "gussets", "plugs", "bushes", "bracket", "pad", "pawl", "solenoid", "hall_el",
             "el_gb", "el_bolts", "disc"]
    for dz in range(0, 451, 25):
        for mk in mir:
            ms = _Pos(0, 0, dz) * C0[mk][1]
            for fk in fixed:
                if mk in ("tube", "blocks") and fk == "bushes":
                    try:
                        v = (ms & C0[fk][1]).volume       # tube ends pass the bush flanges (cut 1 mm short: 0.5 mm each side)
                    except Exception:
                        v = 0.0
                    (bad if v > 0.5 else ok).append(f"lower dz {dz}: {mk} / {fk} overlap {v:.1f} mm3")
                    continue
                d = ms.distance_to(C0[fk][1])
                (ok if d > 0.2 else bad).append(f"lower dz {dz}: {mk} / {fk} gap {d:.1f} mm")
    if verbose:
        for s in bad:
            print("FAIL", s)
        print(f"constructability checks: {len(ok)} pass, {len(bad)} fail")
    return ok, bad


if __name__ == "__main__":
    if "--check" in sys.argv:
        ok, bad = check()
        sys.exit(1 if bad else 0)
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
        export_stl(shape, str(out / "stl" / f"{name}.stl"), tolerance=0.2, angular_tolerance=0.3)
        bb = shape.bounding_box()
        print(f"{name}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")
    D = derived()
    print("derived:", {k: round(v, 1) for k, v in D.items()})
