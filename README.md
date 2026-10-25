# Alarm Panel

ESPHome-based ESP32 alarm controller replacement.

## Repository Layout

```
.
|-- pcb/
|   |-- Alarm Panel.kicad_pro
|   |-- fp-lib-table
|   |-- Alarm Panel.kicad_sch
|   |-- Alarm Panel.kicad_pcb
|   |-- generate_mechanical_board.py
|   |-- repair_schematic_metadata.py
|   |-- wire_schematic_pins.py
|   |-- footprints/
|   |   |-- AlarmPanel_THT.pretty/
|   |   `-- README.md
|   `-- docs/
|       |-- pinout-and-ethernet.md
|       |-- pcb-design-brief.md
|       |-- pcb-first-pass-layout.md
|       |-- pcb-schematic-block-plan.md
|       `-- pcb-top-down-mockup.md
|-- devices/
|   |-- alarm-panel-oled.yaml
|   `-- secrets.yaml
|-- packages/
|   |-- boards/
|   |   `-- esp32dev.yaml
|   `-- common/
|       |-- base.yaml
|       `-- diagnostics.yaml
`-- .gitignore
```

## Getting Started

1. The tracked [devices/secrets.yaml](devices/secrets.yaml) contains placeholder values; replace them locally before connecting the device to real networks or users.
2. Adjust [devices/alarm-panel-oled.yaml](devices/alarm-panel-oled.yaml) for your node name and device-specific components.
3. Add shared configuration to files under `packages/` as the project grows.
4. Compile or upload with ESPHome, for example:

	```bash
	esphome run devices/alarm-panel-oled.yaml
	```

## Notes

- `devices/` holds top-level node definitions.
- `pcb/docs/` holds PCB hardware notes, pin maps, migration plans, and layout drafts.
- `pcb/` holds the KiCad schematic, mechanical PCB baseline, footprint library, and board generator.
- `packages/boards/` holds board-specific platform settings.
- `packages/common/` holds reusable shared configuration blocks.
- `devices/secrets.yaml` is a tracked placeholder template. Never replace its placeholders with real credentials in a commit.
- Root-level `secrets.yaml` files are ignored by git for local ESPHome configurations.

## Hardware Notes

The current config is based on the ideaspark ESP32 0.96in OLED board used for the alarm-panel-oled device. It uses an SSD1306 128x64 OLED on I2C GPIO21/GPIO22 and keeps the alarm-zone inputs and outputs mapped around that layout.

If you add the W5500 Ethernet module, the four relocated zone inputs must use external pull-up resistors to 3.3V because GPIO34, GPIO35, GPIO36, and GPIO39 do not provide internal pull-ups. A 10 kΩ resistor is the normal starting point, with 4.7 kΩ recommended for longer or noisier runs.

See [pcb/docs/pinout-and-ethernet.md](pcb/docs/pinout-and-ethernet.md) for the existing pin-out, the pin-by-pin W5500 migration plan, the updated pin-out, and the resistor guidance.

For PCB work based on the perfboard prototype photos, see [pcb/docs/pcb-design-brief.md](pcb/docs/pcb-design-brief.md).

For a human-readable top-down board mockup, see [pcb/docs/pcb-top-down-mockup.md](pcb/docs/pcb-top-down-mockup.md).

For the schematic-to-footprint handoff plan, see [pcb/docs/pcb-schematic-block-plan.md](pcb/docs/pcb-schematic-block-plan.md).

For the current outstanding design, routing, validation, and JLCPCB release items, see [pcb/docs/pcb-completion-checklist.md](pcb/docs/pcb-completion-checklist.md).

Open [pcb/Alarm Panel.kicad_pro](pcb/Alarm%20Panel.kicad_pro) in KiCad to load the schematic, board, and project-local footprint library together. The schematic is at [pcb/Alarm Panel.kicad_sch](pcb/Alarm%20Panel.kicad_sch).

The current board is [pcb/Alarm Panel.kicad_pcb](pcb/Alarm%20Panel.kicad_pcb); use [pcb/resize_board_for_rj45_notch.py](pcb/resize_board_for_rj45_notch.py) to adjust its outline while preserving manual placements. It contains the 110 x 80 mm outline, mounting holes, RJ45 notch, connector row, ESP32/W5500 footprints, and preliminary routing. The high-current 12V/siren tracks are sized to 1.1 mm using the documented 1 oz copper and 10°C rise assumptions. The replacement case will be designed around the finalized PCB; see [pcb/docs/pcb-completion-checklist.md](pcb/docs/pcb-completion-checklist.md) for remaining electrical, ground-pour, and manufacturing checks.
