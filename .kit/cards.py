"""Storefront images (STANDARDS section 13): media/card.png (800 x 800, profile thumbnail) and
media/social-preview.png (1280 x 640, GitHub social preview), both built from media/render-hero.png.

Usage, from the repo root:  python .kit/cards.py .

Text is wrapped by its rendered width, fonts step down to a floor before anything is shortened,
and the layout is stored in the PNG ("dm-layout") and checked by .kit/image_qc.py. The script
refuses to write an image whose text runs off the image or overlaps other text.
"""
import json, re, sys
from pathlib import Path
import numpy as np, yaml
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from PIL.PngImagePlugin import PngInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from photo_caption import check_layout, wrap  # noqa: E402

F = Path(__file__).resolve().parent / "fonts"
TEAL, INK, GREY = (15, 118, 110), (17, 24, 39), (75, 85, 99)


def font(n, s): return ImageFont.truetype(str(F / n), int(s))


def body_of(hero_path):
    """The render without its caption bands (layout v2), or the middle of an older captioned image."""
    im = Image.open(hero_path)
    lay = im.info.get("dm-layout")
    im = im.convert("RGB")
    if lay:
        return im.crop(tuple(json.loads(lay)["body"]))
    w, h = im.size
    return im.crop((0, int(h * 0.10), w, int(h * 0.92)))


