"""HelioLite sizing calculations (HLT-CAL-001).

Run from the repo root:  python docs/04-calcs/sizing.py
Prints every number quoted in docs/04-calcs/01-sizing.md, each line tagged [A1], [B2] and so on.
Geometry comes from cad/src/model.py (PARAMS and derived) so the note, the STEP files and
drawing HLT-DWG-001 use the same dimensions. First-principles estimates for a paper proof
of concept; not a substitute for datasheets or test.
"""
import csv
import sys
from math import radians, degrees, sin, cos, tan, asin, acos, atan, atan2, sqrt, pi, exp
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cad" / "src"))
from model import PARAMS as P, derived, parts  # noqa: E402

D = derived(P)
RES = {}          # requirement id -> (value text, target text, status)


def out(tag, text):
    print(f"[{tag}] {text}")


# ---------------------------------------------------------------- assumptions
A_M = (P["mirror"] / 1000) ** 2          # mirror area, m2
CHORD = P["mirror"] / 1000               # m
RHO_MIR = 0.93                           # solar-weighted reflectance, clean silvered glass
SOIL = 0.95                              # soiling factor
EDGE = 0.98                              # allowance for mirror edge, sun-shape tails and spill
TAU0 = 0.75                              # double glazing, beam at normal incidence
LM_W = 95.0                              # luminous efficacy of direct sunlight, lm/W
UF = 0.40                                # utilization factor, 3 x 4 m room with light ceiling
ROOM = 12.0                              # m2
SUN = radians(0.53)                      # sun angular diameter
DNI_DP = 800.0                           # design point DNI, W/m2
INC_DP = 32.0                            # design point incidence on the mirror, degrees
DIST_DP = 10.0                           # design point mirror to target, m
WIN_W, WIN_H = 1.0, 1.2                  # target window, m
LAT = 45.0

print("HelioLite sizing, HLT-CAL-001 v0.4")
print(f"Model: mirror {P['mirror']:.0f} mm, axis at {P['axis_z']:.0f} mm, mast {P['mast_od']} x {P['mast_wall']} mm, "
      f"length {P['mast_len']:.0f} mm, arms {P['arm_t']:.0f} x {P['arm_w']:.0f} mm")

# ---------------------------------------------------------------- A. optics at the design point
out("A1", f"Mirror area {A_M:.2f} m2; DNI x area {DNI_DP * A_M:.0f} W")
cosf = cos(radians(INC_DP))
p_int = DNI_DP * A_M * cosf
p_ref = p_int * RHO_MIR * SOIL
p_win = p_ref * EDGE
p_room = p_win * TAU0
lm = p_room * LM_W
lux = lm * UF / ROOM
out("A2", f"Cosine factor {cosf:.3f}; intercepted {p_int:.0f} W; reflected {p_ref:.0f} W; at the glazing {p_win:.0f} W; "
          f"into the room {p_room:.0f} W")
out("A3", f"Luminous flux {lm:,.0f} lm; mean added illuminance {lux:.0f} lx in {ROOM:.0f} m2")
out("A4", f"Beam irradiance at the target {RHO_MIR * SOIL:.2f} to {RHO_MIR:.2f} of DNI (flat mirror, no concentration)")
RES["R1"] = (f"{p_win:.0f} W at the glazing", "200 W or more", "Met" if p_win >= 200 else "Not met")
RES["R2"] = (f"{lux:.0f} lx mean added (UF 0.4 assumed)", "300 lx or more", "Met" if lux >= 300 else "Not met")

# Beam spot: projected mirror outline plus the sun's angular diameter
def spot(d, inc_deg):
    side = sqrt(A_M * cos(radians(inc_deg)))
    return side + d * SUN

POINT_BEAM = 0.5                          # R4 target, degrees
for d in (3.0, 10.0, 15.0, 20.0):
    s = spot(d, INC_DP)
    off = d * tan(radians(POINT_BEAM))
    fits = s + 2 * off <= WIN_W
    out("A5", f"Spot at {d:4.0f} m: {s:.2f} m square; 0.5 deg pointing offset {off * 1000:.0f} mm; "
              f"spot plus offset both sides {s + 2 * off:.2f} m against {WIN_W:.1f} m window: {'fits' if fits else 'spills'}")
d_max = (WIN_W - sqrt(A_M * cosf)) / (SUN + 2 * tan(radians(POINT_BEAM)))
out("A6", f"Largest distance at which spot plus 0.5 deg error fits a 1.0 m wide window: {d_max:.1f} m")

