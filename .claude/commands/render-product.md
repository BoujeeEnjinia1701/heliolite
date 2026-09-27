---
description: Build the appearance model, photoreal renders and storefront images (TRL 3, STANDARDS sections 12 and 13)
---
Read CLAUDE.md and .kit/STANDARDS.md sections 12 and 13. Build or update cad/src/product_model.py (product_parts, TITLE, RENDER_VIEWS) with every main dimension taken from cad/src/model.py; give scale with .kit/context_parts.py (hand, forearm or mannequin). Export one scene per view with .kit/export_views.py, render with .kit/photoreal.py, caption with .kit/photo_caption.py into media/render-<view>.png, and make sure the README opens with media/render-hero.png. Then run `python .kit/cards.py .`. Log appearance deviations in docs/REVIEW.md as "Proposed, awaiting Amish". Run `python .kit/render.py --check`, commit, stop.

Notes from Amish: $ARGUMENTS
