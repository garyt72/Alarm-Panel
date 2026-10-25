import uuid

import repair_schematic_metadata as metadata


SCHEMATIC = metadata.SCHEMATIC

PIN_NETS = {
    "J1": {"1": "12V_IN", "2": "GND", "3": "GND"},
    "F1": {"1": "12V_IN", "2": "FUSED_12V"},
    "D1": {"1": "12V", "2": "FUSED_12V"},
    "C1": {"1": "12V", "2": "GND"},
    "J8": {"2": "12V", "3": "GND", "4": "GND", "5": "5V"},
    "C2": {"1": "5V", "2": "GND"},
    "C3": {"1": "3V3", "2": "GND"},
    "J9": {
        "1": "Z1",
        "3": "OLED_SCL",
        "9": "OLED_SDA",
        "11": "Z2",
        "13": "Z3",
        "17": "Z4",
        "19": "Z5",
        "21": "Z6",
        "27": "GND",
        "29": "3V3",
        "4": "Z10",
        "4": "Z10",
        "6": "Z9",
        "8": "Z8",
        "10": "Z7",
        "14": "ARM_LED",
        "16": "MOSI",
        "18": "MISO",
        "20": "SCS",
        "26": "SCLK",
        "28": "GND",
        "30": "5V",
    },
    "J10": {
        "9": "5V",
        "10": "3V3",
        "7": "GND",
        "8": "MISO",
        "6": "MOSI",
        "4": "SCS",
        "2": "SCLK",
    },
    "J2": {"1": "Z1", "2": "GND", "3": "Z2"},
    "J3": {"1": "Z3", "2": "GND", "3": "Z4"},
    "J4": {"1": "Z5", "2": "GND", "3": "Z6"},
    "J5": {"1": "Z7", "2": "GND", "3": "Z8"},
    "J6": {"1": "Z9", "2": "GND", "3": "Z10"},
    "J7": {"2": "GND"},
    "J11": {"1": "12V", "2": "GND"},
    "J12": {"1": "12V", "2": "GND"},
    "J13": {"1": "12V", "2": "SIREN_DRAIN"},
    "Q1": {"1": "Q1_GATE", "2": "SIREN_DRAIN", "3": "GND"},
    "U1": {
        "1": "12V",
        "2": "SIREN_GATE",
        "4": "GND",
        "5": "GND",
        "6": "GATE_DRIVER_OUT",
        "7": "GATE_DRIVER_OUT",
        "8": "12V",
    },
    "R5": {"1": "GATE_DRIVER_OUT", "2": "Q1_GATE"},
    "R6": {"1": "Q1_GATE", "2": "GND"},
    "R7": {"1": "SIREN_GATE", "2": "GND"},
    "C4": {"1": "12V", "2": "GND"},
    "C5": {"1": "12V", "2": "GND"},
    "D2": {"1": "12V", "2": "SIREN_DRAIN"},
    "#FLG01": {"1": "12V"},
    "#FLG02": {"1": "GND"},
    "R1": {"1": "3V3", "2": "Z7"},
    "R2": {"1": "3V3", "2": "Z8"},
    "R3": {"1": "3V3", "2": "Z9"},
    "R4": {"1": "3V3", "2": "Z10"},
}

NO_CONNECTS = {
    "J8": ["1"],
    "J9": ["2", "5", "7", "15", "22", "23", "24", "25"],
    "J10": ["1", "3", "5"],
    "J7": ["1", "3"],
    "U1": ["3"],
}


def symbol_definitions(root):
    return {
        definition[1].strip('"'): definition
        for definition in metadata.direct_child(root, "lib_symbols")
        if isinstance(definition, list) and definition and definition[0] == "symbol"
    }


def snap_symbol_to_grid(symbol):
    origin = metadata.direct_child(symbol, "at")
    old_x, old_y = float(origin[1]), float(origin[2])
    new_x = round(old_x / 1.27) * 1.27
    new_y = round(old_y / 1.27) * 1.27
    delta_x, delta_y = new_x - old_x, new_y - old_y
    origin[1], origin[2] = f"{new_x:.4f}", f"{new_y:.4f}"

    for prop in symbol:
        if not isinstance(prop, list) or not prop or prop[0] != "property":
            continue
        prop_at = metadata.direct_child(prop, "at")
        if prop_at:
            prop_at[1] = f"{float(prop_at[1]) + delta_x:.4f}"
            prop_at[2] = f"{float(prop_at[2]) + delta_y:.4f}"


def pin_positions(symbol, definitions):
    lib_id = metadata.direct_child(symbol, "lib_id")[1].strip('"')
    definition = definitions[lib_id]
    origin = metadata.direct_child(symbol, "at")
    x0, y0, angle = float(origin[1]), float(origin[2]), int(float(origin[3]))
    if angle != 0:
        raise ValueError(f"Rotated symbol not supported by this wiring pass: {lib_id} at {angle}")

    positions = {}
    for pin in metadata.find_all(definition, "pin"):
        number = metadata.direct_child(pin, "number")
        pin_at = metadata.direct_child(pin, "at")
        if number and pin_at:
            positions[number[1].strip('"')] = (x0 + float(pin_at[1]), y0 - float(pin_at[2]))
    return positions


def make_label(name, x, y):
    return [
        "global_label",
        metadata.quote(name),
        ["shape", "input"],
        ["at", f"{x:.4f}", f"{y:.4f}", "0"],
        ["fields_autoplaced"],
        ["effects", ["font", ["size", "1.27", "1.27"]], ["justify", "left"]],
        ["uuid", metadata.quote(str(uuid.uuid4()))],
    ]


def make_no_connect(x, y):
    return [
        "no_connect",
        ["at", f"{x:.4f}", f"{y:.4f}"],
        ["uuid", metadata.quote(str(uuid.uuid4()))],
    ]


def main():
    root = metadata.parse(SCHEMATIC.read_text(encoding="utf-8"))
    definitions = symbol_definitions(root)
    placed_symbols = {}
    for symbol in root:
        if not isinstance(symbol, list) or not symbol or symbol[0] != "symbol":
            continue
        reference_property = next(
            item for item in symbol
            if isinstance(item, list) and item[:2] == ["property", metadata.quote("Reference")]
        )
        reference = reference_property[2].strip('"')
        snap_symbol_to_grid(symbol)
        placed_symbols[reference] = symbol

    retained = [
        item for item in root
        if not isinstance(item, list) or not item or item[0] not in {"wire", "junction", "global_label", "no_connect", "text"}
    ]
    root[:] = retained

    for reference, pin_nets in PIN_NETS.items():
        symbol = placed_symbols[reference]
        positions = pin_positions(symbol, definitions)
        for pin_number, net_name in pin_nets.items():
            if pin_number not in positions:
                raise ValueError(f"{reference} has no pin {pin_number}")
            root.append(make_label(net_name, *positions[pin_number]))

    for reference, pin_numbers in NO_CONNECTS.items():
        positions = pin_positions(placed_symbols[reference], definitions)
        for pin_number in pin_numbers:
            if pin_number not in positions:
                raise ValueError(f"{reference} has no pin {pin_number}")
            root.append(make_no_connect(*positions[pin_number]))

    SCHEMATIC.write_text(metadata.render(root), encoding="utf-8")
    print(f"Added {sum(map(len, PIN_NETS.values()))} pin-attached net labels")
    print(f"Marked {sum(map(len, NO_CONNECTS.values()))} pins intentionally unconnected")


if __name__ == "__main__":
    main()