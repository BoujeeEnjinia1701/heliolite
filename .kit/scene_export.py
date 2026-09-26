"""Capture the Parts a repo's concept_media.py passes to render_all and save them as meshes.
Usage (from repo root): python .kit/scene_export.py out.npz
Runs concept_media.py with render_all replaced, so no media files are touched."""
import sys, json, runpy
from pathlib import Path
import numpy as np
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / ".kit")); sys.path.insert(0, str(ROOT / "cad" / "src"))
import concept
captured = {}
def fake_render_all(parts, project, title, *a, scale_figure=True, context=(), **k):
    shown = (concept.with_scale_figure(parts) if scale_figure else list(parts)) + list(context)
    captured.update(parts=shown, project=project, title=title,
                    context=[c.name for c in context] + (["Person, 1.75 m (scale)"] if scale_figure else []))
    raise SystemExit(0)
concept.render_all = fake_render_all
try:
    runpy.run_path(str(ROOT / "cad/src/concept_media.py"), run_name="__main__")
except SystemExit:
    pass
materials = {}
if (ROOT / "cad/src/render_detail.py").exists():
    import render_detail, model
    captured["parts"] = list(captured["parts"]) + render_detail.detail_parts(model.build_parts())
    materials = getattr(render_detail, "MATERIALS", {})
arrays, meta = {}, []
for i, p in enumerate(captured["parts"]):
    shapes = [p.shape]
    verts, tris = p.shape.tessellate(0.3, 0.15)
    v = np.array([[q.X, q.Y, q.Z] for q in verts], dtype=np.float32) / 1000.0  # mm to m
    arrays[f"v{i}"] = v; arrays[f"f{i}"] = np.array(tris, dtype=np.int32)
    meta.append(dict(name=p.name, color=p.color, bom=p.bom, alpha=p.alpha,
                     material=materials.get(p.name), context=p.name in captured["context"] or p.name.lower().startswith("person")))
np.savez_compressed(sys.argv[1], **arrays)
Path(sys.argv[1]).with_suffix(".json").write_text(json.dumps(dict(project=captured["project"], title=captured["title"], parts=meta), indent=1))
print(len(meta), "parts;", sum(len(arrays[f'f{i}']) for i in range(len(meta))), "triangles")
for m in meta: print(" ", m["name"], m["color"], "context" if m["context"] else "")
