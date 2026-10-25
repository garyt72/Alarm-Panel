# Alarm Panel Pin-Out and W5500 Migration Plan

This document records the current ESP32 pin usage in [devices/alarm-panel-oled.yaml](../devices/alarm-panel-oled.yaml), then proposes the least disruptive way to add a W5500 Ethernet module while keeping programming and debugging as safe as possible.

## Design Goals

- Keep UART/programming pins off the Ethernet module.
- Avoid ESP32 strap pins for the W5500.
- Preserve all 12 alarm zones if possible.
- Prefer pins that do not interfere with boot or serial flashing.

## Existing Pin-Out

### Reserved or Avoided Pins

| GPIO | Current status | Reason |
| --- | --- | --- |
| 0 | Avoided | Boot strap pin |
| 1 | Avoided | UART0 TX, used for logging/programming |
| 2 | Used | Onboard LED output |
| 3 | Avoided | UART0 RX, used for logging/programming |
| 6-11 | Avoided | Internal SPI flash pins |
| 12 | Avoided | Boot strap pin |
| 15 | Avoided | Boot strap pin |
| 21 | Used | OLED I2C SDA |
| 22 | Used | OLED I2C SCL |

### Alarm Outputs and Sensors

| GPIO | Current role |
| --- | --- |
| 2 | Onboard LED output |
| 4 | Zone 07 |
| 5 | Zone 04 |
| 13 | Zone 12 |
| 14 | Zone 11 |
| 16 | Zone 06 |
| 17 | Zone 05 |
| 18 | Zone 03 |
| 19 | Zone 02 |
| 23 | Zone 01 |
| 25 | Zone 08 |
| 26 | Zone 09 |
| 27 | Zone 10 |
| 32 | Siren output |
| 33 | Armed LED output |

## Pin-By-Pin Migration Plan

This plan keeps the project safe for flashing and debugging, while avoiding loss of alarm zones.

| Existing pin | Current role | New role | Action needed |
| --- | --- | --- | --- |
| GPIO 13 | Zone 12 | W5500 SCLK | Rewire zone 12 to GPIO39 |
| GPIO 25 | Zone 08 | W5500 MOSI | Rewire zone 8 to GPIO34 |
| GPIO 26 | Zone 09 | W5500 MISO | Rewire zone 9 to GPIO35 |
| GPIO 27 | Zone 10 | W5500 SCS | Rewire zone 10 to GPIO36 |
| GPIO 34 | Free | Zone 08 | Add external pull-up to 3.3V |
| GPIO 35 | Free | Zone 09 | Add external pull-up to 3.3V |
| GPIO 36 | Free | Zone 10 | Add external pull-up to 3.3V |
| GPIO 39 | Free | Zone 12 | Add external pull-up to 3.3V |

## Pull-Up Resistor Guidance

The four relocated zone inputs use GPIO34, GPIO35, GPIO36, and GPIO39. These pins are input-only on the ESP32 and do not provide internal pull-ups, so each zone needs its own external pull-up resistor to 3.3V.

Recommended values:

- `10 kΩ` for normal short-to-medium wiring runs and typical reed switches.
- `4.7 kΩ` for longer runs, noisier environments, or if you want a stronger idle-high bias.

Do not add pull-ups to the W5500 SPI lines unless the module documentation specifically requires one. The Ethernet signals should remain direct connections between the ESP32 and the W5500 board.

## Recommended W5500 Wiring

Use the W5500 on GPIOs that stay clear of boot and serial behavior:

| W5500 pin | ESP32 GPIO | Notes |
| --- | --- | --- |
| SCLK | 13 | Frees the zone currently on GPIO13 |
| MOSI | 25 | Frees the zone currently on GPIO25 |
| MISO | 26 | Frees the zone currently on GPIO26 |
| SCS | 27 | Frees the zone currently on GPIO27 |
| RST | Not connected | Leave unused unless later needed |
| INT | Not connected | Leave unused unless later needed |
| 3.3V | 3.3V | Preferred supply for safest logic-level compatibility |
| GND | GND | Common ground |

## Updated Pin-Out

After the migration, the GPIO map becomes:

| GPIO | Updated role |
| --- | --- |
| 2 | Onboard LED output |
| 4 | Zone 07 |
| 5 | Zone 04 |
| 13 | W5500 SCLK |
| 14 | Zone 11 |
| 16 | Zone 06 |
| 17 | Zone 05 |
| 18 | Zone 03 |
| 19 | Zone 02 |
| 23 | Zone 01 |
| 25 | W5500 MOSI |
| 26 | W5500 MISO |
| 27 | W5500 SCS |
| 32 | Siren output |
| 33 | Armed LED output |
| 34 | Zone 08 |
| 35 | Zone 09 |
| 36 | Zone 10 |
| 39 | Zone 12 |

## Notes On The New Zone Pins

- GPIO34, GPIO35, GPIO36, and GPIO39 are input-only.
- They do not have internal pull-ups, so use external pull-up resistors to 3.3V for those four zones.
- Wire each of those zones with one pull-up resistor per input, placed to 3.3V on the ESP32 side of the circuit.
- Keep the existing zone filters and logic unchanged after the move.

## Why This Is The Safest Option

- It leaves GPIO1 and GPIO3 free for serial logging and programming.
- It avoids strap-pin conflicts during boot.
- It keeps the existing OLED I2C pins untouched.
- It preserves all 12 zones by relocating only four of them.

## If You Want The Absolute Minimum Wiring Change

The only way to avoid moving any zones is to use serial or strap pins for the W5500, which is not recommended if programming/debugging stability matters.