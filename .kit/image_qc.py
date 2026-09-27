"""Image quality check for renders and storefront images (STANDARDS section 13, "Image quality").

Usage, from the repo root:  python .kit/image_qc.py

Checks media/render-*.png (except *-plain.png, which carry no caption), media/card.png and
media/social-preview.png:
  - made with the current layout (layout data stored in the PNG by photo_caption.py or cards.py);
  - every line of text sits inside the image with a margin, clear of the render, and clear of every
    other line (no text over text);
  - no text below the minimum size for the image width;
  - image size: renders at least 1200 px wide, card 800 x 800, social preview 1280 x 640 and under 1 MB;
  - the render is sharp (not blurred or upscaled).
Exits non-zero if any image fails.
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from photo_caption import LAYOUT_VERSION, check_layout  # noqa: E402

SHARP_MIN = 15.0   # see sharpness(); portfolio renders measure 22 to 220, a 3 px blur about 14


def sharpness(im):
    """99.5th percentile of the absolute Laplacian at 800 px wide: high for crisp edges, low when blurred."""
    g = im.convert("L")
    g = g.resize((800, max(3, round(800 * g.size[1] / g.size[0]))), Image.LANCZOS)
    a = np.asarray(g, dtype=np.float32)
    lap = -4 * a[1:-1, 1:-1] + a[:-2, 1:-1] + a[2:, 1:-1] + a[1:-1, :-2] + a[1:-1, 2:]
    return float(np.percentile(np.abs(lap), 99.5))


def check_image(path, kind):
    probs = []
    im = Image.open(path)
    raw = im.info.get("dm-layout")
    W, H = im.size
    if not raw:
        return [f"{path.name}: made with an older layout; regenerate it (photo_caption.py or cards.py)"]
    lay = json.loads(raw)
    if lay.get("version", 0) < LAYOUT_VERSION:
        probs.append(f"{path.name}: layout version {lay.get('version')} is out of date")
    if list(lay.get("size", [])) != [W, H]:
        probs.append(f"{path.name}: stored layout does not match the image size")
    ratio = 0.0125 if kind == "social" else 0.0105
    probs += [f"{path.name}: {p}" for p in check_layout(lay, min_px_ratio=ratio)]
    if kind == "render" and W < 1200:
        probs.append(f"{path.name}: {W} px wide; renders must be at least 1200 px wide")
    if kind == "card" and (W, H) != (800, 800):
        probs.append(f"{path.name}: must be 800 x 800, is {W} x {H}")
    if kind == "social":
        if (W, H) != (1280, 640):
            probs.append(f"{path.name}: must be 1280 x 640, is {W} x {H}")
        if path.stat().st_size >= 1_000_000:
            probs.append(f"{path.name}: 1 MB or more; GitHub will refuse it")
    body = lay.get("body")
    region = im.convert("RGB").crop(tuple(body)) if body else im.convert("RGB")
    s = sharpness(region)
    if s < SHARP_MIN:
        probs.append(f"{path.name}: looks blurred (sharpness {s:.1f}, minimum {SHARP_MIN})")
    return probs


def run(root=Path(".")):
    root = Path(root)
    targets = [(p, "render") for p in sorted((root / "media").glob("render-*.png")) if not p.stem.endswith("-plain")]
    targets += [(root / "media/card.png", "card"), (root / "media/social-preview.png", "social")]
    fails, checked = [], 0
    for p, kind in targets:
        if not p.exists():
            continue
        checked += 1
        fails += check_image(p, kind)
    return fails, checked


if __name__ == "__main__":
    fails, n = run(Path("."))
    for f in fails:
        print("FAIL", f)
    print(f"{'FAIL' if fails else 'ok  '} image quality: {n} images checked, {len(fails)} problems")
    sys.exit(1 if fails else 0)
