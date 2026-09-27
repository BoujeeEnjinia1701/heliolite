"""Export every view in cad/src/product_model.py RENDER_VIEWS for .kit/photoreal.py.

Run from the repo root:  python .kit/export_views.py OUTDIR
Writes OUTDIR/<repo>__<view>.npz (+ .json) and OUTDIR/<repo>__jobs.json, which lists the
photoreal.py arguments and caption text for each view. product_parts() is built once.
"""
import sys, json, re
from pathlib import Path
import numpy as np
from build123d import Pos

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad/src")]
import product_model as pm

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
repo = ROOT.name
parts = pm.product_parts()
cache = {}


def mesh(i, p, explode):
    key = (i, explode)
    if key not in cache:
        s = p["shape"]
        if explode and any(p.get("explode", (0, 0, 0))):
            s = Pos(*p["explode"]) * s
        v, t = s.tessellate(0.05, 0.1)
        cache[key] = (np.array([[q.X, q.Y, q.Z] for q in v], dtype=np.float32) / 1000.0, np.array(t, dtype=np.int32))
    return cache[key]


jobs = []
for view in pm.RENDER_VIEWS:
    arrays, meta = {}, []
    for i, p in enumerate(parts):
        if p["group"] not in view.get("groups", ["shell", "internal", "context"]):
            continue
        v, f = mesh(i, p, view.get("explode", False))
        k = len(meta)
        arrays[f"v{k}"], arrays[f"f{k}"] = v, f
        meta.append(dict(name=p["name"], color=p["color"], bom=p.get("bom"), alpha=1.0,
                         material=p.get("material"), context=p["group"] == "context"))
    stem = f"{repo}__{view['name']}"
    np.savez_compressed(out / f"{stem}.npz", **arrays)
    (out / f"{stem}.json").write_text(json.dumps(dict(project=pm.TITLE, title=view["name"], parts=meta), indent=1))
    jobs.append(dict(repo=repo, view=view["name"], npz=f"{stem}.npz",
                     args=["--product", "--res=1600x1200", f"--el={view.get('el', 30)}", f"--az={view.get('az', -40)}"],
                     title=pm.TITLE if view["name"] == "hero" else f"{pm.TITLE.split(':')[0]}: {view['name'].replace('-', ' ')}",
                     note=view.get("note", "")))
    print(stem, len(meta), "parts", sum(len(arrays[f'f{k}']) for k in range(len(meta))), "tris")
(out / f"{repo}__jobs.json").write_text(json.dumps(jobs, indent=1))
