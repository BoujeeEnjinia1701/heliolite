#!/usr/bin/env python3
"""Concept media for the Open Hardware Portfolio (kit v1.2).

Turns a simple build123d assembly into the standard media set (CLAUDE.md section 5):

    media/hero.png              shaded isometric render for the website card
    media/cutaway.png           section view showing the inside
    media/exploded.png          exploded view with numbered callouts matching the BOM
    media/concept-blueprint.*   blueprint concept sheet: views, renders, key figures

Usage from a project's cad/src/concept_media.py:

    import sys; sys.path.insert(0, ".kit")
    from concept import Part, render_all
    parts = [Part("Steel drum", drum, "#8A9299", bom=1), Part("Sand", sand, "#D8B26E", bom=2), ...]
    render_all(parts, project="ThermaBrick", title="Concept overview", dwg_no="TBK-DWG-010",
               key_figures=["18 kWh(th) stored", "3 kW charge", "1 kW output for 14 h"])

At TRL 2 a massing model is enough: correct proportions and main parts.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path.cwd()
INK = "#111827"
ACCENT = "#0F766E"
SECTION = "#C2410C"   # cut faces in cutaways
LIGHT = np.array([0.45, -0.6, 0.75]); LIGHT = LIGHT / np.linalg.norm(LIGHT)


@dataclass
class Part:
    name: str
    shape: object            # build123d Shape
    color: str = "#9CA3AF"
    bom: int | None = None   # BOM line number for callouts
    explode: tuple = (0, 0, 0)  # exploded-view offset in mm
    alpha: float = 1.0


def _tris(shape, tol=1.0):
    verts, tris = shape.tessellate(tol)
    v = np.array([[p.X, p.Y, p.Z] for p in verts])
    return v, np.array(tris)


def _shade(hex_color, normals, alpha=1.0):
    base = np.array(matplotlib.colors.to_rgb(hex_color))
    lam = np.clip(normals @ LIGHT, 0, 1)
    k = 0.45 + 0.55 * lam
    rgb = np.clip(base[None, :] * k[:, None] + 0.08 * (1 - k[:, None]), 0, 1)
    return np.hstack([rgb, np.full((len(rgb), 1), alpha)])


def _zbuffer(tris, cols, elev, azim, W, H, pad=0.06):
    """Orthographic z-buffer rasterizer (numpy). tris: (N,3,3) world mm; cols: (N,4) RGBA. Returns RGB image, mask, projector."""
    e, a = np.radians(elev), np.radians(azim)
    # camera basis: view direction d points from camera toward scene
    d = -np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    right = np.cross(d, [0, 0, 1.0]); right /= np.linalg.norm(right)
    up = np.cross(right, d)
    P = np.stack([right, up, -d])            # rows: screen x, screen y, depth toward camera
    q = tris @ P.T                           # (N,3,3)
    lo, hi = q[..., :2].reshape(-1, 2).min(0), q[..., :2].reshape(-1, 2).max(0)
    span = (hi - lo).max() * (1 + 2 * pad)
    c = (lo + hi) / 2
    scale = min(W, H) / span
    def to_px(xy):
        return np.stack([(xy[..., 0] - c[0]) * scale + W / 2, H / 2 - (xy[..., 1] - c[1]) * scale], -1)
    px = to_px(q[..., :2]); z = q[..., 2]
    img = np.ones((H, W, 3)); zb = np.full((H, W), -np.inf)
    for i in range(len(px)):
        (x0, y0), (x1, y1), (x2, y2) = px[i]
        xmin, xmax = int(max(min(x0, x1, x2), 0)), int(min(max(x0, x1, x2) + 1, W))
        ymin, ymax = int(max(min(y0, y1, y2), 0)), int(min(max(y0, y1, y2) + 1, H))
        if xmin >= xmax or ymin >= ymax:
            continue
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-12:
            continue
        xs, ys = np.meshgrid(np.arange(xmin, xmax) + 0.5, np.arange(ymin, ymax) + 0.5)
        w0 = ((y1 - y2) * (xs - x2) + (x2 - x1) * (ys - y2)) / den
        w1 = ((y2 - y0) * (xs - x2) + (x0 - x2) * (ys - y2)) / den
        w2 = 1 - w0 - w1
        inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not inside.any():
            continue
        zz = w0 * z[i, 0] + w1 * z[i, 1] + w2 * z[i, 2]
        sub = zb[ymin:ymax, xmin:xmax]
        m = inside & (zz > sub)
        sub[m] = zz[m]
        img[ymin:ymax, xmin:xmax][m] = cols[i, :3]
    return img, np.isfinite(zb), (lambda pts: to_px((np.asarray(pts) @ P.T)[..., :2]))


def _render(parts, out, elev=24, azim=-58, offsets=False, labels=False, size=(8, 6), dpi=160, title=None, ss=2, note=None):
    W, H = int(size[0] * dpi), int(size[1] * dpi)
    tris_all, cols_all, items = [], [], []
    for p in parts:
        v, t = _tris(p.shape)
        if offsets:
            v = v + np.array(p.explode)
        tri = v[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n = n / np.clip(np.linalg.norm(n, axis=1, keepdims=True), 1e-9, None)
        # two-sided lighting so cut faces and inner walls shade sensibly
        e, a = np.radians(elev), np.radians(azim)
        cam = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
        n = n * np.sign((n @ cam) + 1e-12)[:, None]
        tris_all.append(tri); cols_all.append(_shade(p.color, n, p.alpha)); items.append((p, v))
    img, mask, proj = _zbuffer(np.vstack(tris_all), np.vstack(cols_all), elev, azim, W * ss, H * ss)
    if ss > 1:
        img = img.reshape(H, ss, W, ss, 3).mean((1, 3))
    fig = plt.figure(figsize=size, dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(img, interpolation="bilinear"); ax.set_axis_off()
    if labels:
        for p, v in items:
            if p.bom is None:
                continue
            ctr = v.mean(0); top = v[np.argmax(v[:, 2])]
            anchor = (ctr + top) / 2
            x, y = proj(anchor) / ss
            ax.text(x, y, f"{p.bom}", fontsize=8, fontweight="bold", color="white", ha="center", va="center",
                    bbox=dict(boxstyle="circle,pad=0.3", fc=ACCENT, ec="white", lw=0.8))
        handles = [plt.Line2D([], [], marker="o", ls="", mfc=p.color, mec=INK, ms=7, label=f"{p.bom}  {p.name}")
                   for p in parts if p.bom is not None]
        ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=7.5, bbox_to_anchor=(0.0, 0.9))
    if title:
        fig.text(0.02, 0.97, title, fontsize=9, fontweight="bold", color=INK, va="top")
        fig.text(0.02, 0.93, "CONCEPT, NOT FOR FABRICATION", fontsize=6.5, color="#B45309", va="top")
    if note:
        fig.text(0.02, 0.03, note, fontsize=7.5, color="#4B5563", va="bottom")
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    return out


def cutaway_parts(parts, keep="+Y"):
    """Cut every part with a half-space so the inside shows. keep='+Y' removes the half nearest a viewer looking from -Y."""
    from build123d import Box, Pos
    allbb = [p.shape.bounding_box() for p in parts]
    big = max(max(b.size.X, b.size.Y, b.size.Z) for b in allbb) * 4
    cy = sum(b.center().Y for b in allbb) / len(allbb)
    cutter = Pos(0, cy - big / 2 if keep == "-Y" else cy + big / 2, 0) * Box(big, big, big)
    out = []
    for p in parts:
        try:
            s = p.shape & cutter
            if s.volume > 1e-6:
                out.append(Part(p.name, s, p.color, p.bom, p.explode, p.alpha))
        except Exception:
            out.append(p)
    return out


def human_figure(height=1750.0, x=0.0, y=0.0, z=0.0):
    """Simple standing mannequin for scale (default 1.75 m), feet at z. Returns a Part."""
    from build123d import Cylinder, Sphere, Pos, Box
    k = height / 1750.0
    leg = lambda dx: Pos(x + dx * k, y, z + 430 * k) * Cylinder(62 * k, 860 * k)
    torso = Pos(x, y, z + 1160 * k) * Box(360 * k, 200 * k, 600 * k)
    arm = lambda dx: Pos(x + dx * k, y, z + 1130 * k) * Cylinder(42 * k, 620 * k)
    head = Pos(x, y, z + 1620 * k) * Sphere(115 * k)
    body = leg(-95) + leg(95) + torso + arm(-230) + arm(230) + head
    return Part(f"Person, {height / 1000:.2f} m (scale)", body, "#9CA3AF", None)


def with_scale_figure(parts, height=1750.0, gap=350.0):
    """Place a mannequin to the right of the assembly, standing on the same floor."""
    from build123d import Compound
    bb = Compound(children=[p.shape for p in parts]).bounding_box()
    fig = human_figure(height, x=bb.max.X + gap + 230 * height / 1750.0, y=(bb.min.Y + bb.max.Y) / 2, z=bb.min.Z)
    return parts + [fig]


def export_web_model(parts, media_dir="media", poster="hero.png", title="3D model"):
    """Export a colored glTF (model.glb) and an interactive viewer page (viewer.html) for the website."""
    from build123d import Compound, Color, export_gltf
    import matplotlib.colors as mc
    md = ROOT / media_dir; md.mkdir(parents=True, exist_ok=True)
    kids = []
    for p in parts:
        sh = p.shape
        sh.color = Color(*mc.to_rgb(p.color))
        sh.label = p.name
        kids.append(sh)
    export_gltf(Compound(children=kids), str(md / "model.glb"), binary=True)
    (md / "viewer.html").write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<script type="module" src="https://cdn.jsdelivr.net/npm/@google/model-viewer@3/dist/model-viewer.min.js"></script>
<style>body{{margin:0;font-family:system-ui,sans-serif;background:#F9FAFB}}model-viewer{{width:100vw;height:100vh}}
.tag{{position:fixed;left:12px;top:10px;font-size:12px;color:#B45309;letter-spacing:.06em}}</style></head>
<body><div class="tag">CONCEPT, NOT FOR FABRICATION</div>
<model-viewer src="model.glb" poster="{poster}" alt="{title}" camera-controls auto-rotate shadow-intensity="0.6"
  exposure="1.0" camera-orbit="-35deg 70deg auto" interaction-prompt="auto"></model-viewer></body></html>
""")
    return md / "model.glb"


