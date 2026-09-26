#!/usr/bin/env python3
"""Standard drawing sheet generator for the Open Hardware Portfolio.

Produces an ANSI B landscape sheet (431.8 x 279.4 mm) with border, title block,
revision table and third-angle projection symbol, as SVG + PDF + PNG.

Typical use from a project's cad/src/sheets.py:

    import sys; sys.path.insert(0, ".kit")
    from drawing import Sheet, project_views
    views = project_views(part, workdir="cad/drawings/_views")
    s = Sheet(project="ThermaBrick", title="General arrangement", dwg_no="TBK-DWG-001",
              rev="P1", author="Amish Chadha", date="2026-09-24", scale=0.1,
              revisions=[("P1", "Concept issue", "2026-09-24", "AC")])
    s.add_ortho(views, ["front", "top", "right"])
    s.add_iso(views["iso"])
    s.save("cad/drawings/TBK-DWG-001")
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

W, H = 431.8, 279.4          # ANSI B landscape, mm
M = 10.0                     # border margin
INK, MUTED, RULE, ACCENT = "#111827", "#4B5563", "#9CA3AF", "#0F766E"
FONT = "IBM Plex Sans, Helvetica, Arial, sans-serif"
MONO = "IBM Plex Mono, Menlo, monospace"
KIT = Path(__file__).resolve().parent
BLUEPRINT = {"#FFFFFF": "#143F73", INK: "#EEF5FF", "#4B5563": "#AFC8EC", "#9CA3AF": "#6F93C4",
             ACCENT: "#8FE3D6", "#F3F4F6": "#1D4F8A", "#B45309": "#FFD37F",
             "rgb(17,23,39)": "rgb(238,245,255)", "rgb(106,113,128)": "rgb(175,200,236)"}

# Title block geometry (bottom right)
TB_W, TB_H = 190.0, 56.0
TB_X, TB_Y = W - M - TB_W, H - M - TB_H


def install_fonts():
    """Make the bundled IBM Plex fonts visible to cairo (local and CI)."""
    import shutil, subprocess
    dest = Path.home() / ".local/share/fonts/ohp-kit"
    if not dest.exists():
        dest.mkdir(parents=True)
        for f in (KIT / "fonts").glob("*.ttf"):
            shutil.copy(f, dest)
        subprocess.run(["fc-cache", "-f", str(dest)], capture_output=True)


def repo_ref(root=None):
    """'github.com/<owner>/<repo>' from the repo's project.yaml ('repo: owner/name'), or None."""
    p = Path(root or Path.cwd()) / "project.yaml"
    try:
        m = re.search(r"^repo:\s*[\"']?([\w.-]+/[\w.-]+)", p.read_text(), re.M)
    except OSError:
        return None
    return f"github.com/{m.group(1)}" if m else None


def _t(x, y, s, size=2.6, weight=400, color=INK, anchor="start", mono=False):
    fam = MONO if mono else FONT
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-family="{fam}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" text-anchor="{anchor}">{escape(str(s))}</text>')


def _viewbox(svg_text: str):
    m = re.search(r'viewBox="([-\d.e]+)[ ,]+([-\d.e]+)[ ,]+([-\d.e]+)[ ,]+([-\d.e]+)"', svg_text)
    if not m:
        raise ValueError("SVG has no viewBox")
    return tuple(float(g) for g in m.groups())


def _inner(svg_text: str) -> str:
    body = re.sub(r"^.*?<svg[^>]*>", "", svg_text, count=1, flags=re.S)
    return re.sub(r"</svg>\s*$", "", body.strip())