# ---------------------------------------------------------------- B. hourly energy at reference sites
def sun_vec(day, hour, lat=LAT):
    dec = radians(23.44) * sin(2 * pi * (284 + day) / 365)
    w = radians(15 * (hour - 12))
    la = radians(lat)
    return np.array([-cos(dec) * sin(w),
                     cos(la) * sin(dec) - sin(la) * cos(dec) * cos(w),
                     sin(la) * sin(dec) + cos(la) * cos(dec) * cos(w)])


def dni_clear(s, day):
    el = degrees(asin(max(min(s[2], 1), -1)))
    if el <= 1:
        return 0.0
    z = 90 - el
    am = 1 / (cos(radians(z)) + 0.50572 * (96.07995 - z) ** -1.6364)
    e0 = 1361 * (1 + 0.033 * cos(2 * pi * day / 365))
    return e0 * 0.7 ** (am ** 0.678)


HOUSE = (np.array([-5.0, -8.0, 0.0]), np.array([5.0, 0.0, 5.5]))   # box south of the north wall (y = 0)
WIN = np.array([0.0, 0.0, 1.5])                                     # window center, facing +y (north)


def hits_box(o, d, box):
    lo, hi = box
    tmin, tmax = 0.0, 1e9
    for i in range(3):
        if abs(d[i]) < 1e-12:
            if o[i] < lo[i] or o[i] > hi[i]:
                return False
        else:
            t1, t2 = (lo[i] - o[i]) / d[i], (hi[i] - o[i]) / d[i]
            tmin, tmax = max(tmin, min(t1, t2)), min(tmax, max(t1, t2))
            if tmin > tmax:
                return False
    return True


def fresnel_tau(theta_deg):
    """Double glazing beam transmittance, 4 air-glass surfaces (n = 1.52), scaled to TAU0 at normal incidence."""
    def surf(th):
        th = radians(th)
        tr = asin(sin(th) / 1.52)
        if th < 1e-6:
            r = ((1.52 - 1) / (1.52 + 1)) ** 2
            return 1 - r, tr
        rs = (sin(th - tr) / sin(th + tr)) ** 2
        rp = (tan(th - tr) / tan(th + tr)) ** 2
        return 1 - (rs + rp) / 2, tr
    t0, _ = surf(0.0)
    t, tr = surf(theta_deg)
    k = TAU0 / t0 ** 4                      # absorption share at normal incidence
    absorb = k ** (1 / cos(tr))
    return t ** 4 * absorb


def site_day(mx, my, day, step_h=1 / 12):
    m = np.array([mx, my, P["axis_z"] / 1000])
    tvec = WIN - m; dist = np.linalg.norm(tvec); t = tvec / dist
    b = -t                                   # beam arrives at the window travelling along t; window normal +y
    th_h = degrees(atan2(abs(t[0]), abs(t[1])))
    th_v = degrees(atan2(abs(t[2]), abs(t[1])))
    th_w = degrees(acos(abs(t[1])))
    tau = fresnel_tau(th_w)
    e_win = e_room = 0.0; hours = 0.0; cos_sum = 0.0; peak = 0.0
    naz = []
    h = 6.0
    while h <= 18.0:
        s = sun_vec(day, h)
        dni = dni_clear(s, day)
        if dni > 0 and not hits_box(m, s, HOUSE):
            n = (s + t) / np.linalg.norm(s + t)
            ci = float(n @ s)
            side = sqrt(A_M * ci) + dist * SUN
            icpt = min(1, WIN_W * cos(radians(th_h)) / side) * min(1, WIN_H * cos(radians(th_v)) / side)
            pw = dni * A_M * ci * RHO_MIR * SOIL * icpt
            e_win += pw * step_h; e_room += pw * tau * step_h
            hours += step_h; cos_sum += ci * step_h; peak = max(peak, pw * tau)
            naz.append(degrees(atan2(n[0], n[1])))
        h += step_h
    return {"dist": dist, "th_w": th_w, "tau": tau, "e_win": e_win / 1000, "e_room": e_room / 1000,
            "hours": hours, "cos": cos_sum / hours if hours else 0, "peak": peak, "naz": naz, "t": t}


# Generic check with the TRL 2 assumptions: 6 h, mean DNI 650, mean cosine 0.80
g_win = 650 * A_M * 0.80 * 6 * RHO_MIR * SOIL * EDGE / 1000
out("B1", f"TRL 2 generic day (6 h, mean DNI 650 W/m2, mean cosine 0.80): {g_win:.2f} kWh at the window, "
          f"{g_win * TAU0:.2f} kWh through the glazing")
