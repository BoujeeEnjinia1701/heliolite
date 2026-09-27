"""Shared scale-context parts for renders: a smooth clay forearm and hand, and a full-body mannequin.

Use in cad/src/product_model.py for wearables and handheld devices:

    import sys; sys.path.insert(0, ".kit")
    from context_parts import forearm_hand
    arm = forearm_hand(side="left", pose="flat")          # wrist at the origin, hand toward +X, back of hand +Z
    arm = Pos(x, y, z) * Rot(0, 0, 90) * arm               # place it with build123d locations

Coordinates in mm. The wrist centre is at the origin, the forearm runs along -X to the elbow, the hand
along +X, the back of the hand faces +Z. side="left" puts the thumb at +Y (palm down, as seen from above),
side="right" at -Y. pose="flat" rests the hand on a table; pose="grip" curls the fingers around a
cylinder of diameter grip_d centred at (grip_x, 0, -grip_d / 2 - 5) so a handle can be placed there.
Proportions follow an average adult (forearm 250 mm, hand 185 mm); this is a render prop, not anatomy.

For larger systems (bicycles, cargo trikes, hand trucks, pallet jacks, walk-inside carriers, shelters,
street furniture) use the full-body mannequin. It faces -Y (toward a viewer at azim -40), the pelvis
sits over x = 0, y = 0, and the feet stand on z = 0 except in "ride" and "sit", which anchor the seat.
Poses: "stand", "walk", "push", "ride", "sit" and "reach"; every joint angle can be overridden.

    from context_parts import mannequin, mannequin_landmarks
    person = mannequin(1750, "stand")                        # one smooth Solid, 1750 mm tall
    parts.append(Part("Person, 1.75 m (scale)", Pos(x, y, 0) * person, "#9CA3AF"))

    lm = mannequin_landmarks(1750, "push")                   # grips at 1.0 m, 520 mm ahead of the pelvis
    gy = lm["hands"][0][1]                                   # both grips share y and z
    pusher = Pos(0, bar_y - gy, 0) * mannequin(1750, "push")   # hands meet a hip bar at y = bar_y

    lm = mannequin_landmarks(1750, "ride")                   # cyclist on an implied bicycle
    bx, by, bz = lm["bb"]                                    # bottom bracket; "seat" and "pedals" too
    rider = Pos(bb_x - bx, bb_y - by, bb_z - bz) * mannequin(1750, "ride")   # onto your frame's BB

    sitter = Pos(x, y, 0) * mannequin(1650, "sit")           # seat contact 450 mm up, 20 mm behind (x, y)
    fitter = mannequin(1750, "reach", shoulder_flex_r=150)   # any preset angle can be overridden

Landmarks (all in mm, world coordinates of the unmoved figure): "pelvis", "seat", "hands", "wrists",
"elbows", "shoulders", "knees", "feet" (sole under the ball of each foot), "heels", "head_top",
"joints" (the resolved angles) and, for "ride", "bb" and "pedals". Pairs are listed [left, right].
"""
from math import radians, sin, cos, atan2, acos, degrees
from build123d import (Plane, Ellipse, Circle, Sketch, loft, Solid, Sphere, Cylinder, Pos, Rot, Compound,
                       Vector, Location, scale)