def _center_lines(part, name, c, bb, min_r):
    """ISO 128 centre lines for cylindrical faces, in the 2D frame project_to_viewport uses."""
    from build123d import GeomType
    view = {"front": (0, 1, 0), "top": (0, 0, 1), "right": (1, 0, 0)}[name]
    to2d = {"front": lambda p: (p[0] - c.X, p[2] - c.Z), "top": lambda p: (p[0] - c.X, p[1] - c.Y),
            "right": lambda p: (p[1] - c.Y, p[2] - c.Z)}[name]
    lo = to2d((bb.min.X, bb.min.Y, bb.min.Z)); hi = to2d((bb.max.X, bb.max.Y, bb.max.Z))
    def clip(u, v):
        return (min(max(u, lo[0]), hi[0]), min(max(v, lo[1]), hi[1]))
    segs = set()
    for f in part.faces():
        if f.geom_type != GeomType.CYLINDER:
            continue
        try:
            ax, r = f.axis_of_rotation, f.radius
        except Exception:
            continue
        if r is None or r < min_r:
            continue
        a = (ax.direction.X, ax.direction.Y, ax.direction.Z)
        dot = abs(sum(i * j for i, j in zip(a, view)))
        fb = f.bounding_box()
        if dot > 0.99:            # seen end on: a cross through the circle centre
            o = ax.position
            u, v = to2d((o.X, o.Y, o.Z)); e = r * 1.25
            segs.add((clip(u - e, v), clip(u + e, v))); segs.add((clip(u, v - e), clip(u, v + e)))
        elif dot < 0.01:          # seen side on: a line along the axis over the face length
            o = ax.position; d = ax.direction
            t = [(p - o).dot(d) for p in (fb.min, fb.max)]
            t0, t1 = min(t), max(t); ext = 0.06 * (t1 - t0) + r * 0.3
            p0 = o + d * (t0 - ext); p1 = o + d * (t1 + ext)
            segs.add((clip(*to2d((p0.X, p0.Y, p0.Z))), clip(*to2d((p1.X, p1.Y, p1.Z)))))
    out = []
    for (a, b) in segs:
        a = tuple(round(x, 2) for x in a); b = tuple(round(x, 2) for x in b)
        if a != b:
            out.append((a, b))
    return sorted(set(out))


def project_views(part, workdir: str | Path, line_weight=0.35, center_lines=True):
    """Project a build123d part to front/top/right/iso SVGs (third-angle). Returns {name: path}.
    Ortho views carry visible lines, hidden lines (ISO dashed) and, for cylinders of useful
    size, ISO 128 centre lines (long dash dot)."""
    from build123d import ExportSVG, LineType, Unit, Edge, Vector
    workdir = Path(workdir); workdir.mkdir(parents=True, exist_ok=True)
    bb = part.bounding_box()
    c = bb.center(); d = max(bb.size.X, bb.size.Y, bb.size.Z) * 10
    min_r = 0.006 * max(bb.size.X, bb.size.Y, bb.size.Z)
    setups = {
        "front": ((c.X, c.Y - d, c.Z), (0, 0, 1)),
        "top":   ((c.X, c.Y, c.Z + d), (0, 1, 0)),
        "right": ((c.X + d, c.Y, c.Z), (0, 0, 1)),
        "iso":   ((c.X + d, c.Y - d, c.Z + d * 0.8), (0, 0, 1)),
    }
    out = {}
    for name, (origin, up) in setups.items():
        visible, hidden = part.project_to_viewport(origin, up, (c.X, c.Y, c.Z))
        ex = ExportSVG(unit=Unit.MM, line_weight=line_weight)
        ex.add_layer("Visible", line_color=0x111827)
        ex.add_layer("Hidden", line_color=0x6B7280, line_type=LineType.ISO_DASH, line_weight=line_weight / 2)
        ex.add_layer("Center", line_color=0x6B7280, line_type=LineType.ISO_LONG_DASH_DOT, line_weight=line_weight / 2)
        ex.add_shape(visible, layer="Visible")
        if name != "iso":
            ex.add_shape(hidden, layer="Hidden")
            if center_lines:
                lines = [Edge.make_line(Vector(a[0], a[1], 0), Vector(b[0], b[1], 0))
                         for a, b in _center_lines(part, name, c, bb, min_r)]
                if lines:
                    ex.add_shape(lines, layer="Center")
        p = workdir / f"{name}.svg"
        ex.write(str(p))
        out[name] = p
    return out


