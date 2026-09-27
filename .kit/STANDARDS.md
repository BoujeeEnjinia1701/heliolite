---
doc_id: OHP-STD-001
title: Documentation and drawing standard
project: Open Hardware Portfolio
doc_type: Standard
version: "1.5"
status: Released
date: 2026-09-27
author: Amish Chadha
license: CC-BY-SA-4.0
revisions:
  - version: "1.0"
    date: 2026-09-24
    author: Amish Chadha
    change: First release of the standard
  - version: "1.1"
    date: 2026-09-24
    author: Amish Chadha
    change: Adopt Technology Readiness Levels (section 9) for project maturity
  - version: "1.2"
    date: 2026-09-24
    author: Amish Chadha
    change: Portfolio phase cap (section 10), concept media standard (section 11), CLAUDE.md guardrails
  - version: "1.3"
    date: 2026-09-24
    author: Amish Chadha
    change: Scale figure, interactive 3D viewer and flow diagrams added to concept media; session slash commands
  - version: "1.4"
    date: 2026-09-26
    author: Amish Chadha
    change: Every sheet and render names the project and its GitHub repository; overall dimensions, ISO centre lines and 300 dpi PNG on sheets; titles name the device and view labels state the viewing direction; optional photoreal renders with Blender
  - version: "1.5"
    date: 2026-09-27
    author: Amish Chadha
    change: Product renders (section 12), storefront images and image quality check (section 13), public release and release gate (section 14), authorship, citation and commit signing (section 15)
---

# Documentation and drawing standard

Every project in the portfolio uses this standard, so that each precis, write-up and sketch looks the same and carries its own version history. The standard ships as a kit in each repo's `.kit/` folder. The kit version is in `.kit/KIT_VERSION`.

## 1. Document types and IDs

Every controlled document has a unique ID in the form `PRJ-TYP-NNN`.

- `PRJ` is the three-letter project code listed in section 7.
- `TYP` is the document type code from the table below.
- `NNN` is a sequence number within that project and type, starting at 001.

| Code | Type | Typical file |
| --- | --- | --- |
| PRC | Design precis | `docs/02-concept.md` |
| PRB | Problem statement | `docs/01-problem.md` |
| REQ | Requirements | `docs/03-requirements.md` |
| CAL | Calculation or sizing note | `docs/04-calcs/*.md` |
| DDR | Design decision record | `docs/decisions/*.md` |
| BOM | Bill of materials | `bom/bom.csv` |
| DWG | Drawing or sketch sheet | `cad/drawings/*.svg` |
| TST | Test plan or test report (front matter adds `environment: lab` or `relevant`) | `docs/05-tests/*.md` |

Example: `TBK-PRC-001` is the ThermaBrick design precis.

## 2. Revision scheme

| Artifact | While in draft | When released | Change after release |
| --- | --- | --- | --- |
| Documents | 0.1, 0.2, 0.3 ... | 1.0 | 1.1 for minor edits, 2.0 for a design change |
| Drawings | Rev P1, P2 ... (preliminary) | Rev A | Rev B, C ... |

- Every change to a controlled document adds a row to its revision history before the commit.
- The `version` field in front matter always equals the newest row in `revisions`. The renderer rejects a document where they differ.
- Status is one of `Draft`, `In review`, `Released` or `Superseded`. Draft and In review documents print with a status band on every page.
- Every release is tagged in Git as `<doc_id>/v<version>`, for example `TBK-PRC-001/v1.0`. Drawings are tagged `TBK-DWG-001/revA`.
- Git history is the full audit trail. The in-document revision table is the human-readable summary.

## 3. Document front matter

Every Markdown document under version control starts with this block:

```yaml
---
doc_id: TBK-PRC-001
title: ThermaBrick design precis
project: ThermaBrick
doc_type: Precis
version: "0.1"
status: Draft
date: 2026-09-24
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
  - version: "0.1"
    date: 2026-09-24
    author: Amish Chadha
    change: Initial draft
---
```

Quote version numbers so YAML keeps `1.0` as text instead of turning it into a number. List revisions newest last.

## 4. Writing style

- Chicago Manual of Style.
- No em dashes. Restructure the sentence instead.
- Lead each section with its conclusion, then support it.
- SI units throughout, in the form `12 kW`, `450 °C`, `3.2 m`. Imperial values may follow in parentheses.
- Number every figure and table ("Figure 2", "Table 1") and give each a caption.
- State every assumption in the calculation that depends on it.
- Put safety notes in a blockquote starting with **Safety:**.

