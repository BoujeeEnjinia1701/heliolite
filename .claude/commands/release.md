---
description: Run the release gate and prepare a public release, REUSE and Zenodo included; never changes visibility (STANDARDS sections 14 to 17)
---
Read CLAUDE.md and .kit/STANDARDS.md sections 14 to 17. Run `python .kit/archive.py reuse` and `python .kit/archive.py zenodo` if the REUSE files, badges or a one-license CITATION.cff are missing. Run `python .kit/release_gate.py`. Fix every FAIL that is within the repo (storefront images, issue templates from .kit/templates/issue or issue-openratio, CITATION.cff, REUSE, em dashes, wording, links to private repos) and report every warning. Draft the release notes and list the design pack contents. Commit the fixes and stop. Do not tag, publish a release, change settings, switch the repository on in Zenodo or make the repository public: Amish approves and runs the release. Remind Amish of the Zenodo switch and, after the release, the concept DOI and Software Heritage steps.

Notes from Amish: $ARGUMENTS