def flow_diagram(stages, out, title, unit="kWh", losses=()):
    """System, data, energy or material flow diagram. Values may be numbers (scaled arrows) or text labels.
    stages: [(name, value)] left to right; losses: [(after_stage_index, name, value)] drawn as branches down.
    Example: stages=[("Surplus PV", 21.9), ("Heaters", 21.9), ("Sand store", 18.3), ("Warm air", 14.5)],
             losses=[(2, "Standby loss", 3.8)]."""
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    n = len(stages)
    fig, ax = plt.subplots(figsize=(max(10, 2.7 * n), 3.6), dpi=160)
    ax.set_xlim(0, n * 3); ax.set_ylim(-2.6, 2); ax.set_axis_off()
    nums = [v for _, v in stages if isinstance(v, (int, float))]
    vmax = max(nums) if nums else 1
    for i, (name, v) in enumerate(stages):
        x = i * 3 + 0.3
        ax.add_patch(FancyBboxPatch((x - 0.15, -0.5), 2.3, 1.2, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc="#F0FDFA", ec=ACCENT, lw=1.4))
        ax.text(x + 0.95, 0.28, name, ha="center", va="center", fontsize=8.5, fontweight="bold", color=INK)
        label = f"{v:g} {unit}".strip() if isinstance(v, (int, float)) else str(v)
        ax.text(x + 0.95, -0.15, label, ha="center", va="center", fontsize=9, color=ACCENT)
        if i < n - 1:
            w = 1 + 6 * v / vmax if isinstance(v, (int, float)) else 3
            ax.add_patch(FancyArrowPatch((x + 2.2, 0.1), (x + 2.8, 0.1), arrowstyle="-|>", mutation_scale=14,
                                         lw=w, color="#0F766E", alpha=0.55))
    for i, name, v in losses:
        x = i * 3 + 0.3 + 0.95
        ax.add_patch(FancyArrowPatch((x, -0.55), (x, -1.7), arrowstyle="-|>", mutation_scale=12,
                                     lw=1 + 6 * v / vmax, color="#C2410C", alpha=0.6))
        ax.text(x, -2.05, f"{name}: {v:g} {unit}", ha="center", va="center", fontsize=8.5, color="#C2410C")
    fig.text(0.01, 0.97, title, fontsize=10, fontweight="bold", color=INK, va="top")
    fig.text(0.01, 0.9, "CONCEPT, NOT FOR FABRICATION", fontsize=6.5, color="#B45309", va="top")
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white", bbox_inches="tight"); plt.close(fig)
    return out


