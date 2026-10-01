"""HelioLite general arrangement sheet HLT-DWG-001, Rev P2 (TRL 3).

Run from the repo root:  python cad/src/sheets.py
Writes cad/drawings/HLT-DWG-001.svg, .pdf and .png from the parametric model in
cad/src/model.py with .kit/drawing.py. The orthographic views show the unit stowed
face-down with the yoke at azimuth 0 (above-ground parts); the isometric view shows the
tracking pose. Dimensions are drawn from PARAMS and the model bounding box, so they
follow any parameter change. The concept sheet is HLT-DWG-010.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
from drawing import Sheet, project_views, _viewbox, _t, M, TB_Y, INK, MUTED  # noqa: E402
from model import PARAMS as P, derived, parts  # noqa: E402
from build123d import Compound  # noqa: E402

DATE = "2026-09-25"


def ortho_cells(sheet, views, names=("front", "top", "right")):
    """Repeat Sheet.add_ortho's layout arithmetic to find where each view lands (x, y, w, h)."""
    ax, ay, aw, ah = M + 10, M + 16, 245, TB_Y - M - 20
    gap, lab = 14, 12
    dims = {n: _viewbox(Path(views[n]).read_text())[2:] for n in names}
    fw, fh = dims["front"]; tw, th = dims["top"]; rw, rh = dims["right"]
    k = sheet.scale
    ax += (aw - (k * (max(fw, tw) + rw) + gap)) / 2
    ay += (ah - (k * (th + max(fh, rh)) + gap + 2 * lab)) / 2
    colw = k * max(fw, tw)
    front_y = ay + k * th + lab + gap
    row_h = k * max(fh, rh)
    return {"top": (ax, ay, colw, k * th), "front": (ax, front_y, colw, row_h),
            "right": (ax + colw + gap, front_y, k * rw, row_h)}


def dim_h(x1, x2, y, text):
    a = 1.4
    return [f'<line x1="{x1:.2f}" y1="{y:.2f}" x2="{x2:.2f}" y2="{y:.2f}" stroke="{INK}" stroke-width="0.18"/>',
            f'<path d="M{x1:.2f} {y:.2f} l{a} -0.5 l0 1 Z" fill="{INK}"/>',
            f'<path d="M{x2:.2f} {y:.2f} l{-a} -0.5 l0 1 Z" fill="{INK}"/>',
            _t((x1 + x2) / 2, y - 1.0, text, 2.3, 400, INK, "middle", mono=True)]


def dim_v(x, y1, y2, text):
    a = 1.4
    cx, cy = x - 1.0, (y1 + y2) / 2
    return [f'<line x1="{x:.2f}" y1="{y1:.2f}" x2="{x:.2f}" y2="{y2:.2f}" stroke="{INK}" stroke-width="0.18"/>',
            f'<path d="M{x:.2f} {y1:.2f} l-0.5 {a} l1 0 Z" fill="{INK}"/>',
            f'<path d="M{x:.2f} {y2:.2f} l-0.5 {-a} l1 0 Z" fill="{INK}"/>',
            f'<g transform="rotate(-90 {cx:.2f} {cy:.2f})">{_t(cx, cy, text, 2.3, 400, INK, "middle", mono=True)}</g>']


def ext(x1, y1, x2, y2):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{MUTED}" stroke-width="0.13"/>'


