"""HelioLite product appearance model (build123d), TRL 3.

Finished-product look for photoreal renders, updated 2026-10-02 to the constructable design (HLT-DDR-003)
and the decisions of that day: the 600 mm glass mirror with a silvered back layer in a black EPDM edge
channel; the painted backing panel on two aluminum rib tubes with tunnels for the torque tube (no torque
tube saddles); trunnion end blocks and pinned stubs; the natural aluminum tube yoke (crossbar, arms and
gusset plates) with printed bearing plugs and bronze bushes; both NEMA17 and NMRV030-class worm drives
with silver-grey cast-look gearbox bodies, output bosses, fins, adapter plates and black motors; the teal
turntable disc on its keyed hub on the galvanized cap plate and floor flange; the stow lug, the aluminum
latch bracket with its stop pad, the sliding pawl and pull solenoid; the spring cans; the homing switches;
an IP65 controller on the mast with a clear lid over the board (ESP32, RTC, two stepper drivers, buck
converter and the supercapacitor stow reserve), a lit green status light, glands and a teal name plate;
the cup anemometer on its side arm; the cabling with stand-off clips; and the dark anchor flange and
socket with their bolts. The mirror, yoke, latch, turntable, cap and spring parts are the solids of
build_components() in model.py, so they match the constructable model exactly.
Context is a compact ground patch with a paver pad and a short section of house wall with the
target window 1.0 m from the mast, a render-only layout much closer than a real site. APPEARANCE MODEL ONLY: no tolerances, no
fabrication detail. CONCEPT, NOT FOR FABRICATION.

Every main dimension, height, pose and interface comes from PARAMS, derived() and parts() in
model.py (tracking pose: mirror normal 25 deg up, yoke turned -36.9 deg). Axes as model.py:
Z up, ground at Z = 0, mast on the Z axis, front toward -Y.

    from product_model import product_parts
    for p in product_parts(): print(p["name"], p["group"], p["material"])
"""
import sys
from math import atan2, cos, degrees, radians, sin
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from build123d import (Axis, Box, Cylinder, Plane, Pos, RectangleRounded, RegularPolygon, Rot, Solid,
                       Sphere, Text, Vector, extrude, fillet)
from model import PARAMS, derived, build_components

TITLE = "HelioLite: two-axis mini heliostat that aims sunlight at a window"

RENDER_VIEWS = [
    {"name": "hero", "groups": ["shell", "internal", "context"], "explode": False, "el": 22, "az": -58,
     "note": "Product render from the front right and above (about 22 deg elevation); mirror in the "
             "tracking pose on its two-axis drive at the mast head, controller with the green status "
             "light on the mast, target window at left (wall drawn 1.0 m from the mast, a render-only layout)"},
    {"name": "exploded", "groups": ["shell", "internal", "accessory"], "explode": True, "el": 28, "az": -55,
     "note": "Exploded view from the front right and above (about 28 deg elevation): mirror, EPDM edge channel and "
             "backing panel; rib tubes, torque tube, stow lug and spring can; aluminum tube yoke; elevation and azimuth worm drives; "
             "turntable and cap plate; controller, board and lid; anemometer; mast and anchor; power adapter"},
    {"name": "detail", "groups": ["internal"], "explode": False, "el": 20, "az": -100,
     "note": "Detail from the front, slightly right and above (about 20 deg elevation): two-axis drive with the "
             "mirror removed; elevation worm drive on the +X arm, azimuth worm drive under the teal "
             "turntable, aluminum latch bracket and spring can on the -X arm"},
]

FONT = str(HERE.parents[1] / ".kit" / "fonts" / "IBMPlexSans-SemiBold.ttf")

# Colours (restrained product palette; kit accent)
C_ACCENT = "#0F766E"
C_GLASS = "#DCEBF5"
C_SILVER = "#E3E8EC"
C_RUBBER = "#1C1F24"
C_PANEL = "#D9DCE0"
C_ALU = "#C9CED4"
C_STEEL = "#9AA1A9"
C_GALV = "#B8BEC6"
C_GB = "#B0B7BF"
C_MOTOR = "#22262B"
C_DARK = "#2B2F36"
C_LATCH = "#4B5159"
C_PAD = "#B45309"
C_BRONZE = "#B07A3B"
C_BOX = "#E9EAEC"
C_LID = "#DDE0E4"
C_WINDOW = "#DCEBF5"
C_PCB = "#166534"
C_CHIP = "#111827"
C_DRIVER = "#1E293B"
C_BUCK = "#1E3A8A"
C_CAP = "#1F4E79"
C_TERM = "#2E7D5B"
C_LED = "#22C55E"
C_WHITE = "#F4F4F2"
C_CABLE = "#16181C"
C_ANCHOR = "#3A3F46"
C_GROUND = "#CFCAC0"
C_PAVER = "#BDB9B2"
C_WALL = "#E3E1DC"
C_FRAME = "#3A3F46"
C_SILL = "#D2CFC8"
C_ROOM = "#4A4E55"


