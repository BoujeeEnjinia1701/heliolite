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


def project_views(part, workdir: str | Path, line_weight=0.35):
    """Project a build123d part to front/top/right/iso SVGs (third-angle). Returns {name: path}."""
    from build123d import ExportSVG, LineType, Unit
    workdir = Path(workdir); workdir.mkdir(parents=True, exist_ok=True)
    bb = part.bounding_box()
    c = bb.center(); d = max(bb.size.X, bb.size.Y, bb.size.Z) * 10
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
        ex.add_shape(visible, layer="Visible")
        if name != "iso":
            ex.add_shape(hidden, layer="Hidden")
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
    _layers: list = field(default_factory=list)

    # ---------- content ----------
    def add_svg(self, svg_path, x, y, w=None, h=None, scale=None, label=None, sublabel=None):
        """Place an SVG with its origin box centered in (x, y, w, h). With scale, size is exact."""
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

    def add_ortho(self, views: dict, names=("front", "top", "right")):
        """Third-angle layout: top above front, right beside front, aligned, at one scale.
        If the sheet scale is None, the largest standard scale that fits is chosen."""
        ax, ay, aw, ah = M + 10, M + 16, 245, TB_Y - M - 20
        gap, lab = 14, 12
        dims = {n: _viewbox(Path(views[n]).read_text())[2:] for n in names}
        fw, fh = dims.get("front", (0, 0)); tw, th = dims.get("top", (0, 0)); rw, rh = dims.get("right", (0, 0))
        def fits(k):
            return k * (max(fw, tw) + rw) + gap <= aw and k * (th + max(fh, rh)) + gap + 2 * lab <= ah
        if self.scale is None:
            self.scale = next((k for k in self.STD_SCALES if fits(k)), self.STD_SCALES[-1])
        k = self.scale
        sc = f"1:{1/k:g}" if k < 1 else f"{k:g}:1"
        ax += (aw - (k * (max(fw, tw) + rw) + gap)) / 2          # center the view group
        ay += (ah - (k * (th + max(fh, rh)) + gap + 2 * lab)) / 2
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
        g.append(_t(x + 5, y + row[4] + 5.8, f"Licensed {self.license} · Open Hardware Portfolio · amishchadha.com", 2.1, 400, MUTED))
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

    def save(self, stem, png_dpi=110):
        stem = Path(stem); stem.parent.mkdir(parents=True, exist_ok=True)
        svg = self.svg()
        svg_path = stem.with_suffix(".svg"); svg_path.write_text(svg)
        import cairosvg
        install_fonts()
        cairosvg.svg2pdf(bytestring=svg.encode(), write_to=str(stem.with_suffix(".pdf")))
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(stem.with_suffix(".png")),
                         output_width=int(W / 25.4 * png_dpi), output_height=int(H / 25.4 * png_dpi))
        return svg_path