def main():
    D = derived(P)
    work = ROOT / "cad" / "drawings" / "_views"
    stow = Compound(children=[p[2] for p in parts(el=-90.0, az=0.0, below_ground=False)])
    track = Compound(children=[p[2] for p in parts(below_ground=False)])
    views = project_views(stow, work / "stowed")
    views["iso"] = project_views(track, work / "tracking")["iso"]
    bb = stow.bounding_box()
    s = Sheet(project="HelioLite", title="General arrangement", dwg_no="HLT-DWG-001", rev="P3",
              author="Amish Chadha", date=DATE, scale=None, theme="technical",
              material="Glass mirror on ACP; printed ASA yoke; NMRV030-class drives; 60.3 mm galv. pipe. PRELIMINARY, NOT FOR FABRICATION",
              revisions=[("P1", "Preliminary GA for TRL 3 (from cad/src/model.py)", DATE, "AC"),
                         ("P2", "Stow stop and latch, preload springs added (DDR-002)", DATE, "AC"),
                         ("P3", "Layout and labels tidied", DATE, "AC")])
    s.add_ortho(views)
    k = s.scale
    c = ortho_cells(s, views)
    L = []
    # front view (from -Y): X to the right, Z up. Ground at the bottom of the view.
    x, y, w, h = c["front"]
    zg = y + h                                    # ground line on the sheet (bb.min.Z = 0)
    xc = x + (0 - bb.min.X) * k                   # mast axis on the sheet
    L += [ext(x - 22, zg, x, zg)]
    za = zg - P["axis_z"] * k
    L += [ext(x - 12, za, xc, za)]
    L += dim_v(x - 10, za, zg, f"{P['axis_z']:,.0f} axis")
    zt = zg - D["mast_top"] * k
    L += [ext(x - 18, zt, xc, zt)]
    L += dim_v(x - 16, zt, zg, f"{D['mast_top']:,.0f} mast top")
    # mirror width and arm spacing above the front view
    hm = P["mirror"] / 2
    L += [ext(xc - hm * k, y - 6, xc - hm * k, za), ext(xc + hm * k, y - 6, xc + hm * k, za)]
    L += dim_h(xc - hm * k, xc + hm * k, y - 5, f"{P['mirror']:.0f} mirror")
    xa1, xa2 = xc - P["arm_x"] * k, xc + P["arm_x"] * k
    L += [ext(xa1, y - 1.5, xa1, za), ext(xa2, y - 1.5, xa2, za)]
    L += dim_h(xa1, xa2, y - 1.2, f"{2 * P['arm_x']:.0f} arms c/c")
    # right view (from +X): Y to the right; controller height and anemometer reach
    x, y, w, h = c["right"]
    yc = x + (0 - bb.min.Y) * k                   # mast axis (the view from +X puts +Y on the right)
    zg = y + h
    zc = zg - P["ctrl_z"] * k
    xb = yc + (-P["mast_od"] / 2 - 5 - P["ctrl"][1]) * k   # outer face of the controller box
    L += [ext(x - 6, zc, xb, zc), ext(x - 6, zg, x, zg)]
    L += dim_v(x - 4, zc, zg, f"{P['ctrl_z']:,.0f} box base")
    zan = zg - P["anemo_z"] * k
    xa = yc + P["anemo_reach"] * k
    L += [ext(xa, zan - 2, xa, zan - 10), ext(yc, zan - 2, yc, zan - 10)]
    L += dim_h(min(xa, yc), max(xa, yc), zan - 9, f"{P['anemo_reach']:.0f}")
    s._layers += L
    s.add_svg(views["iso"], 276, 32, 140, 90, label="Isometric view, tracking pose", sublabel="Not to scale")
    gx, gy, gz = P["gb"]
    s.add_notes("Main dimensions and interfaces (mm)", [
        f"Mirror {P['mirror']:.0f} x {P['mirror']:.0f} x {P['glass_t']:.0f} glass on {P['back_t']:.0f} ACP; sweep radius {D['sweep_r']:.0f}",
        f"Elevation axis at Z {P['axis_z']:,.0f}; {P['tube']:.0f} sq. torque tube, {P['trunnion_d']:.0f} trunnions",
        f"Yoke arms {P['arm_t']:.0f} x {P['arm_w']:.0f} at X +/-{P['arm_x']:.0f}; gaps {D['arm_gap']:.0f} (arm), {D['cross_gap']:.0f} (crossbar)",
        f"Drives: NEMA17 on NMRV030-class 50:1, envelope {gx:.0f} x {gy:.0f} x {gz:.0f}, 14 bore",
        f"Mast {P['mast_od']} x {P['mast_wall']} galv. pipe, {P['mast_len']:,.0f} long; cap {P['cap']:.0f} sq. x {P['cap_t']:.0f}",
        f"Anchor flange {P['flange_d']:.0f} dia.; ground screw {P['screw_d']:.0f} x {P['screw_len']:.0f} (not shown)",
        f"Anemometer at Z {P['anemo_z']:,.0f}, reach {P['anemo_reach']:.0f}; controller box at Z {P['ctrl_z']:,.0f}",
        f"Stow lug {P['lug_t']:.0f} thk at X {P['lug_x']:.0f}; stop pad and latch pawl at R {P['stop_r']:.0f} on -X arm",
        f"Preload spring cans {P['spring_d']:.0f} dia.: -X trunnion and mast top",
        "Top mass about 12.95 kg; stow face-down in 23 s (HLT-CAL-001)",
        "Orthographic views stowed at azimuth 0; front from -Y, right from +X",
    ], x=276, y=138, width=144)
    out = s.save(ROOT / "cad" / "drawings" / "HLT-DWG-001")
    shutil.rmtree(work, ignore_errors=True)
    print(f"wrote {out} and .pdf, .png at scale 1:{1 / k:g}")


if __name__ == "__main__":
    main()
