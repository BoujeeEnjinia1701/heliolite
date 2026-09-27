---
description: Run the release gate and prepare a public release; never changes visibility (STANDARDS section 14)
---
Read CLAUDE.md and .kit/STANDARDS.md section 14. Run `python .kit/release_gate.py`. Fix every FAIL that is within the repo (storefront images, issue templates from .kit/templates/issue or issue-openratio, CITATION.cff, em dashes, wording, links to private repos) and report every warning. Draft the release notes and list the design pack contents. Commit the fixes and stop. Do not tag, publish a release, change settings or make the repository public: Amish approves and runs the release.

Notes from Amish: $ARGUMENTS