SITES = {"A": (6.0, 8.0), "B": (8.0, 5.0), "C": (0.0, 15.0)}
DAYS = {"21 Dec": 355, "1 Feb": 32}
site_res = {}
for name, (mx, my) in SITES.items():
    for dname, day in DAYS.items():
        r = site_day(mx, my, day)
        site_res[(name, dname)] = r
        out("B2", f"Site {name} mirror at ({mx:+.0f}, {my:+.0f}) m, {r['dist']:.1f} m from window, glazing incidence "
                  f"{r['th_w']:.0f} deg (tau {r['tau']:.2f}), {dname}: sunlit tracking {r['hours']:.1f} h, mean cosine "
                  f"{r['cos']:.2f}, {r['e_win']:.2f} kWh at window, {r['e_room']:.2f} kWh into room, peak {r['peak']:.0f} W")
rA = site_res[("A", "21 Dec")]
rA2 = site_res[("A", "1 Feb")]
out("B3", f"Reference site A: {rA['e_room']:.3f} kWh on 21 Dec and {rA2['e_room']:.3f} kWh on 1 Feb through the glazing "
          f"(clear-sky Meinel model, house 10 x 8 x 5.5 m to the south of the window wall)")
best = max(site_res.items(), key=lambda kv: kv[1]["e_room"])
out("B4", f"Best case in the table: site {best[0][0]} on {best[0][1]}, {best[1]['e_room']:.2f} kWh")
r3_ok_dec = rA["e_room"] >= 0.5
RES["R3"] = (f"{rA['e_room']:.2f} kWh on 21 Dec and {rA2['e_room']:.2f} kWh on 1 Feb at reference site A; "
             f"{site_res[('B', '21 Dec')]['e_room']:.2f} kWh at site B on 21 Dec", "0.5 kWh or more on a clear winter day",
             "At risk" if rA2["e_room"] >= 0.5 else "Not met")  # site dependent; site A has no margin on 21 Dec, site B misses

# ---------------------------------------------------------------- C. structure: mast and yoke stiffness
E_ST, G_ST, E_ASA = 200e3, 80e3, 1.8e3          # N/mm2 (ASA as printed, about 1.8 GPa)
ro = P["mast_od"] / 2; ri = ro - P["mast_wall"]
I_m = pi / 4 * (ro ** 4 - ri ** 4); Z_m = I_m / ro; J_m = 2 * I_m
EI = E_ST * I_m
L_m = D["mast_top"]; lev = D["lever"]
out("C1", f"Mast I = {I_m:,.0f} mm4, EI = {EI:.2e} N mm2, section modulus {Z_m:,.0f} mm3")


def q(v):
    return 0.5 * 1.225 * v * v


F8 = 1.2 * q(8) * A_M                             # face-on normal force at 8 m/s, N
M_top = F8 * (lev - L_m)                          # moment at the mast top from the offset above it, N mm
theta_mast = F8 * L_m ** 2 / (2 * EI) + M_top * L_m / EI
out("C2", f"8 m/s face-on: force {F8:.1f} N; mast top slope {degrees(theta_mast):.3f} deg (normal error)")
I_al = 9.0e4; theta_al = F8 * 2200 ** 2 / (2 * 70e3 * I_al)
out("C3", f"Same load on a 2.2 m 40 x 40 mm aluminum extrusion (I about 9e4 mm4): {degrees(theta_al):.2f} deg")
# Yoke arms: aluminum rectangular tube cantilevers (HLT-DDR-003) from the crossbar top to the elevation axis,
# bending in the Y-Z plane (rotation about the elevation axis)
E_AL = 69e3
La = D["arm_free"]
aw_, at_, t_ = P["arm_w"], P["arm_t"], P["arm_wall"]
Ia = (at_ * aw_ ** 3 - (at_ - 2 * t_) * (aw_ - 2 * t_) ** 3) / 12
Mh8 = 0.25 * q(8) * A_M * CHORD * 1000           # hinge moment, N mm
th_arm = ((F8 / 2) * La ** 2 / 2 + Mh8 * La) / (E_AL * Ia)
Ia_asa = 40 * 70 ** 3 / 12
th_asa = ((F8 / 2) * La ** 2 / 2 + Mh8 * La) / (E_ASA * Ia_asa)
out("C4", f"Yoke arm, aluminum tube {P['arm_t']:.0f} x {P['arm_w']:.0f} x {P['arm_wall']:.0f} mm, {La:.0f} mm above the crossbar: "
          f"slope {degrees(th_arm):.3f} deg at 8 m/s (hinge moment {Mh8 / 1000:.1f} N m reacted by the drive arm); "
          f"the concept's solid printed 40 x 70 mm ASA arm would give {degrees(th_asa):.3f} deg")
yaw8 = 0.1 * q(8) * A_M * CHORD * 1000
tw = yaw8 * L_m / (G_ST * J_m)
out("C5", f"Mast twist from an assumed yaw moment {yaw8 / 1000:.2f} N m at 8 m/s: {degrees(tw):.4f} deg")

