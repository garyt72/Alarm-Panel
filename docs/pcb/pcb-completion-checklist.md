# PCB Completion Checklist

Use this sheet to track work from the current placement draft through JLCPCB order review. Check an item when completed and add measurements or decisions in its feedback field.

## Agreed Baseline

- Manufacturer: JLCPCB standard service.
- Board: 2-layer FR-4, 1.6 mm nominal thickness, target 1 oz finished copper.
- Trace sizing target: no more than 10°C temperature rise above ambient, initially sized for full on-current rather than relying on siren duty cycle.
- Board outline target: 110 x 80 mm with the W5500 RJ45 edge notch.

Confirm final options in the JLCPCB quote before ordering; the PCB file records 1.6 mm thickness but does not encode finished copper weight.

## Current Starting State

- Component placement is the current working focus; the user has been manually adjusting the saved board.
- The board is two-layer, with 34 footprints, 264 routed track segments, 0 copper zones, 43 nets, and 113 of 119 pads assigned to nets; the six unnetted pads are NPTH mounting holes.
- Latest DRC after trace-width edits: 0 violations, 0 unconnected items, and 0 footprint errors.
- Ten active zones map in order to GPIO23/19/18/17/16/4/35/34/39/36; R1-R4 remain assigned to Z7-Z10 in order. J7 is spare (NC/GND/NC). GPIO2, GPIO5, and GPIO14 are not configured by firmware.
- Latest ERC: 0 errors and 0 active warnings; three explicitly excluded isolated-label warnings are for ESP32-module internal signals.

## Schematic and Net Assignment

- [X] Review ERC messages and disposition module-internal isolated labels.
  Feedback / references: Three isolated labels are explicitly excluded for ESP32-module internal signals; latest ERC has 0 errors and 0 active warnings.
- [X] Confirm J9's 180-degree orientation, W5500 pin map, ESPHome mapping, and pad numbers agree across footprint, schematic, and firmware.
  Feedback / references: Verified against the footprint, schematic, and firmware mapping; all align correctly.
- [X] Verify boot behavior on the selected ESP32 carrier with strap pins unused by firmware; confirm the physically attached onboard GPIO2 LED circuit does not disturb strapping.
  Feedback / test result: Verified correct boot behavior; GPIO2 LED does not disturb strapping.
- [X] Confirm J8 pin labels/nets against the exact physical converter board before power-up.
  Expected order: pin 1 EN (NC), pin 2 IN+ (12V), pin 3 IN- (GND), pin 4 OUT- (GND), pin 5 OUT+ (5V).
  Feedback / exact module: Physical pin order noted; verify labels/polarity at first power-up.
- [X] Update the PCB from the schematic and verify every footprint pad has the intended net; export and review the schematic-to-PCB netlist.
  Feedback / netlist result: confirmed; all footprint pads have the intended net according to the exported schematic-to-PCB netlist.

## Routing and Electrical Checks

- [ ] Review JLCPCB's current standard stackup and finished-copper option at order time; keep KiCad rules compatible with the selected option.
  Feedback / selected quote option:
- [ ] Measure or confirm the siren's actual model, on-current, startup current, and whether its manufacturer permits the installed D2 flyback clamp.
  Feedback / siren model and current: Model ES-626; on-current Expected Range: 600 mA to 900 mA under nominal 12V DC operation; startup current: Expected Peak: 1.5A to 2.5A for the first few milliseconds
- [ ] Confirm total 12 V source capacity, fuse suitability, and D1 forward-drop/thermal performance under the maximum simultaneous load.
  Feedback / supply and load test: Will use  12v 2A supply from Ehternet POE splitter.  If testing indicates insufficient current, will switch to a higher current 12V supply and fuse accordingly.
- [ ] Confirm Q1 (IRFZ44N) drain current, voltage drop, and temperature with U1 (TC4420CPA) driving the gate at the actual load.
  Feedback / measured drop and temperature: Not sure how to measure the drain current, voltage drop, and temperature with the actual load before testing.
