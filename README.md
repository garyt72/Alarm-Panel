# Alarm Panel

ESPHome-based ESP32 alarm controller replacement.

## Repository Layout

```
.
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
- `packages/boards/` holds board-specific platform settings.
- `packages/common/` holds reusable shared configuration blocks.
- `secrets.yaml` is ignored by git and should stay local.
