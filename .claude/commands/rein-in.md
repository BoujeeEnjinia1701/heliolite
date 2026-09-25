---
description: Stop scope creep and write a review of everything done since the last review
---
Stop adding new scope. Create no new documents, hardware, electronics or firmware.

1. Write docs/REVIEW.md summarizing everything built since the last reviewed commit (or since $ARGUMENTS), every decision recorded on Amish's behalf, and every open issue, including requirements not met, budget changes and safety concerns.
2. Change any "accepted" or "approved" decision that Amish did not explicitly make to "Proposed, awaiting Amish".
3. Mark anything optional as deferred.
4. Set trl to the level the evidence supports and trl_target to no more than the cap in .kit/PHASE.yaml. Keep work beyond the cap, but frozen.

Run `python .kit/render.py --check`, commit, push, then stop and wait for Amish's review.
