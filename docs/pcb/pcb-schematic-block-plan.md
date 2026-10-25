# PCB Schematic Block Plan

This document translates the first-pass floorplan into a schematic-oriented parts and net plan.
It is the next step after the mockup and layout brief: a bridge between the human-readable board sketch and actual KiCad schematic capture.

## Purpose

- Keep the schematic aligned with the current prototype behavior.
- Keep reference designators consistent with the layout docs.
- Identify the minimum set of footprints and nets needed for the first PCB revision.
- Preserve the current choice to document capacitor rails on the board as short callouts rather than full voltage-rating labels.

## Reference Designator Plan

The following reference designators match the current layout documents.

### Power Entry and Regulation

- J1: DC barrel jack, pin 1 center-positive 12V input; pins 2 and 3 are negative/GND.
- F1: selected 2 A time-delay 5x20 mm fuse in the 12V input path, using the supplied 24 x 10 mm holder drawing and 23.6 mm pin pitch; verify lead-slot fit and confirm rating against total siren/accessory load.
- D1: stocked 1N5822, 3 A / 40 V Schottky series reverse-polarity diode; verify forward drop and thermal dissipation at the maximum simultaneous load.
- J8: pluggable power module header; pin order is EN, IN+, IN-, OUT-, OUT+ from left to right.
- J8 pin nets: 1 EN (NC), 2 IN+ (12V), 3 IN- (GND), 4 OUT- (GND), 5 OUT+ (5V); verify against the exact module markings before power-up.
- C1: 680 µF / 18 V bulk capacitor on the 12V rail; silkscreen label `12V CAP`.
- C2: 470 µF / 10 V bulk capacitor on the 5V rail; silkscreen label `5V CAP`.
- C3: 470 µF / 10 V bulk capacitor on the 3.3V rail; silkscreen label `3V3 CAP`.

### Controller and Communication

- J9: ESP32 OLED carrier board footprint.
- J10: W5500 Ethernet module footprint.

### Inputs and Outputs

- J2 through J6: bottom-edge 3-wire zone terminal blocks for ten active zones.
- J7: spare 3-position terminal block; center pin GND, outer pins NC.
- J11 and J12: 2-wire accessory power terminals.
- J13: switched siren output terminal block.
- Q1: IRFZ44N low-side siren MOSFET.
- U1: TC4420CPA non-inverting MOSFET gate driver, powered from 12V and controlled by GPIO32.
- R5: 10 ohm series resistor from U1 output to Q1 gate; R6: 10k gate-to-ground pulldown; R7: 10k U1-input pulldown.
- C4: 100 nF and C5: 1 uF local bypass capacitors across U1's 12V/GND supply.
- D2: 1N5822 across J13, cathode to 12V and anode to SIREN_DRAIN.

## Net Groups

### Power Nets

- `12V_IN`: barrel jack input and downstream protected 12V rail.
- `12V`: main 12V distribution rail.
- `5V`: module supply rail and auxiliary power rail.
- `3V3`: logic rail for ESP32 pull-ups and W5500 logic as required.
- `GND`: common ground.

### Zone Nets

The zone signals remain the same as the current firmware map.

- Z1 -> GPIO23
- Z2 -> GPIO19
- Z3 -> GPIO18
- Z4 -> GPIO17
- Z5 -> GPIO16
- Z6 -> GPIO4
- Z7 -> GPIO35 (D35)
- Z8 -> GPIO34 (D34)
- Z9 -> GPIO39 (VN)
- Z10 -> GPIO36 (VP)

### Ethernet Nets
- GATE_DRIVER_OUT: U1 output pins 6 and 7, tied together and connected through R5 to Q1's gate.
- Q1_GATE: MOSFET gate node, pulled to ground by R6.
- 12V: fixed positive supply on one J13 siren terminal.
### Top Header Row (Odd Pins)

| J9 pin | Carrier label | Net / use |
| --- | --- | --- |
| 1 | D23 | Z1 |
| 3 | D22 | OLED_SCL |
| 5 | TX0 | No connect; preserve serial programming/debug |
| 7 | RX0 | No connect; preserve serial programming/debug |
| 9 | D21 | OLED_SDA |
| 11 | D19 | Z2 |
| 13 | D18 | Z3 |
| 15 | D5 | No connect; strap pin avoided |
| 8 | D34 | Z8 / GPIO34 |
| 10 | D35 | Z7 / GPIO35 |
| 21 | D4 | Z6 / GPIO4 |
| 23 | D2 | No connect; strap pin avoided |
| 25 | D15 | No connect |
| 27 | GND | GND |
| 29 | 3V3 | 3V3 |

### Bottom Header Row (Even Pins)

| J9 pin | Carrier label | Net / use |
| --- | --- | --- |
| 2 | EN | No connect |
| 4 | VP | Z10 / GPIO36 |
| 6 | VN | Z9 / GPIO39 |
| 8 | D34 | Z8 |
| 10 | D35 | Z7 |
| 12 | D32 | SIREN_GATE |
| 14 | D33 | ARM_LED |
| 16 | D25 | MOSI |
| 18 | D26 | MISO |
| 20 | D27 | SCS |
| 22 | D14 | No connect; boot-time transient avoided |
| 24 | D12 | No connect |
| 26 | D13 | SCLK |
| 28 | GND | GND |
| 30 | VIN | 5V |

This pin assignment is reflected in the current schematic netlist. The physical ESP32 board's two 15-pin header rows are confirmed at 27.94 mm center-to-center, the standard 11 x 2.54 mm spacing; J9 uses this pitch.

## Footprint Inventory

### Through-Hole Parts

- J1: right-angle 3-pin DC barrel jack footprint.
- J2-J7: 3-position 2.54 mm terminal block footprints.
- J11-J12: 2-position 2.54 mm terminal block footprints.
- J13: 2-position 2.54 mm terminal block footprint.
- Q1: TO-220-3 through-hole footprint for the stocked IRFZ44N.
- R1-Rn: pull-up resistors for GPIO34/GPIO35/GPIO36/GPIO39 and any other required support parts.

### Module Headers

- J8: 5-pin header pattern for the power module, with the EN pin left unused.
- J9: ESP32 OLED module carrier headers.
- J10: 2x5 header for the W5500 module.

## Capacitor Placement Rules

Use one visible bulk capacitor per rail and make the board labeling descriptive:

- C1 near the 12V input path and input protection stage.
- C2 near the 5V power-module output and downstream 5V distribution.
- C3 near the ESP32 logic feed and 3.3V reference network.

PCB silkscreen should use the short rail names `12V CAP`, `5V CAP`, and `3V3 CAP` rather than full voltage-rating text.

## First Schematic Sheet Structure

If the schematic is split into pages or blocks, a practical first revision is:

1. Power entry and regulation.
2. ESP32 carrier and logic rails.
3. Zone inputs and pull-up network.
4. Siren driver and output terminal.
5. W5500 Ethernet module and SPI wiring.

## KiCad Capture Notes

- Keep refdes numbering stable once assigned so the layout docs stay readable.
- Label each connector with the same J-number used in the floorplan docs.
- Put the rail callout text close to the capacitor clusters, but keep the exact capacitance and voltage rating in the BOM.
- Keep the W5500 and ESP32 module orientation notes visible in the schematic symbol descriptions or sheet annotations.

## Result Expected From This Step

After this planning pass, the next deliverable should be a KiCad schematic draft with the same nets, connector references, and capacitor rail callouts described here.