def _ellipse_section(x, a, b, z=0.0):
    pl = Plane(origin=(x, 0, z), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    return pl * Ellipse(a / 2, b / 2)


def _capsule(p0, p1, r0, r1):
    """Tapered capsule from p0 to p1 (radii r0, r1)."""
    p0, p1 = Vector(*p0), Vector(*p1)
    d = p1 - p0
    L = d.length
    pl0 = Plane(origin=p0, z_dir=d.normalized())
    pl1 = Plane(origin=p1, z_dir=d.normalized())
    body = loft([pl0 * Circle(r0), pl1 * Circle(r1)])
    return body + Pos(*p0) * Sphere(r0) + Pos(*p1) * Sphere(r1)


def _finger(base, length, r, pose, side_sign, spread_deg=0.0, curl=None):
    """Three-segment finger from base, pointing +X, curled toward -Z in the grip pose."""
    segs = [0.45, 0.30, 0.25]
    if curl is None:
        curl = [8, 10, 8] if pose == "flat" else [55, 70, 60]
    pts = [Vector(*base)]
    ang = 0.0
    yaw = radians(spread_deg)
    for s, c in zip(segs, curl):
        ang += radians(c)
        step = length * s
        dx = step * cos(ang) * cos(yaw)
        dy = step * cos(ang) * sin(yaw)
        dz = -step * sin(ang)
        pts.append(pts[-1] + Vector(dx, dy, dz))
    shape = None
    for i in range(3):
        r0 = r * (1.0 - 0.08 * i)
        r1 = r * (1.0 - 0.08 * (i + 1))
        seg = _capsule(tuple(pts[i]), tuple(pts[i + 1]), r0, r1)
        shape = seg if shape is None else shape + seg
    return shape


def forearm_hand(side="left", pose="flat", forearm_len=250.0, grip_d=40.0, include_forearm=True):
    s = 1 if side == "left" else -1
    parts = []
    if include_forearm:
        # forearm: elbow (-L) to wrist (0), elliptical sections, flatter at the wrist
        secs = [(-forearm_len, 78, 68), (-0.7 * forearm_len, 80, 66), (-0.35 * forearm_len, 70, 52), (0.0, 60, 40)]
        parts.append(loft([_ellipse_section(x, a, b) for x, a, b in secs]))
    # palm: wrist to knuckles, widening and flattening
    palm_secs = [(0.0, 60, 40), (25, 76, 34), (60, 84, 30), (88, 82, 26)]
    palm = loft([_ellipse_section(x, a, b, z=0.0) for x, a, b in palm_secs])
    parts.append(palm)
    # fingers: index to little, from the knuckle line
    fingers = [(+0.33, 76, 9.2, 4), (+0.11, 84, 9.4, 1), (-0.11, 80, 9.0, -2), (-0.33, 64, 8.0, -6)]
    for yf, L, r, spread in fingers:
        base = (86, s * yf * 80 * 0.95, -2.0)
        parts.append(_finger(base, L, r, pose, s, spread_deg=s * spread))
    # thumb: from the side of the palm, angled forward and down
    tb = (22, s * 34, -6.0)
    thumb_curl = [20, 12, 10] if pose == "flat" else [35, 45, 40]
    parts.append(_finger(tb, 62, 10.5, pose, s, spread_deg=s * 38, curl=thumb_curl))
    shape = parts[0]
    for p in parts[1:]:
        try:
            shape = shape + p
        except Exception:
            shape = Compound(children=[shape, p])
    if not shape.is_valid:
        shape = Compound(children=parts)
    return shape


# ---------------------------------------------------------------------------------------------------------
# Full-body clay mannequin
# ---------------------------------------------------------------------------------------------------------

_X = Vector(1, 0, 0)
_UP = Vector(0, 0, 1)
_FWD = Vector(0, -1, 0)          # the figure faces -Y

_MQ_POSES = ("stand", "walk", "push", "ride", "sit", "reach")
_MQ_JOINTS = ("shoulder_flex_l", "shoulder_flex_r", "shoulder_abd_l", "shoulder_abd_r",
              "elbow_flex_l", "elbow_flex_r", "hip_flex_l", "hip_flex_r", "knee_flex_l", "knee_flex_r",
              "ankle_flex_l", "ankle_flex_r", "torso_lean", "head_tilt")
_MQ_SIT_SEAT = 450.0             # seat height for pose="sit", mm (not scaled with height)


def _mq_dims(height):
    """Segment lengths for an average adult, scaled from a 1750 mm reference."""
    k = height / 1750.0
    d = dict(hip_dx=88, thigh=410, shank=432, ankle_h=68, heel=20, ball=140, toe=210,
             sh_u=490, sh_dx=171, sh_back=10, upper=318, fore=255, hand=185, neck_u=560,
             seat_back=22, seat_down=100, saddle_bb=707, seat_tube=73.0, crank=170, pedal_sole=15)
    d = {n: (v * k if n != "seat_tube" else v) for n, v in d.items()}
    d["k"] = k
    return d


def _mq_dir(a_deg, up, fwd):
    """Unit vector at a_deg from 'down' toward 'forward' (0 hangs down, 90 points forward, 180 points up)."""
    a = radians(a_deg)
    return -cos(a) * up + sin(a) * fwd


def _mq_frame(tilt_deg, up=_UP, fwd=_FWD):
    """Up and forward axes pitched forward by tilt_deg (the top moves toward 'forward')."""
    t = radians(tilt_deg)
    return cos(t) * up + sin(t) * fwd, cos(t) * fwd - sin(t) * up


def _mq_rotate(v, axis, ang_deg):
    """Rodrigues rotation of v about a unit axis."""
    a = radians(ang_deg)
    return v * cos(a) + axis.cross(v) * sin(a) + axis * (axis.dot(v) * (1 - cos(a)))


def _mq_ik(root, target, l1, l2, up, fwd, bend_forward):
    """Planar two-link inverse kinematics in the (fwd, up) plane.

    Returns (first segment angle, joint flexion) in degrees, using the _mq_dir convention. bend_forward=True
    puts the middle joint in front of the root-target line (a knee); False puts it behind (an elbow).
    """
    t = target - root
    df, du = t.dot(fwd), t.dot(up)
    dist = min(max((df * df + du * du) ** 0.5, abs(l1 - l2) + 1e-6), l1 + l2 - 1e-6)
    phi = degrees(atan2(df, -du))
    alpha = degrees(acos((l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist)))
    beta = degrees(acos((l1 * l1 + l2 * l2 - dist * dist) / (2 * l1 * l2)))
    return (phi + alpha if bend_forward else phi - alpha), 180.0 - beta


def _mq_foot_axes(pitch_deg):
    p = radians(pitch_deg)
    return cos(p) * _FWD + sin(p) * _UP, -sin(p) * _FWD + cos(p) * _UP


def _mq_ankle_for(contact, pitch_deg, d, at="ball"):
    """Ankle centre that puts the sole's ball (or heel) on 'contact' with the foot pitched toes-up by pitch_deg."""
    fd, fu = _mq_foot_axes(pitch_deg)
    back = d["ball"] if at == "ball" else -d["heel"]
    return contact - back * fd + d["ankle_h"] * fu


def _mq_foot_low(sole, fd, fu, k):
    """Lowest z of the foot geometry (heel sphere, sole line, toe ellipsoid) for a given sole frame."""
    hc = sole - 20 * k * fd + 32 * k * fu
    tc = sole + 150 * k * fd + 22 * k * fu
    return min(hc.Z - 32 * k, (sole + 140 * k * fd).Z,
               tc.Z - ((60 * k * fd.Z) ** 2 + (22 * k * fu.Z) ** 2) ** 0.5)


def _mq_pelvis_frame(lean):
    return _mq_frame(0.5 * lean)


def _mq_seat_offset(lean, d):
    """Vector from the pelvis (hip-joint midpoint) to the seat contact under the sitting bones."""
    up_p, f_p = _mq_pelvis_frame(lean)
    return -d["seat_back"] * f_p - d["seat_down"] * up_p


def _mq_ride_bike(d, lean):
    """Implied bicycle for pose='ride': seat contact, bottom bracket and the two pedal axles (world)."""
    seat = Vector(0, _mq_seat_offset(lean, d).Y, 955.5 * d["k"])
    a = radians(d["seat_tube"])
    bb = seat + Vector(0, -d["saddle_bb"] * cos(a), -d["saddle_bb"] * sin(a))
    return seat, bb, bb + Vector(0, 0, d["crank"]), bb - Vector(0, 0, d["crank"])


def _mq_preset(height, pose):
    """Joint angles for a preset pose. IK is used so feet, seat and hands land on their intended targets."""
    d = _mq_dims(height)
    k = d["k"]
    j = dict(shoulder_flex_l=4.0, shoulder_flex_r=4.0, shoulder_abd_l=9.0, shoulder_abd_r=9.0,
             elbow_flex_l=10.0, elbow_flex_r=10.0, hip_flex_l=0.0, hip_flex_r=0.0, knee_flex_l=0.0,
             knee_flex_r=0.0, ankle_flex_l=0.0, ankle_flex_r=0.0, torso_lean=0.0, head_tilt=0.0)
    meta = dict(hand="relaxed", anchor="floor")

    def leg(side, pelvis, contact, pitch, at="ball"):
        s = 1 if side == "l" else -1
        hip = pelvis + s * d["hip_dx"] * _X
        ankle = _mq_ankle_for(contact, pitch, d, at)
        fd, fu = _mq_foot_axes(pitch)
        lift = contact.Z - _mq_foot_low(ankle - d["ankle_h"] * fu, fd, fu, k)
        ankle = Vector(hip.X, ankle.Y, ankle.Z + (lift if contact.Z <= 1e-6 else 0.0))
        a, kf = _mq_ik(hip, ankle, d["thigh"], d["shank"], _UP, _FWD, True)
        j[f"hip_flex_{side}"], j[f"knee_flex_{side}"] = a, kf
        j[f"ankle_flex_{side}"] = pitch - (a - kf)

    def arm(side, pelvis, grip):
        s = 1 if side == "l" else -1
        up_t, f_t = _mq_frame(j["torso_lean"])
        sh = pelvis + d["sh_u"] * up_t - d["sh_back"] * f_t + s * d["sh_dx"] * _X
        along, below = _mq_grip_offset(d, meta["hand"])
        dn = (grip - sh).normalized()
        for _ in range(4):          # the grip sits below the forearm line, so refine the target twice or more
            _, t = _mq_hand_axes(dn, meta["hand"])
            a, ef = _mq_ik(sh, grip + below * t, d["upper"], d["fore"] + along, up_t, f_t, False)
            dn = _mq_dir(a + ef, up_t, f_t)
        j[f"shoulder_flex_{side}"], j[f"elbow_flex_{side}"], j[f"shoulder_abd_{side}"] = a, ef, 0.0

    if pose == "stand":
        pass
    elif pose == "walk":
        j.update(torso_lean=3.0, shoulder_flex_r=20.0, elbow_flex_r=24.0, shoulder_flex_l=-16.0,
                 elbow_flex_l=10.0, shoulder_abd_l=7.0, shoulder_abd_r=7.0)
        pelvis = Vector(0, 0, 868 * k)
        leg("l", pelvis, Vector(0, -270 * k, 0), 16.0, at="heel")
        leg("r", pelvis, Vector(0, 290 * k, 0), -32.0)
    elif pose == "push":
        j.update(torso_lean=13.0, head_tilt=-6.0)
        meta["hand"] = "grip"
        pelvis = Vector(0, 0, 900 * k)
        leg("l", pelvis, Vector(0, -70 * k, 0), 0.0)
        leg("r", pelvis, Vector(0, 250 * k, 0), -26.0)
        for sd in "lr":
            s = 1 if sd == "l" else -1
            arm(sd, pelvis, Vector(s * d["sh_dx"], -520 * k, 1000 * k))
    elif pose == "ride":
        j.update(torso_lean=38.0, head_tilt=-30.0)
        meta.update(hand="grip", anchor="seat")
        seat, bb, p_top, p_bot = _mq_ride_bike(d, j["torso_lean"])
        pelvis = seat - _mq_seat_offset(j["torso_lean"], d)
        n_top, n_bot = p_top + Vector(0, 0, d["pedal_sole"]), p_bot + Vector(0, 0, d["pedal_sole"])
        leg("l", pelvis, n_top, 2.0)
        leg("r", pelvis, n_bot, -22.0)
        for sd in "lr":
            s = 1 if sd == "l" else -1
            arm(sd, pelvis, Vector(s * d["sh_dx"], pelvis.Y - 620 * k, seat.Z + 60 * k))
        meta.update(seat=seat, bb=bb, pedals=[p_top, p_bot])
    elif pose == "sit":
        j.update(torso_lean=-4.0)
        meta.update(hand="flat", anchor="seat")
        seat = Vector(0, 0, _MQ_SIT_SEAT)
        pelvis = seat - _mq_seat_offset(j["torso_lean"], d)
        pelvis = Vector(0, 0, pelvis.Z)
        leg("l", pelvis, Vector(0, -(d["thigh"] + 40 * k), 0), 0.0)
        leg("r", pelvis, Vector(0, -(d["thigh"] + 40 * k), 0), 0.0)
        for sd in "lr":
            s = 1 if sd == "l" else -1
            hip = pelvis + s * d["hip_dx"] * _X
            knee = hip + d["thigh"] * _mq_dir(j[f"hip_flex_{sd}"], _UP, _FWD)
            on_thigh = hip + 0.72 * (knee - hip) + Vector(0, 0, 95 * k)
            arm(sd, pelvis, Vector(s * d["sh_dx"], on_thigh.Y, on_thigh.Z))
    elif pose == "reach":
        j.update(torso_lean=-3.0, head_tilt=-22.0, shoulder_flex_r=168.0, elbow_flex_r=10.0,
                 shoulder_abd_r=8.0, shoulder_flex_l=6.0, elbow_flex_l=14.0)
    else:
        raise ValueError(f"pose must be one of {_MQ_POSES}, got {pose!r}")
    return j, meta


def _mq_skeleton(height, pose, joints):
    """Forward kinematics: joint centres, axes and landmarks for a pose, with the feet or seat anchored."""
    bad = set(joints) - set(_MQ_JOINTS)
    if bad:
        raise TypeError(f"unknown mannequin joint(s) {sorted(bad)}; use {_MQ_JOINTS}")
    d = _mq_dims(height)
    j, meta = _mq_preset(height, pose)
    j.update({n: float(v) for n, v in joints.items()})
    lean = j["torso_lean"]
    up_t, f_t = _mq_frame(lean)
    up_p, f_p = _mq_pelvis_frame(lean)
    pelvis = Vector(0, 0, 0)
    sk = dict(d=d, j=j, hand=meta["hand"], up_t=up_t, f_t=f_t, up_p=up_p, f_p=f_p)
    legs, arms = {}, {}
    for sd, s in (("l", 1), ("r", -1)):
        hip = pelvis + s * d["hip_dx"] * _X
        a1, kf = j[f"hip_flex_{sd}"], j[f"knee_flex_{sd}"]
        knee = hip + d["thigh"] * _mq_dir(a1, _UP, _FWD)
        ankle = knee + d["shank"] * _mq_dir(a1 - kf, _UP, _FWD)
        fd, fu = _mq_foot_axes(a1 - kf + j[f"ankle_flex_{sd}"])
        sole = ankle - d["ankle_h"] * fu
        legs[sd] = dict(hip=hip, knee=knee, ankle=ankle, fd=fd, fu=fu, sole=sole,
                        heel=sole - d["heel"] * fd + 32 * d["k"] * (fu - _UP), ball=sole + d["ball"] * fd,
                        toe=sole + d["toe"] * fd)
        legs[sd]["low"] = _mq_foot_low(sole, fd, fu, d["k"])
    for sd, s in (("l", 1), ("r", -1)):
        sh = pelvis + d["sh_u"] * up_t - d["sh_back"] * f_t + s * d["sh_dx"] * _X
        sf, ef, abd = j[f"shoulder_flex_{sd}"], j[f"elbow_flex_{sd}"], j[f"shoulder_abd_{sd}"]
        ud = _mq_rotate(_mq_dir(sf, up_t, f_t), f_t, s * abd)
        fd = _mq_rotate(_mq_dir(sf + ef, up_t, f_t), f_t, s * abd)
        elbow = sh + d["upper"] * ud
        wrist = elbow + d["fore"] * fd
        arms[sd] = dict(shoulder=sh, elbow=elbow, wrist=wrist, dir=fd, side=s,
                        tip=wrist + d["hand"] * fd)
        along, below = _mq_grip_offset(d, meta["hand"])
        arms[sd]["grip"] = wrist + along * fd - below * _mq_hand_axes(fd, meta["hand"])[1]
    h = j["head_tilt"]
    up_h, f_h = _mq_frame(h, up_t, f_t)
    neck = pelvis + d["neck_u"] * up_t
    head_c = neck + 166 * d["k"] * up_h + 12 * d["k"] * f_h
    sk.update(legs=legs, arms=arms, neck=neck, head_c=head_c, up_h=up_h, f_h=f_h)
    # anchor: lowest sole point on z=0 (standing poses) or seat contact on its target (ride, sit)
    if meta["anchor"] == "floor":
        low = min(lg["low"] for lg in legs.values())
        shift = Vector(0, 0, -low)
    else:
        seat_target = meta["seat"] if "seat" in meta else Vector(0, 0, _MQ_SIT_SEAT)
        shift = Vector(0, 0, seat_target.Z - _mq_seat_offset(lean, d).Z)
    sk["shift"] = shift
    sk["meta"] = meta
    return sk


def mannequin_landmarks(height=1750.0, pose="stand", **joints):
    """Key points (mm, world) of mannequin(height, pose, **joints) for placing products around the figure.

    Keys: "pelvis" (hip-joint midpoint), "seat" (contact under the sitting bones), "hands" ([left, right]
    grip centres, mid-palm), "wrists", "elbows", "shoulders", "knees", "feet" ([left, right] sole points
    under the balls of the feet, which sit on the pedals in "ride"), "heels", "head_top", "joints" (the
    resolved angle dict) and, for "ride", "bb" (bottom bracket) and "pedals" ([top, bottom] axles).
    """
    sk = _mq_skeleton(height, pose, joints)
    sh = sk["shift"]
    L, A = sk["legs"], sk["arms"]
    tup = lambda v: (round(v.X + sh.X, 1), round(v.Y + sh.Y, 1), round(v.Z + sh.Z, 1))
    lm = dict(pelvis=tup(Vector(0, 0, 0)),
              seat=tup(_mq_seat_offset(sk["j"]["torso_lean"], sk["d"])),
              hands=[tup(A[s]["grip"]) for s in "lr"],
              wrists=[tup(A[s]["wrist"]) for s in "lr"],
              elbows=[tup(A[s]["elbow"]) for s in "lr"],
              shoulders=[tup(A[s]["shoulder"]) for s in "lr"],
              knees=[tup(L[s]["knee"]) for s in "lr"],
              feet=[tup(L[s]["ball"]) for s in "lr"],
              heels=[tup(L[s]["heel"]) for s in "lr"],
              head_top=tup(sk["head_c"] + 114 * sk["d"]["k"] * sk["up_h"]),
              joints={n: round(v, 1) for n, v in sk["j"].items()})
    if "bb" in sk["meta"]:
        lm["bb"] = tup(sk["meta"]["bb"] - sh)
        lm["pedals"] = [tup(p - sh) for p in sk["meta"]["pedals"]]
    return lm


def _ellipsoid(center, x_dir, z_dir, rx, ry, rz):
    """Ellipsoid with semi-axes rx along x_dir, rz along z_dir and ry along their cross product."""
    e = scale(Sphere(1.0), by=(rx, ry, rz))
    return Location(Plane(origin=center, x_dir=x_dir, z_dir=z_dir)) * e


def _limb(p0, p1, stations):
    """Smooth limb from p0 to p1: circles lofted at (fraction, radius) stations, sphere caps at both ends."""
    p0, p1 = Vector(*p0), Vector(*p1)
    ax = (p1 - p0).normalized()
    L = (p1 - p0).length
    if len(stations) == 2 and stations[0][0] == 0 and stations[-1][0] == 1:
        parts = [Solid.make_cone(stations[0][1], stations[1][1], L, Plane(origin=p0, z_dir=ax))]
    else:
        secs = [Plane(origin=p0 + ax * (t * L), z_dir=ax) * Circle(r) for t, r in stations]
        parts = [loft(secs)]
    parts.append(Pos(*p0) * Sphere(1.03 * stations[0][1]))     # a touch larger than the loft ends so
    parts.append(Pos(*p1) * Sphere(1.03 * stations[-1][1]))    # the booleans never meet edge on edge
    return parts


def _mq_hand_axes(dn, mode):
    """Width axis w and back-of-hand axis t (the palm faces -t) for a hand pointing along dn."""
    if mode == "relaxed":
        w = dn.cross(_X)                                # palm toward the body side, thumb forward
    else:
        w = _X - dn * _X.dot(dn)                        # palm down
    if w.length < 1e-6:
        w = _FWD - dn * _FWD.dot(dn)
    w = w.normalized()
    return w, dn.cross(w)


def _mq_grip_offset(d, mode):
    """Grip point relative to the wrist: distance along the hand and distance toward the palm."""
    if mode == "grip":
        return 0.52 * d["hand"], 30 * d["k"]           # centre of a 32 mm bar held in the curled fingers
    return 0.45 * d["hand"], 0.0


def _mq_hand(arm, d, mode):
    """Mitten hand: flat (relaxed or palm down) or curled around a 32 mm bar (mode='grip')."""
    k = d["k"]
    w0, dn = arm["wrist"], arm["dir"]
    w, t = _mq_hand_axes(dn, mode)
    thumb = w if mode == "relaxed" else -arm["side"] * w * (1 if w.dot(_X) > 0 else -1)
    L = d["hand"]
    if mode != "grip":
        secs = [(0.0, 56, 32), (0.30, 82, 32), (0.62, 80, 25)]
        shape = [loft([Plane(origin=w0 + dn * (s * L), x_dir=w, z_dir=dn) * Ellipse(a * k / 2, b * k / 2)
                       for s, a, b in secs])]
        shape.append(_ellipsoid(w0 + dn * (0.62 * L), w, dn, 42 * k, 13.5 * k, 0.36 * L))
        tb0 = w0 + dn * (0.16 * L) + thumb * (30 * k) + t * (6 * k)
        tb1 = w0 + dn * (0.52 * L) + thumb * (44 * k) + t * (10 * k)
        shape += _limb(tuple(tb0), tuple(tb1), [(0, 13 * k), (1, 10.5 * k)])
        return shape
    # palm from the wrist to the knuckles, then the fingers wrapped around the bar centre C
    along, below = _mq_grip_offset(d, mode)
    C = w0 + dn * along - t * below
    R = below                                           # finger mid-surface radius about the bar
    secs = [(0.0, 56, 32), (0.28, 82, 32), (0.50, 82, 28)]
    shape = [loft([Plane(origin=w0 + dn * (s * L), x_dir=w, z_dir=dn) * Ellipse(a * k / 2, b * k / 2)
                   for s, a, b in secs])]
    shape.append(_ellipsoid(w0 + dn * (0.50 * L), w, dn, 43 * k, 15 * k, 20 * k))
    fsecs = []
    for th, wd, th_k in ((10, 84, 30), (55, 83, 28), (100, 80, 26), (140, 76, 24)):
        a = radians(th)
        pos = C + (cos(a) * t + sin(a) * dn) * R
        tan = -sin(a) * t + cos(a) * dn
        fsecs.append(Plane(origin=pos, x_dir=w, z_dir=tan) * Ellipse(wd * k / 2, th_k * k / 2))
    shape.append(loft(fsecs))
    a = radians(140)
    shape.append(_ellipsoid(C + (cos(a) * t + sin(a) * dn) * R, w, -sin(a) * t + cos(a) * dn,
                            40 * k, 13 * k, 14 * k))
    tb0 = w0 + dn * (0.18 * L) + thumb * (30 * k) - t * (4 * k)
    tb1 = C + thumb * (34 * k) - t * (26 * k) + dn * (8 * k)
    shape += _limb(tuple(tb0), tuple(tb1), [(0, 14 * k), (1, 12 * k)])
    return shape


def _mq_foot(leg, d):
    k = d["k"]
    S, fd, fu = leg["sole"], leg["fd"], leg["fu"]
    # (station along the sole, width, height, centre height); the last one sits inside the toe cap
    secs = [(-20, 60, 58, 33), (15, 80, 82, 41), (80, 94, 58, 29), (145, 96, 40, 22)]
    loft_secs = [Plane(origin=S + fd * (s * k) + fu * (c * k), x_dir=_X, z_dir=fd) * Ellipse(wd * k / 2, h * k / 2)
                 for s, wd, h, c in secs]
    parts = [loft(loft_secs)]
    parts.append(Pos(*(S - fd * (20 * k) + fu * (32 * k))) * Sphere(32 * k))
    parts.append(_ellipsoid(S + fd * (150 * k) + fu * (22 * k), _X, fd, 51 * k, 22 * k, 60 * k))
    return parts


def mannequin(height=1750.0, pose="stand", **joints):
    """Smooth clay full-body mannequin for scale context in renders of larger systems.

    Returns one build123d shape in mm: a single fused Solid, checked for validity, completeness and a
    clean mesh at tessellate(0.05, 0.1), or a Compound of the overlapping pieces if no fuse passes.
    Building takes about 5 to 10 s; the fine mesh is cached, so later tessellation is quick.
    The figure faces -Y, the pelvis (hip-joint midpoint) sits over x = 0, y = 0, and the feet stand on
    z = 0 in the floor poses. In "ride" and "sit" the seat contact is anchored instead (saddle at
    0.546 * height, chair seat at 450 mm), so the feet land on the implied pedals or the floor.
    Presets scale with height except the 450 mm chair; overriding a leg angle in "ride" or "sit"
    moves the feet, not the seat.

    Poses (presets; every angle can be overridden by keyword, in degrees):
      "stand"  arms relaxed at the sides.
      "walk"   mid-stride, left heel striking ahead, right foot pushing off behind, arms swinging.
      "push"   leaning 13 degrees forward, hands gripping a 32 mm bar 520 mm ahead of the pelvis at
               1.0 m (both scaled with height), as on a handlebar or a hip bar; left foot forward.
      "ride"   seated cyclist leaning 38 degrees: seat 956 mm (at 1.75 m), bottom bracket 207 mm ahead of and 676 mm
               below the seat contact (73-degree seat tube), cranks 170 mm and vertical (left pedal at
               the top, right at the bottom), hands 620 mm ahead of the pelvis at seat height + 60 mm.
      "sit"    upright on a 450 mm seat, feet flat on the floor, hands resting on the thighs.
      "reach"  right arm raised overhead, head tilted back, for installing things on a mast or roof edge.

    Joint keywords (degrees): shoulder_flex_l/r (0 hangs down, 90 forward, 180 overhead, measured from
    the torso axis), shoulder_abd_l/r (outward), elbow_flex_l/r, hip_flex_l/r (thigh angle from world
    vertical, positive forward), knee_flex_l/r, ankle_flex_l/r (toes up), torso_lean (forward from world
    vertical, pivoting at the pelvis) and head_tilt (forward nod relative to the torso). "_l" is the
    figure's left, on the +X side.

    Use mannequin_landmarks(height, pose, **joints) for the exact hands, feet, seat, pelvis and, for
    "ride", bottom bracket and pedal points; the geometry is built from the same kinematics. This is a
    render prop with average adult proportions, not anatomy.
    """
    sk = _mq_skeleton(height, pose, joints)
    d, k = sk["d"], sk["d"]["k"]
    up_t, f_t, up_p, f_p = sk["up_t"], sk["f_t"], sk["up_p"], sk["f_p"]
    O = Vector(0, 0, 0)
    core = []
    # pelvis and torso
    core.append(_ellipsoid(O - f_p * (22 * k) + up_p * (30 * k), _X, up_p, 168 * k, 118 * k, 130 * k))
    torso = [(40, 296, 184, -14), (150, 272, 182, 0), (260, 292, 202, 10), (360, 306, 214, 12),
             (445, 328, 190, 0), (500, 270, 130, -8)]
    core.append(loft([Plane(origin=O + up_t * (h * k) + f_t * (o * k), x_dir=_X, z_dir=up_t) *
                      Ellipse(w * k / 2, dp * k / 2) for h, w, dp, o in torso]))
    # ellipsoid poles are kept away from joins (the scaled-sphere pole is a weak spot for booleans)
    core.append(_ellipsoid(O + up_t * (462 * k) - f_t * (8 * k), _X, f_t, 205 * k, 78 * k, 90 * k))
    # neck and head
    n0, n1 = O + up_t * (470 * k), sk["head_c"] - sk["up_h"] * (30 * k)     # both ends buried, so no caps
    core.append(Solid.make_cone(52 * k, 46 * k, (n1 - n0).length, Plane(origin=n0, z_dir=(n1 - n0).normalized())))
    core.append(_ellipsoid(sk["head_c"], sk["up_h"], _X, 114 * k, 98 * k, 78 * k))
    groups = [core]
    # arms
    for sd in "lr":
        a = sk["arms"][sd]
        g = _limb(tuple(a["shoulder"]), tuple(a["elbow"]), [(0, 48 * k), (0.4, 45 * k), (1, 36 * k)])
        g += _limb(tuple(a["elbow"]), tuple(a["wrist"]), [(0, 37 * k), (0.28, 40 * k), (1, 26 * k)])
        g += _mq_hand(a, d, sk["hand"])
        groups.append(g)
    # legs
    for sd in "lr":
        lg = sk["legs"][sd]
        g = _limb(tuple(lg["hip"]), tuple(lg["knee"]), [(0, 84 * k), (0.45, 72 * k), (1, 53 * k)])
        g += _limb(tuple(lg["knee"]), tuple(lg["ankle"]), [(0, 52 * k), (0.3, 56 * k), (1, 35 * k)])
        g += _mq_foot(lg, d)
        groups.append(g)
    shift = Pos(*sk["shift"])
    groups = [[shift * p for p in g] for g in groups]
    # one batch fuse of everything first; if that fails its checks, fuse each body group and then the
    # groups, and any step that still fails keeps its pieces as they are
    probes = [p.center() for g in groups for p in (g[0], g[len(g) // 2], g[-1])]
    body = _mq_fuse([p for g in groups for p in g], probes, tries=((None, False),))
    if isinstance(body, Solid):
        return body
    fused = [_mq_fuse(g, [p.center() for p in g]) for g in groups]
    return _mq_fuse(fused, probes)


def _mq_fuse(pieces, probes, tries=((None, False), (0.05, False), (None, True))):
    """Fuse pieces into one solid and verify it; return Compound(children=pieces) if that fails.

    Each try is (fuzzy tolerance, one piece at a time); the default runs a batch fuse, a fuzzy batch
    fuse and a stepwise fuse, in that order.
    """
    ref = Compound(children=pieces).bounding_box()
    for tol, stepwise in tries:
        try:
            if stepwise:
                body = pieces[0]
                for p in pieces[1:]:
                    body = body.fuse(p)
            else:
                body = pieces[0].fuse(*pieces[1:], tol=tol)
            body = body.clean()
            bb = body.bounding_box()
            if (body.is_valid and len(body.solids()) == 1 and (bb.min - ref.min).length < 5.0
                    and (bb.max - ref.max).length < 5.0
                    and all(body.is_inside(q, tolerance=0.1) for q in probes) and _mq_meshes(body)):
                return body
        except Exception:
            pass
    return Compound(children=pieces)


def _mq_meshes(shape, tol=0.05):
    """True when every face of a fused body tessellates (a failed boolean can leave unmeshable faces).

    The fine mesh stays cached on the faces, so coarse preview renders reuse it and stay smooth.
    """
    try:
        for f in shape.faces():
            f.tessellate(tol, 0.1)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    import time
    for pose in ("flat", "grip"):
        t = time.time()
        h = forearm_hand(pose=pose)
        bb = h.bounding_box()
        print(pose, h.is_valid, round(bb.size.X), round(bb.size.Y), round(bb.size.Z), f"{time.time()-t:.1f}s")
