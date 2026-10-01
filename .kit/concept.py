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


def _zbuffer(tris, cols, elev, azim, W, H, pad=0.06, ids=None):
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
    idb = np.full((H, W), -1, dtype=np.int32) if ids is not None else None
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
        if idb is not None:
            idb[ymin:ymax, xmin:xmax][m] = ids[i]
    proj = (lambda pts: to_px((np.asarray(pts) @ P.T)[..., :2]))
    if idb is not None:
        return img, np.isfinite(zb), proj, idb
    return img, np.isfinite(zb), proj


def _repo():
    try:
        from drawing import repo_ref
        return repo_ref()
    except Exception:
        return None


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
    ids = np.concatenate([np.full(len(t), k) for k, t in enumerate(tris_all)])
    img, mask, proj0, idb = _zbuffer(np.vstack(tris_all), np.vstack(cols_all), elev, azim, W * ss, H * ss, ids=ids)
    # Crop to the drawn subject (plus a margin) so it fills its box instead of floating in white space
    ys_, xs_ = np.nonzero(mask)
    if len(xs_):
        mx = int(0.04 * max(np.ptp(xs_), np.ptp(ys_))) + 4 * ss
        x0, x1 = max(xs_.min() - mx, 0), min(xs_.max() + mx + 1, W * ss)
        y0, y1 = max(ys_.min() - mx, 0), min(ys_.max() + mx + 1, H * ss)
        x1 = x0 + (x1 - x0) // ss * ss; y1 = y0 + (y1 - y0) // ss * ss
        img, idb = img[y0:y1, x0:x1], idb[y0:y1, x0:x1]
    else:
        x0 = y0 = 0
    Hc, Wc = img.shape[0] // ss, img.shape[1] // ss
    if ss > 1:
        img = img.reshape(Hc, ss, Wc, ss, 3).mean((1, 3))
        idb = idb[::ss, ::ss]
    proj = (lambda pts: (proj0(pts) - np.array([x0, y0])))
    # Layout: a header band (title, banner, repo), a footer band (note) and, for labelled views, a
    # legend column on the left. The render sits in its own box, so no text can fall on the model.
    import textwrap
    head, foot = 0.12, 0.09 if note else 0.03
    leg_w = 0.0
    if labels:
        entries = [f"{p.bom}  {p.name}" for p in parts if p.bom is not None]
        longest = max((len(e) for e in entries), default=0)
        leg_w = min(0.42, 0.03 + longest * 0.0105 * 8 / size[0])
    fig = plt.figure(figsize=size, dpi=dpi)
    ax = fig.add_axes([leg_w, foot, 1 - leg_w, 1 - head - foot]); ax.imshow(img, interpolation="bilinear"); ax.set_axis_off(); ax.set_anchor("C")
    if labels:
        # Callout bubbles start on their part; overlapping bubbles are pushed apart and joined to
        # their part by a thin leader, so no number sits on another.
        # Each number goes on a pixel where its part is actually visible (the visible pixel nearest
        # the part's centre); a number whose parts are all hidden gets no bubble, only a legend entry.
        pts, nums, best = [], [], {}
        for k, (p, v) in enumerate(items):
            if p.bom is None:
                continue
            yy, xx = np.nonzero(idb == k)
            if not len(xx):
                continue
            c = proj(v.mean(0)) / ss
            j = int(np.argmin((xx - c[0]) ** 2 + (yy - c[1]) ** 2))
            if p.bom not in best or len(xx) > best[p.bom][0]:
                best[p.bom] = (len(xx), (xx[j], yy[j]))
        W, H = Wc, Hc
        # bubble radius in image pixels: the bubble is drawn at a fixed size on the figure, so convert
        axw = (1 - leg_w) * size[0] * dpi; axh = (1 - head - foot) * size[1] * dpi
        r = 15.0 * max(Wc / axw, Hc / axh)
        small = []
        for bom, (area, xy) in best.items():
            pts.append(xy); nums.append(bom); small.append(area < (1.6 * r) ** 2)
        hidden = {p.bom for p in parts if p.bom is not None} - set(best)
        pts = np.array(pts, float).reshape(-1, 2); pos = pts.copy()
        # A part smaller than its bubble gets the bubble set off to the side, away from the middle of
        # the picture, with a leader to the part, so the bubble never hides the part or floats alone.
        ctr_img = np.array([W / 2, H / 2])
        for i, sm in enumerate(small):
            if sm:
                d = pts[i] - ctr_img; nd = np.hypot(*d)
                u = d / nd if nd > 1e-6 else np.array([1.0, 0.0])
                # outward first; if that leaves the picture, try other directions
                for v in (u, np.array([-u[1], u[0]]), np.array([u[1], -u[0]]), np.array([0.0, -1.0]),
                          np.array([0.0, 1.0]), -u):
                    q = pts[i] + v * 3.2 * r
                    if 1.2 * r <= q[0] <= W - 1.2 * r and 1.2 * r <= q[1] <= H - 1.2 * r:
                        pos[i] = q
                        break
                else:
                    pos[i] = pts[i] - u * 3.2 * r     # point back toward the middle; clipped below
        for _ in range(200):
            moved = False
            for i in range(len(pos)):
                for j in range(i + 1, len(pos)):
                    d = pos[j] - pos[i]; dist = np.hypot(*d)
                    if dist < 2.25 * r:
                        u = d / dist if dist > 1e-6 else np.array([1.0, 0.0])
                        push = (2.25 * r - dist) / 2 + 0.5
                        pos[i] -= u * push; pos[j] += u * push; moved = True
            pos[:, 0] = np.clip(pos[:, 0], r, W - r); pos[:, 1] = np.clip(pos[:, 1], r, H - r)
            if not moved:
                break
        for (ax0, ay0), (x, y), n in zip(pts, pos, nums):
            if np.hypot(x - ax0, y - ay0) > 0.6 * r:
                ax.plot([ax0, x], [ay0, y], color=INK, lw=0.6, zorder=3)
                ax.plot([ax0], [ay0], marker="o", ms=2.2, color=INK, zorder=3)
            ax.text(x, y, f"{n}", fontsize=8, fontweight="bold", color="white", ha="center", va="center", zorder=4,
                    bbox=dict(boxstyle="circle,pad=0.3", fc=ACCENT, ec="white", lw=0.8))
        ax.set_xlim(0, W); ax.set_ylim(H, 0)
        legend = {}
        for p in parts:
            if p.bom is None:
                continue
            e = legend.setdefault(p.bom, [p.color, []])
            if p.name not in e[1]:
                e[1].append(p.name)
        handles = [plt.Line2D([], [], marker="o", ls="", mfc=c, mec=INK, ms=7,
                              label=f"{b}  {' and '.join(ns)}" + ("  (hidden in this view)" if b in hidden else ""))
                   for b, (c, ns) in sorted(legend.items(), key=lambda kv: (str(type(kv[0])), kv[0]))]
        n = len(handles)
        fs = 7.5 if n <= 18 else max(5.5, 7.5 * 18 / n)
        fig.legend(handles=handles, loc="upper left", frameon=False, fontsize=fs, bbox_to_anchor=(0.01, 1 - head),
                   handletextpad=0.4, borderaxespad=0.0, labelspacing=0.5)
    if title:
        fig.text(0.02, 0.975, title, fontsize=9, fontweight="bold", color=INK, va="top")
        fig.text(0.02, 0.93, "CONCEPT, NOT FOR FABRICATION", fontsize=6.5, color="#B45309", va="top")
        if _repo():
            fig.text(0.98, 0.975, _repo(), fontsize=7, color=ACCENT, va="top", ha="right", family="monospace")
    if note:
        fig.text(0.02, 0.015, textwrap.fill(note, int(size[0] * 15)), fontsize=7.5, color="#4B5563", va="bottom")
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