# ---------------------------------------------------------------- D. pointing error budget and calibration
clock_s = 2e-6 * 182.5 * 86400
clock_beam = clock_s / 3600 * 15.0              # deg of sun motion at 15 deg/h (conservative)
out("D1", f"Clock drift at +/-2 ppm for 6 months: {clock_s:.1f} s, sun moves {clock_beam:.3f} deg (beam), "
          f"{clock_beam / 2:.3f} deg (normal equivalent)")
RES["R6"] = (f"{clock_s:.0f} s after 6 months (DS3231, +/-2 ppm)", "60 s or less", "Met" if clock_s <= 60 else "Not met")
step = 1.8 / 16 / 50
out("D2", f"Step resolution {step:.4f} deg at the output (1.8 deg, 16 microsteps, 50:1)")

# Calibration simulation: mount model with azimuth and elevation zero offsets, two base tilts and mirror cant
rng = np.random.default_rng(3)
t_A = site_res[("A", "21 Dec")]["t"]


def rotz(a):
    return np.array([[cos(a), -sin(a), 0], [sin(a), cos(a), 0], [0, 0, 1]])


def rotx(a):
    return np.array([[1, 0, 0], [0, cos(a), -sin(a)], [0, sin(a), cos(a)]])


def roty(a):
    return np.array([[cos(a), 0, sin(a)], [0, 1, 0], [-sin(a), 0, cos(a)]])


def normal(p, a, e):
    a0, e0, tx, ty, g = p
    n0 = np.array([sin(g), cos(g), 0.0])
    return rotx(tx) @ roty(ty) @ rotz(-(a + a0)) @ rotx(e + e0) @ n0


def ideal_angles(n):
    return atan2(n[0], n[1]), asin(n[2])


def calib_trial(hours, sigma_deg, day=355):
    true = np.array([radians(rng.uniform(-10, 10)), radians(rng.uniform(-3, 3)),
                     radians(rng.normal(0, 1)), radians(rng.normal(0, 1)), radians(rng.normal(0, 0.3))])
    meas = []
    for h in hours:
        s = sun_vec(day, h); n = (s + t_A) / np.linalg.norm(s + t_A)
        # find the motor angles that put the true normal on n, then add the user's jog error
        a, e = ideal_angles(n)
        sol = least_squares(lambda x: normal(true, x[0], x[1]) - n, [a, e])
        a, e = sol.x + np.radians(rng.normal(0, sigma_deg, 2))
        meas.append((a, e, n))
    fit = least_squares(lambda p: np.concatenate([normal(p, a, e) - n for a, e, n in meas]), np.zeros(5))
    worst = 0.0
    for h in np.arange(9.0, 15.01, 0.25):
        s = sun_vec(day, h); n = (s + t_A) / np.linalg.norm(s + t_A)
        cmd = least_squares(lambda x: normal(fit.x, x[0], x[1]) - n, ideal_angles(n)).x
        got = normal(true, cmd[0], cmd[1])
        worst = max(worst, degrees(acos(min(1.0, float(got @ n)))))
    return worst


SIG = 0.05
cal = {}
for label, hrs in {"3 points over 30 min": [11.75, 12.0, 12.25], "3 points over 3 h": [10.5, 12.0, 13.5],
                   "4 points over 4 h": [10.0, 11.33, 12.67, 14.0]}.items():
    w = np.array([calib_trial(hrs, SIG) for _ in range(120)])
    cal[label] = (np.median(w), np.percentile(w, 95))
    out("D3", f"Calibration, {label}, jog error {SIG} deg per axis: worst normal error over 09:00 to 15:00, "
              f"median {cal[label][0]:.3f} deg, 95th percentile {cal[label][1]:.3f} deg")
cal_resid = cal["4 points over 4 h"][0]
cal_resid95 = cal["4 points over 4 h"][1]

BACKLASH = 1.0          # NMRV030 listed output backlash, degrees
PRELOAD_RESID = 0.05    # lost motion left when a preload keeps the teeth on one flank, degrees (assumption)
budget = [("Sun-position algorithm (Grena 5)", 0.0027 / 2),
          ("Clock, 6 months without network time", clock_beam / 2),
          ("Mount model residual, 4 points over 4 h (median)", cal_resid),
          ("Worm backlash with preload", PRELOAD_RESID),
          ("Step resolution", step),
          ("Mast bending, 8 m/s", degrees(theta_mast)),
          ("Yoke arm flex, 8 m/s", degrees(th_arm))]
rss = sqrt(sum(v * v for _, v in budget))
for n_, v in budget:
    out("D4", f"  {n_:58s} {v:.3f} deg normal")
