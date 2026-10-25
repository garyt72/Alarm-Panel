# Alarm Panel Final Pin-Out and W5500 Wiring

This document records the final ESP32 pin usage in [devices/alarm-panel-oled.yaml](../../devices/alarm-panel-oled.yaml). The design keeps the W5500 Ethernet module and uses ten alarm zones to avoid boot-strapping and programming/debug pins.

## Design Goals

- Keep UART/programming pins off the Ethernet module.
- Avoid ESP32 strapping pins and UART pins for field inputs and W5500 signals.
- Use ten active zones; J7 remains a grounded spare connector.
- Prefer pins that do not interfere with boot or serial flashing.

## Final GPIO Map

### Reserved or Avoided Pins

| GPIO | Current status | Reason |
| --- | --- | --- |
| 0 | Avoided | Boot strap pin |
| 1 | Avoided | UART0 TX, used for logging/programming |
| 2 | Avoided | Strapping pin; onboard LED is not configured by firmware |
| 3 | Avoided | UART0 RX, used for logging/programming |
| 6-11 | Avoided | Internal SPI flash pins |
| 12 | Avoided | Boot strap pin |
| 15 | Avoided | Boot strap pin |
| 5 | Avoided | Boot strap pin; not assigned to a zone |
| 14 | Avoided | Not assigned; carrier documentation notes a brief boot-time transient |
| 21 | Used | OLED I2C SDA |
| 22 | Used | OLED I2C SCL |

### Active Zones and Outputs

| GPIO | Current role |
| --- | --- |
| 4 | Zone 06 |
| 13 | W5500 SCLK |
| 16 | Zone 05 |
| 17 | Zone 04 |
| 18 | Zone 03 |
| 19 | Zone 02 |
| 23 | Zone 01 |
| 25 | W5500 MOSI |
| 26 | W5500 MISO |
| 27 | W5500 SCS |
| 32 | Siren output |
| 33 | Armed LED output |
| 34 | Zone 08 (D34, external pull-up) |
| 35 | Zone 07 (D35, external pull-up) |
| 36 | Zone 10 (VP, external pull-up) |
| 39 | Zone 09 (VN, external pull-up) |

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
| SCLK | 13 | Dedicated W5500 SPI clock |
| MOSI | 25 | Dedicated W5500 SPI data from ESP32 |
| MISO | 26 | Dedicated W5500 SPI data to ESP32 |
| SCS | 27 | Dedicated W5500 chip select |
| RST | Not connected | Leave unused unless later needed |
| INT | Not connected | Leave unused unless later needed |
| 3.3V | 3.3V | Preferred supply for safest logic-level compatibility |
| GND | GND | Common ground |

## Zone Mapping

Ten zones remain active. GPIO5 and GPIO14 are no longer used for field inputs; J7 is a spare connector with NC/GND/NC pins.

| Zone | GPIO | J9 carrier pin | Field terminal |
| --- | --- | --- | --- |
| Z1 | 23 | D23 | J2 pin 1 |
| Z2 | 19 | D19 | J2 pin 3 |
| Z3 | 18 | D18 | J3 pin 1 |
| Z4 | 17 | TX2 | J3 pin 3 |
| Z5 | 16 | RX2 | J4 pin 1 |
| Z6 | 4 | D4 | J4 pin 3 |
| Z7 | 34 | D34 | J5 pin 1 |
| Z8 | 35 | D35 | J5 pin 3 |
| Z9 | 36 | VP | J6 pin 1 |
| Z10 | 39 | VN | J6 pin 3 |

GPIO34, GPIO35, GPIO36, and GPIO39 are input-only and have no internal pull-ups; each uses an external pull-up to 3.3V. GPIO1/3 remain available for UART logging/programming. GPIO2, GPIO5, GPIO12, and GPIO15 are not configured as GPIO functions; GPIO14 is also unused due to the documented boot-time transient.