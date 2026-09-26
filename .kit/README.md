# Portfolio kit (.kit)

Shared documentation and drawing kit for every Open Hardware Portfolio repo. The house rules are in [STANDARDS.md](STANDARDS.md). The version is in `KIT_VERSION`.

| File | Purpose |
| --- | --- |
| `render.py` | Checks document control and renders branded PDFs to `docs/pdf/` |
| `drawing.py` | ANSI B drawing sheets with title block and revision table (SVG, PDF, PNG) |
| `concept.py` | Concept media: hero, cutaway, exploded, blueprint sheet, 3D viewer, flow diagram |
| `photoreal.py` | Optional photoreal renders with Blender Cycles (studio or product mode) |
| `scene_export.py`, `product_export.py` | Export a repo's concept scene or `cad/src/product_model.py` for `photoreal.py` |
| `photo_caption.py` | Adds the project name, concept label, repository and view note to a render |
| `style/` | PDF template and stylesheet |
| `templates/` | Starting points for new controlled documents |
| `fonts/` | IBM Plex (SIL Open Font License, see `fonts/OFL.txt`) |

Setup: `pip install -r .kit/requirements.txt`, then run `python .kit/render.py` from the repo root.

Do not edit the kit inside a project repo. Change it once in the kit source and sync it to every repo, so all projects stay identical.

## Photoreal renders (optional, kit 1.4)

Needs Blender 4.2 or later (`pip install bpy` gives the same engine without the app). From the repo root:

```
python .kit/product_export.py /tmp/scene.npz            # or: python .kit/scene_export.py /tmp/scene.npz
python .kit/photoreal.py /tmp/scene.npz /tmp/raw.png --product --res=1600x1200 --el=32 --az=-40
python .kit/photo_caption.py /tmp/raw.png media/render-hero.png "Name: device" "View note"
```

On a Mac with Blender installed, render on the GPU (much faster):
`/Applications/Blender.app/Contents/MacOS/Blender -b -P .kit/photoreal.py -- /tmp/scene.npz /tmp/raw.png --product --gpu`
