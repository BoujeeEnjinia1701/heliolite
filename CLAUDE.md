# Instructions for Claude working in this repo

This repo is one design in Amish Chadha's Open Hardware Portfolio. These rules apply to every session and override any broader instruction in a prompt. If a prompt conflicts with them, stop and ask.

## 1. Current portfolio phase: TRL cap 3

- The whole portfolio is capped at **TRL 3** (proof of concept on paper) until every repo is populated. The cap is set in `.kit/PHASE.yaml`.
- Do **not** create TRL 4 or later work: no test articles, build procedures, cut lists, purchasing checklists, test plans or reports (TST), PCB layouts or Gerbers, firmware beyond a clearly labeled sketch, or build-log tooling.
- `trl` and `trl_target` in `project.yaml` must not exceed the cap. `python .kit/render.py --check` enforces this.
- If the design looks ready for TRL 4, write that up as a recommendation in the review note (section 4) and stop.

## 2. Decision rights

- Amish makes all decisions on scope, budget, naming, visibility, safety trade-offs and anything that changes the pitch.
- Never record a decision as made, accepted or approved unless Amish stated it in this session. Record it as **"Proposed, awaiting Amish"** with the options and a recommendation.
- Never raise a budget past the figure in `project.yaml` without flagging it as proposed.

## 3. Scope of a session

- Do exactly what the prompt asks, in the order asked. Do not add deliverables the prompt did not name.
- Optional ideas go in the review note as suggestions, not into the repo.
- Keep each session to one TRL step for one repo.

## 4. End every session with a review note

Write or update `docs/REVIEW.md` before the final commit:

- What was done, with file paths
- Key results and numbers, including any requirement that is **not** met
- Decisions proposed and awaiting Amish
- Safety concerns
- Recommended next step

Then commit, push and **stop**. Do not continue into the next step without a new instruction.

## 5. Required concept media (all repos, TRL 2 and up)

Every repo needs visuals that explain the idea. Generate them from `cad/src/concept_media.py` with `.kit/concept.py` (`render_all`):

| File | What it shows | When |
| --- | --- | --- |
| `media/hero.png` | Shaded isometric render with a 1.75 m person for scale; the website card | Always |
| `media/concept-blueprint.png` (+ `.pdf`) | Blueprint concept sheet: views, scale, key figures | Always |
| `media/model.glb` + `media/viewer.html` | Interactive 3D viewer for the website | Always |
| `media/cutaway.png` | Section view | When the inside matters |
| `media/exploded.png` | Exploded view with numbered callouts matching the BOM | Recommended |
| `media/flow.png` | System, energy or material flow diagram | When the concept moves energy or material |

For small objects (wearables, handheld tools) use a context part such as a hand or forearm instead of the 1.75 m person (`scale_figure=False, context=[...]`); see `tremortrace` for a worked example. At TRL 2 the model may be a simple massing model: correct proportions and main parts, not detailed geometry. Label concept media "CONCEPT, NOT FOR FABRICATION". Mark estimated flow values as estimates.

## 5a. Session commands

Use the repo's slash commands rather than improvising scope: `/populate` (strong TRL 2 with media), `/advance-trl3` (only after Amish approves), `/rein-in` (stop and review), `/refresh-media`, `/render-product` (appearance model, photoreal renders and storefront images), `/release` (release gate and release preparation; never makes the repo public).

## 5b. Product renders and storefront images (TRL 3)

- Build `cad/src/product_model.py` (`product_parts()`, `TITLE`, `RENDER_VIEWS`) with every main dimension taken from `cad/src/model.py`. Record any appearance deviation in `docs/REVIEW.md` as "Proposed, awaiting Amish".
- Give scale with `.kit/context_parts.py`: a hand or forearm for small objects, `mannequin()` for body-scale products. Never render a floating person.
- Render with `.kit/export_views.py` and `.kit/photoreal.py`, caption with `.kit/photo_caption.py`, and lead the README with `media/render-hero.png`.
- Then run `python .kit/cards.py .` for `media/card.png` and `media/social-preview.png`. See `.kit/STANDARDS.md` sections 12 and 13.
- Run `python .kit/image_qc.py` and look at every image yourself. Text must be inside the image, never overlap other text or the render, and be readable; renders must be sharp. Fix and regenerate anything that fails.

## 6. Standards

- Follow `.kit/STANDARDS.md` (document IDs, versions, revision history, TRL evidence).
- Chicago Manual of Style. **Never use em dashes.** Restructure the sentence instead.
- SI units, with imperial in parentheses where useful.
- Safety notes stay in every document that describes something hazardous. Mains voltage, high temperature, pressure, lithium cells and moving machinery always get a safety section.
- Run `python .kit/render.py --check` before committing. Do not commit if it fails.

## 7. Release and authorship

- Making a repository public, tagging a release or changing repository settings is Amish's decision. Prepare, then ask.
- Before any release, `python .kit/release_gate.py` must pass (`.kit/STANDARDS.md` section 14). Fix what fails; report warnings.
- Author commits as Amish Chadha <amish@designmolecule.com> with a `Co-Authored-By: Claude` trailer. Commits must reach GitHub signed with Amish's key (Verified). Never rewrite history once a repository is public.
- Keep `CITATION.cff` (Amish first, ORCID 0009-0000-8079-7141), `CONTRIBUTORS.md` and the README Credits section in agreement.
- OpenRatio and BioMedical repos: soft, non-clinical wording only ("research and educational prototype, not a medical device").

