# Top-Down PCB Mockup

This is a human-readable, not-to-scale board mockup for the first PCB pass.
It shows the intended placement of the major modules and connectors while keeping the original prototype feel where practical.

Board outline: 110 mm x 80 mm; replacement case to be designed around the final PCB and RJ45 notch.

ESP32 module size: 58 mm x 31.5 mm

```text
                           TOP OF BOARD
    ┌────────────────────────────────────────────────────────────┐
    │ J13 SIREN -> [Q1 IRFZ44N]        [W5500]   ┌RJ45 NOTCH      │
    │ shifted right along top edge     right edge└outboard        │
    │ F1 FUSE     D1 SCHOTTKY                                  │
    │ above J1 and the capacitor row                            │
    │                    [Q1 IRFZ44N]                            │
    │             J8 PWR MODULE   R1                             │
    │             left channel    R2                             │
    │                             R3                             │
    │                             R4                             │
    │                                                            │
    │             C1 12V                                         │
    │             C2 5V     [ESP32 OLED BOARD]                  │
    │             C3 3V3   USB -> right edge                    │
    │ J1 DC IN left edge                                        │
    │          R1    R2    R3    R4                             │
    │                                                            │
    │                                                            │
    │ J11: AUX 12V/GND   J2: Z1/GND/Z2   J3: Z3/GND/Z4   J4: Z5 │
    │ J5: Z7/GND/Z8      J6: Z9/GND/Z10  J7: NC/GND/NC   J12:   │
    │ AUX 12V/GND       in-line with zone inputs                 │
    │                                                            │
    │ [mount]                                              [mount]│
    └────────────────────────────────────────────────────────────┘
                           BOTTOM OF BOARD
```

## Visual Notes

- The lower edge has five active 3-wire sensor blocks and spare J7 (NC/GND/NC).
- The center pin on each bottom block is ground/common.
- The two accessory 2-pin 12V/GND terminals are inline with the bottom sensor blocks so the lower edge reads as one connector row.
- Leave about 1.5 mm to 2.0 mm of clearance between neighboring terminal block bodies when laying out the bottom row, if space allows.
- The switched siren terminal is shifted right along the top edge; Q1 sits between it and the W5500 region.
- The W5500 module board's right edge is flush with the host PCB edge; an edge-open notch provides 1 mm clearance on the RJ45 housing's three inboard sides.
- The two Ø3 mm W5500 mounting holes beside the RJ45 align with host-board clearance holes for case support.
- The ESP32/OLED carrier is rotated 180 degrees, with D23/EN near the right edge and its antenna area beyond the host PCB edge.
- The USB connector faces inward from the opposite end; preserve its approach clearance and keep metal/enclosure parts clear of the antenna.
- The ESP32 module outline should be treated as a 58 mm x 31.5 mm rectangle, with header rows centered along its long edges.
- F1 and D1 are above the lower-positioned barrel jack and the capacitor row.
- The barrel jack and power module remain in the left channel; C1-C3 form a vertical column shifted left into the resistor-capacitor gap.
- J8 is shifted left of the main module stack; its power-module pin row aligns with J9's lower header row.
- F1/D1 sit above the barrel jack and capacitor row.
- R1-R4 are 10 kΩ external pull-ups for Z7/Z8/Z9/Z10 in order, in a horizontal row below J9 near the ESP32 rather than beside the field terminals.
- The single capacitor on each rail can be silkscreened with a short rail name such as 12V CAP, 5V CAP, and 3V3 CAP.
- The 12V capacitor belongs near the power entry, the 5V capacitor belongs beside the 5V module output, and the 3V3 capacitor belongs near the ESP32 logic feed.

## Connector Summary

### Bottom Edge Connector Row

- J11: 12V / GND accessory power, bottom-left end of the row
- J2: Zone 1, GND, Zone 2
- J3: Zone 3, GND, Zone 4
- J4: Zone 5, GND, Zone 6
- J5: Zone 7, GND, Zone 8
- J6: Zone 9, GND, Zone 10
- J7: Spare connector, NC / GND / NC
- J12: 12V / GND accessory power, bottom-right end of the row

### Top Edge and Major Modules

- J1: Barrel jack, center positive
- J8: Power module, left side
- Q1: IRFZ44N low-side MOSFET siren driver
- J13: Switched siren output
- J9: ESP32 OLED board, center-right
- J10: W5500 module, right edge, upside down

## Layout Intent

This mockup keeps the sensor wiring low and clean, keeps powered accessories close to the corners, and preserves enough space for the W5500 RJ45 body to overhang the PCB edge without forcing major case changes.