## 5. Visual identity

| Element | Specification |
| --- | --- |
| Typeface | IBM Plex Sans for text, IBM Plex Mono for code and values (SIL Open Font License, bundled in `.kit/fonts`) |
| Ink | `#111827` |
| Secondary text | `#4B5563` |
| Rules and grid | `#D1D5DB` |
| Accent (one only) | `#0F766E` teal |
| Document page | US Letter, 20 mm margins |
| Drawing sheet | ANSI B landscape (431.8 x 279.4 mm) |
| Footer | Document ID, version, status, license and designmolecule.com on every page |

## 6. Drawing and sketch conventions

- Units are millimeters unless the title block says otherwise.
- Third-angle projection, marked with the symbol in the title block.
- Line weights: visible outlines 0.5 mm, hidden lines 0.25 mm dashed, center lines 0.18 mm chain.
- The title block contains the project, title, drawing number, revision, scale, units, projection, sheet, author, date, material or notes, and license.
- Every sheet and every render names the project and its GitHub repository (from `repo:` in `project.yaml`), at the top of the sheet and in the title block, so a printed or forwarded sheet is never anonymous.
- The drawing title names the device, not only the drawing type (for example "Handheld near-infrared resin scanner: general arrangement").
- Every view label states its scale and viewing direction (for example "Scale 1:1; side elevation looking along +Y"), and every isometric or render states where it is seen from.
- Orthographic views generated with `add_ortho` carry overall dimensions (length and depth on the top view, height on the front view) and ISO 128 centre lines on cylinders; hidden lines are dashed. Tolerances are not shown before TRL 4.
- Sheets are exported as SVG, PDF and a 300 dpi PNG.
- The revision table in the top right of the sheet lists every revision.
- Concept sketches use the same sheet and title block and carry the label "CONCEPT, NOT FOR FABRICATION".
- Geometry comes from `cad/src/*.py` (build123d). Sheets are generated by `.kit/drawing.py` and never edited by hand.

## 7. Project codes

| Code | Project | Code | Project | Code | Project |
| --- | --- | --- | --- | --- | --- |
| TBK | ThermaBrick | PCF | PicoFlow | HLT | HelioLite |
| CCB | CharCube | DRN | DustRunner | TRT | TremorTrace |
| STC | StepCue | FXH | FlexHand | CPD | ColdPod |
| SCL | SunClave | STR | SteamRoot | GGD | GrainGuard |
| SDL | SeedLine | ZBX | ZeerBox | RMS | RootMesh |
| DWD | DewDrive | SSK | StillStack | PPR | PotPress |
| WWT | WaterWatch | LMF | LumaFlow | FCL | FieldCell |
| CNP | ConePro | CVC | CulvertCrawl | EGD | EmberGuard |
| SNF | SnapFrame | CGM | CargoMule | SCM | StepClimber |
| SWC | SwapCell | PLP | PalletPilot | FTK | FlatTrike |
| WWK | WaterWalker | GRR | GrowRider | SSP | SunSpoke |
| SGN | StepGen | PBX | PowerBox | WML | WasteWise-ml |
| WSC | WasteWise Scan | RFE | ReflowEconomy | | |
| OHP | Portfolio-wide | | | | |

## 8. Build and publish

- `python .kit/render.py` checks every controlled document and renders it to `docs/pdf/<doc_id>_v<version>.pdf`.
- `python .kit/drawing.py` (called from each project's `cad/src/sheets.py`) builds drawing sheets as SVG and PDF in `cad/drawings/`.
- The GitHub Action in `.github/workflows/docs.yml` runs the checks on every push and attaches PDFs to a GitHub Release whenever a release tag is pushed.
- Public releases follow section 14: `python .kit/release_gate.py` must pass, and the release tag is `v0.<TRL>.0` (for example `v0.3.0` at TRL 3).

## 9. Technology Readiness Level (TRL)

Each project states its maturity as a Technology Readiness Level on the NASA and US DOE 1 to 9 scale. The TRL rates this specific design, not the underlying technology. A sand battery is commercial elsewhere, but a new sand battery design starts at TRL 2 until evidence shows otherwise.

| TRL | Definition | Evidence the repo must contain |
| --- | --- | --- |
| 1 | Basic principles observed | Problem statement (PRB) |
| 2 | Technology concept formulated | Draft precis (PRC) and requirements (REQ) |
| 3 | Analytical or experimental proof of concept | Calculation note (CAL), working build123d model with STEP export, drawing sheet (DWG), priced BOM with every unit cost filled in |
| 4 | Components validated in the lab | Test report (TST) with `environment: lab`, build log entries |
| 5 | Validated in a relevant environment | Test report (TST) with `environment: relevant` |
| 6 | System prototype demonstrated in a relevant environment | Precis at version 1.0 or later with status Released, a drawing at a lettered revision (Rev A or later), and a system-level TST with `environment: relevant` |
| 7 to 9 | Operational demonstration through proven in service | Beyond portfolio scope; claim only with a named deployment partner and evidence |

Rules:

- `project.yaml` records `trl` (current level), `trl_target` (the level the current effort aims for) and `trl_evidence` (the files that support the claim).
- `python .kit/render.py --check` fails if the evidence for the claimed TRL is missing. CI runs this check on every push.
- Documentation alone cannot go past TRL 3. TRL 4 and above require hardware and a test report.
- TRL and visibility are independent. A repo can be public at TRL 3 as a documented design ready to build.
- A change of TRL is recorded in the build log with the date and the evidence that justified it.

## 10. Portfolio phase and TRL cap

`.kit/PHASE.yaml` sets the current phase. During the **populate** phase every repo is capped at **TRL 3**: `trl` and `trl_target` may not exceed 3, and the check fails if they do. Work that belongs to TRL 4 or later (test articles, test plans and reports, build procedures, purchasing lists, PCB layouts) must not be started. Where it already exists it is kept, flagged in the check output, and not extended. Only Amish changes `PHASE.yaml`.

Every repo carries a `CLAUDE.md` with the working rules for AI sessions: the TRL cap, decision rights (nothing is recorded as decided unless Amish decided it), one step per session, and a mandatory `docs/REVIEW.md` before stopping.

## 11. Concept media

Every repo at TRL 2 or above explains its idea visually. Media are generated from a build123d massing model with `.kit/concept.py`, never drawn by hand, so they stay in step with the design.

| File | Required | Purpose |
| --- | --- | --- |
| `media/hero.png` | TRL 2+ | Shaded isometric render with a 1.75 m person for scale; the website card image |
| `media/concept-blueprint.png` and `.pdf` | TRL 2+ | Blueprint concept sheet: orthographic and isometric views, scale, key figures, title block |
| `media/model.glb` and `media/viewer.html` | TRL 2+ | Interactive 3D viewer (glTF plus model-viewer) for the website |
| `media/cutaway.png` | When the inside matters | Section view showing internal parts |
| `media/exploded.png` | Recommended | Exploded view with numbered callouts matching the BOM |
| `media/flow.png` | When energy or material moves | System, energy or material flow diagram with losses |

Session commands in `.claude/commands/` (`/populate`, `/advance-trl3`, `/rein-in`, `/refresh-media`) carry the standard prompts, so every Claude Code session starts from the same instructions.

At TRL 2 a massing model is enough: correct overall proportions and main components. All concept media carry "CONCEPT, NOT FOR FABRICATION". The check warns when required media are missing at TRL 2 and fails at TRL 3.

## 12. Product renders

Every repo at TRL 3 shows the product as it would look, not only as a massing model.

- `cad/src/product_model.py` is the appearance model. It defines `product_parts()` (named parts with a shape and a material), `TITLE` ("Name: what it is") and `RENDER_VIEWS`. It is for renders only: every main dimension comes from `cad/src/model.py`, never typed in again.
- Where the appearance model departs from `model.py` (a chamfer, a label, a fastener drawn for realism), record the deviation in `docs/REVIEW.md` as "Proposed, awaiting Amish".
- Scale comes from context, not from a floating figure: a hand or forearm for handheld objects, and the posed mannequin (`mannequin()` in `.kit/context_parts.py`: stand, walk, push, ride, sit, reach) for anything a person uses at body scale.
- Renders are made with `.kit/export_views.py` (one scene per view) and `.kit/photoreal.py` (Blender Cycles), then captioned with `.kit/photo_caption.py`. Files are `media/render-<view>.png`; `media/render-hero.png` is required.
- Every caption names the project, the repository and the viewing direction, and carries "CONCEPT, NOT FOR FABRICATION".
- Captions never sit on the render. `.kit/photo_caption.py` adds a header band (title, concept label, repository) above the render and a footer band (view note) below it, wraps every line to the image width, and steps the font down to a floor before adding a line.
- The README opens with `media/render-hero.png`.
- Software-only and scene repositories (no single product) may use a scene render as the hero instead of a product model.

## 13. Storefront images

Two images, both made from `media/render-hero.png` by `python .kit/cards.py .`:

| File | Size | Purpose |
| --- | --- | --- |
| `media/card.png` | 800 x 800 | Square thumbnail for the organization profile page |
| `media/social-preview.png` | 1280 x 640, under 1 MB | GitHub social preview, shown when a repository link is shared |

- The social preview shows the area, name, one-line description, the first sentence of the pitch, the brand line and the repository address. Design Molecule repos read "Design Molecule · open hardware concept, TRL n"; OpenRatio repos read "OpenRatio · research and educational prototype, TRL n".
- GitHub has no API for the social preview. Upload it under the repository's Settings, Social preview, on release day.
- Regenerate both images whenever `render-hero.png` changes.

### Image quality

Every render, card and social preview must be clear and readable. `python .kit/image_qc.py` checks each one, and the release gate blocks on any failure:

| Check | Rule |
| --- | --- |
| Layout | Made by the current `photo_caption.py` or `cards.py`, which store the text layout in the PNG |
| Text inside the image | Every line at least 1.2 % of the image width from each edge; nothing runs off the side |
| No overlap | No line of text touches another line, and no caption text sits on the render |
| Text size | Render captions at least 1.05 % of the image width in pixel height (17 px at 1600 px); social preview text at least 16 px |
| Resolution | Renders at least 1200 px wide; card 800 x 800; social preview 1280 x 640 and under 1 MB |
| Sharpness | The render is not blurred or upscaled (edge sharpness at least 15 on the `image_qc.py` scale) |

Long titles and notes wrap to more lines rather than shrinking below the floor. The social preview shortens the pitch sentence with an ellipsis only if it cannot fit at the smallest size.

## 14. Public release

A repository goes public only when Amish approves it, and only after `python .kit/release_gate.py` passes. The gate checks:

1. `render.py --check` passes (document control, TRL cap, concept media).
2. Storefront: hero render, card, social preview under 1 MB, README leading with the hero, and every image passing the image quality check (section 13).
3. Issue templates in `.github/ISSUE_TEMPLATE/`: question, build report, design suggestion. The build report template restates that the design is a TRL 3 concept, not released for fabrication (OpenRatio: a research and educational prototype, not a medical device).
4. `CITATION.cff` valid, with an author ORCID.
5. License files match `project.yaml`.
6. No em dashes in the repository's own text.
7. BioMedical and OpenRatio repos use soft, non-clinical wording: "research and educational prototype, not a medical device".
8. No secrets anywhere in the history (gitleaks).
9. No links to sibling repositories that are still private.

It warns, without blocking, when the README lacks a Safety heading or a "not for fabrication" statement, so a person can confirm.

On release day, per repository:

- A signed, annotated tag `v0.<TRL>.0` on `main`.
- A GitHub release with short notes (what it is, TRL, status, licenses, how to cite) and a design pack, `<repo>-v0.<TRL>.0-design-pack.zip`, holding `cad/step`, `cad/drawings`, `docs/pdf`, `bom`, README, licenses and `CITATION.cff`.
- Description from the first sentences of `pitch` (350 characters at most), website `https://designmolecule.com` (OpenRatio: `https://openratio.ai`), topics from `project.yaml`.
- Visibility switched to public last, after the release exists.
- The social preview uploaded and the organization profile updated with the new cards.

The internal working files (`CLAUDE.md`, `.kit/CLAUDE.md`, `.claude/commands/`, `docs/REVIEW.md`) stay public, and open "Proposed, awaiting Amish" items stay visible as open questions (Amish, 2026-09-27). No Zenodo DOI at this stage.

## 15. Authorship, citation and signing

- Amish Chadha is the author of every design, ORCID 0009-0000-8079-7141. Commits are authored as Amish Chadha <amish@designmolecule.com>.
- `CITATION.cff` lists Amish (with ORCID) first, then any credited contributors; `CONTRIBUTORS.md` and the README Credits section agree with it.
- Work done with Claude carries the trailer `Co-Authored-By: Claude <noreply@anthropic.com>` (with the model name), and the README Credits section says designs are developed with AI assistance.
- Every commit and tag pushed to GitHub is signed with Amish's SSH signing key, so GitHub shows it as Verified. Commits prepared elsewhere are re-signed on Amish's Mac before they are pushed.
- Once a repository is public, its history is never rewritten.

