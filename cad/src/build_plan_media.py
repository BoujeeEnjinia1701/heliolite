"""HelioLite prototype build plan pictures (HLT-BLD-001, STANDARDS section 18).

Run from the repo root:  python cad/src/build_plan_media.py [overview|sheets|joints|steps|wiring ...]
With no argument it draws everything. Pass a name and a number to draw one picture, for example
"sheets 106" or "steps 7" (one picture per process keeps memory low). Every picture is drawn from
cad/src/model.py (build_components), so the pictures and the model never disagree:
    docs/05-build-plan/overview.png        every component pulled apart, numbered in build order
    cad/drawings/HLT-DWG-101 to 115        making sketches for the made components
    docs/05-build-plan/joint-NN.png        close-ups of the joints that need explaining
    docs/05-build-plan/step-NN.png         one picture per assembly step
    docs/05-build-plan/wiring.png          block-level wiring with wire sizes (matplotlib)
Uses .kit/build_views.py. BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
import build_views as bv  # noqa: E402
from build_views import Part  # noqa: E402
from model import PARAMS as P, build_components, derived  # noqa: E402
import build123d as b  # noqa: E402

OUT = ROOT / "docs" / "05-build-plan"
DWG = ROOT / "cad" / "drawings"
DATE = "2026-10-01"
D = derived(P)
AX = P["axis_z"]

_cache = {}


def comps(el=-90.0, az=0.0, compact=False):
    """Components in a pose. compact=True draws the mast 1.1 m shorter (pictures of the whole unit only)."""
    key = (el, az, compact)
    if key not in _cache:
        PP = dict(P)
        if compact:
            PP.update(mast_len=P["mast_len"] - 1100, axis_z=P["axis_z"] - 1100, ctrl_z=190.0, anemo_z=450.0)
        _cache[key] = build_components(el=el, az=az, P=PP, below_ground=False)
    return _cache[key]


def fuse(shapes):
    out = None
    for s in shapes:
        out = s if out is None else out + s
    return out


def S(C, *ks):
    return fuse([C[k][1] for k in ks])


def part(name, shape, color, explode=(0, 0, 0), alpha=1.0):
    return Part(name, shape, color, None, tuple(explode), alpha)


def P_(C, key, name=None, explode=(0, 0, 0), keys=None, color=None):
    keys = keys or [key]
    return part(name or C[key][0], S(C, *keys), color or C[key][2], explode)


def half(shape, axis, sign):
    """Keep the part of a shape on one side of the plane through the origin normal to axis."""
    big = 5000
    lo = [-big] * 3; hi = [big] * 3
    i = "xyz".index(axis)
    if sign > 0:
        lo[i] = 0
    else:
        hi[i] = 0
    box = b.Pos((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2) * b.Box(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
    return shape & box


def win(shape, x0, x1, y0, y1, z0, z1):
    return shape & (b.Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * b.Box(x1 - x0, y1 - y0, z1 - z0))


def local(shape):
    """Move a shape so its bounding box centre sits at the origin (for the three views)."""
    c = shape.bounding_box().center()
    return b.Pos(-c.X, -c.Y, -c.Z) * shape


# ----------------------------------------------------------------- overview
def overview():
    C = comps(-90.0, 0.0, compact=True)
    hb = (560, 460, 470)                                  # the head (yoke and drive), moved off to the right
    mb = (-560, -460, 860)                                # the mirror assembly, moved off to the left
    H = lambda dx, dy, dz: (hb[0] + dx, hb[1] + dy, hb[2] + dz)  # noqa: E731
    M = lambda dx, dy, dz: (mb[0] + dx, mb[1] + dy, mb[2] + dz)  # noqa: E731
    items = [
        ("Rib tubes (2)", ["ribs"], M(0, 0, 330)),
        ("Backing panel", ["panel"], M(0, 0, 0)),
        ("Torque tube", ["tube"], M(0, 0, 170)),
        ("Trunnion end blocks (2)", ["blocks"], M(0, 0, 240)),
        ("Stow lug", ["lug"], M(-160, -160, 170)),
        ("Glass mirror", ["glass"], M(-330, -330, -190)),
        ("Crossbar", ["crossbar"], H(0, 0, 0)),
        ("Arms (2)", ["arm_r", "arm_l"], H(0, 0, 130)),
        ("Gusset plates (4) and bolts", ["gussets", "gusset_bolts"], H(0, -260, -70)),
        ("Bearing plugs and bronze bushes", ["plugs", "bushes"], H(0, 0, 300)),
        ("Latch bracket, pad, pawl, solenoid", ["bracket", "pad", "pawl", "solenoid"], H(-260, -330, 60)),
        ("Elevation Hall switch", ["hall_el"], H(-120, 200, 380)),
        ("Turntable disc and hub", ["disc", "hub"], (0, 0, 560)),
        ("Trunnion stubs (2)", ["stubs"], H(0, -380, 420)),
        ("Elevation drive", ["el_gb", "el_motor"], H(240, 0, 130)),
        ("Elevation spring can", ["spring_el"], H(-330, 0, 130)),
        ("Ground anchor", ["anchor"], (0, 0, -140)),
        ("Mast pipe (drawn shortened)", ["mast"], (0, 0, 0)),
        ("Controller box and plate", ["ctrl", "ctrl_plate", "ctrl_ubolts"], (0, -200, 0)),
        ("Anemometer and clamp", ["anemo", "anemo_clamp"], (0, 150, 0)),
        ("Floor flange", ["floor_flange"], (0, 0, 90)),
        ("Mast cap plate", ["cap", "hall_az"], (0, 0, 190)),
        ("Azimuth drive", ["az_gb", "az_motor"], (0, 0, 300)),
        ("Shaft, spring can, thrust washer", ["shaft", "spring_az", "washer"], (0, 0, 420)),
        ("Cabling", ["cable"], (-260, -520, -120)),
    ]
    parts = [part(n, S(C, *ks), C[ks[0]][2], e) for n, ks, e in items]
    return bv.overview(parts, OUT / "overview.png", "HelioLite prototype: every component, pulled apart",
                       subtitle="Numbered in build order. Mirror face-down (stowed); mast drawn shortened. Seen from the front right and above",
                       elev=18, azim=-52, size=(12, 9), dpi=150, key=True)


# ----------------------------------------------------------------- making sketches
def sheets(only=None):
    Cs = comps(-90.0, 0.0)          # stowed at azimuth 0: every part square to the axes
    base = dict(project="HelioLite", date=DATE)
    out = []

    def sheet(no, title, shape, color, neighbours, material, notes, view_shape=None, inset_view=(24, -58), name=None):
        if only and str(no) not in only:
            return
        out.append(bv.component_sheet(Part(name or title, shape, color), neighbours, dwg_no=f"HLT-DWG-{no}",
                                      title=f"HelioLite {title}: making sketch", material=material, notes=notes,
                                      view_shape=local(view_shape if view_shape is not None else shape), inset_view=inset_view, **base))

    mir = [P_(Cs, "panel"), P_(Cs, "tube"), P_(Cs, "ribs")]
    rib_r = half(Cs["ribs"][1], "x", +1)
    sheet(101, "rib tube (make 2)", rib_r, Cs["ribs"][2], [P_(Cs, "panel"), P_(Cs, "tube"), P_(Cs, "glass")],
          "Aluminum rectangular tube 25 x 40 x 1.5 mm, 6063",
          ["Cut two 560 mm lengths of 25 x 40 x 1.5 mm tube; square and deburr.",
           "Tunnel for the torque tube, at mid-length (280 mm from each end):",
           "  a notch 25.5 mm long and 25.25 mm deep, cut from one 25 mm face",
           "  (the face that goes on the panel) down through both 40 mm sides.",
           "  Saw the two sides, chain drill and file the floor flat.",
           "Push a 25 mm tube offcut through the tunnel: it must slide, not rock.",
           "Fit plastic end caps in both ends.",
           "Fit: the notched face is bonded to the back of the backing panel with",
           "  structural silicone, the rib centre line 227.5 mm from the panel",
           "  centre line and its ends 20 mm in from the panel edges.",
           "The torque tube runs through both tunnels and touches the panel.",
           "Check: both tunnels line up when the ribs lie side by side."],
          inset_view=(40, -30))
    sheet(102, "torque tube", Cs["tube"][1], Cs["tube"][2], [P_(Cs, "panel"), P_(Cs, "ribs"), P_(Cs, "blocks")],
          "Aluminum square tube 25 x 25 x 2 mm, 6063",
          ["Cut to 635 mm (1 mm shorter than the 636 mm between the bush",
           "  flanges, so the mirror drops into the yoke). Square both ends.",
           "Through both side walls, 6.5 mm holes 35 and 50 mm from each end",
           "  (end block bolts), on the centre line of the side.",
           "Through both side walls, a 5 mm hole 20 mm from each end (cross pin):",
           "  drill these with the end blocks and stubs in place (step 11).",
           "On the left end only: a shallow 4 mm spot 11 mm from the end on",
           "  the face away from the panel, for the stow lug's set screw.",
           "Deburr inside and out so the end blocks slide in.",
           "Fit: runs through both rib tunnels, its top face bonded to the panel",
           "  with structural silicone; ends 318 mm each side of the centre.",
           "Check: straight within 0.5 mm over its length on a flat bench."],
          inset_view=(40, -30))
    blk = half(S(Cs, "blocks"), "x", +1) + half(S(Cs, "stubs"), "x", +1)
    sheet(103, "trunnion end block and stub", blk, Cs["blocks"][2], [P_(Cs, "panel"), P_(Cs, "ribs")],
          "Aluminum square bar 22 mm (block); 14 mm keyed steel shaft (stub)",
          ["End blocks (make 2): cut 60 mm of 22 mm square bar; file to 21 mm",
           "  square, a sliding fit in the tube. Drill and ream 14 mm along",
           "  the centre, right through. Cross holes 6.5 mm at 10 and 25 mm",
           "  from the inner end, through two opposite faces.",
           "Stubs: cut 14 mm keyed shaft (5 mm key) to 148 mm for the drive",
           "  (right) side and 108 mm for the spring (left) side.",
           "Each stub goes 38 mm into its block. With the stub in the block in",
           "  the tube, drill 5 mm through tube, block and stub 20 mm from the",
           "  tube end and drive in a 5 x 24 mm roll pin (step 11).",
           "Left stub only: saw a 3 mm slot 10 mm deep across its outer end",
           "  for the inner end of the spiral spring.",
           "Fit: block bolted in the tube end with two M6 bolts; stub through",
           "  the bronze bush, into the gearbox bore (right) or spring can (left).",
           "Check: the stub turns the tube with no play once pinned."],
          view_shape=blk, inset_view=(30, -40))
    lw = lambda k: part(Cs[k][0], win(Cs[k][1], -380, -200, -120, 120, AX - 120, AX + 120), Cs[k][2])  # noqa: E731
    sheet(104, "stow lug", Cs["lug"][1], Cs["lug"][2], [lw("tube"), lw("panel"), lw("bracket"), lw("pad"), lw("arm_l")],
          "Steel plate 8 mm, S275 or similar, painted",
          ["Cut from 8 mm steel plate: a collar 37.5 mm square with a",
           "  tongue 25 mm wide running out to 75 mm from the collar's centre.",
           "Cut the 25 mm square hole in the collar: drill 20 mm, file square",
           "  to a sliding fit on the torque tube.",
           "Drill and tap M5 through the collar side opposite the tongue",
           "  for a set screw.",
           "On one face of the tongue, 30 mm from the centre: a 6 mm hole",
           "  3 mm deep for the homing magnet (glue it in).",
           "Round the tongue corners 2 mm and break all edges.",
           "Fit: slides onto the left end of the torque tube, magnet toward",
           "  the arm, mid-plane 11 mm from the tube end; set screw into the",
           "  spot on the tube, medium threadlocker.",
           "When stowed, the tongue rests on the stop pad and the latch pawl",
           "  closes over it.",
           "Check: the tongue is square to the tube and does not rock."],
          inset_view=(35, -60))
    yoke = [P_(Cs, "crossbar"), P_(Cs, "arm_r"), P_(Cs, "arm_l"), P_(Cs, "disc")]
    sheet(105, "crossbar", Cs["crossbar"][1], Cs["crossbar"][2], [P_(Cs, "arm_r"), P_(Cs, "arm_l"), P_(Cs, "gussets"), P_(Cs, "disc"), P_(Cs, "hub")],
          "Aluminum rectangular tube 60 x 40 x 2 mm, 6063",
          ["Cut 720 mm of 60 x 40 x 2 mm tube; square and deburr the ends.",
           "Lay it with a 60 mm face up. All holes 6.5 mm.",
           "Gusset bolt holes, horizontal through both 40 mm sides, at",
           "  mid-height: 20 mm and 75 mm in from each end.",
           "Turntable bolt holes, vertical through top and bottom: four holes,",
           "  45 mm each side of the centre and 15 mm each side of the",
           "  centre line.",
           "Slide a 6 mm bore aluminum crush sleeve into each bolt hole pair",
           "  (cut to the inside height) so bolts do not crush the tube.",
           "Fit: sits flat on the turntable disc, held by four M6 bolts into",
           "  the disc's tapped holes; the arms stand on its ends.",
           "Check: holes in line; the tube lies flat on the disc."],
          inset_view=(30, -50))
    arm_notes_r = ["Cut 397 mm of 60 x 40 x 2 mm tube; square and deburr. The 60 mm",
                   "  faces are the sides; the 40 mm faces are the front and back.",
                   "Bush hole: 18 mm through both sides, centred, 40 mm below the",
                   "  top end. Drill 6 mm pilot, open with a step drill, ream.",
                   "Gearbox holes (right arm): four 6.5 mm through both sides on a",
                   "  44 mm square round the bush hole (22 mm each way). Check the",
                   "  gearbox's output-face holes before drilling.",
                   "Gusset bolt holes: 6.5 mm through the front and back faces,",
                   "  centred, 15 mm and 45 mm above the bottom end.",
                   "Fit: stands on the crossbar end; two gussets clamp it; the",
                   "  bearing plug fills its top 75 mm; the gearbox bolts to the",
                   "  outer side.",
                   "Check: the bush hole is square to the side (a 14 mm rod through",
                   "  it stands at 90 degrees to the arm)."]
    sheet(106, "right arm (drive side)", Cs["arm_r"][1], Cs["arm_r"][2], [P_(Cs, "crossbar"), P_(Cs, "arm_l"), P_(Cs, "el_gb"), P_(Cs, "gussets"), P_(Cs, "tube")],
          "Aluminum rectangular tube 60 x 40 x 2 mm, 6063", arm_notes_r, inset_view=(25, -40))
    sheet(107, "left arm (latch side)", Cs["arm_l"][1], Cs["arm_l"][2], [P_(Cs, "crossbar"), P_(Cs, "arm_r"), P_(Cs, "bracket"), P_(Cs, "spring_el"), P_(Cs, "gussets"), P_(Cs, "tube")],
          "Aluminum rectangular tube 60 x 40 x 2 mm, 6063",
          ["Cut and drill as the right arm (HLT-DWG-106) for length, bush hole",
           "  and gusset bolt holes, but without the four gearbox holes.",
           "Spring can holes: three 4.5 mm on a 40 mm circle round the bush",
           "  hole, outer side only.",
           "Latch bracket holes: two 6.5 mm through both sides, 8 mm from",
           "  the front face, 18 mm and 55 mm below the top end.",
           "Hall switch holes: two 3.2 mm in the inner side, 10 mm below the",
           "  top end, 5 mm each side of the centre line.",
           "Fit: as the right arm; the latch bracket bolts to the inner side",
           "  at the front, the spring can to the outer side.",
           "Check: lay both arms side by side: bush holes and gusset holes",
           "  match."], inset_view=(25, -130))
    g1 = half(half(Cs["gussets"][1], "x", +1), "y", -1)
    sheet(108, "gusset plate (make 4)", g1, Cs["gussets"][2], [P_(Cs, "crossbar"), P_(Cs, "arm_r"), P_(Cs, "gusset_bolts")],
          "Aluminum sheet 3 mm, 5052 or 6061",
          ["Mark on 3 mm sheet: bottom edge 90 mm, outer edge 100 mm tall,",
           "  top edge 40 mm, then a straight edge down to a point 40 mm up",
           "  the inner end. Cut with a jigsaw or snips; file the edges.",
           "Four 6.5 mm holes, measured from the outer edge and up from the",
           "  bottom edge: 20 and 20; 75 and 20; 20 and 55; 20 and 85.",
           "All four plates are the same: drill them as a stack.",
           "Fit: one plate on the front and one on the back of each arm",
           "  foot, bottom edge flush with the crossbar's bottom face and",
           "  outer edge flush with its end. Four M6 bolts go through plate,",
           "  tube and plate, with crush sleeves and nyloc nuts.",
           "Check: the arm stands square to the crossbar when bolted."],
          inset_view=(20, -60))
    plug = half(Cs["plugs"][1], "x", +1)
    sheet(109, "bearing plug (make 2, printed)", plug, Cs["plugs"][2], [part("Bush", half(Cs["bushes"][1], "x", +1), Cs["bushes"][2]), P_(Cs, "el_gb"), part("Arm (cut away above the crossbar)", win(Cs["arm_r"][1], 300, 400, -50, 50, AX - 400, AX - 120), Cs["arm_r"][2])],
          "ASA, printed; 6 walls, 60 % infill",
          ["Print a block 36 x 56 x 75 mm with an 18 mm hole across its",
           "  36 mm thickness, centred, 40 mm below the top face.",
           "Print it standing on its 36 x 56 end so the hole axis is",
           "  horizontal; six walls so screws bite in solid plastic.",
           "Fit: pressed into the top of each arm, top faces flush; the",
           "  bronze bush passes through arm side, plug and arm side.",
           "Drill the bolt holes (gearbox, latch, spring can) through the",
           "  plug from the arm's holes once it is in place.",
           "The plug spreads the bolt loads and keeps the thin tube walls",
           "  from crushing.",
           "Check: a firm press fit; the hole lines up with the arm's 18 mm",
           "  holes so the bush slides through."],
          inset_view=(30, -40))
    lb = S(Cs, "bracket", "pawl")
    sheet(110, "latch bracket, stop block and pawl", lb, Cs["bracket"][2],
          [lw("arm_l"), lw("lug"), lw("solenoid"), lw("tube"), lw("spring_el")],
          "Steel plate 4 mm and bar 15 x 30 mm, 12 x 8 mm; painted",
          ["Bracket: from 4 mm steel cut a leg 68 x 62 mm with a 15 mm flange",
           "  on its front edge; bend the flange 90 degrees.",
           "In the leg: a 21 mm radius bite at the back edge, centred 31 mm up,",
           "  clear of the turning tube end; a 14 x 9 mm slot for the pawl,",
           "  21 mm from the front edge, 40 mm up. Two 6.6 mm countersunk",
           "  holes 7 mm from the back edge, 12.5 and 49.5 mm up.",
           "Stop block: 15 x 30 x 11.5 mm steel, screwed to the leg's foot",
           "  with two M5 screws; bond the 3 mm polyurethane pad on top.",
           "Pawl: 26 mm of 12 x 8 mm steel bar; chamfer the top of its tip",
           "  45 degrees by 4 mm; tap M3 in the tail for the solenoid plunger.",
           "Fit: leg flat on the left arm's inner side, two M6 countersunk",
           "  screws; the pawl slides in the slot, its tip over the lug.",
           "Check: the pawl slides freely 12 mm; pad top 0.5 mm under the",
           "  stowed lug."],
          inset_view=(30, -45))
    capn = Cs["cap"][1]
    mt = lambda k: part(Cs[k][0], win(Cs[k][1], -150, 150, -150, 150, D["mast_top"] - 200, D["mast_top"] + 120), Cs[k][2])  # noqa: E731
    sheet(111, "mast cap plate", capn, Cs["cap"][2], [mt("floor_flange"), mt("az_gb"), mt("az_motor"), mt("mast"), mt("hall_az")],
          "Steel plate 8 mm, S275, zinc sprayed or painted",
          ["Cut 160 x 160 mm from 8 mm plate; break the edges.",
           "Centre hole 16 mm for the azimuth shaft.",
           "Flange screws: four holes drilled 6.8 mm and tapped M8 on a",
           "  105 mm circle at 45 degrees (37.1 mm each way from the centre).",
           "  Check against your floor flange's holes before drilling.",
           "Gearbox screws: four 6.6 mm holes on a 44 mm square (22 mm each",
           "  way), countersunk from the underside so the heads sit flush.",
           "Hall post screw: one M4 tapped hole 54 mm from the centre, on",
           "  the line through the centre square to the motor (top view).",
           "Fit: the gearbox sits on the top face (screws first, from below);",
           "  the plate then sits on the floor flange, held by four M8 screws",
           "  up through the flange into the tapped holes.",
           "Check: the shaft passes the centre hole without touching."],
          inset_view=(25, -50))
    sheet(112, "turntable disc", Cs["disc"][1], Cs["disc"][2], [P_(Cs, "hub"), P_(Cs, "crossbar"), P_(Cs, "az_gb"), P_(Cs, "washer")],
          "Aluminum plate 10 mm, 6082",
          ["Cut a 120 mm disc from 10 mm plate (or buy a blank); face both",
           "  sides flat.",
           "Centre hole 30 mm, a close fit on the hub's boss.",
           "Hub screws: four 5.5 mm holes on a 40 mm circle at 45 degrees,",
           "  countersunk from the top so the crossbar sits flat over them.",
           "Crossbar bolts: four holes drilled 5 mm and tapped M6, 45 mm",
           "  each side of the centre and 15 mm each side of the centre line.",
           "Homing magnet: a 6 mm hole 3 mm deep in the underside, 54 mm",
           "  from the centre on the crossbar's centre line (glue it in).",
           "Fit: the hub screws to its underside; the crossbar bolts to its",
           "  top; the whole turns on the azimuth shaft.",
           "Check: the disc runs flat within 0.3 mm at its rim when turned",
           "  on the shaft."],
          inset_view=(-20, -50))
    cw = lambda k: part(Cs[k][0], win(Cs[k][1], -150, 150, -150, 150, P["ctrl_z"] - 120, P["ctrl_z"] + 300), Cs[k][2])  # noqa: E731
    sheet(113, "controller mounting plate", Cs["ctrl_plate"][1], Cs["ctrl_plate"][2], [cw("ctrl"), cw("mast"), cw("ctrl_ubolts")],
          "Aluminum sheet 3 mm, 5052",
          ["Cut 140 x 220 mm from 3 mm sheet; round the corners 5 mm.",
           "U-bolt holes: two pairs of 8.5 mm holes, 66 mm apart, centred",
           "  across the plate, 10 mm in from the top and bottom edges.",
           "Box holes: hold the controller box centred on the plate and",
           "  drill through its mounting lugs (four 4.5 mm holes).",
           "Fit: the plate's back touches the mast; two 2 in U-bolts go",
           "  round the mast and through the plate with nyloc nuts; the box",
           "  screws to the plate's front with M4 screws.",
           "The box sits 3 mm off the mast, its base 1.1 m above the ground.",
           "Check: the plate does not turn on the mast with the nuts tight."],
          inset_view=(20, 130))
    sheet(114, "spring can (make 2, printed)", Cs["spring_el"][1], Cs["spring_el"][2], [lw("arm_l"), lw("tube"), lw("lug")],
          "ASA, printed; 100 % infill",
          ["Elevation can: a 50 mm diameter cup 30 mm long with a 14 mm",
           "  centre hole through its closed end, the open end toward the arm.",
           "  Three 4.5 mm holes on a 40 mm circle, lengthwise, for M4 screws",
           "  into the left arm and plug. A 3 mm pin hole near the rim inside",
           "  holds the spring's outer end.",
           "Azimuth can: the same cup at 52.5 mm diameter, a push fit in the",
           "  mast pipe, with an M5 insert in its side for a screw through",
           "  the pipe wall, 37 mm below the pipe's top end.",
           "Fit the bought flat spiral spring: inner end in the stub's slot",
           "  (or the shaft's), outer end on the pin. Wind it 1 turn before",
           "  fixing so it holds about 3 N m toward stow.",
           "Check: the spring holds the shaft one way with no slack."],
          inset_view=(25, -130))
    sheet(115, "azimuth Hall switch post (printed)", Cs["hall_az"][1], Cs["hall_az"][2], [P_(Cs, "cap"), P_(Cs, "az_gb")],
          "ASA, printed; 100 % infill",
          ["Print a post 16 x 16 mm and 64 mm tall with a 4.5 mm hole down",
           "  its centre, counterbored 8 mm from the top for the screw head.",
           "Fit: one M4 screw down through the post into the tapped hole in",
           "  the cap plate, 54 mm from the shaft centre.",
           "Glue the Hall switch (12 x 12 x 5 mm) on top, sensing face up.",
           "Its face sits 4 mm under the turntable disc, under the magnet",
           "  when the yoke points at azimuth zero.",
           "Run its lead down the post with the motor lead.",
           "Check: turn the disc by hand: the switch changes state as the",
           "  magnet passes, and nothing rubs."],
          inset_view=(25, -150))
    return out


# ----------------------------------------------------------------- joints
def joints(only=None):
    out = []
    C0 = comps(0.0, 0.0)
    Cs = comps(-90.0, 0.0)

    def J(n, items, title, subtitle, **kw):
        if only and str(n) not in only:
            return
        out.append(bv.joint(items, OUT / f"joint-{n:02d}.png", title, subtitle=subtitle, size=(8, 6), **kw))

    z = AX
    # 01 rib tunnel and torque tube, cut at the rib's centre
    bx = (P["rib_x"], 262, -40, 40, z - 45, z + 45)
    J(1, [part("Glass mirror", win(C0["glass"][1], *bx), C0["glass"][2]),
          part("Backing panel", win(C0["panel"][1], *bx), C0["panel"][2]),
          part("Rib tube, cut through its tunnel", win(C0["ribs"][1], *bx), "#94A3B8"),
          part("Torque tube in the tunnel", win(C0["tube"][1], *bx), C0["tube"][2])],
      "Joint 1: torque tube through a rib tunnel (cut at the rib's centre)",
      "Seen from the left. The square tube sits in the square tunnel and touches the panel; silicone fills the gaps",
      elev=18, azim=200)
    # 02 left arm head, cut open on the axis
    bx = (-400, -270, 0, 60, z - 70, z + 70)
    J(2, [part("Torque tube", win(C0["tube"][1], *bx), C0["tube"][2]),
          part("End block", win(C0["blocks"][1], *bx), C0["blocks"][2]),
          part("Spring stub and cross pin", win(S(C0, "stubs", "pins"), *bx), C0["stubs"][2]),
          part("Bronze bush (flange inside)", win(C0["bushes"][1], *bx), C0["bushes"][2]),
          part("Printed bearing plug", win(C0["plugs"][1], *bx), C0["plugs"][2]),
          part("Left arm", win(C0["arm_l"][1], *bx), C0["arm_l"][2]),
          part("Spring can", win(C0["spring_el"][1], *bx), C0["spring_el"][2]),
          part("Stow lug", win(C0["lug"][1], *bx), C0["lug"][2]),
          part("Backing panel and glass", win(S(C0, "panel", "glass"), *bx), C0["panel"][2])],
      "Joint 2: left arm head, cut open along the elevation axis",
      "Seen from the front. Tube end on the bush flange; stub pinned in the end block, through the bush, into the spring can",
      elev=12, azim=-90)
    # 03 right arm head with the elevation gearbox
    bx = (300, 440, -70, 70, z - 150, z + 80)
    J(3, [part("Right arm", win(C0["arm_r"][1], *bx), C0["arm_r"][2]),
          part("Torque tube", win(C0["tube"][1], *bx), C0["tube"][2]),
          part("Drive stub (keyed)", win(C0["stubs"][1], *bx), C0["stubs"][2]),
          part("Elevation gearbox", win(C0["el_gb"][1], *bx), "#374151"),
          part("Motor and adapter", win(C0["el_motor"][1], *bx), "#6B7280"),
          part("Four M6 bolts from inside the arm", win(C0["el_bolts"][1], *bx), "#111827")],
      "Joint 3: elevation gearbox on the right arm",
      "Seen from the front left, inside the yoke. Four bolts through the arm into the gearbox's output face; the keyed stub drives its bore",
      elev=18, azim=-140)
    # 04 arm foot
    zb = D["yoke_base"]
    bx = (250, 380, -50, 50, zb - 10, zb + 130)
    J(4, [part("Crossbar", win(C0["crossbar"][1], *bx), C0["crossbar"][2]),
          part("Right arm", win(C0["arm_r"][1], *bx), "#94A3B8"),
          part("Gusset plates, front and back", win(C0["gussets"][1], *bx), C0["gussets"][2]),
          part("M6 bolts with crush sleeves", win(C0["gusset_bolts"][1], *bx), "#111827")],
      "Joint 4: arm foot on the crossbar end (right side)",
      "Seen from the front right. The arm stands on the crossbar; a gusset on each face, two bolts into each tube",
      elev=18, azim=-55)
    # 05 stow latch, stowed
    bx = (-372, -296, -92, 4, z - 34, z + 44)
    J(5, [part("Left arm", win(Cs["arm_l"][1], *bx), "#CBD5E1"),
          part("Stow lug (stowed)", win(Cs["lug"][1], *bx), Cs["lug"][2]),
          part("Torque tube", win(Cs["tube"][1], *bx), Cs["tube"][2]),
          part("Latch bracket and stop block", win(Cs["bracket"][1], *bx), Cs["bracket"][2]),
          part("Stop pad", win(Cs["pad"][1], *bx), Cs["pad"][2]),
          part("Sliding pawl", win(Cs["pawl"][1], *bx), Cs["pawl"][2]),
          part("Release solenoid", win(Cs["solenoid"][1], *bx), "#57534E"),
          part("Elevation Hall switch", win(Cs["hall_el"][1], *bx), Cs["hall_el"][2])],
      "Joint 5: stow stop and latch, mirror stowed (left arm, inner side)",
      "Seen from the front right, mirror removed. The lug sits on the pad; the pawl closes over it; the solenoid pulls it back",
      elev=22, azim=-40)
    # 06 mast top, cut open
    zt = D["mast_top"]
    bx = (-95, 95, 0, 100, zt - 70, D["tt_top"] + 45)
    J(6, [part("Mast pipe", win(C0["mast"][1], *bx), C0["mast"][2]),
          part("Floor flange (threaded)", win(C0["floor_flange"][1], *bx), C0["floor_flange"][2]),
          part("M8 screws up into the cap", win(C0["flange_screws"][1], *bx), "#111827"),
          part("Cap plate", win(C0["cap"][1], *bx), C0["cap"][2]),
          part("Azimuth gearbox", win(C0["az_gb"][1], *bx), "#374151"),
          part("Output shaft (keyed)", win(C0["shaft"][1], *bx), C0["shaft"][2]),
          part("Azimuth spring can", win(C0["spring_az"][1], *bx), C0["spring_az"][2]),
          part("Thrust washer", win(C0["washer"][1], *bx), C0["washer"][2]),
          part("Keyed flange hub", win(C0["hub"][1], *bx), "#78716C"),
          part("Turntable disc", win(C0["disc"][1], *bx), C0["disc"][2]),
          part("Crossbar", win(C0["crossbar"][1], *bx), C0["crossbar"][2]),
          part("Hall switch on its post", win(C0["hall_az"][1], *bx), C0["hall_az"][2])],
      "Joint 6: mast top and turntable, cut open through the shaft",
      "Seen from the front. Flange on the pipe thread; cap on the flange; shaft through the gearbox into the spring can",
      elev=10, azim=-90)
    # 07 controller plate on the mast
    cz = P["ctrl_z"]
    bx = (-110, 110, -130, 45, cz - 45, cz + 70)
    J(7, [part("Mast pipe", win(C0["mast"][1], *bx), C0["mast"][2]),
          part("Mounting plate", win(C0["ctrl_plate"][1], *bx), C0["ctrl_plate"][2]),
          part("U-bolt round the mast, nuts in front", win(C0["ctrl_ubolts"][1], *bx), "#111827"),
          part("Controller box", win(C0["ctrl"][1], *bx), C0["ctrl"][2])],
      "Joint 7: controller box plate on the mast (lower U-bolt)",
      "Seen from behind the mast and above. The U-bolt goes round the pipe and through the plate; the box is on the far side",
      elev=28, azim=60)
    # 08 anemometer clamp
    za = P["anemo_z"]
    bx = (-70, 70, -40, 160, za - 60, za + 60)
    J(8, [part("Mast pipe", win(C0["mast"][1], *bx), C0["mast"][2]),
          part("Right-angle pipe clamp", win(C0["anemo_clamp"][1], *bx), C0["anemo_clamp"][2]),
          part("Anemometer arm, 20 mm tube", win(C0["anemo"][1], *bx), C0["anemo"][2])],
      "Joint 8: anemometer arm clamp on the mast",
      "Seen from the right. The clamp grips the pipe and the arm at right angles with its own bolts",
      elev=20, azim=-20)
    return out


# ----------------------------------------------------------------- assembly steps
def steps(only=None):
    out = []

    def st(n, done, new, title, sub, **kw):
        if only and str(n) not in only:
            return
        out.append(bv.step(done, new, OUT / f"step-{n:02d}.png", f"Step {n}: {title}", subtitle=sub, **kw))

    Cs = comps(-90.0, 0.0)
    C0 = comps(0.0, 0.0)
    Cu = comps(90.0, 0.0)
    g = lambda C, k, e=(0, 0, 0), name=None: P_(C, k, name=name, explode=e)  # noqa: E731
    # mirror assembly, on the bench (face-down, back up)
    st(1, [g(Cs, "panel", name="Backing panel, face down on a padded bench")],
       [part("Rib tube (right)", half(Cs["ribs"][1], "x", +1), Cs["ribs"][2], (0, 0, 120)),
        part("Rib tube (left)", half(Cs["ribs"][1], "x", -1), Cs["ribs"][2], (0, 0, 120))],
       "bond the ribs to the back of the panel",
       "Structural silicone on the notched faces; ribs 227.5 mm each side of the centre; tunnels in line; weight down, cure",
       elev=30, azim=-60, label_done=True)
    st(2, [g(Cs, "panel"), g(Cs, "ribs")], [g(Cs, "tube", (450, 0, 0))],
       "slide the torque tube through the tunnels",
       "Butter the tunnels and the tube's panel face with silicone; centre the tube, ends 318 mm each side", elev=30, azim=-60)
    st(3, [g(Cs, "panel"), g(Cs, "ribs"), g(Cs, "tube")],
       [part("End block (right)", half(Cs["blocks"][1], "x", +1), Cs["blocks"][2], (140, 0, 0)),
        part("End block (left)", half(Cs["blocks"][1], "x", -1), Cs["blocks"][2], (-140, 0, 0))],
       "end blocks into the tube ends",
       "Flush with the tube ends; two M6 bolts each through tube and block, nyloc nuts", elev=30, azim=-60)
    st(4, [g(Cs, "panel"), g(Cs, "ribs"), g(Cs, "tube"), g(Cs, "blocks")], [g(Cs, "lug", (-160, 0, 0))],
       "stow lug onto the left end of the tube",
       "Magnet toward the tube end; tongue pointing away from the ribs' centre as shown; M5 set screw, threadlocker",
       elev=30, azim=-120)
    st(5, [g(Cu, "panel", name="Mirror backing, turned face up"), g(Cu, "ribs"), g(Cu, "tube"), g(Cu, "lug")],
       [g(Cu, "glass", (0, 0, 160))],
       "bond the glass mirror to the panel",
       "Two people, gloves; mirror adhesive in beads, glass on spacers, then cover the glass with card", elev=35, azim=-60,
       label_done=False)
    # yoke on the bench
    yoke = ["crossbar", "arm_r", "arm_l", "gussets", "gusset_bolts"]
    st(6, [g(C0, "crossbar")],
       [g(C0, "arm_r", (0, 0, 160)), g(C0, "arm_l", (0, 0, 160)),
        part("Front gusset (left)", half(half(S(C0, "gussets"), "y", -1), "x", -1), C0["gussets"][2], (0, -110, 0)),
        part("Front gusset (right)", half(half(S(C0, "gussets"), "y", -1), "x", +1), C0["gussets"][2], (0, -110, 0)),
        part("Back gusset (left)", half(half(S(C0, "gussets"), "y", +1), "x", -1), C0["gussets"][2], (0, 110, 0)),
        part("Back gusset (right)", half(half(S(C0, "gussets"), "y", +1), "x", +1), C0["gussets"][2], (0, 110, 0))],
       "arms and gussets onto the crossbar",
       "Arms square to the crossbar; four M6 bolts per foot through gussets, tubes and crush sleeves, nyloc nuts",
       elev=20, azim=-55)
    st(7, [g(C0, k) for k in yoke],
       [part("Bearing plug (left)", half(C0["plugs"][1], "x", -1), C0["plugs"][2], (0, 0, 140)),
        part("Bearing plug (right)", half(C0["plugs"][1], "x", +1), C0["plugs"][2], (0, 0, 140)),
        part("Bush (right), flange inside", half(C0["bushes"][1], "x", +1), C0["bushes"][2], (-90, 0, 0)),
        part("Bush (left), flange inside", half(C0["bushes"][1], "x", -1), C0["bushes"][2], (90, 0, 0))],
       "bearing plugs and bushes into the arms",
       "Press each plug into its arm top, flush; push each bush in from the inside so its flange sits on the arm",
       elev=22, azim=-55, label_done=False)
    st(8, [g(C0, k) for k in yoke + ["plugs", "bushes"]],
       [part("Latch bracket, stop block and pad", S(C0, "bracket", "pad"), C0["bracket"][2], (110, 0, 0)),
        g(C0, "pawl", (-70, 0, 0)), g(C0, "solenoid", (-110, 0, 0)), g(C0, "hall_el", (90, 0, 60))],
       "latch, solenoid and Hall switch onto the left arm",
       "Bracket on the arm's inner side, two M6 countersunk screws; pawl in its slot; solenoid strap on the leg's outside",
       elev=25, azim=-120, label_done=False)
    head0 = yoke + ["plugs", "bushes", "bracket", "pad", "pawl", "solenoid", "hall_el"]
    st(9, [g(C0, k) for k in head0],
       [g(C0, "disc", (0, 0, -120)), part("Keyed flange hub", C0["hub"][1], "#78716C", (0, 0, -230))],
       "turntable disc and hub under the crossbar",
       "Hub to the disc with four M5 countersunk screws; disc to the crossbar with four M6 bolts from above. Seen from below",
       elev=-25, azim=-55, label_done=False)
    head1 = head0 + ["disc", "hub"]
    mir = ["glass", "panel", "ribs", "tube", "blocks", "lug"]
    st(10, [g(C0, k) for k in head1],
       [part("Mirror assembly, glass covered", S(C0, *mir), C0["panel"][2], (0, 0, 420))],
       "lower the mirror assembly into the yoke",
       "Two people. Mirror upright, glass to the front, lug at the top of the left end; tube ends between the bush flanges",
       elev=18, azim=-55, label_done=False)
    head2 = head1 + mir
    st(11, [g(C0, k) for k in head2],
       [part("Drive stub (right)", half(C0["stubs"][1], "x", +1), C0["stubs"][2], (160, 0, 0)),
        part("Spring stub (left)", half(C0["stubs"][1], "x", -1), C0["stubs"][2], (-160, 0, 0)),
        part("Cross pins (in place)", C0["pins"][1], "#111827", (0, 0, 0))],
       "trunnion stubs through the bushes into the end blocks",
       "Each stub in 38 mm; drill 5 mm through tube, block and stub 20 mm from the tube end; drive in the roll pins",
       elev=20, azim=-55, label_done=False)
    head3 = head2 + ["stubs", "pins"]
    st(12, [g(C0, k) for k in head3],
       [part("Elevation gearbox and motor", S(C0, "el_gb", "el_motor"), "#374151", (200, 0, 0)),
        g(C0, "spring_el", (-150, 0, 0))],
       "elevation drive and spring can onto the stubs",
       "Key in the drive stub; gearbox onto it and flat on the arm, four M6 bolts. Spring can: wind 1 turn, three M4 screws",
       elev=20, azim=-55, label_done=False)
    # mast at the site (mast drawn shortened)
    Cc = comps(0.0, 0.0, compact=True)
    st(13, [g(Cc, "anchor", name="Ground anchor, screwed in plumb")],
       [part("Mast pipe (drawn shortened)", Cc["mast"][1], Cc["mast"][2], (0, 0, 320)), g(Cc, "set_screws", (120, 0, 0))],
       "mast pipe into the ground anchor",
       "Anchor screwed in plumb (services checked first); pipe down to the socket floor, plumb, two M10 set bolts",
       elev=20, azim=-55)
    st(14, [g(Cc, "anchor"), g(Cc, "mast")],
       [part("Controller box on its plate", S(Cc, "ctrl", "ctrl_plate"), Cc["ctrl"][2], (0, -160, 0)),
        part("U-bolts (2)", Cc["ctrl_ubolts"][1], "#111827", (0, 120, 0)),
        part("Anemometer and clamp", S(Cc, "anemo", "anemo_clamp"), Cc["anemo"][2], (0, 160, 0))],
       "controller box and anemometer onto the mast",
       "Box on its plate, plate on the mast with two U-bolts; anemometer clamp at 1.5 m, arm level, pointing away from the house",
       elev=20, azim=-55, label_done=False)
    zt = D["mast_top"]
    top = lambda C, k: win(C[k][1], -200, 200, -200, 200, zt - 260, zt + 400)  # noqa: E731
    st(15, [part("Mast pipe, top end", top(C0, "mast"), C0["mast"][2])],
       [g(C0, "floor_flange", (0, 0, 110))],
       "floor flange onto the mast top",
       "Thread sealant on the pipe thread; screw the flange on until the pipe end is flush with the flange face",
       elev=22, azim=-55)
    capset = ["cap", "az_gb", "az_motor", "shaft", "spring_az", "hall_az", "washer"]
    st(16, [part("Mast pipe, top end", top(C0, "mast"), C0["mast"][2]), g(C0, "floor_flange")],
       [part("Cap assembly", S(C0, *capset), "#0F766E", (0, 0, 220))],
       "cap and azimuth drive onto the floor flange",
       "Built on the bench first (gearbox screwed on from below). Lower the spring can into the pipe; four M8 screws up into the cap",
       elev=22, azim=-55, label_done=False)
    mastset = ["floor_flange", "flange_screws"] + capset
    head = head3 + ["el_gb", "el_motor", "spring_el"]
    st(17, [part("Mast pipe, top end", top(C0, "mast"), C0["mast"][2])] + [g(C0, k) for k in mastset],
       [part("Head: yoke, mirror, drive and latch", S(C0, *head), "#0F766E", (0, 0, 300))],
       "lift the head onto the azimuth shaft",
       "Two people on stable steps; glass covered. Hub's keyway on the shaft key; set screw tight. Then the anchor check",
       elev=18, azim=-55, label_done=False)
    st(18, [g(Cc, k) for k in ["anchor", "mast", "ctrl", "ctrl_plate", "anemo", "anemo_clamp", "floor_flange", "cap", "az_gb",
                               "az_motor", "washer", "hub", "disc"] + head],
       [g(Cc, "cable", (-140, -140, 0))],
       "cabling and the service loop",
       "Clip the cable up the mast, round the flange, and leave a loop to the crossbar for 270 degrees of azimuth travel",
       elev=18, azim=-55, label_done=False)
    return out


# ----------------------------------------------------------------- wiring
def wiring():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    fig = plt.figure(figsize=(12, 7.4), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 120); ax.set_ylim(0, 74); ax.set_axis_off()
    INK, MUT = "#111827", "#4B5563"
    ax.text(2, 72, "HelioLite prototype: block-level wiring", fontsize=13, fontweight="bold", color=INK, va="top")
    ax.text(2, 68.6, "Bought modules wired at block level; no circuit board is laid out. Stranded copper; ferrules on every screw terminal.",
            fontsize=8.5, color=MUT, va="top")
    ax.text(2, 1.5, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
    ax.text(118, 1.5, "github.com/BoujeeEnjinia1701/heliolite", fontsize=7, color="#0F766E", ha="right", family="monospace")
    ax.add_patch(FancyBboxPatch((22, 13), 62, 50, boxstyle="round,pad=0.4", fc="#F8FAFC", ec="#94A3B8", lw=1, ls="--"))
    ax.text(23.5, 14.0, "Inside the IP65 controller box on the mast", fontsize=8, color=MUT, va="bottom")
    ax.add_patch(FancyBboxPatch((2, 40), 14, 14, boxstyle="round,pad=0.4", fc="#FEF3C7", ec="#B45309", lw=1, ls="--"))
    ax.text(3, 53.2, "Indoors", fontsize=7.5, color="#B45309", va="top")

    def blk(x, y, w, h, title, sub, color):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3", fc="white", ec=color, lw=1.8))
        ax.text(x + w / 2, y + h - 1.4, title, ha="center", va="top", fontsize=8.8, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h - 4.2, sub, ha="center", va="top", fontsize=7, color=MUT, linespacing=1.3)

    def wire(pts, color, lw=2.0):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=1)

    def lab(x, y, text, color, ha="left"):
        ax.text(x, y, text, fontsize=7, color=color, ha=ha, va="center", zorder=3,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"))
    RED, BLU, GRY = "#B91C1C", "#1D4ED8", "#6B7280"
    blk(3.5, 42, 11, 9, "12 V adapter", "listed, 3 A,\nmains side indoors", "#B45309")
    blk(25, 44, 15, 13, "Input fuse and diode", "3 A fuse, then a\nSchottky diode to\nthe 12 V bus", "#16A34A")
    blk(25, 24, 15, 14, "Stow reserve", "5 x 2.7 V 25 F in\nseries, balancing,\ncharge resistor,\nvoltage sense", "#C2410C")
    blk(46, 50, 15, 9, "5 V converter", "12 V to 5 V buck", "#16A34A")
    blk(46, 33, 15, 13, "ESP32 and RTC", "ESP32 module,\nDS3231 clock with\ncoin cell", "#0F766E")
    blk(66, 47, 15, 12, "Stepper drivers", "two TMC2209,\nmotor supply\nfrom the 12 V bus", "#16A34A")
    blk(66, 26, 15, 13, "Solenoid driver", "logic MOSFET,\nflyback diode,\n12 V coil", "#16A34A")
    blk(46, 16, 15, 11, "Terminal strip", "sensor inputs,\npull-ups", "#7C3AED")
    blk(92, 52, 24, 10, "Elevation and azimuth motors", "NEMA17, 4-wire, shielded\n1.5 m leads", "#374151")
    blk(92, 37, 24, 10, "Release solenoid", "on the latch bracket,\nleft arm", "#991B1B")
    blk(92, 21, 24, 11, "Hall switches (2)", "azimuth post and left arm;\n3-wire, 5 V", "#C2410C")
    blk(92, 8, 24, 10, "Cup anemometer", "reed switch,\n2-wire pulse output", "#7C3AED")
    wire([(14.5, 46), (25, 46)], RED); lab(17.0, 42.6, "outdoor 2-core\n1.0 mm², 15 m", RED)
    wire([(32.5, 44), (32.5, 38)], RED); lab(33.2, 41, "12 V bus, 1.0 mm²", RED)
    wire([(40, 54), (46, 54)], RED); lab(43, 56.2, "0.5 mm²", RED, "center")
    wire([(53.5, 50), (53.5, 46)], RED); lab(54.2, 48, "5 V, 0.5 mm²", RED)
    wire([(40, 52), (43, 52), (43, 61), (73.5, 61), (73.5, 59)], RED); lab(58, 62.6, "motor supply 1.0 mm², via the bus", RED, "center")
    wire([(61, 42), (66, 42), (66, 47)], BLU, 1.3); lab(61.3, 44, "step, dir,\nUART", BLU)
    wire([(61, 36), (66, 36)], BLU, 1.3); lab(63.5, 38, "gate", BLU, "center")
    wire([(81, 55), (92, 55)], GRY, 2.0); lab(86.5, 57, "4-core shielded", GRY, "center")
    wire([(81, 32), (92, 40)], RED, 1.5); lab(85.0, 31.0, "0.5 mm²", RED)
    wire([(61, 22), (92, 26)], BLU, 1.3); lab(76, 21.2, "0.25 mm², 3-core", BLU, "center")
    wire([(61, 18), (92, 13)], BLU, 1.3); lab(76, 17.9, "0.25 mm², 2-core", BLU, "center")
    wire([(53.5, 27), (53.5, 33)], BLU, 1.3); lab(54.2, 30, "inputs", BLU)
    wire([(40, 31), (49, 31), (49, 33)], GRY, 1.2); lab(40.6, 29, "sense, 0.25 mm²", GRY)
    ax.text(23, 9.4, "Safety: the stow reserve holds about 360 J at 12 V. Fuse its output, bleed it before work, and label the box.",
            fontsize=7.6, color="#B45309", fontweight="bold")
    ax.text(23, 6.1, "Red: power. Blue: signal. Grey: motor leads and sensing. Only 12 V DC runs outdoors; the mains adapter stays indoors.",
            fontsize=7.2, color=MUT)
    out = OUT / "wiring.png"
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    fns = {"overview": overview, "sheets": sheets, "joints": joints, "steps": steps, "wiring": wiring}
    if not args:
        for w in fns:
            print(w, "->", fns[w]())
        sys.exit(0)
    what, nums = args[0], args[1:]
    r = fns[what](only=nums or None) if what in ("sheets", "joints", "steps") else fns[what]()
    print(what, "->", r)