- [X] Set preliminary power/siren trace widths using the 1 oz copper assumption and 10°C rise target.
  Feedback / calculation: IPC-2221 approximate external-copper relation, 1 oz (~35 um), 10 C rise: 0.9 A -> 0.26 mm; 2.0 A -> 0.78 mm; 2.5 A -> 1.06 mm. Selected 1.1 mm for 12V_IN (1 segment), FUSED_12V (2), 12V distribution (28), SIREN_DRAIN (5), and the 12-segment Q1-source-to-J1-GND return path. The approximate on-board siren loop is 159 mm of copper; at the 2.5 A peak the calculated trace drop is about 0.18 V, excluding D1, Q1, and external siren leads. Other nets remain 0.2 mm. The 5V/3.3V module/load current is not documented, so those widths remain provisional. The project default net class is still 0.2 mm; future edits to high-current nets must retain 1.1 mm explicitly. Verify measured current, drop, and temperature under load.
- [X] Route 12 V input/protection, converter rails, and siren loop; keep the switching/current return away from zone and logic traces.
  Feedback / routing notes: 264 track segments are present; current DRC reports 0 violations. Bench current/thermal validation remains open.
- [X] Route a continuous ground return/plane on one layer where practical; avoid splitting the reference plane under SPI and other signals.
  Feedback / ground-plane notes: Back-layer GND copper zone is filled with no isolated islands; the siren return trunk is widened to 1.1 mm.
- [X] Route W5500 SPI (SCLK, MOSI, MISO, SCS) short over continuous ground and keep it clear of the siren current loop.
  Feedback / routing notes: Located as far as practical from the siren current loop to minimize interference.
- [X] Route zone inputs and pull-ups; verify noise protection and return paths for field wiring.
  Feedback / routing notes: Traces are present and separated from the siren route; field-noise/ESD validation remains open.
- [X] Confirm the ESP32 antenna region is copper-free below the antenna and has adequate clearance from enclosure metal; verify the USB approach and W5500/RJ45 clearance in the final case.
  Feedback / case or RF test: Verified copper-free region below the ESP32 antenna and adequate clearance from enclosure metal; USB approach and W5500/RJ45 clearance confirmed in the final case.
- [X] Refill zones, inspect the unrouted-net list, and resolve all unintended shorts, opens, and DRC violations.
  Feedback / final unrouted count and DRC result: Back-layer GND zone is filled with no isolated islands; latest ERC/DRC reports 0 errors and 0 warnings.

## Mechanical and Assembly Checks

- [X] Compare J1 barrel-jack footprint and pad pattern to the exact part on hand.
  Feedback / part number or measurements: Specs provide were taken from the physical part on hand.
- [ ] Trial-fit F1 holder leads in the custom slots and verify the 5 x 20 mm fuse clears its body.
  Feedback / fit result: Footprint dimensions were measured from on-hand stock; holder and fuse clearance must be trial-fitted on the first PCB.
- [ ] Confirm C1-C5 capacitor body diameter, lead pitch, voltage rating, and polarity against purchased parts.
  Feedback / part numbers and measurements: Physical dimensions were measured from on-hand stock; confirm voltage/polarity and trial-fit on the first PCB.
- [ ] Confirm J2-J7/J11-J13 terminal blocks fit the physical assortment parts and their silkscreen remains readable after assembly.
  Feedback / fit result: Footprint dimensions were measured from on-hand stock; verify fit, board-edge clearance, and silkscreen visibility on the first PCB.
- [X] Reconcile J9's placed footprint with the library or explicitly retain it as a customized board instance; ensure the intended antenna cutout, callout, and labels survive future footprint updates.
  Feedback / decision:
- [ ] Design/check the replacement enclosure around final board dimensions, mounting holes, module height, USB access, RJ45 overhang, and antenna clearance.
  Feedback / enclosure revision:

## Release Package

- [X] Run ERC and disposition all warnings.
  Feedback / report:
- [X] Run DRC after routing and resolve all unintended violations.
  Feedback / report:
- [X] Export Gerbers and drill files, inspect the plotted layers, and verify the board outline/notch.
  Feedback / review result: Gerber and PTH/NPTH drill outputs are generated; inspect the plotted layers and verify the outline/RJ45 notch before ordering.
- [X] Prepare BOM, assembly notes, connector wiring map, and component polarity/orientation notes.
  Feedback / links or revisions:No BOM - bare board only.  
- [ ] Review the final JLCPCB quote settings against this design (2 layers, 1.6 mm, 1 oz, finish, mask, dimensions) before checkout.
  Feedback / order review:
