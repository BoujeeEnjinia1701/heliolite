"""Export product_parts() from cad/src/product_model.py for .kit/photoreal.py.
Usage (repo root): python .kit/product_export.py out.npz [--explode] [--groups=shell,internal,accessory]"""
import sys, json
from pathlib import Path
import numpy as np
from build123d import Pos
ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad/src")]
import product_model
import re


def _name():
    m = re.search(r"^name:\s*(.+)$", (ROOT / "project.yaml").read_text(), re.M)
    return m.group(1).strip() if m else ROOT.name


explode = "--explode" in sys.argv
groups = None
for a in sys.argv:
    if a.startswith("--groups="): groups = a[9:].split(",")
arrays, meta = {}, []
i = 0
for p in product_model.product_parts():
    if groups and p["group"] not in groups:
        continue
    s = p["shape"]
    if explode and any(p.get("explode", (0, 0, 0))):
        s = Pos(*p["explode"]) * s
    verts, tris = s.tessellate(0.05, 0.1)
    arrays[f"v{i}"] = np.array([[q.X, q.Y, q.Z] for q in verts], dtype=np.float32) / 1000.0
    arrays[f"f{i}"] = np.array(tris, dtype=np.int32)
    meta.append(dict(name=p["name"], color=p["color"], bom=p.get("bom"), alpha=1.0,
                     material=p.get("material"), context=p["group"] == "context"))
    i += 1
np.savez_compressed(sys.argv[1], **arrays)
Path(sys.argv[1]).with_suffix(".json").write_text(json.dumps(dict(project=_name(), title="", parts=meta), indent=1))
print(i, "parts", sum(len(arrays[f"f{k}"]) for k in range(i)), "tris")
