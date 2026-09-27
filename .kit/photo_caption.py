"""Caption a photoreal render (STANDARDS section 12).

Usage (repo root):
    python .kit/photo_caption.py raw.png media/render-<view>.png "Name: what it is" "Note on the view" [--fonts .kit/fonts]

The render itself is never written on. The title, the concept label and the repository sit in a
header band above it, and the view note sits in a footer band below it. Every line is wrapped to
the image width and the font steps down to a floor before a line is added, so no text runs off the
image or overlaps other text. The layout is stored in the PNG ("dm-layout") and checked by
.kit/image_qc.py; this script refuses to write an image that fails the check.
The repository line comes from project.yaml ('repo: owner/name').
"""
import json, re, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from PIL.PngImagePlugin import PngInfo

LAYOUT_VERSION = 2
INK, AMBER, SLATE, TEAL = (17, 24, 39), (180, 83, 9), (55, 65, 81), (15, 118, 110)


def font(fonts, name, px):
    return ImageFont.truetype(str(fonts / name), int(round(px)))


def wrap(draw, text, f, width):
    """Greedy word wrap by rendered pixel width."""
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= width or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, fonts, name, sizes, width, max_lines):
    """Largest size whose wrapped text fits in max_lines; else the smallest size, however many lines."""
    for s in sizes:
        f = font(fonts, name, s)
        lines = wrap(draw, text, f, width)
        if len(lines) <= max_lines:
            return f, lines
    return f, lines


def band(strip, height, width):
    """A smooth fill that continues the studio background: column medians, blurred sideways."""
    col = np.median(strip, axis=0).astype(np.uint8)[None, :, :]
    im = Image.fromarray(np.repeat(col, 8, axis=0)).filter(ImageFilter.GaussianBlur(radius=max(8, width // 24)))
    return im.resize((width, height), Image.BILINEAR)


def overlaps(a, b, gap=4):
    return not (a[2] + gap <= b[0] or b[2] + gap <= a[0] or a[3] + gap <= b[1] or b[3] + gap <= a[1])


def caption(raw, out, title, note, fonts=Path(".kit/fonts"), repo=None):
    body = Image.open(raw).convert("RGB")
    W, H = body.size
    u = W / 1280
    pad, gap = round(26 * u), round(10 * u)
    cw = W - 2 * pad
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))

    tf, tlines = fit(probe, title, fonts, "IBMPlexSans-SemiBold.ttf", [28 * u, 26 * u, 24 * u, 22 * u], cw, 2)
    lf = font(fonts, "IBMPlexSans-Medium.ttf", 15 * u)
    mf = font(fonts, "IBMPlexMono-Regular.ttf", 15 * u)
    nf, nlines = fit(probe, note, fonts, "IBMPlexSans-Regular.ttf", [17 * u, 16 * u, 15 * u], cw, 3)
    label = "CONCEPT, NOT FOR FABRICATION"
    ref = f"github.com/{repo}" if repo else ""

    tlh, llh, nlh = round(tf.size * 1.28), round(lf.size * 1.5), round(nf.size * 1.45)
    ref_same_line = ref and probe.textlength(label, font=lf) + 3 * gap + probe.textlength(ref, font=mf) <= cw
    top = pad + tlh * len(tlines) + gap + llh + (0 if ref_same_line or not ref else llh) + round(pad * 0.7)
    bottom = round(pad * 0.7) + nlh * len(nlines) + pad
    arr = np.asarray(body)
    im = Image.new("RGB", (W, top + H + bottom))
    im.paste(band(arr[:12], top, W), (0, 0))
    im.paste(body, (0, top))
    im.paste(band(arr[-12:], bottom, W), (0, top + H))
    d = ImageDraw.Draw(im)
    boxes = []

    def put(xy, text, f, fill, kind):
        d.text(xy, text, font=f, fill=fill)
        boxes.append({"kind": kind, "box": list(d.textbbox(xy, text, font=f)), "px": f.size, "text": text})

    y = pad
    for line in tlines:
        put((pad, y), line, tf, INK, "title"); y += tlh
    y += gap
    put((pad, y), label, lf, AMBER, "label")
    if ref:
        if ref_same_line:
            put((W - pad - d.textlength(ref, font=mf), y + round((lf.size - mf.size) / 2)), ref, mf, TEAL, "repo")
        else:
            y += llh
            put((pad, y), ref, mf, TEAL, "repo")
    y = top + H + round(pad * 0.7)
    for line in nlines:
        put((pad, y), line, nf, SLATE, "note"); y += nlh

    layout = {"version": LAYOUT_VERSION, "kind": "render", "size": [W, im.size[1]],
              "body": [0, top, W, top + H], "boxes": boxes}
    problems = check_layout(layout)
    if problems:
        raise SystemExit("caption layout failed: " + "; ".join(problems))
    info = PngInfo(); info.add_text("dm-layout", json.dumps(layout))
    im.save(out, optimize=True, pnginfo=info)
    return im.size


def check_layout(layout, min_px_ratio=0.0105):
    """Rules shared with .kit/image_qc.py: text inside the image, clear of the render, never overlapping."""
    W, Ht = layout["size"]
    edge = round(W * 0.012)
    body = layout.get("body")
    probs = []
    boxes = layout["boxes"]
    for b in boxes:
        x0, y0, x1, y1 = b["box"]
        if x0 < edge or y0 < edge or x1 > W - edge or y1 > Ht - edge:
            probs.append(f"{b['kind']} text runs off the image: {b['text'][:40]}")
        if body and overlaps(b["box"], body, gap=0):
            probs.append(f"{b['kind']} text overlaps the render: {b['text'][:40]}")
        if b["px"] < W * min_px_ratio:
            probs.append(f"{b['kind']} text too small ({b['px']} px): {b['text'][:40]}")
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if overlaps(boxes[i]["box"], boxes[j]["box"]):
                probs.append(f"{boxes[i]['kind']} and {boxes[j]['kind']} text overlap")
    return probs


if __name__ == "__main__":
    raw, out, title, note = sys.argv[1:5]
    fonts = Path(sys.argv[sys.argv.index("--fonts") + 1]) if "--fonts" in sys.argv else Path(".kit/fonts")
    try:
        m = re.search(r"^repo:\s*[\"']?([\w.-]+/[\w.-]+)", Path("project.yaml").read_text(), re.M)
    except OSError:
        m = None
    size = caption(raw, out, title, note, fonts, m.group(1) if m else None)
    print("wrote", out, size)
