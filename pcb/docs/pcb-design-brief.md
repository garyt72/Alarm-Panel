# PCB Design Brief From Perfboard Prototype

This document translates the current perfboard prototype into a production PCB plan.
It is based on:

- [devices/alarm-panel-oled.yaml](../../devices/alarm-panel-oled.yaml)
- photos in [images/](../../images/)

It captures what is already known, what is inferred, and what still needs confirmation before final manufacturing output (Gerbers, drill files, pick-and-place, and BOM).

## Known Mechanical Constraints

The existing [3d/Alarm Panel OLED case.stl](../../3d/Alarm%20Panel%20OLED%20case.stl) and [3d/Drawing.png](../../3d/Drawing.png) are historical references only; the enclosure will be redesigned around the finalized PCB.

Confirmed PCB target:

- Current board target: 110 mm (X) x 80 mm (Y), including the W5500 RJ45 edge notch. Design the new enclosure around this PCB.
- Mounting hole centers: 2 mm inset from each board edge at all four corners.
- Mounting hole diameter: 2 mm.
- Mounting holes: non-plated (NPTH).

Suggested PCB coordinate definition for layout:

- Origin at top-left board corner.
- Top-left hole center: X=2, Y=2.
- Top-right hole center: X=108, Y=2.
- Bottom-right hole center: X=108, Y=78.
- Bottom-left hole center: X=2, Y=78.

Do not use dimensions from the existing case drawing as PCB fit constraints; the replacement case will be designed to provide clearance and support for the final component layout.

## Goal

Create a manufacturable alarm panel controller PCB that:

- Uses the ideaspark ESP32 OLED development board as the controller module.
- Preserves 10 alarm zones, siren control, and the external armed indicator; J7 is retained as a spare.
- Integrates W5500 Ethernet support with Ethernet priority and Wi-Fi fallback.
- Supports the existing 12V alarm ecosystem with onboard 12V, 5V, and 3.3V rails.
- Supports bare-PCB assembly (all modules, headers, and components hand-soldered by builder).

## Known Inputs From Current Firmware

Active GPIO map from [devices/alarm-panel-oled.yaml](../../devices/alarm-panel-oled.yaml):

- W5500 SPI:
  - SCLK: GPIO13
  - MOSI: GPIO25
  - MISO: GPIO26
  - CS: GPIO27
- OLED I2C (on dev board):
  - SDA: GPIO21
  - SCL: GPIO22
- Zone inputs:
  - Zone 01: GPIO23
  - Zone 02: GPIO19
  - Zone 03: GPIO18
   - Zone 04: GPIO17
   - Zone 05: GPIO16
   - Zone 06: GPIO4
   - Zone 07: GPIO35 (D35)
   - Zone 08: GPIO34 (D34)
   - Zone 09: GPIO39 (VN)
   - Zone 10: GPIO36 (VP)
- Outputs:
  - Siren control: GPIO32
  - Armed LED: GPIO33
   - GPIO2 onboard status LED: unused in firmware because GPIO2 is a strapping pin

## Known Inputs From Photos

Prototype features visible in [images/top-board-assembled-powered-on.png](../../images/top-board-assembled-powered-on.png):

- 12V barrel jack input.
- Terminal blocks for zones and power (2.54 mm pitch to match the perfboard-style layout and available space).
- Terminal-block pins measure about 0.70-0.75 mm; use 0.8 mm as the nominal pin diameter and 1.0 mm through-holes for insertion clearance.
- Separate power module with selectable output voltage (labeled 12V/9V/5V/3.3V/2.5V/1.8V), shown in [images/power-board-pins.png](../../images/power-board-pins.png).
- MOSFET + gate network for switching 12V alarm/siren circuit.
- Bulk electrolytic capacitors for power rails.

Barrel-jack reference and dimensions are provided in:

- [images/power-plug-dimensions.png](../../images/power-plug-dimensions.png)
- [images/power-plug-bottom-angle.png](../../images/power-plug-bottom-angle.png)

Use these as the default footprint target for the DC input connector:

- Through-hole right-angle DC barrel jack, 3-pin style.
- Plug compatibility target: 2.1 mm ID x 5.5 mm OD barrel plugs.
- Face size: 9.0 mm x 11.0 mm (per drawing).
- Body length: 13.6 mm nominal.
- Front barrel opening drawing callout is 2.0/2.5 mm with 6.4 mm outer feature; select the final jack footprint variant that is specified for 2.1 mm x 5.5 mm plugs.
- Pin style callout indicates 3 pins with approximately 1.0 mm pin thickness (`3-1.0`).
- User-confirmed pinout: pin 1 is center-positive; pins 2 and 3 are negative/GND.
- Keep placement consistent with prototype orientation (connector opening at board edge, pins toward board interior).

W5500 module pin labels are visible in [images/w5500-bottom.png](../../images/w5500-bottom.png):

- 5V, 3.3V, GND, MISO, RST, MOSI, INT, SCS, NC, SCLK.

W5500 mechanical and placement constraints from updated images and prototype notes:

- Module board size: 55.1 mm (X) x 28.1 mm (Y), per the authoritative [images/w5500-drawing.png](../../images/w5500-drawing.png).
- Mounting orientation: module is installed upside down on host-board headers.
- W5500 module board right edge aligns flush with the host PCB right edge.
- Cut an edge-open notch from the host PCB's right edge for the RJ45 housing, with 1.0 mm clearance on its inboard, top, and bottom sides.
- The current drawing-based notch is X=90.7..110.0 mm, Y=8.4..26.6 mm from the board origin.
- Distance from the outside edge of the far header-pin column to the RJ45 body: 31.1 mm.
- Header footprint: 2x5 at 2.54 mm pitch.
- Two Ø3 mm mounting holes beside the RJ45 are included in the W5500 footprint and pass through the host PCB.
- Header pins are approximately 0.75 mm in diameter; the five pin pairs run along the module short axis.
- The drawing gives 2.8 mm from the short module edge to the first pin-column center and 2.3 mm from the long edge to the nearest pin-row center.
- RJ45 body: 21.8 mm x 16.2 mm, centered along the module short axis, with a 3.5 mm bump beyond the module's long edge.
- The W5500 module PCB right edge is flush with the host PCB edge; the RJ45 housing sits in the edge notch and protrudes 3.5 mm beyond the module/host edge. The redesigned case must support the overhanging module and clear the notch/housing.

W5500 2x5 header mapping (from underside silkscreen in [images/w5500-bottom.png](../../images/w5500-bottom.png)):

- Left column (top to bottom): `5V`, `GND`, `RST`, `INT`, `NC`
- Right column (top to bottom): `3.3V`, `MISO`, `MOSI`, `SCS`, `SCLK`

Equivalent row pairs:

- Row 1: `5V` | `3.3V`
- Row 2: `GND` | `MISO`
- Row 3: `RST` | `MOSI`
- Row 4: `INT` | `SCS`
- Row 5: `NC` | `SCLK`

J10 footprint pad numbers (top view of the PCB, module installed upside down): pin 1 (`NC`) is the square pad at the lower left of the header, with odd pins up the left column and even pins up the right column. This gives pin 9 = `5V`, pin 10 = `3V3`, pin 7 = `GND`, pin 8 = `MISO`, pin 5 = `RST`, pin 6 = `MOSI`, pin 3 = `INT`, pin 4 = `SCS`, pin 1 = `NC`, pin 2 = `SCLK`. The header sits at the upper-left of the module outline.

Power module placement and header orientation are confirmed from the prototype photos:

- Power module location: left side of board, between the two capacitors.
- Power module body size: 15 mm (X width) x 20 mm (Y height).
- Header side: pins face the bottom edge of the board.
- Include footprint holes for all 5 header pins, centered along the module bottom edge, matching prototype geometry.
- Pin order (left to right in the saved J8 orientation): EN, IN+, IN-, OUT-, OUT+.
- EN is pin 1 and is unused; pins 2/3 are the 12V input, and pins 4/5 are the 5V output.
- Verify the module's printed labels and input/output polarity against the exact converter board before power-up.

ESP32 module orientation and silkscreen pin labels are confirmed from [images/esp-wroom-32-ideaspark-pinout.png](../../images/esp-wroom-32-ideaspark-pinout.png):

