# BOM notes

- Prices are indicative US retail figures for one prototype, not quotes. The NMRV030 gearbox price ($34.02) and its listed rating (17 N·m at 50:1, 1° backlash) are from the [StepperOnline listing](https://www.omc-stepperonline.com/nmrv30-worm-gearbox), checked on 2026-09-25; other lines are estimates by supplier type.
- All 17 lines are priced. The total is $451 against the $455 budget in `project.yaml` (raised from $400 to $430 by Amish on 2026-09-25, HLT-DDR-001 D4, then to $455 by a top-up he approved on 2026-09-26, HLT-DDR-002 P1), a $4 margin, so R15 is met. `docs/04-calcs/sizing.py` reads this file and prints the total [J1].
- Items 1 to 11, 14, 16 and 17 match the numbered callouts in `media/exploded.png`. Items 12 (indoor adapter), 13 (hardware) and 15 (stow reserve, inside the controller box) have no callout.
- Changes at TRL 3: drives are now NEMA17 motors on NMRV030-class 50:1 gearboxes with a listed rating, with adapter plates and shaft sleeves (lines 4 and 5); the yoke arms grew to 40 x 70 mm (line 3); the turntable carries one thrust bearing on the gearbox output (line 6); the anemometer (line 14) and supercapacitor stow reserve (line 15) were added after decisions D2 and D3.
- Changes under HLT-DDR-002 (2026-09-25, recommendations accepted by Amish): drive preload springs added (line 16, $6 for two) and the stow stop and latch added (line 17, $20: steel lug, bracket, polyurethane pad, sprung pawl, 12 V pull solenoid and MOSFET driver).
- Not included: tools, 3D printer time and shipping.
- Shared SwapCell packs are not used by HelioLite, so the portfolio rule that prices them once does not apply here.
