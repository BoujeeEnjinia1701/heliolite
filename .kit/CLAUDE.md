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

Every repo needs visuals that explain the idea. Generate them from `cad/src/` with `.kit/concept.py`:

| File | What it shows |
| --- | --- |
| `media/concept-blueprint.png` (+ `.pdf`) | Blueprint-style concept sheet: views, key dimensions, callouts |
| `media/hero.png` | Shaded isometric render for the website card |
| `media/cutaway.png` | Section view when the inside matters (storage, flow, mechanisms) |
| `media/exploded.png` | Exploded view with numbered callouts matching the BOM |

At TRL 2 the model may be a simple massing model: correct proportions and main parts, not detailed geometry. Label concept media "CONCEPT, NOT FOR FABRICATION".

## 6. Standards

- Follow `.kit/STANDARDS.md` (document IDs, versions, revision history, TRL evidence).
- Chicago Manual of Style. **Never use em dashes.** Restructure the sentence instead.
- SI units, with imperial in parentheses where useful.
- Safety notes stay in every document that describes something hazardous. Mains voltage, high temperature, pressure, lithium cells and moving machinery always get a safety section.
- Run `python .kit/render.py --check` before committing. Do not commit if it fails.
