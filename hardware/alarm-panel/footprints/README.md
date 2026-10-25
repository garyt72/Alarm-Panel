# Local KiCad Footprints

This folder contains project-local, through-hole footprints for the Alarm Panel PCB.

## Library Folder

- `AlarmPanel_THT.pretty`

## Included Footprints

- `TerminalBlock_1x03_P2.54mm_Body8.15x6.40mm`
- `TerminalBlock_1x02_P2.54mm_Body5.60x6.40mm`
- `MountingHole_NPTH_2.0mm`
- `ESP32_OLED_2x15_P2.54mm_Row27.94mm`
- `W5500_2x5_P2.54mm_Module55.1x28.1mm`
- `PowerModule_1x05_P2.54mm_Body15x20mm`
- `FuseHolder_Body24x10_P23.6mm`

Both footprints are:

- Through-hole (THT)
- 2.54 mm pin pitch
- Sized to the provided body dimensions for layout keepout planning
- Terminal-block pin diameter: use 0.8 mm nominal, based on measured 0.70-0.75 mm pins
- Terminal-block pads use 1.0 mm drills to provide insertion clearance for those pins
- Offset 0.55 mm from the body center so pin centers sit 3.75 mm from the defined front edge

The adjacent `fp-lib-table` loads this library automatically when opening `Alarm Panel.kicad_pro`. The schematic references the custom names with the `AlarmPanel_THT:` prefix. The footprints define the front as the row's outboard-facing edge; the installed footprints should be oriented with that edge facing the PCB bottom.

The ESP32 carrier outline is 58 mm x 31.5 mm. Its 15-pin header rows are confirmed at 27.94 mm center-to-center (11 x 2.54 mm standard spacing).

The W5500 footprint follows [the reference drawing](../../../docs/pcb/images/w5500-drawing.png): 55.1 mm x 28.1 mm module outline, five pin pairs at 2.54 mm pitch, and 1.0 mm drills for the approximately 0.75 mm pins. Pin 1 is 2.8 mm from the short edge and 15.64 mm from the top edge; the bottom row center is 2.3 mm from the long edge. The RJ45 body is 21.8 mm x 16.2 mm, centered on the module short axis, with a 3.5 mm bump beyond the module edge. The W5500 module right edge is flush with the host PCB; the RJ45 housing occupies the edge notch with 1 mm clearance on its three inboard sides.

The mounting-hole footprint is used by the mechanical PCB baseline.

The fuse-holder footprint matches the supplied 24 x 10 x 6.25 mm drawing, including the 23.6 mm pin-center pitch and rectangular 0.4 x 1.4 mm leads. The 0.6 x 1.6 mm oval drills provide 0.2 mm nominal clearance on each lead dimension.
