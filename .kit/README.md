# Portfolio kit (.kit)

Shared documentation and drawing kit for every Open Hardware Portfolio repo. The house rules are in [STANDARDS.md](STANDARDS.md). The version is in `KIT_VERSION`.

| File | Purpose |
| --- | --- |
| `render.py` | Checks document control and renders branded PDFs to `docs/pdf/` |
| `drawing.py` | ANSI B drawing sheets with title block and revision table (SVG, PDF, PNG) |
| `style/` | PDF template and stylesheet |
| `templates/` | Starting points for new controlled documents |
| `fonts/` | IBM Plex (SIL Open Font License, see `fonts/OFL.txt`) |

Setup: `pip install -r .kit/requirements.txt`, then run `python .kit/render.py` from the repo root.

Do not edit the kit inside a project repo. Change it once in the kit source and sync it to every repo, so all 25 projects stay identical.