@dataclass
class Sheet:
    project: str
    title: str
    dwg_no: str
    rev: str
    author: str
    date: str
    scale: float | None = None          # sheet mm per model mm for ortho views; None picks a standard scale
    sheet: str = "1 of 1"
    units: str = "mm"
    material: str = ""
    license: str = "CERN-OHL-S-2.0"
    concept: bool = True
    theme: str = "technical"            # "technical" (white) or "blueprint" (white lines on blue)
    revisions: list = field(default_factory=list)   # [(rev, description, date, by)]
    notes: list = field(default_factory=list)
    repo: str | None = None             # 'github.com/owner/name'; read from project.yaml when not given
    _layers: list = field(default_factory=list)

    def __post_init__(self):
        if self.repo is None:
            self.repo = repo_ref()

    # ---------- content ----------
    VIEW_DIRECTIONS = {
        "top": "looking down (along -Z)",
        "front": "looking at the front (along +Y)",
        "right": "looking at the right side (along -X)",
        "left": "looking at the left side (along +X)",
        "rear": "looking at the back (along -Y)",
        "bottom": "looking up (along +Z)",
        "isometric": "seen from the front right and above, about 30 deg elevation",
    }

    @classmethod
    def with_direction(cls, label, sublabel):
        """Every view label states where it is seen from (standard section 6)."""
        if not label:
            return sublabel
        import re as _re
        tokens = _re.findall(r"[a-z]+", label.lower())
        key = "isometric" if "isometric" in tokens else (tokens[0] if tokens else "")
        words = (sublabel or "").lower()
        if key in cls.VIEW_DIRECTIONS and not any(k in words for k in ("looking", "seen from", "from the", "along")):
            direction = cls.VIEW_DIRECTIONS[key]
            return f"{sublabel}; {direction}" if sublabel else direction[0].upper() + direction[1:]
        return sublabel

    def add_svg(self, svg_path, x, y, w=None, h=None, scale=None, label=None, sublabel=None):
        """Place an SVG with its origin box centered in (x, y, w, h). With scale, size is exact."""
        sublabel = self.with_direction(label, sublabel)
        txt = Path(svg_path).read_text()
        vx, vy, vw, vh = _viewbox(txt)
        if scale is not None:
            dw, dh = vw * scale, vh * scale
        else:
            k = min(w / vw, h / vh); dw, dh = vw * k, vh * k
        bx = x + ((w or dw) - dw) / 2; by = y + ((h or dh) - dh) / 2
        k = dw / vw  # sheet mm per model unit; keep printed line weights constant
        txt = re.sub(r'stroke-width="([\d.]+)"', lambda m: f'stroke-width="{float(m.group(1)) / k:.4f}"', txt)
        txt = re.sub(r'stroke-dasharray="([^"]+)"', lambda m: 'stroke-dasharray="' + " ".join(
            f"{float(v) / k:.3f}" for v in re.split(r"[ ,]+", m.group(1).strip()) if v) + '"', txt)
        self._layers.append(
            f'<svg x="{bx:.2f}" y="{by:.2f}" width="{dw:.2f}" height="{dh:.2f}" viewBox="{vx} {vy} {vw} {vh}" '
            f'preserveAspectRatio="xMidYMid meet" overflow="visible">{_inner(txt)}</svg>')
        if label:
            ly = (y + (h or dh)) + 6
            self._layers.append(_t(x + (w or dw) / 2, ly, label.upper(), 2.8, 600, INK, "middle"))
            if sublabel:
                self._layers.append(_t(x + (w or dw) / 2, ly + 4, sublabel, 2.2, 400, MUTED, "middle"))

    STD_SCALES = [5, 2, 1, 1/2, 1/5, 1/10, 1/20, 1/25, 1/50, 1/100]

    def _dim(self, x1, y1, x2, y2, value, side, off=7.0):
        """Linear dimension between two sheet points (mm). side: 'above', 'below', 'left' or 'right'.
        ISO 129 style: thin extension lines with a small gap, filled arrowheads, value in mm."""
        g, ov, lw, al, aw = 1.2, 1.8, 0.18, 2.6, 0.9
        out = []
        if side in ("above", "below"):
            s_ = -1 if side == "above" else 1
            yb = (min(y1, y2) if s_ < 0 else max(y1, y2)); yd = yb + s_ * off
            for x, y in ((x1, y1), (x2, y2)):
                out.append(f'<line x1="{x:.2f}" y1="{y + s_ * g:.2f}" x2="{x:.2f}" y2="{yd + s_ * ov:.2f}" stroke="{INK}" stroke-width="{lw}"/>')
            out.append(f'<line x1="{x1:.2f}" y1="{yd:.2f}" x2="{x2:.2f}" y2="{yd:.2f}" stroke="{INK}" stroke-width="{lw}"/>')
            out.append(f'<path d="M{x1:.2f} {yd:.2f} l{al} {-aw/2} l0 {aw} Z M{x2:.2f} {yd:.2f} l{-al} {-aw/2} l0 {aw} Z" fill="{INK}"/>')
            out.append(_t((x1 + x2) / 2, yd - 1.0, value, 2.5, 500, INK, "middle"))
        else:
            s_ = -1 if side == "left" else 1
            xb = (min(x1, x2) if s_ < 0 else max(x1, x2)); xd = xb + s_ * off
            for x, y in ((x1, y1), (x2, y2)):
                out.append(f'<line x1="{x + s_ * g:.2f}" y1="{y:.2f}" x2="{xd + s_ * ov:.2f}" y2="{y:.2f}" stroke="{INK}" stroke-width="{lw}"/>')
            out.append(f'<line x1="{xd:.2f}" y1="{y1:.2f}" x2="{xd:.2f}" y2="{y2:.2f}" stroke="{INK}" stroke-width="{lw}"/>')
            out.append(f'<path d="M{xd:.2f} {y1:.2f} l{-aw/2} {al} l{aw} 0 Z M{xd:.2f} {y2:.2f} l{-aw/2} {-al} l{aw} 0 Z" fill="{INK}"/>')
            ym = (y1 + y2) / 2; xt = xd - 1.0
            out.append(f'<g transform="translate({xt:.2f} {ym:.2f}) rotate(-90)">{_t(0, 0, value, 2.5, 500, INK, "middle")}</g>')
        self._layers += out

    def add_ortho(self, views: dict, names=("front", "top", "right"), dims=True):
        """Third-angle layout: top above front, right beside front, aligned, at one scale.
        If the sheet scale is None, the largest standard scale that fits is chosen."""
        ax, ay, aw, ah = M + 10, M + 16, 245, TB_Y - M - 20
        gap, lab = 14, 12
        vb = {n: _viewbox(Path(views[n]).read_text())[2:] for n in names}
        fw, fh = vb.get("front", (0, 0)); tw, th = vb.get("top", (0, 0)); rw, rh = vb.get("right", (0, 0))
        dl = 11 if dims else 0          # room for overall dimensions left of and above the views
        def fits(k):
            return k * (max(fw, tw) + rw) + gap + dl <= aw and k * (th + max(fh, rh)) + gap + 2 * lab + dl <= ah
        if self.scale is None:
            self.scale = next((k for k in self.STD_SCALES if fits(k)), self.STD_SCALES[-1])
        k = self.scale
        sc = f"1:{1/k:g}" if k < 1 else f"{k:g}:1"
        ax += (aw - (k * (max(fw, tw) + rw) + gap + dl)) / 2 + dl     # center the view group
        ay += (ah - (k * (th + max(fh, rh)) + gap + 2 * lab + dl)) / 2 + dl
        colw = k * max(fw, tw)
        top_h = k * th
        front_y = ay + top_h + lab + gap
        row_h = k * max(fh, rh)
        cells = {"top": (ax, ay, colw, top_h),
                 "front": (ax, front_y, colw, row_h),
                 "right": (ax + colw + gap, front_y, k * rw, row_h)}
        for n in names:
            x, y, w, h = cells[n]
            self.add_svg(views[n], x, y, w, h, scale=k, label=f"{n} view", sublabel=f"Scale {sc}")
        if dims:
            # overall sizes, each shown once: length and depth on the top view, height on the front view
            def box(n):   # sheet box of the view's geometry (the SVG is centered in its cell)
                x, y, w, h = cells[n]; vw, vh = dims_[n]
                return x + (w - k * vw) / 2, y + (h - k * vh) / 2, k * vw, k * vh
            dims_ = {n: (vb[n][0] - 0.35, vb[n][1] - 0.35) for n in vb}
            if "top" in cells and "top" in names:
                x, y, w, h = box("top")
                self._dim(x, y, x + w, y, f"{dims_['top'][0]:.0f}", "above")
                self._dim(x, y, x, y + h, f"{dims_['top'][1]:.0f}", "left")
            if "front" in names:
                x, y, w, h = box("front")
                self._dim(x, y, x, y + h, f"{dims_['front'][1]:.0f}", "left")

    def add_iso(self, svg_path, label="Isometric view", sublabel="Not to scale"):
        x = M + 8 + 258; y = M + 8 + 22
        self.add_svg(svg_path, x, y, W - M - 8 - x, TB_Y - y - 26, label=label, sublabel=sublabel)

    def add_notes(self, title, lines, x=None, y=None, width=150):
        """Key-figures box, e.g. capacity, mass, power. Placed above the title block by default."""
        x = TB_X if x is None else x
        n = len(lines); h = 8 + 4.6 * n
        y = TB_Y - h - 6 if y is None else y
        self._layers.append(f'<rect x="{x}" y="{y}" width="{width}" height="{h}" fill="#FFFFFF" stroke="{INK}" stroke-width="0.35"/>')
        self._layers.append(_t(x + 3, y + 5, title.upper(), 2.3, 600, ACCENT))
        for i, line in enumerate(lines):
            self._layers.append(_t(x + 3, y + 10 + 4.6 * i, line, 2.6, 400, INK))

    def add_image(self, png_path, x, y, w, h, label=None, sublabel=None):
        """Embed a raster render (hero, cutaway, exploded) on the sheet."""
        import base64
        data = base64.b64encode(Path(png_path).read_bytes()).decode()
        self._layers.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" '
                            f'href="data:image/png;base64,{data}"/>')
        if label:
            self._layers.append(_t(x + w / 2, y + h + 6, label.upper(), 2.8, 600, INK, "middle"))
            if sublabel:
                self._layers.append(_t(x + w / 2, y + h + 10, sublabel, 2.2, 400, MUTED, "middle"))

    # ---------- frame ----------
    def _frame(self):
        f = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="#FFFFFF"/>',
             f'<rect x="{M}" y="{M}" width="{W-2*M}" height="{H-2*M}" fill="none" stroke="{INK}" stroke-width="0.7"/>']
        # Zone ticks
        for i in range(1, 8):
            x = M + i * (W - 2 * M) / 8
            f += [f'<line x1="{x:.1f}" y1="{M}" x2="{x:.1f}" y2="{M+3}" stroke="{INK}" stroke-width="0.35"/>',
                  f'<line x1="{x:.1f}" y1="{H-M}" x2="{x:.1f}" y2="{H-M-3}" stroke="{INK}" stroke-width="0.35"/>']
        if self.theme == "blueprint":
            for gx in range(int(M) + 10, int(W - M), 10):
                f.append(f'<line x1="{gx}" y1="{M}" x2="{gx}" y2="{H-M}" stroke="#2E5C94" stroke-width="0.12"/>')
            for gy in range(int(M) + 10, int(H - M), 10):
                f.append(f'<line x1="{M}" y1="{gy}" x2="{W-M}" y2="{gy}" stroke="#2E5C94" stroke-width="0.12"/>')
        if self.concept:
            f.append(_t(M + 6, M + 9, "CONCEPT, NOT FOR FABRICATION", 3.2, 600, "#B45309"))
        # project and repository on every sheet, so a printed or forwarded sheet is never anonymous
        ref = self.project + (f"  ·  {self.repo}" if self.repo else "")
        f.append(_t(M + 80, M + 9, ref, 3.2, 600, INK))
        return f

    def _title_block(self):
        x, y, w, h = TB_X, TB_Y, TB_W, TB_H
        g = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFFFFF" stroke="{INK}" stroke-width="0.7"/>',
             f'<rect x="{x}" y="{y}" width="3" height="{h}" fill="{ACCENT}"/>']
        row = [0, 14, 26, 38, 47, 56]
        for r in row[1:-1]:
            g.append(f'<line x1="{x}" y1="{y+r}" x2="{x+w}" y2="{y+r}" stroke="{RULE}" stroke-width="0.3"/>')

        def cell(cx, cy, cw, label, value, size=3.0, weight=500, mono=False):
            g.append(_t(cx + 2, cy + 3.4, label.upper(), 1.8, 500, MUTED))
            g.append(_t(cx + 2, cy + 3.4 + size + 1.4, value, size, weight, INK, mono=mono))
            return cw

        # Row 0: project + title
        g.append(_t(x + 6, y + 5, self.project.upper(), 2.2, 600, ACCENT))
        if self.repo:
            g.append(_t(x + w - 3, y + 5, self.repo, 2.2, 500, ACCENT, "end", mono=True))
        g.append(_t(x + 6, y + 11, self.title, 4.4, 600, INK))
        # Row 1: drawing no / rev / sheet
        cx = x + 3
        for (label, val, cw, mono) in [("Drawing no.", self.dwg_no, 80, True), ("Rev", self.rev, 25, True),
                                       ("Sheet", self.sheet, 30, False), ("Size", "ANSI B", 52, False)]:
            cell(cx, y + row[1], cw, label, val, 3.4, 600, mono)
            if cx > x + 3:
                g.append(f'<line x1="{cx}" y1="{y+row[1]}" x2="{cx}" y2="{y+row[2]}" stroke="{RULE}" stroke-width="0.3"/>')
            cx += cw
        # Row 2: scale / units / projection / date / author
        k = self.scale or 1
        sc = f"1:{1/k:g}" if k < 1 else f"{k:g}:1"
        cx = x + 3
        for (label, val, cw) in [("Scale", sc, 30), ("Units", self.units, 25), ("Projection", "", 35),
                                 ("Date", self.date, 40), ("Drawn", self.author, 57)]:
            if label == "Projection":
                g.append(_t(cx + 2, y + row[2] + 3.4, "PROJECTION", 1.8, 500, MUTED))
            else:
                cell(cx, y + row[2], cw, label, val)
            if label == "Projection":
                g += self._third_angle(cx + 22, y + row[2] + 7.5)
            if cx > x + 3:
                g.append(f'<line x1="{cx}" y1="{y+row[2]}" x2="{cx}" y2="{y+row[3]}" stroke="{RULE}" stroke-width="0.3"/>')
            cx += cw
        # Row 3: material / notes
        cell(x + 3, y + row[3], w, "Material / notes", self.material or "; ".join(self.notes) or "See BOM", 2.6, 400)
        # Row 4: license + site
        g.append(_t(x + 5, y + row[4] + 5.8, f"Licensed {self.license} · Design Molecule Lab · designmolecule.com", 2.1, 400, MUTED))
        g.append(_t(x + w - 3, y + row[4] + 5.8, "Generated from cad/src; do not edit by hand", 1.9, 400, MUTED, "end"))
        return g

    @staticmethod
    def _third_angle(cx, cy):
        s = INK
        return [f'<path d="M{cx-9} {cy-2.5} L{cx-3} {cy-4} L{cx-3} {cy+4} L{cx-9} {cy+2.5} Z" fill="none" stroke="{s}" stroke-width="0.3"/>',
                f'<circle cx="{cx+3}" cy="{cy}" r="4" fill="none" stroke="{s}" stroke-width="0.3"/>',
                f'<circle cx="{cx+3}" cy="{cy}" r="2.3" fill="none" stroke="{s}" stroke-width="0.3"/>',
                f'<line x1="{cx-11}" y1="{cy}" x2="{cx+8.5}" y2="{cy}" stroke="{s}" stroke-width="0.18" stroke-dasharray="3 1 0.6 1"/>']

    def _rev_table(self):
        rows = self.revisions or [(self.rev, "Initial issue", self.date, "")]
        cols = [("Rev", 14), ("Description", 92), ("Date", 26), ("By", 16)]
        w = sum(c for _, c in cols); x = W - M - w; y = M; rh = 5.2
        g = [f'<rect x="{x}" y="{y}" width="{w}" height="{rh*(len(rows)+1)}" fill="#FFFFFF" stroke="{INK}" stroke-width="0.5"/>',
             f'<rect x="{x}" y="{y}" width="{w}" height="{rh}" fill="#F3F4F6" stroke="{INK}" stroke-width="0.5"/>']
        cx = x
        for name, cw in cols:
            g.append(_t(cx + 1.8, y + 3.6, name.upper(), 2.0, 600, INK))
            cx += cw
        for i, r in enumerate(rows, start=1):
            cx = x; ry = y + i * rh
            g.append(f'<line x1="{x}" y1="{ry}" x2="{x+w}" y2="{ry}" stroke="{RULE}" stroke-width="0.3"/>')
            for (name, cw), val in zip(cols, r):
                g.append(_t(cx + 1.8, ry + 3.6, val, 2.3, 400, INK, mono=(name == "Rev")))
                cx += cw
        return g

    # ---------- output ----------
    def svg(self) -> str:
        parts = self._frame() + self._layers + self._rev_table() + self._title_block()
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">'
               + "".join(parts) + "</svg>")
        if self.theme == "blueprint":
            for a, b in BLUEPRINT.items():
                svg = svg.replace(a, b)
        return svg

    def save(self, stem, png_dpi=300):
        stem = Path(stem); stem.parent.mkdir(parents=True, exist_ok=True)
        svg = self.svg()
        svg_path = stem.with_suffix(".svg"); svg_path.write_text(svg)
        import cairosvg
        install_fonts()
        cairosvg.svg2pdf(bytestring=svg.encode(), write_to=str(stem.with_suffix(".pdf")))
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(stem.with_suffix(".png")),
                         output_width=int(W / 25.4 * png_dpi), output_height=int(H / 25.4 * png_dpi))
        return svg_path
