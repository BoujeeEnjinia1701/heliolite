---
description: Take a scaffolded repo from TRL 1 or 2 to TRL 3 in one run (populate, advance, build plan), then stop for Amish's review
---
Work only in this repo. Read CLAUDE.md, .kit/STANDARDS.md and project.yaml first. Every repo targets TRL 3 (STANDARDS section 10), so run the whole path in one session:

1. Do everything /populate asks (.claude/commands/populate.md), without stopping at its end.
2. Then do everything /advance-trl3 asks (.claude/commands/advance-trl3.md), including the prototype build plan BLD-001. Amish's go for this command counts as the TRL 2 approval that /advance-trl3 needs.

Record every design choice as "Proposed, awaiting Amish". Set trl: 3 and trl_target: 3 with trl_evidence listing the files. Write docs/REVIEW.md with a TRL 2 section and a TRL 3 section (results, requirements not met, proposed decisions, build plan findings, safety concerns). Run `python .kit/render.py --check`, commit, push, then stop for Amish's review.

Additional instructions from Amish: $ARGUMENTS
