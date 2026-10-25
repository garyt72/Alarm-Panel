import pcbnew

from project_paths import PROJECT_DIR
from wire_schematic_pins import PIN_NETS

PCB_FILE = PROJECT_DIR / "Alarm Panel.kicad_pcb"
GROUP_NAME = "pin-labels"
REFS = ("J8", "J10", "U1", "Q1")
OFFSET_MM = 1.8
J9_ROW_CENTER_Y_MM = 49.9
J9_LABEL_ROW_Y_MM = 49.9
J9_LABEL_LANE_OFFSET_MM = 0.6

J9_CARRIER_NAMES = {
    "1": "D23", "3": "D22", "5": "TX0", "7": "RX0", "9": "D21",
    "11": "D19", "13": "D18", "15": "D5", "17": "TX2", "19": "RX2",
    "21": "D4", "23": "D2", "25": "D15", "27": "GND", "29": "3V3",
    "2": "EN", "4": "VP", "6": "VN", "8": "D34", "10": "D35",
    "12": "D32", "14": "D33", "16": "D25", "18": "D26", "20": "D27",
    "22": "D14", "24": "D12", "26": "D13", "28": "GND", "30": "VIN",
}
J8_MODULE_NAMES = {"1": "EN", "2": "IN+", "3": "IN-", "4": "OUT-", "5": "OUT+"}
EXTRA_NAMES = {
    "J8": {"1": "NC"},
    "J9": {"2": "EN", "5": "TX0", "7": "RX0", "15": "D5", "22": "D14", "23": "D2", "24": "D12", "25": "D15"},
    "J10": {"1": "NC", "3": "INT", "5": "RST"},
    "U1": {"3": "NC"},
    "Q1": {"1": "G", "2": "D", "3": "S"},
}
NAME_OVERRIDES = {
    "Q1": {"1": "G", "2": "D", "3": "S"},
    "U1": {"1": "VDD", "2": "IN", "6": "OUT", "7": "OUT", "8": "VDD", "4": "GND", "5": "GND"},
    "J9": {"12": "SIREN"},
}

# placement: (angle, h-justify, dx, dy) relative to pad, given pad location rules below
def mm(v):
    return pcbnew.FromMM(v)


def purpose(ref, number):
    if number in NAME_OVERRIDES.get(ref, {}):
        return NAME_OVERRIDES[ref][number]
    if number in PIN_NETS.get(ref, {}):
        return PIN_NETS[ref][number]
    return EXTRA_NAMES[ref][number]


def label_text(ref, number):
    if ref in ("J8", "J9"):
        name = (J8_MODULE_NAMES if ref == "J8" else J9_CARRIER_NAMES)[number]
        use = purpose(ref, number)
        return name if name == use else f"{name}:{use}"
    return purpose(ref, number)


def placement(ref, number, x, y):
    """Return (angle, justify, anchor_x, anchor_y) in mm."""
    n = int(number)
    if ref == "J9":
        lane = J9_LABEL_LANE_OFFSET_MM if n % 2 else -J9_LABEL_LANE_OFFSET_MM
        return 90, pcbnew.GR_TEXT_H_ALIGN_CENTER, x + lane, J9_LABEL_ROW_Y_MM
    if ref == "J8":
        return 90, pcbnew.GR_TEXT_H_ALIGN_LEFT, x, y - OFFSET_MM
    if ref == "J10":
        if n % 2 == 1:
            return 0, pcbnew.GR_TEXT_H_ALIGN_RIGHT, x - 3.3, y
        return 0, pcbnew.GR_TEXT_H_ALIGN_LEFT, x + OFFSET_MM, y
    if ref == "U1":
        if y < 65:
            return 0, pcbnew.GR_TEXT_H_ALIGN_CENTER, x, y - OFFSET_MM
        return 0, pcbnew.GR_TEXT_H_ALIGN_CENTER, x, y + OFFSET_MM
    if ref == "Q1":
        return 0, pcbnew.GR_TEXT_H_ALIGN_CENTER, x - OFFSET_MM, y
    raise ValueError(ref)


def main():
    board = pcbnew.LoadBoard(str(PCB_FILE))

    for group in list(board.Groups()):
        if group.GetName() == GROUP_NAME:
            for item in list(group.GetItems()):
                group.RemoveItem(item)
            board.Remove(group)

    pads = []
    for f in board.GetFootprints():
        if f.GetReference() in REFS:
            for p in f.Pads():
                if p.GetNumber():
                    pads.append((f.GetReference(), p.GetNumber(), pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)))

    wanted = {label_text(ref, number) for ref, number, _, _ in pads}
    wanted |= {purpose(ref, number) for ref, number, _, _ in pads}
    wanted |= {"SIREN_DRAIN", "Q1_GATE", "SIREN_GATE"}
    for drawing in list(board.GetDrawings()):
        if not isinstance(drawing, pcbnew.PCB_TEXT) or drawing.GetLayer() != pcbnew.F_SilkS:
            continue
        if drawing.GetText() not in wanted:
            continue
        dx, dy = pcbnew.ToMM(drawing.GetPosition().x), pcbnew.ToMM(drawing.GetPosition().y)
        if any(abs(dx - px) < 4 and abs(dy - py) < 4 for _, _, px, py in pads):
            board.Remove(drawing)

    count = 0
    for ref, number, x, y in pads:
        size = 0.8 if ref == "U1" else 0.9
        angle, justify, ax, ay = placement(ref, number, x, y)
        text = pcbnew.PCB_TEXT(board)
        text.SetText(label_text(ref, number))
        text.SetLayer(pcbnew.F_SilkS)
        text.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
        text.SetTextThickness(mm(0.12))
        text.SetHorizJustify(justify)
        text.SetTextAngleDegrees(angle)
        text.SetPosition(pcbnew.VECTOR2I(mm(ax), mm(ay)))
        board.Add(text)
        count += 1

    pcbnew.SaveBoard(str(PCB_FILE), board)
    print(f"Added {count} pin labels")


if __name__ == "__main__":
    main()
