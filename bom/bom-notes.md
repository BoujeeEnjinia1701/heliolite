# BOM notes

- Prices are indicative US retail figures for one prototype, not quotes. The NMRV030 gearbox price ($34.02) and its listed rating (17 N·m at 50:1, 1° backlash) are from the [StepperOnline listing](https://www.omc-stepperonline.com/nmrv30-worm-gearbox), checked on 2026-09-25; other lines are estimates by supplier type.
- All 15 lines are priced. The total is $425 against the $430 budget in `project.yaml` (raised from $400 by Amish on 2026-09-25, HLT-DDR-001 D4), a margin of $5. `docs/04-calcs/sizing.py` reads this file and prints the total [J1].
- Items 1 to 11 and 14 match the numbered callouts in `media/exploded.png` and drawing HLT-DWG-001. Items 12 (indoor adapter), 13 (hardware) and 15 (stow reserve, inside the controller box) have no callout.
- Changes at TRL 3: drives are now NEMA17 motors on NMRV030-class 50:1 gearboxes with a listed rating, with adapter plates and shaft sleeves (lines 4 and 5); the yoke arms grew to 40 x 70 mm (line 3); the turntable carries one thrust bearing on the gearbox output (line 6); the anemometer (line 14) and supercapacitor stow reserve (line 15) were added after decisions D2 and D3.
- Not included: drive preload springs (about $6 for two, proposed, awaiting Amish), a larger elevation gearbox or stow stops if chosen for R9, tools, 3D printer time and shipping.
- Shared SwapCell packs are not used by HelioLite, so the portfolio rule that prices them once does not apply here.