# ---------------------------------------------------------------- helpers
def _fillet_try(shape, edges, radii):
    """Fillet `edges` with the first radius that gives a valid solid; else return the input."""
    edges = list(edges)
    if not edges:
        return shape
    for r in radii:
        try:
            out = fillet(edges, r)
            if out.is_valid and out.volume > 0:
                return out
        except Exception:
            pass
    return shape


def _box(x0, x1, y0, y1, z0, z1):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    z0, z1 = min(z0, z1), max(z0, z1)
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def _fbox(x0, x1, y0, y1, z0, z1, radii):
    """Box with all edges filleted (first radius that works)."""
    return _fillet_try(_box(x0, x1, y0, y1, z0, z1), _box(x0, x1, y0, y1, z0, z1).edges(), radii)


def _zcyl(x, y, z0, z1, r):
    z0, z1 = min(z0, z1), max(z0, z1)
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(r, z1 - z0)


def _xcyl(x0, x1, y, z, r):
    x0, x1 = min(x0, x1), max(x0, x1)
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(r, x1 - x0)


def _ycyl(x, y0, y1, z, r):
    y0, y1 = min(y0, y1), max(y0, y1)
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(r, y1 - y0)


def _rod(a, b, r):
    a, b = Vector(*a), Vector(*b)
    d = b - a
    return Solid.make_cylinder(r, d.length, Plane(origin=a, z_dir=d.normalized()))


def _pipe(points, r):
    """Round cable through `points` with spherical joints."""
    out = None
    for a, b in zip(points, points[1:]):
        seg = _rod(a, b, r)
        out = seg if out is None else out + seg
    for q in points[1:-1]:
        out += Pos(*q) * Sphere(r)
    return out


def _top(s):
    return s.faces().sort_by(Axis.Z)[-1].edges()


def _bottom(s):
    return s.faces().sort_by(Axis.Z)[0].edges()


def _hex_z(x, y, z0, af, h):
    """Hex head, across flats `af`, from z0 up by h (h < 0 builds downward)."""
    s = Pos(x, y, z0) * extrude(RegularPolygon(af / 2 / cos(radians(30)), 6), amount=h)
    return s


def _text_plate(txt, size, depth):
    """Raised text in the XY plane, centred, from z = 0 up by depth."""
    t = Text(txt, font_size=size, font_path=FONT)
    return extrude(t, amount=depth)