def product_square(hero_path, size):
    body = body_of(hero_path)
    bw, bh = body.size
    e = np.asarray(body.convert("L").filter(ImageFilter.FIND_EDGES))[4:-4, 4:-4]
    # strong edges belong to the product; faint ones are mostly the studio backdrop
    ys, xs = np.nonzero(e > 40)
    if len(xs) < 500:
        ys, xs = np.nonzero(e > 16)
    if len(xs) < 50:
        x0, y0, x1, y1 = 0, 0, bw, bh
    else:
        x0, x1 = np.percentile(xs, [0.15, 99.85]) + 4; y0, y1 = np.percentile(ys, [0.05, 99.9]) + 4
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    side = int(max(x1 - x0, y1 - y0) * 1.3)
    # Background: the render itself, heavily blurred and stretched, so any area outside the
    # render continues its studio backdrop; the render is laid on top with a feathered edge.
    n = side * 3
    ox, oy = int(n / 2 - cx), int(n / 2 - cy)
    soft = np.asarray(body.filter(ImageFilter.GaussianBlur(24)))
    pads = ((max(0, oy), max(0, n - oy - bh)), (max(0, ox), max(0, n - ox - bw)), (0, 0))
    back = Image.fromarray(np.pad(soft, pads, mode="edge")).crop((max(0, -ox), max(0, -oy), max(0, -ox) + n, max(0, -oy) + n))
    mask = Image.new("L", (n, n), 0)
    f = max(6, side // 40)
    mask.paste(255, (ox + f, oy + f, ox + bw - f, oy + bh - f))
    mask = mask.filter(ImageFilter.GaussianBlur(f))
    front = back.copy(); front.paste(body, (ox, oy))
    canvas = Image.composite(front, back, mask)
    c = n // 2
    return canvas.crop((c - side // 2, c - side // 2, c - side // 2 + side, c - side // 2 + side)).resize((size, size), Image.LANCZOS)


def fit_lines(d, text, name, sizes, width, max_lines):
    for s in sizes:
        f = font(name, s); lines = wrap(d, text, f, width)
        if len(lines) <= max_lines:
            return f, lines
    return f, lines


def make(root):
    root = Path(root); y = yaml.safe_load(open(root / "project.yaml"))
    readme = (root / "README.md").read_text()
    m = re.search(r"!\[([^\]]+?), product render\]\(media/render-hero\.png\)", readme)
    title = m.group(1) if m else y["name"]; name, _, tag = title.partition(": ")
    name = name or y["name"]
    sq = product_square(root / "media/render-hero.png", 800)
    info = PngInfo(); info.add_text("dm-layout", json.dumps({"version": 2, "kind": "card", "size": [800, 800], "boxes": []}))
    sq.save(root / "media/card.png", optimize=True, pnginfo=info)

    W, H = 1280, 640
    im = Image.new("RGB", (W, H), (255, 255, 255)); im.paste(sq.resize((H, H), Image.LANCZOS), (0, 0))
    d = ImageDraw.Draw(im)
    x, cw = H + 48, W - H - 48 - 40
    boxes = []

    def put(xy, text, f, fill, kind):
        d.text(xy, text, font=f, fill=fill)
        boxes.append({"kind": kind, "box": list(d.textbbox(xy, text, font=f)), "px": f.size, "text": text})

    brand = "OpenRatio" if "enjinia1929" in y.get("repo", "") else "Design Molecule"
    kind = "research and educational prototype" if brand == "OpenRatio" else "open hardware concept"
    foot1 = f"{brand} · {kind}, TRL {y.get('trl', 3)}"
    foot2 = "github.com/" + y.get("repo", "")
    f1, l1 = fit_lines(d, foot1, "IBMPlexSans-Medium.ttf", [20, 18, 16], cw, 1)
    f2 = font("IBMPlexMono-Regular.ttf", 18)
    while d.textlength(foot2, font=f2) > cw and f2.size > 16:
        f2 = font("IBMPlexMono-Regular.ttf", f2.size - 1)
    foot_top = H - 56 - round(f1.size * 1.4) - round(f2.size * 1.4)

    yy = 56
    put((x, yy), (y.get("area") or "").upper(), font("IBMPlexSans-SemiBold.ttf", 20), TEAL, "area"); yy += 32
    nf, nl = fit_lines(d, name, "IBMPlexSans-SemiBold.ttf", [56, 50, 44, 38, 34], cw, 1)
    for line in nl:
        put((x, yy), line, nf, INK, "name"); yy += round(nf.size * 1.2)
    yy += 12
    if tag:
        tf, tl = fit_lines(d, tag[:1].upper() + tag[1:], "IBMPlexSans-Medium.ttf", [28, 26, 24, 22], cw, 3)
        for line in tl:
            put((x, yy), line, tf, INK, "tagline"); yy += round(tf.size * 1.36)
        yy += 14
    first = re.split(r"(?<=[.!?])\s", " ".join(y["pitch"].split()))[0]
    room = foot_top - 20 - yy
    for s in [20, 19, 18, 17, 16]:
        pf = font("IBMPlexSans-Regular.ttf", s); lh = round(s * 1.45)
        pl = wrap(d, first, pf, cw)
        if len(pl) * lh <= room:
            break
    else:
        keep = max(0, room // lh)
        pl = pl[:keep]
        if pl:
            while d.textlength(pl[-1] + " ...", font=pf) > cw and " " in pl[-1]:
                pl[-1] = pl[-1].rsplit(" ", 1)[0]
            pl[-1] = pl[-1].rstrip(",;:") + " ..."
    for line in pl:
        put((x, yy), line, pf, GREY, "pitch"); yy += lh
    put((x, foot_top), l1[0], f1, INK, "brand")
    put((x, foot_top + round(f1.size * 1.4)), foot2, f2, TEAL, "repo")

    layout = {"version": 2, "kind": "social-preview", "size": [W, H], "body": [0, 0, H, H], "boxes": boxes}
    probs = check_layout(layout, min_px_ratio=0.0125)
    if probs:
        raise SystemExit(f"{root.name}: social preview layout failed: " + "; ".join(probs))
    info = PngInfo(); info.add_text("dm-layout", json.dumps(layout))
    im.save(root / "media/social-preview.png", optimize=True, pnginfo=info)


if __name__ == "__main__":
    for r in sys.argv[1:] or ["."]:
        try:
            make(r); print("ok", r)
        except SystemExit as e:
            print("FAIL", r, e)
        except Exception as e:
            print("FAIL", r, e)
