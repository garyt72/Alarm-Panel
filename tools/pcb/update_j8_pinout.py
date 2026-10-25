import pcbnew

import repair_schematic_metadata as metadata
import wire_schematic_pins as wiring
from project_paths import PROJECT_DIR


PCB_DIR = PROJECT_DIR
PCB_FILE = PCB_DIR / "Alarm Panel.kicad_pcb"
PIN_ORDER = {"1": "EN", "2": "IN+", "3": "IN-", "4": "OUT-", "5": "OUT+"}
PIN_NETS = {"1": "NC", "2": "12V", "3": "GND", "4": "GND", "5": "5V"}
PCB_LABELS = {"1": "EN:NC", "2": "IN+:12V", "3": "IN-:GND", "4": "OUT-:GND", "5": "OUT+:5V"}
OLD_SCHEMATIC_LABELS = {"1": "5V", "2": "GND", "3": "12V", "4": "GND", "5": None}
OLD_PCB_LABELS = {"1": "OUT+:5V", "2": "OUT-:GND", "3": "IN+:12V", "4": "IN-:GND", "5": "EN"}
EPSILON = 0.001


def schematic_pin_positions(root):
    symbols = wiring.symbol_definitions(root)
    symbol = next(
        item for item in root
        if isinstance(item, list) and item and item[0] == "symbol"
        and any(isinstance(p, list) and p[:2] == ["property", metadata.quote("Reference")] and p[2].strip('"') == "J8" for p in item)
    )
    lib_id = metadata.direct_child(symbol, "lib_id")[1].strip('"')
    definition = symbols[lib_id]
    origin = metadata.direct_child(symbol, "at")
    x0, y0, angle = float(origin[1]), float(origin[2]), int(float(origin[3]))
    if angle != 90:
        raise RuntimeError(f"J8 is rotated {angle} degrees; expected its current 90-degree symbol orientation")

    pin_positions = {}
    for pin in metadata.find_all(definition, "pin"):
        number = metadata.direct_child(pin, "number")[1].strip('"')
        if number not in PIN_ORDER:
            continue
        at = metadata.direct_child(pin, "at")
        local_x, local_y = float(at[1]), float(at[2])
        pin_positions[number] = (x0 - local_y, y0 + local_x)
    return pin_positions


def update_schematic():
    root = metadata.parse(metadata.SCHEMATIC.read_text(encoding="utf-8"))
    positions = schematic_pin_positions(root)
    old_items = []
    for number, expected_old in OLD_SCHEMATIC_LABELS.items():
        px, py = positions[number]
        stubs = []
        for wire in root:
            if not isinstance(wire, list) or not wire or wire[0] != "wire":
                continue
            pts = metadata.direct_child(wire, "pts")
            coords = [
                (float(point[1]), float(point[2]))
                for point in pts[1:]
                if isinstance(point, list) and point and point[0] == "xy"
            ]
            if len(coords) == 2 and any(abs(x-px) < EPSILON and abs(y-py) < EPSILON for x, y in coords):
                pin_index = next(i for i, (x, y) in enumerate(coords) if abs(x-px) < EPSILON and abs(y-py) < EPSILON)
                stubs.append((coords[1-pin_index], wire))
        if number == "5":
            if stubs:
                raise RuntimeError("J8 pin 5 unexpectedly has a label wire stub")
            anchor_x, anchor_y = px, py
        else:
            if len(stubs) != 1:
                raise RuntimeError(f"Expected one wire stub for J8 pin {number}, found {len(stubs)}")
            (anchor_x, anchor_y), wire = stubs[0]
            old_items.append(wire)
        matches = []
        for item in root:
            if not isinstance(item, list) or not item or item[0] not in {"global_label", "no_connect"}:
                continue
            at = metadata.direct_child(item, "at")
            if not at or abs(float(at[1])-anchor_x) >= EPSILON or abs(float(at[2])-anchor_y) >= EPSILON:
                continue
            if expected_old is None and item[0] == "no_connect":
                matches.append(item)
            elif expected_old is not None and item[0] == "global_label" and item[1].strip('"') == expected_old:
                matches.append(item)
        if len(matches) != 1:
            raise RuntimeError(f"Expected existing J8 pin {number} label {expected_old}, found {len(matches)}")
        old_items.append(matches[0])

    root[:] = [item for item in root if all(item is not old for old in old_items)]
    for number in PIN_ORDER:
        x, y = positions[number]
        if PIN_NETS[number] == "NC":
            root.append(wiring.make_no_connect(x, y))
        else:
            root.append(wiring.make_label(PIN_NETS[number], x, y))
    metadata.SCHEMATIC.write_text(metadata.render(root), encoding="utf-8")


def update_board_labels():
    board = pcbnew.LoadBoard(str(PCB_FILE))
    footprint = next(item for item in board.GetFootprints() if item.GetReference() == "J8")
    pad_positions = {
        pad.GetNumber(): pad.GetPosition()
        for pad in footprint.Pads()
        if pad.GetNumber() in PCB_LABELS
    }
    updated = set()
    for text in board.GetDrawings():
        if not isinstance(text, pcbnew.PCB_TEXT) or text.GetLayer() != pcbnew.F_SilkS:
            continue
        if text.GetText() not in OLD_PCB_LABELS.values():
            continue
        dx, dy = text.GetPosition().x, text.GetPosition().y
        nearest = min(
            pad_positions,
            key=lambda number: (dx-pad_positions[number].x)**2 + (dy-pad_positions[number].y)**2,
        )
        pad = pad_positions[nearest]
        if abs(dx-pad.x) <= pcbnew.FromMM(0.1) and abs(dy-pad.y) <= pcbnew.FromMM(3.0):
            if text.GetText() != OLD_PCB_LABELS[nearest]:
                continue
            text.SetText(PCB_LABELS[nearest])
            updated.add(nearest)
    if updated != set(PCB_LABELS):
        raise RuntimeError(f"Updated J8 board labels for pins {sorted(updated)}, expected all five pins")
    pcbnew.SaveBoard(str(PCB_FILE), board)
    return updated


def main():
    update_schematic()
    updated = update_board_labels()
    print("J8 physical map applied: pin 1 EN/NC, 2 IN+/12V, 3 IN-/GND, 4 OUT-/GND, 5 OUT+/5V")
    print("Updated PCB label pins:", ", ".join(sorted(updated)))


if __name__ == "__main__":
    main()
