---
description: Populate this repo to a strong TRL 2 with concept media (current portfolio phase)
---
Work only in this repo. Read CLAUDE.md, .kit/STANDARDS.md and project.yaml first and follow them. Use the three-letter project code from the document IDs in docs/.

Goal: a strong TRL 2, meaning the concept is clearly formulated and visualized. Deliverables, and nothing else:

1. Update the problem statement (PRB-001: problem, users, context, constraints; keep any co-design checklist) and requirements (REQ-001: numbered, measurable requirements with targets).
2. Update the design precis (PRC-001): how it works, main components, key design choices, first-order numbers with stated assumptions, safety section, open questions.
3. Write a massing model in cad/src/concept_media.py (correct proportions and main parts only, each part a concept.Part with a BOM number) and call .kit/concept.py render_all to generate: media/hero.png with the 1.75 m scale figure, media/concept-blueprint.png and .pdf, media/model.glb and media/viewer.html (interactive 3D viewer), media/cutaway.png if the inside matters, media/exploded.png with BOM callouts, and media/flow.png (system, energy or material flow) where the concept moves energy or material. Label any flow values that are estimates.
4. Update bom/bom.csv with main components and indicative costs. Keep project.yaml budget_usd within the concept budget; if it must rise, propose it, never accept it.

Keep trl: 2 and trl_target: 3. Do not start TRL 3 work (detailed calculations, detailed CAD, drawing sheets) or any TRL 4 work. Record every decision as "Proposed, awaiting Amish". Write docs/REVIEW.md (what was done, results, requirements not met, proposed decisions, safety concerns, recommended next step). Run `python .kit/render.py --check`, commit, push, then stop.

Additional instructions from Amish, if any: $ARGUMENTS