out("D5", f"Root sum square {rss:.3f} deg normal, {2 * rss:.2f} deg beam, against 0.5 deg beam")
rss95 = sqrt(rss ** 2 - cal_resid ** 2 + cal_resid95 ** 2)
out("D5", f"With the 95th percentile calibration residual ({cal_resid95:.3f} deg): {rss95:.3f} deg normal, {2 * rss95:.2f} deg beam")
rss_nopre = sqrt(rss ** 2 - PRELOAD_RESID ** 2 + (BACKLASH / 2) ** 2)
out("D6", f"Without preload, half the listed {BACKLASH:.0f} deg backlash can appear when the wind reverses the load: "
          f"{2 * rss_nopre:.2f} deg beam")
Mimb = None  # filled in section H
RES["R4"] = (f"{2 * rss:.2f} deg beam typical and {2 * rss95:.2f} deg at the 95th percentile with the decided preload springs; "
             f"{2 * rss_nopre:.2f} deg without preload",
             "0.5 deg beam at up to 8 m/s", "At risk")

# ---------------------------------------------------------------- E. wind, gearboxes, mast and anchor
C_F, C_MH, C_MS, C_FS = 1.2, 0.25, 0.15, 0.6     # face-on force, operating hinge moment, stowed hinge moment, stowed normal force
GB_RATED, GB_MAX = 17.0, 22.0                   # N m, NMRV030 50:1 listed rated and maximum output torque
YIELD = 240.0                                    # MPa, ASTM A53 grade B pipe
mast_drag = lambda v: 1.2 * q(v) * (P["mast_od"] / 1000) * (L_m / 1000)
rows = []
for v, pose in [(8, "tracking"), (15, "tracking"), (20, "tracking"), (35, "stowed"), (35, "tracking")]:
    qq = q(v)
    if pose == "stowed":
        F = C_FS * qq * A_M; Mh = C_MS * qq * A_M * CHORD
    else:
        F = C_F * qq * A_M; Mh = C_MH * qq * A_M * CHORD
    Mb = F * lev / 1000 + mast_drag(v) * L_m / 2000
    sig = Mb * 1000 / Z_m
    rows.append((v, pose, qq, F, Mh, Mb, sig))
    gb = "within rating" if Mh <= GB_RATED else ("above rating, below listed maximum" if Mh <= GB_MAX else "ABOVE listed maximum")
    out("E1", f"{v:>2} m/s {pose:8s}: q {qq:5.0f} Pa, mirror force {F:5.0f} N, hinge moment {Mh:5.1f} N m ({gb}), "
              f"mast base moment {Mb:5.0f} N m, mast stress {sig:4.0f} MPa")
Mh_stow = rows[3][4]; Mb_face = rows[4][5]; sig_face = rows[4][6]
out("E2", f"Stowed hinge moment at 35 m/s {Mh_stow:.1f} N m against {GB_RATED:.0f} N m rated and {GB_MAX:.0f} N m maximum "
          f"(stowed moment coefficient {C_MS} assumed)")
v_ok = sqrt(GB_RATED / (C_MS * 0.5 * 1.225 * A_M * CHORD))
out("E3", f"Stowed gust at which the hinge moment reaches the {GB_RATED:.0f} N m rating: {v_ok:.1f} m/s")
out("E4", f"Worst case, caught face-on at 35 m/s: mast stress {sig_face:.0f} MPa against {YIELD:.0f} MPa yield "
          f"(factor {YIELD / sig_face:.1f}); anchor must resist {Mb_face / 1000:.2f} kN m")
TRIG = 15.0
out("E5", f"Stow trigger: gust {TRIG:.0f} m/s from the anemometer, or a forecast gust above {TRIG:.0f} m/s; hinge moment at the "
          f"trigger {rows[1][4]:.1f} N m, within the rating")
out("E6", f"Without the stow latch the stowed moment would exceed the gearbox's listed maximum by {Mh_stow - GB_MAX:.1f} N m (TRL 3, v0.1 result)")
# Stow stop and latch (decided 2026-09-25, HLT-DDR-002 N1): lug trapped between a polyurethane stop pad and a sprung latch pawl
SF_COEF = 2.0                                    # design factor on the assumed stowed hinge moment coefficient
M_des = SF_COEF * Mh_stow
F_stop = M_des / (P["stop_r"] / 1000)
PAD_A = 24.0 * P["lug_t"]                        # pad contact area, mm2 (24 mm wide pad on the 8 mm lug)
E_PU = 50.0                                      # MPa, polyurethane 90A (assumed)
d_pad = F_stop * P["pad_t"] / (E_PU * PAD_A)
d_free = radians(BACKLASH / 2) * P["stop_r"]     # lug travel at mid-backlash before the worm teeth touch
# Sliding pawl (HLT-DDR-003): 12 x 8 mm steel tongue cantilevered from its slot in the bracket to the lug center
PW_B, PW_H, PW_L = 12.0, 8.0, 13.0               # width, depth, lever from the bracket face to the lug mid-plane (mm)
sig_pawl = F_stop * PW_L / (PW_B * PW_H ** 2 / 6)
# Bracket screws: two M6 through the -X arm, 37 mm apart, 33 mm from the contact line
F_scr = F_stop / 2 + F_stop * 33.0 / 37.0
out("E7", f"Stow latch design moment {M_des:.1f} N m ({SF_COEF:.0f}x the assumed stowed moment, i.e. a stowed moment coefficient up to "
          f"{SF_COEF * C_MS:.2f}); force at the {P['stop_r']:.0f} mm contact radius {F_stop:.0f} N")
