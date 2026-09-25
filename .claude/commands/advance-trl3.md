---
description: Advance this repo from TRL 2 to TRL 3 (only after Amish approved the TRL 2 review)
---
Work only in this repo. Read CLAUDE.md, .kit/STANDARDS.md and docs/REVIEW.md first. Only proceed if Amish has approved the TRL 2 review in this session or in $ARGUMENTS; otherwise stop and ask.

Goal: TRL 3 evidence and nothing beyond it. Deliverables:

1. CAL-001 in docs/04-calcs: sizing calculations with a script, stated assumptions, and a results table against every requirement, marking any requirement that is not met.
2. A parametric build123d model in cad/src/model.py with STEP and STL exports.
3. Drawing sheet DWG-001 at Rev P1 (general arrangement) generated with .kit/drawing.py.
4. bom/bom.csv with every line priced, and a supplier where known.
5. Refresh all concept media from the updated model (as in /populate step 3).

Then set trl: 3 and trl_target: 3 in project.yaml, with trl_evidence listing the files. Do not create test articles, test plans, firmware, PCB layouts, build procedures or purchasing lists. If the design misses a requirement, report it; do not redesign beyond TRL 3 scope. Record decisions as "Proposed, awaiting Amish". Write docs/REVIEW.md, run `python .kit/render.py --check`, commit, push, then stop.

Additional instructions from Amish: $ARGUMENTS
