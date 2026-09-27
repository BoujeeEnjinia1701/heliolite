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
| `export_views.py`, `context_parts.py` | One scene per `RENDER_VIEWS` entry; scale context (hand, forearm, posed mannequin) |
| `cards.py` | Storefront images: `media/card.png` and `media/social-preview.png` from the hero render |
| `image_qc.py` | Image quality: caption text inside the image, never overlapping, readable size, sharp renders |
| `release_gate.py` | Checks a repo is ready to go public (STANDARDS section 14) |
| `style/` | PDF template and stylesheet |
| `templates/` | Starting points for new controlled documents; `templates/issue/` and `templates/issue-openratio/` hold the GitHub issue templates |
| `fonts/` | IBM Plex (SIL Open Font License, see `fonts/OFL.txt`) |

Setup: `pip install -r .kit/requirements.txt`, then run `python .kit/render.py` from the repo root.

Do not edit the kit inside a project repo. Change it once in the kit source and sync it to every repo, so all projects stay identical.

## Photoreal renders (kit 1.4, required at TRL 3 from kit 1.5)

Needs Blender 4.2 or later (`pip install bpy` gives the same engine without the app). From the repo root:

```
python .kit/product_export.py /tmp/scene.npz            # or: python .kit/scene_export.py /tmp/scene.npz
python .kit/photoreal.py /tmp/scene.npz /tmp/raw.png --product --res=1600x1200 --el=32 --az=-40
python .kit/photo_caption.py /tmp/raw.png media/render-hero.png "Name: device" "View note"
```

On a Mac with Blender installed, render on the GPU (much faster):
`/Applications/Blender.app/Contents/MacOS/Blender -b -P .kit/photoreal.py -- /tmp/scene.npz /tmp/raw.png --product --gpu`

## Storefront and release (kit 1.5)

```
python .kit/cards.py .            # media/card.png and media/social-preview.png
python .kit/image_qc.py           # renders, card and social preview are clear and readable
python .kit/release_gate.py       # must pass before a repo goes public
```

Issue templates are copied into `.github/ISSUE_TEMPLATE/` from `templates/issue/` (OpenRatio: `templates/issue-openratio/`).