out("E8", f"Stop pad {P['pad_t']:.0f} mm PU 90A (E {E_PU:.0f} MPa assumed) on {PAD_A:.0f} mm2: stress {F_stop / PAD_A:.1f} MPa, "
          f"deflection {d_pad:.2f} mm against {d_free:.2f} mm free travel with the worm backed off to mid-backlash, so the gearbox carries "
          f"{'no stowed moment' if d_pad < d_free else 'part of the moment'}; sliding pawl 12 x 8 mm bending {sig_pawl:.0f} MPa "
          f"(steel, 275 MPa yield); bracket screws up to {F_scr:.0f} N each in shear (M6 8.8 about 9 kN)")
RES["R9"] = (f"Stowed moment {Mh_stow:.0f} N m at 35 m/s carried by the stow stop and latch (designed for {M_des:.0f} N m), not the gearbox; "
             f"stow trigger {rows[1][4]:.1f} N m within the {GB_RATED:.0f} N m rating; mast {sig_face:.0f} MPa worst case",
             "Hold R4 to 8 m/s; survive 35 m/s in stow",
             "Met" if (d_pad < d_free and Mh_stow <= M_des) else "Not met")

# ---------------------------------------------------------------- F. stow on power loss
RATE = 10.0                                      # deg/s output slew in a stow
t_stow = 180.0 / RATE
DETECT = 5.0                                     # s to detect power loss and start
P_STOW = 2 * 1.0 ** 2 * 1.5 + 0.3 + 0.5          # two coils at 1.0 A rms in 1.5 ohm, driver, ESP32 without Wi-Fi, W
E_need = P_STOW * (t_stow + DETECT)
C_bank = 25.0 / 5; V1, V2, ETA = 12.0 - 0.3, 7.0, 0.85
E_avail = 0.5 * C_bank * (V1 ** 2 - V2 ** 2) * ETA
out("F1", f"Worst-case stow: 180 deg of elevation at {RATE:.0f} deg/s = {t_stow:.0f} s, plus {DETECT:.0f} s to detect; "
          f"power {P_STOW:.1f} W, energy {E_need:.0f} J")
out("F2", f"Bank of five 2.7 V 25 F cells: {C_bank:.0f} F, {V1:.1f} V to {V2:.1f} V, {E_avail:.0f} J usable after "
          f"{ETA:.0%} conversion; margin {E_avail / E_need:.1f}x; {V1 / 5:.2f} V per cell against 2.7 V rated")
# Beam path during a stow from the design pose at site A (rotating the normal downward about the elevation axis)
s0 = sun_vec(355, 11.0); n0 = (s0 + t_A) / np.linalg.norm(s0 + t_A)
az0, el0 = ideal_angles(n0)
t_beyond = 0.0; t_lit = 0.0; max_up = -90.0
dt = 0.05; e = el0
while e > -pi / 2:
    n = np.array([cos(e) * sin(az0), cos(e) * cos(az0), sin(e)])
    if n @ s0 > 0:
        r = -s0 + 2 * (n @ s0) * n
        rel = degrees(asin(r[2]))
        max_up = max(max_up, rel)
        t_lit += dt
        if r[2] < 0:
            dg = (P["axis_z"] / 1000) / tan(-asin(r[2]))
            if dg > 3.0:
                t_beyond += dt
        else:
            t_beyond += dt
    e -= radians(RATE) * dt
init_el = degrees(asin((-s0 + 2 * (n0 @ s0) * n0)[2]))
out("F4", f"Stow from site A at 11:00 on 21 Dec: beam starts at {init_el:.1f} deg elevation, never rises above {max_up:.1f} deg; "
          f"reflection ends after {t_lit:.1f} s; beam on ground beyond 3 m from the mast (or above ground) for {t_beyond:.1f} s")
RES["R10"] = (f"Stow in {t_stow + DETECT:.0f} s on stored energy (margin {E_avail / E_need:.1f}x); beam moves only downward, "
              f"sweeping the ground between target and mast for about {t_beyond:.1f} s",
              "Target or ground within 3 m when stowed; beam only downward during a stow; stow within 60 s",
              "Met" if (max_up < 0 and t_stow + DETECT <= 60 and E_avail > E_need) else "Not met")

