# Alarm Panel

ESPHome-based ESP32 alarm controller replacement.

## Repository Layout

```
.
|-- docs/
|   `-- pinout-and-ethernet.md
|-- devices/
|   `-- alarm-panel.yaml
|-- packages/
|   |-- boards/
|   |   `-- esp32dev.yaml
|   `-- common/
|       |-- base.yaml
|       `-- diagnostics.yaml
|-- secrets.example.yaml
`-- .gitignore
```

## Getting Started

1. Copy `secrets.example.yaml` to `secrets.yaml` and fill in your local values.
2. Adjust [devices/alarm-panel.yaml](devices/alarm-panel.yaml) for your node name and device-specific components.
3. Add shared configuration to files under `packages/` as the project grows.
4. Compile or upload with ESPHome, for example:

	```bash
	esphome run devices/alarm-panel.yaml
	```

## Notes

- `devices/` holds top-level node definitions.
- `docs/` holds hardware notes, pin maps, and migration plans.
- `packages/boards/` holds board-specific platform settings.
- `packages/common/` holds reusable shared configuration blocks.
- `secrets.yaml` is ignored by git and should stay local.

## Hardware Notes

The current config is based on the ideaspark ESP32 0.96in OLED board used for the alarm-panel-oled device. It uses an SSD1306 128x64 OLED on I2C GPIO21/GPIO22 and keeps the alarm-zone inputs and outputs mapped around that layout.

If you add the W5500 Ethernet module, the four relocated zone inputs must use external pull-up resistors to 3.3V because GPIO34, GPIO35, GPIO36, and GPIO39 do not provide internal pull-ups. A 10 kΩ resistor is the normal starting point, with 4.7 kΩ recommended for longer or noisier runs.

See [docs/pinout-and-ethernet.md](docs/pinout-and-ethernet.md) for the existing pin-out, the pin-by-pin W5500 migration plan, the updated pin-out, and the resistor guidance.