def _keep_units(text):
    """Join a number to its unit with a no-break space so wrapping never strands the unit."""
    import re
    return re.sub(r"(\d)\s+([A-Za-z%\u00b0/]{1,6})(?=\W|$)", "\\1\u00a0\\2", str(text))


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
        import textwrap as _tw
        name = _keep_units(str(name))
        ax.text(x + 0.95, 0.3, _tw.fill(name, 18), ha="center", va="center", fontsize=8 if len(str(name)) > 18 else 8.5,
                fontweight="bold", color=INK, linespacing=1.1)
        label = f"{v:g}\u00a0{unit}".strip() if isinstance(v, (int, float)) else str(v)
        import re as _re
        label = _keep_units(label)
        ax.text(x + 0.95, -0.22, _tw.fill(label, 20), ha="center", va="center", fontsize=8 if len(label) > 20 else 9,
                color=ACCENT, linespacing=1.1)
        if i < n - 1:
            w = 1 + 6 * v / vmax if isinstance(v, (int, float)) else 3
            ax.add_patch(FancyArrowPatch((x + 2.2, 0.1), (x + 2.8, 0.1), arrowstyle="-|>", mutation_scale=14,
                                         lw=w, color="#0F766E", alpha=0.55))
    for i, name, v in losses:
        x = i * 3 + 0.3 + 0.95
        ax.add_patch(FancyArrowPatch((x, -0.55), (x, -1.7), arrowstyle="-|>", mutation_scale=12,
                                     lw=1 + 6 * v / vmax, color="#C2410C", alpha=0.6))
        ax.text(x, -2.1, _tw.fill(_keep_units(f"{name}: {v:g} {unit}"), 24), ha="center", va="center", fontsize=8, color="#C2410C")
    import textwrap as _tw2
    fw = fig.get_size_inches()[0]
    ttl = _tw2.fill(title, max(30, int((fw - 3.6) * 11)))
    nl = ttl.count("\n") + 1
    fig.text(0.01, 0.97, ttl, fontsize=10, fontweight="bold", color=INK, va="top", linespacing=1.2)
    fig.text(0.01, 0.97 - 0.075 * nl, "CONCEPT, NOT FOR FABRICATION", fontsize=6.5, color="#B45309", va="top")
    if _repo():
        fig.text(0.99, 0.97, _repo(), fontsize=7, color=ACCENT, va="top", ha="right", family="monospace")
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
    scale_note = ("Grey figure: 1.75 m person for scale" if scale_figure else
                  ("Grey: " + ", ".join(c.name for c in context) + " for scale" if context else None))
    view_note = "Seen from the front right and above, 24 deg elevation"
    hero = _render(shown, md / "hero.png", title=f"{project}",
                   note=f"{view_note}. {scale_note}" if scale_note else view_note)
    outs = {"hero": hero}
    if cut:
        outs["cutaway"] = _render(cutaway_parts([p for p in parts if p.name not in cut_exclude]), md / "cutaway.png", azim=-90, elev=18,
                                  title=f"{project}: cutaway",
                                  note="Front half removed; seen from the front and above, 18 deg elevation")
    if any(any(p.explode) for p in parts):
        outs["exploded"] = _render(parts, md / "exploded.png", offsets=True, labels=True,
                                   title=f"{project}: exploded view",
                                   note="Seen from the front right and above, 24 deg elevation; numbers match bom/bom.csv")
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
