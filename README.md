# Alarm Panel

ESPHome-based ESP32 alarm controller replacement.

## Repository Layout

```
.
|-- hardware/
|   `-- alarm-panel/
|       |-- Alarm Panel.kicad_pro
|       |-- fp-lib-table
|       |-- sym-lib-table
|       |-- Alarm Panel.kicad_sch
|       |-- Alarm Panel.kicad_pcb
|       |-- footprints/
|       |   |-- AlarmPanel_THT.pretty/
|       |   `-- README.md
|       `-- symbols/
|   `-- enclosure/
|       `-- 3d-printing/
|           `-- legacy/
|-- tools/
|   `-- pcb/
|       |-- project_paths.py
|       `-- *.py
|-- docs/
|   `-- pcb/
|       |-- images/
|       |-- pinout-and-ethernet.md
|       |-- pcb-design-brief.md
|       |-- pcb-first-pass-layout.md
|       |-- pcb-schematic-block-plan.md
|       `-- pcb-top-down-mockup.md
|-- esphome/
|   |-- alarm-panel-oled.yaml
|   `-- secrets.yaml
`-- .gitignore
```

## Getting Started

1. The tracked [esphome/secrets.yaml](esphome/secrets.yaml) contains placeholder values; replace them locally before connecting the device to real networks or users.
2. Adjust [esphome/alarm-panel-oled.yaml](esphome/alarm-panel-oled.yaml) for your node name and device-specific components.
3. Compile or upload with ESPHome, for example:

	```bash
	esphome run esphome/alarm-panel-oled.yaml
	```

## Notes

- `esphome/` holds the top-level ESPHome node configuration and its secrets file.
- `hardware/alarm-panel/` holds the KiCad project and its project-local footprint and symbol libraries.
- `tools/pcb/` holds scripts that generate, inspect, or update the KiCad design.
- `docs/pcb/` holds hardware notes, pin maps, validation checklists, and reference images.
- `hardware/enclosure/3d-printing/` holds printable enclosure models; historical versions are kept under `legacy/`.
- `esphome/secrets.yaml` is a tracked placeholder template. Never replace its placeholders with real credentials in a commit.
- Root-level `secrets.yaml` files are ignored by git for local ESPHome configurations.

## Hardware Notes

The current config is based on the ideaspark ESP32 0.96in OLED board used for the alarm-panel-oled device. It uses an SSD1306 128x64 OLED on I2C GPIO21/GPIO22 and keeps the alarm-zone inputs and outputs mapped around that layout.

If you add the W5500 Ethernet module, the four relocated zone inputs must use external pull-up resistors to 3.3V because GPIO34, GPIO35, GPIO36, and GPIO39 do not provide internal pull-ups. A 10 kΩ resistor is the normal starting point, with 4.7 kΩ recommended for longer or noisier runs.

See [docs/pcb/pinout-and-ethernet.md](docs/pcb/pinout-and-ethernet.md) for the existing pin-out, the pin-by-pin W5500 migration plan, the updated pin-out, and the resistor guidance.

For PCB work based on the perfboard prototype photos, see [docs/pcb/pcb-design-brief.md](docs/pcb/pcb-design-brief.md).

For a human-readable top-down board mockup, see [docs/pcb/pcb-top-down-mockup.md](docs/pcb/pcb-top-down-mockup.md).

For the schematic-to-footprint handoff plan, see [docs/pcb/pcb-schematic-block-plan.md](docs/pcb/pcb-schematic-block-plan.md).

For the current outstanding design, routing, validation, and JLCPCB release items, see [docs/pcb/pcb-completion-checklist.md](docs/pcb/pcb-completion-checklist.md).

Open [hardware/alarm-panel/Alarm Panel.kicad_pro](hardware/alarm-panel/Alarm%20Panel.kicad_pro) in KiCad to load the schematic, board, and project-local footprint library together. The schematic is at [hardware/alarm-panel/Alarm Panel.kicad_sch](hardware/alarm-panel/Alarm%20Panel.kicad_sch).

The current board is [hardware/alarm-panel/Alarm Panel.kicad_pcb](hardware/alarm-panel/Alarm%20Panel.kicad_pcb); use [tools/pcb/resize_board_for_rj45_notch.py](tools/pcb/resize_board_for_rj45_notch.py) to adjust its outline while preserving manual placements. It contains the 110 x 80 mm outline, mounting holes, RJ45 notch, connector row, ESP32/W5500 footprints, and preliminary routing. The high-current 12V/siren tracks are sized to 1.1 mm using the documented 1 oz copper and 10°C rise assumptions. The replacement case will be designed around the finalized PCB; see [docs/pcb/pcb-completion-checklist.md](docs/pcb/pcb-completion-checklist.md) for remaining electrical, ground-pour, and manufacturing checks.
