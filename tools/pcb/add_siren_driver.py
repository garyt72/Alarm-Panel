from pathlib import Path
import uuid

import pcbnew

import repair_schematic_metadata as metadata
from project_paths import PROJECT_DIR


PCB_DIR = PROJECT_DIR
PCB_FILE = PCB_DIR / "Alarm Panel.kicad_pcb"
STANDARD_FOOTPRINTS = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")
PARTS = [
    ("U1", "AlarmPanel:TC4420CPA", "TC4420CPA", "Package_DIP:DIP-8_W7.62mm"),
    ("R5", "Device:R", "10 ohm gate resistor", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"),
    ("R6", "Device:R", "10k Q1 gate pulldown", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"),
    ("R7", "Device:R", "10k driver input pulldown", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"),
    ("C4", "Device:C", "100 nF / 25 V", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"),
    ("C5", "Device:C", "1 uF / 25 V", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"),
    ("D2", "Device:D_Schottky", "1N5822 flyback", "Diode_THT:D_DO-201AD_P5.08mm_Vertical_AnodeUp"),
]
POWER_FLAGS = [
    ("#FLG01", 204.47, 209.55),
    ("#FLG02", 204.47, 222.25),
]
SYMBOL_PLACEMENTS = {
    "U1": (213.36, 215.90),
    "R5": (233.68, 215.90),
    "R6": (248.92, 228.60),
    "R7": (233.68, 243.84),
    "C4": (213.36, 246.38),
    "C5": (233.68, 246.38),
    "D2": (248.92, 246.38),
}
BOARD_PLACEMENTS = {
    "U1": ("Package_DIP", "DIP-8_W7.62mm", "TC4420CPA", 18.0, 68.5, 270),
    "R5": ("Resistor_THT", "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", "10 ohm", 31.0, 70.0, 0),
    "R6": ("Resistor_THT", "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", "10k gate pulldown", 41.0, 70.0, 0),
    "R7": ("Resistor_THT", "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal", "10k input pulldown", 51.0, 70.0, 0),
    "C4": ("Capacitor_THT", "C_Disc_D5.0mm_W2.5mm_P5.00mm", "100 nF / 25 V", 30.5, 61.0, 0),
    "C5": ("Capacitor_THT", "C_Disc_D5.0mm_W2.5mm_P5.00mm", "1 uF / 25 V", 30.5, 65.5, 0),
    "D2": ("Diode_THT", "D_DO-201AD_P5.08mm_Vertical_AnodeUp", "1N5822 flyback", 8.5, 60.0, 0),
}


def property_node(name, value, property_id, x, y, hidden=False):
    effects = ["effects", ["font", ["size", "1.27", "1.27"]]]
    if hidden:
        effects.append("hide")
    else:
        effects.append(["justify", "left"])
    return [
        "property",
        metadata.quote(name),
        metadata.quote(value),
        ["id", str(property_id)],
        ["at", f"{x:.4f}", f"{y:.4f}", "0"],
        effects,
    ]


def make_symbol(reference, lib_id, value, footprint, x, y, schematic_uuid, definition, in_bom="yes", on_board="yes", hidden_fields=False):
    symbol = [
        "symbol",
        ["lib_id", metadata.quote(lib_id)],
        ["at", f"{x:.4f}", f"{y:.4f}", "0"],
        ["unit", "1"],
        ["in_bom", in_bom],
        ["on_board", on_board],
        ["uuid", metadata.quote(str(uuid.uuid4()))],
        property_node("Reference", reference, 0, x, y - 8.0, hidden_fields),
        property_node("Value", value, 1, x, y - 6.0, hidden_fields),
        property_node("Footprint", footprint, 2, x, y, True),
    ]
    for pin_number in metadata.symbol_pin_numbers(definition):
        symbol.append(["pin", pin_number, ["uuid", metadata.quote(str(uuid.uuid4()))]])
    symbol.append([
        "instances",
        [
            "project",
            metadata.quote("Alarm Panel"),
            [
                "path",
                metadata.quote(f"/{schematic_uuid}"),
                ["reference", metadata.quote(reference)],
                ["unit", "1"],
            ],
        ],
    ])
    return symbol


def add_schematic_parts():
    root = metadata.parse(metadata.SCHEMATIC.read_text(encoding="utf-8"))
    existing = {
        next(
            item[2].strip('"')
            for item in symbol
            if isinstance(item, list) and item[:2] == ["property", metadata.quote("Reference")]
        )
        for symbol in root
        if isinstance(symbol, list) and symbol and symbol[0] == "symbol"
    }
    expected = {part[0] for part in PARTS} | {flag[0] for flag in POWER_FLAGS}
    if expected <= existing:
        return False

    lib_symbols = metadata.direct_child(root, "lib_symbols")
    definitions = {
        item[1].strip('"'): item
        for item in lib_symbols
        if isinstance(item, list) and item and item[0] == "symbol"
    }
    library_ids = [part[1] for part in PARTS] + ["power:PWR_FLAG"]
    for lib_id in library_ids:
        if lib_id not in definitions:
            library_name, symbol_name = lib_id.split(":", 1)
            definition = metadata.library_symbol(library_name, symbol_name)
            lib_symbols.append(definition)
            definitions[lib_id] = definition

    schematic_uuid = metadata.direct_child(root, "uuid")[1].strip('"')
    for reference, lib_id, value, footprint in PARTS:
        if reference in existing:
            continue
        x, y = SYMBOL_PLACEMENTS[reference]
        root.append(make_symbol(reference, lib_id, value, footprint, x, y, schematic_uuid, definitions[lib_id]))
    for reference, x, y in POWER_FLAGS:
        if reference in existing:
            continue
        root.append(make_symbol(
            reference,
            "power:PWR_FLAG",
            "PWR_FLAG",
            "",
            x,
            y,
            schematic_uuid,
            definitions["power:PWR_FLAG"],
            in_bom="no",
            on_board="no",
            hidden_fields=True,
        ))
    metadata.SCHEMATIC.write_text(metadata.render(root), encoding="utf-8")
    return True


def add_board_parts():
    board = pcbnew.LoadBoard(str(PCB_FILE))
    footprints = {footprint.GetReference(): footprint for footprint in board.GetFootprints()}
    existing = set(footprints)
    expected = set(BOARD_PLACEMENTS)
    if expected & existing:
        if expected <= existing:
            for reference, (_, _, _, x, y, rotation) in BOARD_PLACEMENTS.items():
                footprint = footprints[reference]
                footprint.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
                footprint.SetOrientationDegrees(rotation)
            pcbnew.SaveBoard(str(PCB_FILE), board)
            return True
        raise RuntimeError(f"Partial siren-driver PCB already exists: {sorted(expected & existing)}")

    for reference, (library, name, value, x, y, rotation) in BOARD_PLACEMENTS.items():
        library_path = STANDARD_FOOTPRINTS / f"{library}.pretty"
        footprint = pcbnew.FootprintLoad(str(library_path), name)
        if footprint is None:
            raise RuntimeError(f"Could not load footprint {library}:{name}")
        footprint.SetReference(reference)
        footprint.SetValue(value)
        footprint.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        footprint.SetOrientationDegrees(rotation)
        board.Add(footprint)

    pcbnew.SaveBoard(str(PCB_FILE), board)
    return True


def main():
    schematic_changed = add_schematic_parts()
    board_changed = add_board_parts()
    print(f"Schematic parts {'added' if schematic_changed else 'already present'}: {', '.join(part[0] for part in PARTS)}")
    print(f"PCB footprints {'added' if board_changed else 'already present'}: {', '.join(BOARD_PLACEMENTS)}")


if __name__ == "__main__":
    main()