- Module board size: 58 mm (W) x 31.5 mm (H).
- Orientation: horizontal, with USB connector on the right side.
- Top header row labels (left to right, as oriented with USB on right):
   - D23, D22, TX0, RX0, D21, D19, D18, D5, TX2, RX2, D4, D2, D15, GND, 3V3.
- Bottom header row labels (left to right, as oriented with USB on right):
   - EN, VP, VN, D34, D35, D32, D33, D25, D26, D27, D14, D12, D13, GND, VIN.
- Note: the "U3" text visible near the lower-left mounting hole appears to be a board/component marking, not a pin label.
- User verification: top and bottom row pin readings were confirmed against a second physical board.

## Preliminary Electrical Architecture

1. Power input and regulation:
   - 12V input from barrel jack and/or field terminal.
   - 12V rail for alarm peripherals and siren power path.
   - 5V rail for module supply where needed.
   - 3.3V rail for ESP32 logic references and pull-up network.
   - Power module integrated as a pluggable module on 2.54 mm pitch header connectors.

2. ESP32 module carrier:
   - ideaspark ESP32 OLED dev board mounted via 2.54 mm pitch header connectors.
   - Horizontal orientation with USB connector on right.
   - Board size 58 mm x 31.5 mm, with header rows centered along the long edges.
   - Optional USB edge keepout for cable access.

3. Zone interface:
   - 10 zone terminal inputs on J2-J6; J7 is spare with GND on its center pin and NC on both outer pins.
   - Pull-up network for GPIO34/35/36/39 using external resistors (no internal pull-ups on these pins).
   - ESD/EMI filtering placeholders (optional RC or TVS per channel).

4. Output interface:
   - Low-side siren switch using the user's IRFZ44N N-channel MOSFET (Q1).
   - TC4420CPA gate driver (U1), powered from the protected 12V rail and controlled by ESP32 GPIO32.
   - U1 drives Q1 through R5 (10 ohm); R6 (10k) pulls Q1's gate to ground and R7 (10k) holds U1's input low.
   - C4 (100 nF) and C5 (1 uF) bypass U1's 12V supply locally.
   - D2 (1N5822) is installed across J13: cathode to 12V, anode to the switched siren return (SIREN_DRAIN).
   - Armed indicator output terminal or onboard LED driver.
   - Design target for this revision: one 12V siren up to 15W.

5. Ethernet:
   - W5500 as a pluggable module via header connectors.
   - W5500 mounted upside down with RJ45 body overhanging host-board edge.
   - SPI routing matched to current firmware map.
   - Optional RST/INT breakout pads for future use.

## Assembly and Manufacturing Intent

- Target output is a bare PCB only (no pre-assembled parts).
- All terminal blocks, headers, modules, MOSFET, passives, and other components are hand-installed by the builder.
- Prefer through-hole footprints where practical to match prototype-style assembly and simplify field rework.
- Use generic 2.54 mm through-hole terminal-block footprints compatible with common assortment-kit parts.
- Place five active zone blocks, spare J7, and two accessory power blocks in one bottom-edge row, ordered J11, J2-J7, J12. Place the switched siren terminal on the top edge.
- The existing enclosure is not a fit constraint; design a replacement case for the finalized PCB, connector access, and W5500 overhang/notch.

## Power Budget Notes (PoE Splitter + Siren Load)

Current plan includes using a 12V 2A PoE splitter for both board power and Ethernet backhaul.

Reference load math:

- One 12V 15W siren: ~1.25A.
- Two 12V 15W sirens: ~2.50A.
- 12V 2A splitter capacity: 24W max (ideal), before converter and wiring losses.

Implications:

- Two 15W sirens are not feasible on a 12V 2A PoE splitter.
- One 15W siren may be feasible, but available margin for ESP32/W5500/power-module overhead is limited and must be validated in testing.
- For reliable dual-siren operation, use a higher-current external 12V supply for the siren rail (with common ground to controller), or upgrade to a power source with sufficient continuous current headroom.

Selected strategy for current revision:

- Single siren support only.
- Primary plan uses 12V 2A PoE splitter (power + Ethernet).
- Future fallback/upgrade path: use regular Ethernet plus a dedicated 12V supply if more siren power headroom is needed.

## Pull-Up Resistor Plan

For zones on GPIO34/GPIO35/GPIO36/GPIO39:

- Use one pull-up resistor per zone to 3.3V.
- Default value: 10k.
- Use 4.7k in higher-noise wiring environments.

## Suggested PCB Implementation Strategy

1. Create a 2-layer PCB first revision.
2. Manufacturer: standard JLCPCB service.
3. Use the standard 2-layer FR-4 baseline at 1.6 mm board thickness and 1 oz finished copper; confirm these selections against the final JLCPCB order configuration before ordering.
4. Use a 10°C maximum trace temperature rise above ambient as the initial trace-width sizing target.
5. Keep high-current 12V siren path wide and isolated from logic traces.
6. Use a solid ground plane on one layer where possible.
7. Keep SPI traces between ESP32 header and W5500 short and direct.
8. Place bulk capacitance near power entry and switching node.
9. Keep all terminal blocks on the top board edge for field wiring access.

## DFM and Reliability Targets

- Creepage/clearance suitable for 12V automotive/security wiring environments.
- Test points for 12V, 5V, 3.3V, GND, and siren gate/control node.
- F1 is a selected 2 A time-delay 5x20 mm fuse on the 12V input; confirm its rating is adequate for simultaneous siren, accessory, and controller load before ordering.
- D1 is a stocked 1N5822, 3 A / 40 V Schottky series reverse-polarity diode in the axial THT footprint. Verify forward drop and thermal rise at the maximum simultaneous siren/accessory load.
- U1 is a TC4420CPA gate driver powered from the 12V rail; GPIO32 drives its TTL/CMOS-compatible input. Its output drives Q1's gate through R5, so the IRFZ44N is not driven directly by the ESP32's 3.3V GPIO.
- D2 is a 1N5822 flyback diode across J13, cathode to +12V and anode to SIREN_DRAIN. Confirm the selected siren's manufacturer permits a simple external flyback clamp before powering it.
- Validate Q1 voltage drop and temperature, the D1/D2 thermal performance, and total input current at the measured siren load before ordering.
- Consider separate protected terminal for external high-current siren supply input if dual-siren support is required.

## Silkscreen and Connector Labeling Conventions

Use assembly-first labeling to reduce wiring and placement mistakes:

- Mirror connector and module pin naming on silkscreen wherever practical.
- Label every terminal block position with both function and polarity/signal name.
- Add Pin 1 markers on all pluggable headers.

Recommended labels:

- Power input/output:
   - `12V_IN+`, `12V_IN-`
   - `5V`, `GND`
   - Power-module header pins, left to right: `EN`, `IN+`, `IN-`, `OUT-`, `OUT+`
   - DC barrel jack polarity marking: `Center +` (center-positive) near the jack footprint.
- Siren/output:
   - `SIREN+`, `SIREN-`, `ARM_LED` (or equivalent chosen net names)
- Zones:
   - `Z1` through `Z10`; J2-J6 carry paired zone signals with GND center pins, and J7 is labeled `NC / GND / NC`.
- W5500 header:
   - `5V`, `3V3`, `GND`, `MISO`, `RST`, `MOSI`, `INT`, `SCS`, `NC`, `SCLK`
- ESP32 carrier:
   - Top/bottom row pin names matching the verified board silkscreen where readable.

Component outlines:

- Draw courtyard-style silkscreen outlines for major pluggable modules:
   - ESP32 board
   - W5500 module
   - Power module
- Place clear reference text inside/near each outline:
   - `ESP32`, `W5500`, `PWR`
- Include a small orientation cue (for example, `USB ->` on the ESP32 outline).

Capacitor callouts:

- C1: 680 µF / 18 V on the 12V rail.
- C2: 470 µF / 10 V on the 5V rail.
- C3: 470 µF / 10 V on the 3.3V rail.
- Print short rail markers `12V CAP`, `5V CAP`, and `3V3 CAP` on the PCB; retain the full values and ratings in the BOM.

## Information Still Required To Finish Manufacturing Files

The photos, case drawing, and current constraints are enough for architecture and initial placement; case support can be adjusted later if needed.

## Deliverables After Confirmation

After the items above are confirmed, the final output can include:

- KiCad schematic and PCB files.
- Gerbers + drill files.
- BOM and assembly notes.
- Optional position file and CPL for assembly.
- Wiring map cross-reference to firmware pins.