# ---------------------------------------------------------------- G. calibration time (task analysis)
tasks = [("Open the web page, enter location and target", 5), ("Jog the spot onto the target, point 1", 3),
         ("Point 2", 3), ("Point 3", 3), ("Point 4", 3), ("Fit, check the spot, save", 2)]
hands_on = sum(m for _, m in tasks)
out("G1", "Calibration hands-on time: " + "; ".join(f"{n} {m} min" for n, m in tasks) + f"; total {hands_on} min")
out("G2", "Elapsed time: four or more points spread over about 4 h give a residual near 0.1 deg (D3); over 30 min the fit is poorly conditioned")
RES["R7"] = (f"{hands_on} min hands-on for four points spread over about 4 h of one day", "30 min hands-on or less, over one clear day; no survey instrument",
             "Met" if hands_on <= 30 else "Not met")

# ---------------------------------------------------------------- H. mass and balance
from model import build_components  # noqa: E402
CC = build_components()
vol = lambda *ks: sum(CC[k][1].volume for k in ks) / 1e3        # noqa: E731  cm3
RHO_AL, RHO_ST, RHO_BR, RHO_ASA = 2.70e-3, 7.85e-3, 8.8e-3, 1.07e-3 * 0.60   # kg/cm3 (ASA at 60 % infill)
m_glass = A_M * P["glass_t"] / 1000 * 2500
m_acp = A_M * 5.5
m_tube = vol("tube") * RHO_AL
m_ribs = vol("ribs") * RHO_AL
m_trun = vol("blocks") * RHO_AL + vol("stubs", "block_bolts") * RHO_ST
m_glue = 0.2
m_mirror = m_glass + m_acp + m_tube + m_ribs + m_trun + m_glue
m_yoke_al = vol("crossbar", "arm_r", "arm_l", "gussets") * RHO_AL
m_yoke = m_yoke_al + vol("gusset_bolts", "cross_bolts") * RHO_ST + vol("plugs") * RHO_ASA + vol("bushes") * RHO_BR
M_GB, M_MOT, M_ADP = 1.2, 0.36, 0.10
m_drive = M_GB + M_MOT + M_ADP + vol("el_bolts") * RHO_ST / 2
m_tt = vol("disc", "hub") * RHO_AL + vol("shaft") * RHO_ST + vol("washer") * RHO_BR
m_lug = vol("lug") * RHO_ST
M_SOL = 0.06                                     # pull solenoid (assumed)
M_SPRING = 0.08                                  # each spiral spring in its can (assumed)
m_latch = m_lug + vol("bracket", "pawl", "latch_bolts") * RHO_ST + M_SOL
m_top = m_mirror + m_yoke + 2 * m_drive + m_tt + m_latch + 2 * M_SPRING
M_LIMIT = 13.0                                   # R13 as relaxed on 2026-09-25 (HLT-DDR-002 N3)
m_mast = pi / 4 * (P["mast_od"] ** 2 - (P["mast_od"] - 2 * P["mast_wall"]) ** 2) * P["mast_len"] * 7.85e-6
m_cap = P["cap"] ** 2 * P["cap_t"] * 7.85e-6
out("H1", f"Mirror assembly {m_mirror:.2f} kg (glass {m_glass:.2f}, panel {m_acp:.2f}, tube {m_tube:.2f}, ribs {m_ribs:.2f}, "
          f"trunnion blocks, stubs and bolts {m_trun:.2f}, adhesive and film {m_glue:.2f})")
out("H2", f"Yoke {m_yoke:.2f} kg (aluminum tubes and gussets {m_yoke_al:.2f}, bolts, printed plugs and bushes); each drive {m_drive:.2f} kg "
          f"(gearbox {M_GB} kg assumed); turntable, hub and shaft {m_tt:.2f} kg")
out("H3", f"Stow stop and latch {m_latch:.2f} kg (lug {m_lug:.2f}, solenoid {M_SOL} assumed); preload springs 2 x {M_SPRING} kg (assumed)")
out("H3", f"On the mast top {m_top:.2f} kg against {M_LIMIT:.0f} kg (margin {M_LIMIT - m_top:.2f} kg); mast pipe {m_mast:.1f} kg; cap plate {m_cap:.1f} kg")
zb = P["tube"] / 2
com = (m_glass * (zb + P["back_t"] + P["glass_t"] / 2) + m_acp * (zb + P["back_t"] / 2) + m_ribs * (zb - P["rib"][1] / 2)
       + m_glue * (zb + P["back_t"])) / m_mirror
Mimb = m_mirror * 9.81 * com / 1000
out("H4", f"Mirror center of mass {com:.1f} mm in front of the elevation axis; gravity moment up to {Mimb:.2f} N m")
Mpre = Mh8 / 1000 + Mimb
out("H5", f"Preload to keep the worm on one flank at 8 m/s: more than {Mpre:.1f} N m (hinge {Mh8 / 1000:.1f} plus imbalance "
          f"{Mimb:.1f}); motor torque with a 3 N m spring plus wind and imbalance, worm efficiency 0.4: "
          f"{(3 + Mpre) / 50 / 0.4:.2f} N m")
RES["R13"] = (f"{m_top:.2f} kg on the mast top (margin {M_LIMIT - m_top:.2f} kg)", "13 kg or less; two people, hand tools, 4 h",
              "Met" if m_top <= M_LIMIT else "Not met")

# ---------------------------------------------------------------- I. power
P_IDLE, P_MOVE, T_MOVE = 0.40, 5.0, 1.0
P_BAL = 5 * (2.4 ** 2 / 1000)
p_avg = P_IDLE + P_MOVE * T_MOVE / 30 + P_BAL
out("I1", f"Average power {p_avg:.2f} W (idle {P_IDLE} W, moves {P_MOVE * T_MOVE / 30:.2f} W, stow reserve balancing "
          f"{P_BAL:.3f} W); {p_avg * 24:.0f} Wh/day")
RES["R14"] = (f"{p_avg:.2f} W average", "3 W or less", "Met" if p_avg <= 3 else "Not met")

# ---------------------------------------------------------------- J. cost
VE_TARGET = 455.0  # budget_usd: a hypothetical value-engineering target, not a limit (Amish, 2026-10-01)
rows_b = list(csv.DictReader((ROOT / "bom" / "bom.csv").open()))
total = sum(float(r["qty"]) * float(r["unit_cost_usd"]) for r in rows_b)
diff = total - VE_TARGET
out("J1", f"BOM {len(rows_b)} lines, all priced: estimated cost ${total:,.2f} against the ${VE_TARGET:.0f} value-engineering target; "
          f"${abs(diff):.2f} {'over' if diff > 0 else 'under'} the target")
out("J2", "Not in the BOM: tools, printer time, shipping. Lines 16 and 17 added under HLT-DDR-002; lines 2, 3, 5, 6, 9, 13, 14 and 17 "
          "repriced under HLT-DDR-003 (design for construction)")
RES["R15"] = (f"${total:,.0f} (${abs(diff):.0f} {'over' if diff > 0 else 'under'} the target)",
              "$455 value-engineering target (a hypothetical control target)",
              "Over the value-engineering target" if diff > 0 else "Met")

# ---------------------------------------------------------------- K. remaining requirements and summary
naz = site_res[("A", "21 Dec")]["naz"]
t_az = degrees(atan2(t_A[0], t_A[1]))
spread = max(abs(((a - t_az + 180) % 360) - 180) for a in naz) if naz else 0
out("K1", f"Site A: normal azimuth within {spread:.0f} deg of the target direction (range +/-135 deg); arm gap {D['arm_gap']:.0f} mm, "
          f"crossbar gap {D['cross_gap']:.0f} mm to the mirror sweep, so face-down stow clears the yoke; stow lug {-(P['lug_x'] + P['lug_t'] / 2) - P['mirror'] / 2:.0f} mm "
          f"outside the mirror edge and {(P['lug_x'] - P['lug_t'] / 2) - (-P['arm_x'] + P['arm_t'] / 2):.0f} mm inside the -X arm")
RES["R5"] = ("Time, location and target only; Hall switches for homing, anemometer for weather", "No sun sensor or camera", "Met")
RES["R8"] = (f"Mechanical range met; spot plus error fits a 1.0 m window up to {d_max:.0f} m", "3 to 20 m; +/-135 deg; -90 to +90 deg",
             "Met")
RES["R11"] = ("12 V SELV outdoors, IP65 box, listed indoor adapter", "SELV, IP65, listed adapter", "Met")
RES["R12"] = ("ASA, galvanized steel, glass with backing film by selection", "-20 to +45 C, UV, corrosion, 10 years",
              "Not verifiable at TRL 3")
order = {"Not met": 0, "Over the value-engineering target": 1, "At risk": 2, "Not verifiable at TRL 3": 3, "Met": 4}
print("\nResults by requirement")
for rid in sorted(RES, key=lambda k: (order[RES[k][2]], int(k[1:]))):
    v, tgt, st = RES[rid]
    out("K2", f"{rid:4s} {st:24s} {v}  (target: {tgt})")
counts = {s: sum(1 for r in RES.values() if r[2] == s) for s in order}
out("K3", ", ".join(f"{n} {s.lower()}" for s, n in counts.items()) + f"; {len(RES)} requirements")
