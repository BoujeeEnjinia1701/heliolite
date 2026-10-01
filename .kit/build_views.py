"""Illustrations for the prototype build plan (STANDARDS section 18).

Every build plan is drawn, not just written. This module turns the repo's own model into four
kinds of picture, all from the same parts list, so the words and the pictures never disagree:

    overview(parts, out)             the whole prototype pulled apart, every component numbered
    component_sheet(part, ...)       a making sketch for one component: three views with overall
                                     sizes, a 3D view, plain-English making notes, and an inset that
                                     shows where the component goes (it is coloured, its
                                     neighbours are grey)
    joint(parts, out, ...)           a close-up of two or more parts that fit together, optionally
                                     cut open, with each part named
    step(done, new, out, ...)        one assembly step: parts already fitted in grey, the part being
                                     fitted in colour, pulled back along the way it goes in, with an
                                     arrow and plain names

Parts are concept.Part objects (name, shape, color, bom, explode). `explode` is the direction and
distance a part moves to come out; step() uses it as the fitting direction.

Run from the repo root. Pictures go to docs/05-build-plan/ (PNG) and component sheets to
cad/drawings/ (SVG, PDF, PNG), named <CODE>-DWG-1NN.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from concept import Part, _tris, _shade, _zbuffer, INK, ACCENT  # noqa: E402

GHOST = "#D1D5DB"
NEW = "#0F766E"
EDGE = "#6B7280"
OUT_DIR = Path("docs/05-build-plan")
BANNER = "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT"
PIC_BOTTOM, PIC_HEIGHT = 0.045, 0.855   # the picture sits between the footer and the title lines


def _repo():
    try:
        from drawing import repo_ref
        return repo_ref()
    except Exception:
        return None


def _raster(items, elev, azim, W, H, ss=2):
    """items: list of (Part, color, alpha, offset). Returns image and a projector to pixel space."""
    tris_all, cols_all, verts = [], [], []
    e, a = np.radians(elev), np.radians(azim)
    cam = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    for p, color, alpha, off in items:
        v, t = _tris(p.shape)
        v = v + np.asarray(off, float)
        tri = v[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n = n / np.clip(np.linalg.norm(n, axis=1, keepdims=True), 1e-9, None)
        n = n * np.sign((n @ cam) + 1e-12)[:, None]
        tris_all.append(tri); cols_all.append(_shade(color, n, alpha)); verts.append(v)
    img, mask, proj = _zbuffer(np.vstack(tris_all), np.vstack(cols_all), elev, azim, W * ss, H * ss)
    if ss > 1:
        img = img.reshape(H, ss, W, ss, 3).mean((1, 3))
    return img, (lambda pts: proj(pts) / ss), verts


def _frame(size, dpi, title, subtitle=None):
    fig = plt.figure(figsize=size, dpi=dpi)
    ax = fig.add_axes([0, PIC_BOTTOM, 1, PIC_HEIGHT]); ax.set_axis_off()   # picture band clear of the title and footer
    if title:
        fig.text(0.02, 0.975, title, fontsize=10, fontweight="bold", color=INK, va="top")
    if subtitle:
        fig.text(0.02, 0.935, subtitle, fontsize=8, color="#374151", va="top")
    fig.text(0.02, 0.02, BANNER, fontsize=6.5, color="#B45309", va="bottom")
    if _repo():
        fig.text(0.98, 0.02, _repo(), fontsize=6.5, color=ACCENT, va="bottom", ha="right", family="monospace")
    return fig, ax


def _label(ax, xy, text, W, H, side=None, color=INK, n=None):
    """Leader-line label from a point on the part to clear space at the image edge."""
    x, y = xy
    side = side or ("left" if x < W / 2 else "right")
    tx = 0.04 * W if side == "left" else 0.96 * W
    ha = "left" if side == "left" else "right"
    txt = f"{n}  {text}" if n is not None else text
    ax.annotate(txt, xy=(x, y), xytext=(tx, y), fontsize=7.5, color=color, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=EDGE, lw=0.6, shrinkA=2, shrinkB=2),
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=EDGE, lw=0.5))


def _anchor(v):
    """A point on a part for its leader line: the part's own vertex nearest to the point between
    its centre and its highest point (so a leader never ends in the empty space between the
    pieces of a part made of several separate pieces)."""
    target = (v.mean(0) + v[np.argmax(v[:, 2])]) / 2
    return v[np.argmin(np.linalg.norm(v - target, axis=1))]


def _spread(labels, H, min_gap):
    """Nudge label y positions on each side apart so they do not overlap."""
    for side in ("left", "right"):
        idx = [i for i, l in enumerate(labels) if l[2] == side]
        idx.sort(key=lambda i: labels[i][1])
        last = -1e9
        for i in idx:
            y = max(labels[i][1], last + min_gap)
            labels[i] = (labels[i][0], min(y, H - min_gap), side, labels[i][3], labels[i][4])
            last = labels[i][1]
    return labels


def _draw_labels(ax, proj, pts, names, W, H, numbers=None):
    labels = []
    for k, (pt, name) in enumerate(zip(pts, names)):
        x, y = proj(pt)
        labels.append((x, y, "left" if x < W / 2 else "right", name, None if numbers is None else numbers[k]))
    ys = [(l[0], l[1], l[2], l[3], l[4]) for l in labels]
    spread = _spread([(l[0], l[1], l[2], l[3], l[4]) for l in ys], H, 0.045 * H)
    for (x0, y0, *_), (x, ty, side, name, n) in zip(labels, spread):
        tx = 0.04 * W if side == "left" else 0.96 * W
        ax.annotate(f"{n}  {name}" if n is not None else name, xy=(x0, y0), xytext=(tx, ty), fontsize=7.5,
                    color=INK, ha="left" if side == "left" else "right", va="center",
                    arrowprops=dict(arrowstyle="-", color=EDGE, lw=0.6, shrinkA=2, shrinkB=2),
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=EDGE, lw=0.5))


def overview(parts, out, title, subtitle="Every component, pulled apart and numbered in build order",
             elev=24, azim=-58, size=(10, 7), dpi=160, key=False):
    """Exploded view of the whole prototype. parts are numbered in list order (the build order).
    key=True puts a numbered bubble on each part and the names in a key column on the left, in place
    of leader lines; use it when there are many parts and leaders would cross the picture."""
    if not key:
        W, H = int(size[0] * dpi), int(size[1] * dpi * PIC_HEIGHT)
        items = [(p, p.color, p.alpha, p.explode) for p in parts]
        img, proj, verts = _raster(items, elev, azim, W, H)
        fig, ax = _frame(size, dpi, title, subtitle)
        ax.imshow(img, interpolation="bilinear")
        _draw_labels(ax, proj, [_anchor(v) for v in verts], [p.name for p in parts], W, H,
                     numbers=list(range(1, len(parts) + 1)))
    else:
        longest = max(len(p.name) for p in parts)
        kw = min(0.34, 0.05 + longest * 0.0105 * 8 / size[0])
        W, H = int(size[0] * dpi * (1 - kw)), int(size[1] * dpi * PIC_HEIGHT)
        items = [(p, p.color, p.alpha, p.explode) for p in parts]
        img, proj, verts = _raster(items, elev, azim, W, H)
        fig, ax = _frame(size, dpi, title, subtitle)
        ax.set_position([kw, PIC_BOTTOM, 1 - kw, PIC_HEIGHT])
        ax.imshow(img, interpolation="bilinear")
        for k, v in enumerate(verts):
            x, y = proj(_anchor(v))
            ax.text(x, y, str(k + 1), fontsize=7.5, fontweight="bold", color="white", ha="center", va="center",
                    bbox=dict(boxstyle="circle,pad=0.3", fc=ACCENT, ec="white", lw=0.8))
        top = PIC_BOTTOM + PIC_HEIGHT - 0.02
        step_ = min(0.042, (PIC_HEIGHT - 0.04) / max(len(parts), 1))
        for k, p in enumerate(parts):
            yk = top - k * step_
            fig.text(0.025, yk, str(k + 1), fontsize=7.5, fontweight="bold", color="white", ha="center", va="center",
                     bbox=dict(boxstyle="circle,pad=0.3", fc=ACCENT, ec="white", lw=0.8))
            fig.patches.append(plt.Rectangle((0.042, yk - 0.008), 0.012, 0.016, transform=fig.transFigure,
                                             fc=p.color, ec=INK, lw=0.5))
            fig.text(0.062, yk, p.name, fontsize=8, color=INK, va="center")
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    return out


def step(done, new, out, title, subtitle=None, context=(), pull=1.0, elev=24, azim=-58,
         size=(8, 6), dpi=160, label_done=True):
    """One assembly step. done: parts already fitted (grey). new: the parts fitted in this step
    (coloured), drawn pulled back by pull x their explode offset, with an arrow to where they go.
    context: extra parts drawn faint for orientation (a pole, the floor)."""
    W, H = int(size[0] * dpi), int(size[1] * dpi * PIC_HEIGHT)
    items = [(p, GHOST, 1.0, (0, 0, 0)) for p in done]
    items += [(p, "#E5E7EB", 0.6, (0, 0, 0)) for p in context]
    items += [(p, p.color if p.color not in (GHOST,) else NEW, 1.0, np.asarray(p.explode) * pull) for p in new]
    img, proj, verts = _raster(items, elev, azim, W, H)
    fig, ax = _frame(size, dpi, title, subtitle)
    ax.imshow(img, interpolation="bilinear")
    nd, nc = len(done), len(context)
    for k, p in enumerate(new):
        v = verts[nd + nc + k]
        off = np.asarray(p.explode) * pull
        if np.linalg.norm(off) > 1e-6:
            a = proj(v.mean(0)); b = proj(v.mean(0) - off * 0.85)
            ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color="#C2410C", lw=1.6, mutation_scale=14))
    names = [p.name for p in new]; pts = [_anchor(verts[nd + nc + k]) for k in range(len(new))]
    if label_done:
        names += [p.name for p in done]; pts += [_anchor(v) for v in verts[:nd]]
    _draw_labels(ax, proj, pts, names, W, H)
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    return out


def _cut(parts, cut):
    """Slice parts through their common centre. cut is '+X', '-X', '+Y' or '-Y': the half kept."""
    from build123d import Box, Pos
    bbs = [p.shape.bounding_box() for p in parts]
    lo = np.min([[b.min.X, b.min.Y, b.min.Z] for b in bbs], 0); hi = np.max([[b.max.X, b.max.Y, b.max.Z] for b in bbs], 0)
    c = (lo + hi) / 2; big = float((hi - lo).max()) * 4 + 10
    ax = 0 if cut[1].upper() == "X" else 1; sgn = 1 if cut[0] == "+" else -1
    pos = list(c); pos[ax] = c[ax] + sgn * big / 2
    cutter = Pos(*pos) * Box(big, big, big)
    out = []
    for p in parts:
        try:
            s = p.shape & cutter
            if s.volume > 1e-6:
                out.append(Part(p.name, s, p.color, p.bom, p.explode, p.alpha))
        except Exception:
            out.append(p)
    return out


def _has_volume(shape):
    try:
        return shape is not None and shape.volume > 1e-6
    except Exception:
        return False


def joint(parts, out, title, subtitle=None, cut=None, elev=24, azim=-58, size=(7, 5), dpi=160):
    """Close-up of parts that fit together. Only the given parts are drawn, so the view zooms in
    on them. cut='+Y' or '-Y' slices them in half to show how they sit inside each other."""
    if cut:
        parts = _cut(parts, cut)
    parts = [p for p in parts if _has_volume(p.shape)]      # a window or cut can leave a part empty
    W, H = int(size[0] * dpi), int(size[1] * dpi * PIC_HEIGHT)
    img, proj, verts = _raster([(p, p.color, p.alpha, (0, 0, 0)) for p in parts], elev, azim, W, H)
    fig, ax = _frame(size, dpi, title, subtitle)
    ax.imshow(img, interpolation="bilinear")
    _draw_labels(ax, proj, [_anchor(v) for v in verts], [p.name for p in parts], W, H)
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    return out


def where_it_goes(part, neighbours, out, elev=24, azim=-58, size=(5, 4), dpi=160):
    """Small picture: this part in colour among its neighbours in grey. Used as the sheet inset."""
    W, H = int(size[0] * dpi), int(size[1] * dpi)
    items = [(p, GHOST, 1.0, (0, 0, 0)) for p in neighbours] + [(part, NEW, 1.0, (0, 0, 0))]
    img, proj, verts = _raster(items, elev, azim, W, H)
    fig = plt.figure(figsize=size, dpi=dpi); ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    ax.imshow(img, interpolation="bilinear")
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    return out


def component_sheet(part, neighbours, project, dwg_no, title, material, notes, date,
                    rev="P1", author="Amish Chadha", revisions=None, out_dir="cad/drawings",
                    view_shape=None, inset_view=(24, -58)):
    """Making sketch for one component. notes: plain-English lines (key sizes, how to make it,
    how it fits its neighbours). Writes <out_dir>/<dwg_no>.svg, .pdf and .png.
    view_shape: the same part moved to lie square to the axes (a sloping bar laid flat, say), used
    for the three views and overall sizes; the inset still shows the part where it sits.
    inset_view: (elevation, azimuth) of the inset camera."""
    from drawing import Sheet, project_views
    work = Path(out_dir) / f"_{dwg_no}_views"
    views = project_views(view_shape if view_shape is not None else part.shape, work)
    inset = where_it_goes(part, neighbours, work / "where.png", elev=inset_view[0], azim=inset_view[1])
    s = Sheet(project=project, title=title, dwg_no=dwg_no, rev=rev, author=author, date=date, concept="BUILD PLAN SKETCH, PLAN NOT YET BUILT",
              scale=None, material=material,
              revisions=revisions or [(rev, "Making sketch for the prototype build plan", date, "AC")])
    s.add_ortho(views, ["front", "top", "right"])
    s.add_image(str(inset), 276, 30, 140, 70, label="Where it goes", sublabel="This part in colour, its neighbours in grey")
    s.add_notes("How to make it and how it fits", notes, x=276, y=112, width=140)
    s.save(Path(out_dir) / dwg_no)
    shutil.rmtree(work, ignore_errors=True)
    return Path(out_dir) / f"{dwg_no}.png"


__all__ = ["Part", "overview", "step", "joint", "where_it_goes", "component_sheet"]