def render_all(parts, project, title, dwg_no, key_figures, author="Amish Chadha", date=None,
               media_dir="media", rev="P1", cut=True, scale_figure=True, web_model=True, flow=None, context=(), cut_exclude=()):
    """flow: optional dict for flow_diagram, e.g. {"stages": [...], "losses": [...], "unit": "kWh"}.
    cut_exclude: part names left out of the cutaway (e.g. a strap that hides the section).
    context: Parts shown only in the hero render for scale (e.g. a forearm for a wearable). For small
    objects set scale_figure=False and pass a context part instead of the 1.75 m person."""
    import datetime, sys
    sys.path.insert(0, str(Path(__file__).parent))
    from drawing import Sheet, project_views
    from build123d import Compound
    date = date or datetime.date.today().isoformat()
    md = ROOT / media_dir
    shown = (with_scale_figure(parts) if scale_figure else parts) + list(context)
    hero = _render(shown, md / "hero.png", title=f"{project}",
                   note="Grey figure: 1.75 m person for scale" if scale_figure else
                   ("Grey: " + ", ".join(c.name for c in context) + " for scale" if context else None))
    outs = {"hero": hero}
    if cut:
        outs["cutaway"] = _render(cutaway_parts([p for p in parts if p.name not in cut_exclude]), md / "cutaway.png", azim=-90, elev=18,
                                  title=f"{project}: cutaway")
    if any(any(p.explode) for p in parts):
        outs["exploded"] = _render(parts, md / "exploded.png", offsets=True, labels=True,
                                   title=f"{project}: exploded view")
    if web_model:
        outs["web"] = export_web_model(parts, media_dir, title=f"{project}: {title}")
    if flow:
        outs["flow"] = flow_diagram(flow["stages"], md / "flow.png", f"{project}: {flow.get('title', 'system flow')}",
                                    flow.get("unit", "kWh"), flow.get("losses", ()))
    views = project_views(Compound(children=[p.shape for p in parts]), md / "_views")
    if scale_figure or context:  # scale reference only in the isometric view, never overlapping orthographic views
        views["iso"] = project_views(Compound(children=[p.shape for p in shown]), md / "_views_fig")["iso"]
    s = Sheet(project=project, title=title, dwg_no=dwg_no, rev=rev, author=author, date=date,
              theme="blueprint", material="Massing model for concept communication",
              revisions=[(rev, "Concept sheet", date, "".join(w[0] for w in author.split()))])
    s.add_ortho(views)
    s.add_svg(views["iso"], 276, 32, 140, 118, label="Isometric view",
              sublabel="Not to scale; figure is a 1.75 m person" if scale_figure else
              ("Not to scale; grey is for scale" if context else "Not to scale"))
    s.add_notes("Key figures", key_figures, x=276, y=168, width=140)
    s.save(md / "concept-blueprint")
    outs["blueprint"] = md / "concept-blueprint.png"
    return outs
