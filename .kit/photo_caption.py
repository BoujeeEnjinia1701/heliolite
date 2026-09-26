"""Caption a photoreal render: project name, concept label, repository and a view note.
Usage (repo root): python .kit/photo_caption.py raw.png out.png "Title" "Note on the view" [--fonts .kit/fonts]
The repository line comes from project.yaml ('repo: owner/name')."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

raw, out, project, note = sys.argv[1:5]
fonts = Path(sys.argv[sys.argv.index("--fonts") + 1]) if "--fonts" in sys.argv else Path(".kit/fonts")
im = Image.open(raw).convert("RGB")
W, H = im.size
u = W / 1280
d = ImageDraw.Draw(im, "RGBA")
semi = ImageFont.truetype(str(fonts / "IBMPlexSans-SemiBold.ttf"), int(26 * u))
med = ImageFont.truetype(str(fonts / "IBMPlexSans-Medium.ttf"), int(14 * u))
reg = ImageFont.truetype(str(fonts / "IBMPlexSans-Regular.ttf"), int(15 * u))
pad = int(26 * u)
d.text((pad, pad), project, font=semi, fill=(17, 24, 39))
d.text((pad, pad + int(38 * u)), "CONCEPT, NOT FOR FABRICATION", font=med, fill=(180, 83, 9))
d.text((pad, H - pad - int(18 * u)), note, font=reg, fill=(55, 65, 81))
import re
try:
    m = re.search(r"^repo:\s*[\"']?([\w.-]+/[\w.-]+)", Path("project.yaml").read_text(), re.M)
except OSError:
    m = None
if m:
    mono = ImageFont.truetype(str(fonts / "IBMPlexMono-Regular.ttf"), int(14 * u))
    ref = f"github.com/{m.group(1)}"
    d.text((W - pad - d.textlength(ref, font=mono), pad + int(8 * u)), ref, font=mono, fill=(15, 118, 110))
im.save(out, optimize=True)
print("wrote", out, im.size)