# ---------------------------------------------------------------- model
def product_parts(P=PARAMS):
    D = derived(P)
    el, az = P["track_el"], P["track_az"]
    h = P["mirror"] / 2
    t = P["tube"]
    gx, gy, gz = P["gb"]
    AZ_ = P["axis_z"]
    ax_, at, aw = P["arm_x"], P["arm_t"], P["arm_w"]
    ro = P["mast_od"] / 2
    ri = ro - P["mast_wall"]
    out = []

    def add(name, shape, color, material, bom, group, explode):
        out.append({"name": name, "shape": shape, "color": color, "material": material,
                    "bom": bom, "group": group, "explode": tuple(float(v) for v in explode)})

    def on_yoke(s):
        return Pos(0, 0, AZ_) * Rot(0, 0, az) * s

    def on_mirror(s):
        return on_yoke(Rot(90 - el, 0, 0) * s)

    # unit vectors for explode directions
    n = (sin(radians(az)) * cos(radians(el)),
         -cos(radians(az)) * cos(radians(el)), sin(radians(el)))          # mirror normal, world
    yx = (cos(radians(az)), sin(radians(az)))                              # yoke +X in plan

    def ex(base_z, along_n=0.0, along_yx=0.0, dy=0.0):
        return (n[0] * along_n + yx[0] * along_yx, n[1] * along_n + yx[1] * along_yx + dy,
                n[2] * along_n + base_z)

    Z_HEAD = 380.0   # explode lift of the mirror assembly and elevation axis

    # ============================================================ mirror assembly (BOM 1, 2)
    zb = t / 2
    zg0, zg1 = zb + P["back_t"], zb + P["back_t"] + P["glass_t"]
    silver_t = 0.4
    glass = _box(-h, h, -h, h, zg0 + silver_t, zg1)
    glass = _fillet_try(glass, glass.edges().filter_by(Axis.Z), [3.0, 2.0])
    glass = _fillet_try(glass, _top(glass), [0.8, 0.5])                     # seamed edge
    add("Glass mirror (float glass)", on_mirror(glass), C_GLASS, "clear", 1, "shell", ex(Z_HEAD, 520))
    silver = _box(-h, h, -h, h, zg0, zg0 + silver_t)
    silver = _fillet_try(silver, silver.edges().filter_by(Axis.Z), [3.0, 2.0])
    add("Mirror silvering", on_mirror(silver), C_SILVER, "metal", 1, "shell", ex(Z_HEAD, 500))

    # Constructable components from model.py (decisions of 2026-10-02: aluminum tube yoke, rib tunnels,
    # aluminum latch bracket, EPDM edge channel; no torque tube saddles)
    C = build_components(el=el, az=az, P=P, below_ground=False)

    def mcomp(*keys):
        sh = None
        for k in keys:
            sh = C[k][1] if sh is None else sh + C[k][1]
        return sh

    add("Mirror edge channel (EPDM)", mcomp("edge"), C_RUBBER, "rubber", 1, "shell", ex(Z_HEAD, 420))
    rw, rd = P["rib"]
    panel = _box(-h, h, -h, h, zb, zb + P["back_t"])
    panel = _fillet_try(panel, panel.edges().filter_by(Axis.Z), [3.0, 2.0])
    add("Backing panel (ACP)", on_mirror(panel), C_PANEL, "painted", 2, "shell", ex(Z_HEAD, 260))
    plugs = None
    for sx in (-1, 1):
        x0 = sx * P["rib_x"] - rw / 2
        for y in (-h + 20, h - 20):
            s_ = 1 if y > 0 else -1
            p_ = _box(x0 + 0.5, x0 + rw - 0.5, y, y + s_ * 3.0, zb - rd + 0.5, zb - 0.5)
            p_ = _fillet_try(p_, p_.edges(), [0.8, 0.4])
            plugs = p_ if plugs is None else plugs + p_
    add("Rib tubes with tunnels (aluminum)", mcomp("ribs"), C_ALU, "metal", 2, "shell", ex(Z_HEAD, 220))
    add("Rib end plugs", on_mirror(plugs), C_RUBBER, "rubber", 2, "shell", ex(Z_HEAD, 220))
    add("Torque tube (aluminum)", mcomp("tube"), C_ALU, "metal", 2, "internal", ex(Z_HEAD))
    add("Trunnion end blocks (aluminum)", mcomp("blocks"), C_ALU, "metal", 2, "internal", ex(Z_HEAD))
    add("Trunnion stubs and cross pins (steel)", mcomp("stubs", "pins"), C_STEEL, "metal", 2, "internal", ex(Z_HEAD))

    # ============================================================ yoke (BOM 3): natural aluminum tube frame
    add("Yoke crossbar (aluminum tube)", mcomp("crossbar"), C_ALU, "metal", 3, "internal", ex(280))
    add("Yoke arms (aluminum tube)", mcomp("arm_r", "arm_l"), C_ALU, "metal", 3, "internal", ex(280))
    add("Gusset plates (aluminum)", mcomp("gussets"), C_ALU, "metal", 3, "internal", ex(280))
    add("Bearing plugs (printed ASA)", mcomp("plugs"), C_DARK, "plastic", 3, "internal", ex(280))
    add("Flanged bronze bushes", mcomp("bushes"), C_BRONZE, "metal", 3, "internal", ex(280))
    add("Yoke, trunnion and latch bolts (M6)", mcomp("gusset_bolts", "cross_bolts", "el_bolts", "block_bolts", "latch_bolts"),
        C_STEEL, "metal", 13, "internal", ex(280))

    # ============================================================ worm drive helper
    def worm_box(x0, x1, y0, y1, z0, z1, bore_axis):
        """NMRV030-class housing in its envelope: filleted body, output bosses, fins, cover bolts."""
        body = _box(x0, x1, y0, y1, z0, z1)
        body = _fillet_try(body, body.edges(), [5.0, 3.0, 1.5])
        cx_, cy_, cz_ = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
        extra = None
        if bore_axis == "X":
            bc = (cy_, 0.0)            # boss centre (y, z): bore on the axis
            for xf, s in ((x0, -1), (x1, 1)):
                ring = _xcyl(min(xf, xf + s * 2), max(xf, xf + s * 2), 0, 0, 26) - \
                    _xcyl(xf - 3, xf + 3, 0, 0, P["trunnion_d"] / 2 + 3)
                extra = ring if extra is None else extra + ring
            for sy in (-1, 1):
                for k in range(4):
                    zf = z1 - 12 - k * 9
                    yf = y1 if sy > 0 else y0
                    extra += _box(x0 + 8, x1 - 8, yf - sy * 0.5, yf + sy * 2.0, zf - 2, zf + 2)
        else:
            extra = _zcyl(cx_, 0, z1, z1 + 2, 30) - _zcyl(cx_, 0, z1 - 1, z1 + 3, P["trunnion_d"] / 2 + 3)
            for sx in (-1, 1):
                for k in range(4):
                    zf = z0 + 14 + k * 11
                    xf = x1 if sx > 0 else x0
                    extra += _box(xf - 0.5 * sx, xf + 2 * sx, y0 + 10, y1 - 10, zf - 2, zf + 2)
        return body + extra

    def nema(x0, x1, y0, y1, z0, z1, axis):
        """NEMA17 motor: chamfered black body, aluminum end caps, connector."""
        ax = {"X": Axis.X, "Y": Axis.Y, "Z": Axis.Z}[axis]
        m_ = _box(x0, x1, y0, y1, z0, z1)
        m_ = _fillet_try(m_, m_.edges().filter_by(ax), [4.5, 3.0])
        caps = None
        L = {"X": x1 - x0, "Y": y1 - y0, "Z": z1 - z0}[axis]
        for f0, f1 in ((-0.3, 7.0), (L - 9.0, L + 0.3)):
            if axis == "Z":
                c_ = _box(x0 - 0.3, x1 + 0.3, y0 - 0.3, y1 + 0.3, z0 + f0, z0 + f1)
            elif axis == "Y":
                c_ = _box(x0 - 0.3, x1 + 0.3, y0 + f0, y0 + f1, z0 - 0.3, z1 + 0.3)
            else:
                c_ = _box(x0 + f0, x0 + f1, y0 - 0.3, y1 + 0.3, z0 - 0.3, z1 + 0.3)
            c_ = _fillet_try(c_, c_.edges().filter_by(ax), [4.8, 3.0])
            caps = c_ if caps is None else caps + c_
        return m_, caps

    # ============================================================ elevation drive (BOM 4), yoke frame
    x0 = ax_ + at / 2
    gb_e = worm_box(x0, x0 + gz, -gx / 2, gx / 2, -gy / 3, gy * 2 / 3, "X")
    add("Elevation gearbox (NMRV030)", on_yoke(gb_e), C_GB, "metal", 4, "internal", ex(Z_HEAD, along_yx=190))
    mo = P["motor"]
    xm = x0 + gz / 2
    zA1 = -gy / 3
    zA0 = zA1 - P["adapter_t"]
    adapter = _fbox(xm - 30, xm + 30, -30, 30, zA0, zA1, [2.0, 1.0])
    for sx in (-1, 1):
        for sy in (-1, 1):
            adapter += _hex_z(xm + sx * 23, sy * 23, zA0, 5.5, -3.0)
    add("Elevation adapter plate", on_yoke(adapter), C_ALU, "metal", 4, "internal", ex(Z_HEAD, along_yx=190))
    mb, mc = nema(xm - mo / 2, xm + mo / 2, -mo / 2, mo / 2, zA0 - P["motor_l"], zA0, "Z")
    mb += _box(xm - 8, xm + 8, mo / 2 - 0.5, mo / 2 + 5, zA0 - P["motor_l"] + 3, zA0 - P["motor_l"] + 12)
    add("Elevation motor (NEMA17)", on_yoke(mb), C_MOTOR, "painted", 4, "internal", ex(Z_HEAD - 60, along_yx=190))
    add("Elevation motor end caps", on_yoke(mc), C_ALU, "metal", 4, "internal", ex(Z_HEAD - 60, along_yx=190))

    # ============================================================ azimuth drive, cap plate (BOM 5), world
    zc0 = D["mast_top"]
    z0 = zc0 + P["cap_t"]
    add("Mast cap plate (galvanized)", mcomp("cap"), C_GALV, "metal", 5, "internal", (0, 0, 40))
    add("Floor flange (galvanized)", mcomp("floor_flange"), C_GALV, "metal", 5, "internal", (0, 0, 20))
    add("Flange screws (M8)", mcomp("flange_screws"), C_STEEL, "metal", 13, "internal", (0, 0, 20))
    gb_a = worm_box(-gx / 2, gx / 2, -gy / 3, gy * 2 / 3, z0, z0 + gz, "Z")
    add("Azimuth gearbox (NMRV030)", gb_a, C_GB, "metal", 5, "internal", (0, 0, 110))
    zc = z0 + gz / 2
    yA1 = -gy / 3
    yA0 = yA1 - P["adapter_t"]
    adp = _fbox(-30, 30, yA0, yA1, zc - 30, zc + 30, [2.0, 1.0])
    for sx in (-1, 1):
        for sz in (-1, 1):
            adp += Pos(sx * 23, yA0, zc + sz * 23) * Rot(90, 0, 0) * \
                extrude(RegularPolygon(5.5 / 2 / cos(radians(30)), 6), amount=3.0)
    add("Azimuth adapter plate", adp, C_ALU, "metal", 5, "internal", (0, -60, 110))
    mb, mc = nema(-mo / 2, mo / 2, yA0 - P["motor_l"], yA0, zc - mo / 2, zc + mo / 2, "Y")
    mb += _box(mo / 2 - 0.5, mo / 2 + 5, yA0 - P["motor_l"] + 3, yA0 - P["motor_l"] + 12, zc - 8, zc + 8)
    add("Azimuth motor (NEMA17)", mb, C_MOTOR, "painted", 5, "internal", (0, -130, 110))
    add("Azimuth motor end caps", mc, C_ALU, "metal", 5, "internal", (0, -130, 110))

    # ============================================================ turntable (BOM 6): teal disc on a keyed hub
    add("Azimuth turntable disc", mcomp("disc"), C_ACCENT, "painted", 6, "internal", (0, 0, 190))
    add("Keyed flange hub and output shaft", mcomp("hub", "shaft"), C_STEEL, "metal", 6, "internal", (0, 0, 160))
    add("Bronze thrust washer", mcomp("washer"), C_BRONZE, "metal", 6, "internal", (0, 0, 140))

    # ============================================================ preload springs (BOM 16)
    add("Elevation spring can", mcomp("spring_el"), C_DARK, "plastic", 16, "internal", ex(Z_HEAD, along_yx=-170))
    add("Azimuth spring can (in mast top)", mcomp("spring_az"), C_DARK, "plastic", 16, "internal", (0, 0, 60))

    # ============================================================ stow stop and latch (BOM 17)
    add("Stow lug (steel)", mcomp("lug"), C_LATCH, "painted", 17, "internal", ex(Z_HEAD))
    add("Latch bracket and stop block (aluminum)", mcomp("bracket"), C_ALU, "metal", 17, "internal", ex(280, along_yx=-130))
    add("Stop pad (PU 90A)", mcomp("pad"), C_PAD, "rubber", 17, "internal", ex(280, along_yx=-130))
    add("Sliding latch pawl (steel)", mcomp("pawl"), C_STEEL, "metal", 17, "internal", ex(280, along_yx=-130))
    add("Pull solenoid (12 V)", mcomp("solenoid"), C_GALV, "metal", 17, "internal", ex(280, along_yx=-160))

    # ============================================================ homing Hall switches (BOM 10)
    add("Azimuth homing switch on its post", mcomp("hall_az"), C_DARK, "plastic", 10, "internal", (0, 0, 110))
    add("Elevation homing switch", mcomp("hall_el"), C_DARK, "plastic", 10, "internal", ex(280, along_yx=-60))

    # ============================================================ mast (BOM 7) and anchor (BOM 8)
    mast = _zcyl(0, 0, P["flange_t"], D["mast_top"], ro) - _zcyl(0, 0, P["flange_t"] - 1, D["mast_top"] + 1, ri)
    add("Mast (galvanized pipe)", mast, C_GALV, "metal", 7, "shell", (0, 0, 0))
    fl = _zcyl(0, 0, 0, P["flange_t"], P["flange_d"] / 2)
    fl = _fillet_try(fl, _top(fl), [2.0, 1.0])
    sl_ = _zcyl(0, 0, P["flange_t"], P["flange_t"] + P["sleeve_h"], P["sleeve_d"] / 2)
    sl_ = _fillet_try(sl_, _top(sl_), [3.0, 2.0])
    anchor = fl + sl_ - _zcyl(0, 0, P["flange_t"], P["flange_t"] + P["sleeve_h"] + 1, ro + 0.5)
    for k in range(3):
        a = radians(-90 + 120 * k)
        anchor += Pos((P["sleeve_d"] / 2 - 1) * cos(a), (P["sleeve_d"] / 2 - 1) * sin(a), P["flange_t"] + 100) * \
            Rot(0, 0, k * 120 - 90) * Rot(0, 90, 0) * Cylinder(7.0, 10.0)
    add("Ground anchor flange and socket", anchor, C_ANCHOR, "painted", 8, "shell", (0, 0, -220))
    fb = None
    for k in range(4):
        a = radians(45 + 90 * k)
        b_ = _hex_z(90 * cos(a), 90 * sin(a), P["flange_t"], 13.0, 6.0)
        b_ += _zcyl(90 * cos(a), 90 * sin(a), P["flange_t"], P["flange_t"] + 1.5, 11.0)
        fb = b_ if fb is None else fb + b_
    for k in range(3):
        a = radians(-90 + 120 * k)
        r_ = P["sleeve_d"] / 2 + 9
        fb += Pos(r_ * cos(a), r_ * sin(a), P["flange_t"] + 100) * Rot(0, 0, k * 120 - 90) * Rot(0, 90, 0) * \
            extrude(RegularPolygon(10.0 / 2 / cos(radians(30)), 6), amount=6.0, both=True)
    add("Anchor bolts and set screws", fb, C_STEEL, "metal", 13, "shell", (0, 0, -220))

    # ============================================================ controller (BOM 9, 15)
    cx, cy, ch = P["ctrl"]
    y_back = -ro - 5
    y_front = y_back - cy
    zc0_, zc1_ = P["ctrl_z"], P["ctrl_z"] + ch
    y_split = y_front + 20.0
    body = _box(-cx / 2, cx / 2, y_split, y_back, zc0_, zc1_)
    body = _fillet_try(body, body.edges().filter_by(Axis.Y), [8.0, 5.0])
    body = _fillet_try(body, body.faces().sort_by(Axis.Y)[-1].edges(), [2.0, 1.0])
    body -= _box(-cx / 2 + 3, cx / 2 - 3, y_split - 1, y_back - 3, zc0_ + 3, zc1_ - 3)
    for sx in (-1, 1):                       # side ribs
        for k in range(5):
            zz = zc0_ + 40 + k * 25
            body += _box(sx * (cx / 2 - 0.5), sx * (cx / 2 + 1.5), y_split + 8, y_back - 8, zz - 1.5, zz + 1.5)
    add("Controller box (IP65)", body, C_BOX, "plastic", 9, "shell", (0, -250, 0))
    lid = _box(-cx / 2, cx / 2, y_front, y_split - 0.8, zc0_, zc1_)                  # 0.8 mm parting line
    lid = _fillet_try(lid, lid.edges().filter_by(Axis.Y), [8.0, 5.0])
    lid = _fillet_try(lid, lid.faces().sort_by(Axis.Y)[0].edges(), [3.0, 2.0])
    lid -= _box(-cx / 2 + 3, cx / 2 - 3, y_front + 3, y_split, zc0_ + 3, zc1_ - 3)
    wx, wz0, wz1 = 62.0, zc0_ + 38, zc1_ - 24
    win_cut = _box(-wx, wx, y_front - 1, y_front + 4, wz0, wz1)
    win_cut = _fillet_try(win_cut, win_cut.edges().filter_by(Axis.Y), [5.0, 3.0])
    lid -= win_cut
    for sx in (-1, 1):
        for zz in (zc0_ + 12, zc1_ - 12):
            lid -= _ycyl(sx * (cx / 2 - 12), y_front - 1, y_front + 1.5, zz, 5.0)
    add("Controller lid", lid, C_LID, "plastic", 9, "shell", (0, -420, 0))
    pane = _box(-wx - 4, wx + 4, y_front + 2.2, y_front + 4.2, wz0 - 4, wz1 + 4)
    pane = _fillet_try(pane, pane.edges().filter_by(Axis.Y), [7.0, 5.0])
    add("Controller window (polycarbonate)", pane, C_WINDOW, "clear", 9, "shell", (0, -440, 0))
    scr = None
    for sx in (-1, 1):
        for zz in (zc0_ + 12, zc1_ - 12):
            s_ = _ycyl(sx * (cx / 2 - 12), y_front + 0.5, y_front + 1.0, zz, 4.2)
            s_ += _ycyl(sx * (cx / 2 - 12), y_front - 0.6, y_front + 0.5, zz, 4.2)
            s_ -= _box(sx * (cx / 2 - 12) - 0.5, sx * (cx / 2 - 12) + 0.5, y_front - 1, y_front, zz - 3, zz + 3)
            scr = s_ if scr is None else scr + s_
    add("Lid screws", scr, C_STEEL, "metal", 13, "shell", (0, -470, 0))
    # status light below the window, lit green
    led = _ycyl(cx / 2 - 30, y_front - 1.2, y_front + 0.5, zc0_ + 19, 3.2)
    add("Status light (lit)", led, C_LED, "emissive", 9, "shell", (0, -470, 0))
    ring = _ycyl(cx / 2 - 30, y_front - 0.8, y_front + 0.5, zc0_ + 19, 5.2) - _ycyl(cx / 2 - 30, y_front - 2, y_front + 1, zc0_ + 19, 3.3)
    add("Status light bezel", ring, C_DARK, "plastic", 9, "shell", (0, -470, 0))
    # teal name plate with wordmark on the +X side
    plate = _box(cx / 2 + 1.5, cx / 2 + 2.7, y_split + 4, y_back - 4, zc1_ - 44, zc1_ - 16)
    plate = _fillet_try(plate, plate.edges().filter_by(Axis.X), [3.0, 2.0])
    add("Name plate", plate, C_ACCENT, "painted", 9, "shell", (60, -250, 0))
    word = _text_plate("HelioLite", 7.5, 0.5)
    word = Plane(origin=(cx / 2 + 2.7, (y_split + y_back) / 2, zc1_ - 30), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * word
    add("Wordmark", word, C_WHITE, "painted", None, "shell", (60, -250, 0))

    # board and parts behind the window (BOM 9, 15)
    yp = y_back - 16.0                         # board plane, components toward -Y
    pcb = _box(-cx / 2 + 8, cx / 2 - 8, yp, yp + 1.6, zc0_ + 8, zc1_ - 8)
    pcb = _fillet_try(pcb, pcb.edges().filter_by(Axis.Y), [3.0, 2.0])
    add("Controller board", pcb, C_PCB, "plastic", 9, "shell", (0, -330, 0))
    esp = _box(-58, -30, yp - 3.2, yp, zc1_ - 60, zc1_ - 26)          # ESP32 shield can
    add("ESP32 module", esp, C_GALV, "metal", 9, "shell", (0, -330, 0))
    ant = _box(-58, -30, yp - 1.0, yp, zc1_ - 26, zc1_ - 18)
    add("ESP32 antenna area", ant, C_CHIP, "plastic", 9, "shell", (0, -330, 0))
    rtc = _box(-20, 10, yp - 1.6, yp, zc1_ - 50, zc1_ - 26)
    add("RTC board (DS3231)", rtc, C_BUCK, "plastic", 9, "shell", (0, -330, 0))
    coin = _ycyl(-5, yp - 5.0, yp - 1.6, zc1_ - 38, 10.0)
    add("RTC coin cell", coin, C_GALV, "metal", 9, "shell", (0, -330, 0))
    drv, sinks = None, None
    for xx in (22, 50):
        d_ = _box(xx - 10, xx + 10, yp - 1.6, yp, zc1_ - 70, zc1_ - 30)
        drv = d_ if drv is None else drv + d_
        s_ = _box(xx - 7, xx + 7, yp - 4.0, yp - 1.6, zc1_ - 58, zc1_ - 44)
        for k in range(5):
            s_ += _box(xx - 6 + k * 3, xx - 5 + k * 3, yp - 10, yp - 4.0, zc1_ - 58, zc1_ - 44)
        sinks = s_ if sinks is None else sinks + s_
    add("Stepper drivers (TMC2209)", drv, C_DRIVER, "plastic", 9, "shell", (0, -330, 0))
    add("Driver heat sinks", sinks, C_ALU, "metal", 9, "shell", (0, -330, 0))
    buck = _box(-58, -24, yp - 1.6, yp, zc0_ + 70, zc0_ + 92)
    buck += _ycyl(-48, yp - 8, yp - 1.6, zc0_ + 81, 4.0)
    add("Buck converter (12 V to 5 V)", buck, C_BUCK, "plastic", 9, "shell", (0, -330, 0))
    caps = None
    for k in range(5):
        xx = -48 + k * 18
        c_ = _zcyl(xx, yp - 9.5, zc0_ + 18, zc0_ + 52, 8.0)
        c_ = _fillet_try(c_, _top(c_), [1.2, 0.8])
        caps = c_ if caps is None else caps + c_
    add("Supercapacitor stow reserve (5 x 25 F)", caps, C_CAP, "painted", 15, "shell", (0, -330, 0))
    term = _box(30, 66, yp - 10, yp, zc0_ + 16, zc0_ + 30)
    for k in range(6):
        term -= _ycyl(33 + k * 6, yp - 11, yp - 8, zc0_ + 23, 1.6)
    add("Terminal block", term, C_TERM, "plastic", 9, "shell", (0, -330, 0))
    # glands (bottom for the feed, top for the lead to the mast head)
    gl = None
    cyy = -ro - 12
    for (xx, zz, s) in ((40, zc0_, -1), (-40, zc1_, 1)):
        g_ = Pos(xx, cyy - 1, zz) * extrude(RegularPolygon(9.0 / cos(radians(30)), 6), amount=s * 6.0)
        d_ = _zcyl(xx, cyy - 1, min(zz + s * 6, zz + s * 14), max(zz + s * 6, zz + s * 14), 7.5)
        d_ = _fillet_try(d_, (_top(d_) if s > 0 else _bottom(d_)), [2.5, 1.5])
        g_ += d_
        gl = g_ if gl is None else gl + g_
    vent = _zcyl(-40, cyy - 1, zc0_ - 4, zc0_, 6.0)
    vent = _fillet_try(vent, _bottom(vent), [1.5, 1.0])
    gl += vent
    add("Cable glands and vent", gl, C_DARK, "plastic", 11, "shell", (0, -250, 0))
    # mast straps behind the box
    straps = None
    for zz in (zc0_ + 35, zc1_ - 35):
        s_ = _zcyl(0, 0, zz - 10, zz + 10, ro + 2.5) - _zcyl(0, 0, zz - 11, zz + 11, ro)
        s_ += _box(-cx / 2 + 25, cx / 2 - 25, y_back - 0.5, -ro + 1.5, zz - 10, zz + 10) - \
            _zcyl(0, 0, zz - 11, zz + 11, ro)
        straps = s_ if straps is None else straps + s_
    add("Controller mast straps", straps, C_GALV, "metal", 13, "shell", (0, -150, 0))

    # ============================================================ cabling (BOM 11) and clips
    cab = _pipe([(-40, cyy, zc1_ + 14), (-40, cyy, D["mast_top"] - 5)], 4)
    cab += _pipe([(40, cyy, zc0_ - 14), (40, cyy, 60), (-150, cyy, 8), (-500, cyy, 8)], 4)
    add("Cabling (12 V and motor leads)", cab, C_CABLE, "rubber", 11, "shell", (0, 0, 0))
    clips = None
    for (xx, zz) in ((-40, 1420), (-40, 1620), (40, 900), (40, 620), (40, 340)):
        dirv = Vector(xx, cyy, 0).normalized()
        c_ = _zcyl(0, 0, zz - 7, zz + 7, ro + 2.0) - _zcyl(0, 0, zz - 8, zz + 8, ro)
        c_ += _rod((dirv.X * (ro + 1), dirv.Y * (ro + 1), zz), (xx - dirv.X * 4.5, cyy - dirv.Y * 4.5, zz), 3.0)
        c_ += _zcyl(xx, cyy, zz - 7, zz + 7, 6.0) - _zcyl(xx, cyy, zz - 8, zz + 8, 4.0)
        clips = c_ if clips is None else clips + c_
    add("Cable stand-off clips", clips, C_DARK, "plastic", 13, "shell", (0, 0, 0))

    # ============================================================ anemometer (BOM 14)
    ar, za = P["anemo_reach"], P["anemo_z"]
    arm = _rod((0, ro - 2, za), (0, ar, za), 10)
    arm += Pos(0, ar, za) * Sphere(10)
    clamp = _zcyl(0, 0, za - 22, za + 22, ro + 4) - _zcyl(0, 0, za - 23, za + 23, ro)
    clamp += _box(-12, 12, ro, ro + 22, za - 22, za + 22) - _ycyl(0, ro - 1, ro + 30, za, 10)
    for zz in (za - 14, za + 14):
        clamp += _xcyl(-18, -12, ro + 11, zz, 4.5) + _xcyl(12, 18, ro + 11, zz, 4.5)
    post = _zcyl(0, ar, za, za + 60, 8)
    body = _zcyl(0, ar, za + 60, za + 94, 18)
    body = _fillet_try(body, _top(body), [8.0, 5.0])
    body = _fillet_try(body, _bottom(body), [3.0, 2.0])
    add("Anemometer side arm", arm, C_ALU, "metal", 14, "shell", (0, 300, 0))
    add("Anemometer arm clamp", clamp, C_GALV, "metal", 14, "shell", (0, 120, 0))
    add("Anemometer body", post + body, C_WHITE, "plastic", 14, "shell", (0, 300, 0))
    hub = _zcyl(0, ar, za + 94, za + 100, 9)
    hub = _fillet_try(hub, _top(hub), [3.0, 2.0])
    cups = None
    for dx, dy in [(70, 0), (-35, 61), (-35, -61)]:
        a = Vector(dx, dy, 0).normalized()
        tip = (a.X * 55, ar + a.Y * 55, za + 97)
        hub += _rod((0, ar, za + 97), tip, 3)
        c_ = Sphere(20) - Sphere(18.5) - Pos(0, -25, 0) * Box(60, 50, 60)          # open toward -Y (local)
        c_ = _fillet_try(c_, c_.edges(), [0.6, 0.4])
        yaw = degrees(atan2(dy, dx))
        c_ = Pos(dx, ar + dy, za + 97) * Rot(0, 0, yaw) * c_
        cups = c_ if cups is None else cups + c_
    add("Anemometer hub and spokes", hub, C_DARK, "plastic", 14, "shell", (0, 300, 40))
    add("Anemometer cups", cups, C_WHITE, "plastic", 14, "shell", (0, 300, 40))

    # ============================================================ power adapter (BOM 12), accessory
    pa = _fbox(-600, -530, -300, -255, 0, 42, [6.0, 4.0])
    pa += _pipe([(-530, -277, 20), (-480, -277, 20), (-470, -277, 8)], 2.5)
    for dz in (-8, 8):
        pa += _box(-608, -600, -281, -273, 21 + dz - 1.2, 21 + dz + 1.2)
    add("Power adapter, 12 V 3 A (indoor)", pa, C_DARK, "plastic", 12, "accessory", (-150, -250, 0))

    # ============================================================ context: ground patch, wall and window
    gpat = _box(-1160, 560, -470, 520, -60, -8)
    gpat = _fillet_try(gpat, gpat.edges().filter_by(Axis.Z), [60.0, 30.0])
    gpat = _fillet_try(gpat, _top(gpat), [6.0, 3.0])
    add("Ground patch (context)", gpat, C_GROUND, "paper", None, "context", (0, 0, 0))
    pav = _box(-320, 320, -320, 320, -60, 0)
    pav = _fillet_try(pav, _top(pav), [4.0, 2.0])
    add("Paver pad (context)", pav, C_PAVER, "paper", None, "context", (0, 0, 0))
    WX = -1000.0                                   # outside face of the wall (faces +X, toward the mast)
    wall = _box(WX - 140, WX, -460, 460, -60, 2250)
    wall -= _box(WX - 150, WX + 10, -400, 400, 950, 1950)
    add("House wall section (context)", wall, C_WALL, "paper", None, "context", (0, 0, 0))
    fr = _box(WX - 110, WX - 50, -400, 400, 950, 1950) - _box(WX - 120, WX - 40, -345, 345, 1005, 1895)
    fr += _box(WX - 100, WX - 60, -12, 12, 1005, 1895)             # mullion
    fr = _fillet_try(fr, fr.edges().filter_by(Axis.X), [3.0, 1.5])
    add("Target window frame (context)", fr, C_FRAME, "painted", None, "context", (0, 0, 0))
    pane_w = _box(WX - 83, WX - 77, -345, 345, 1005, 1895)
    add("Target window glazing (context)", pane_w, C_WINDOW, "clear", None, "context", (0, 0, 0))
    room = _box(WX - 140, WX - 130, -400, 400, 950, 1950)
    add("Room interior (context)", room, C_ROOM, "paper", None, "context", (0, 0, 0))
    sill = _box(WX - 50, WX + 45, -440, 440, 915, 950)
    sill = _fillet_try(sill, sill.edges().filter_by(Axis.Y), [4.0, 2.0])
    add("Window sill (context)", sill, C_SILL, "paper", None, "context", (0, 0, 0))
    feed = _pipe([(-500, cyy, 8), (-560, cyy, 0), (-620, cyy, -3), (WX + 20, cyy, -3), (WX + 20, cyy, 300)], 4)
    feed += _fbox(WX, WX + 14, cyy - 14, cyy + 14, 286, 314, [3.0, 1.5])            # wall entry grommet
    add("Outdoor feed cable to the house (context)", feed, C_CABLE, "rubber", 11, "context", (0, 0, 0))
    return out


if __name__ == "__main__":
    from collections import Counter
    ps = product_parts()
    for p in ps:
        s = p["shape"]
        print(f"{p['name']:44s} {p['group']:9s} {p['material']:8s} valid={s.is_valid} vol={s.volume / 1000:9.2f} cm3")
    print(Counter(p["group"] for p in ps))
