import pcbnew

from project_paths import PROJECT_DIR


PCB_FILE = PROJECT_DIR / "Alarm Panel.kicad_pcb"
REF_Y_MM = 71.3
PIN_LABEL_Y_MM = 70.4
PIN_LABEL_SIZE_MM = 0.8
REF_SIZE_MM = 1.0
LABEL_REGION_TOP_MM = 66.6

# Zones are numbered 1-9, A-C to match the ESP Home display.
PIN_LABELS = {
    "J2": ["1", "GND", "2"],
    "J3": ["3", "GND", "4"],
    "J4": ["5", "GND", "6"],
    "J5": ["7", "GND", "8"],
    "J6": ["9", "GND", "A"],
        "J7": ["NC", "GND", "NC"],
    "J11": ["12V+", "GND"],
    "J12": ["12V+", "GND"],
}


def mm(value):
    return pcbnew.FromMM(value)


def main():
    board = pcbnew.LoadBoard(str(PCB_FILE))

    rows = []
    for footprint in board.GetFootprints():
        ref = footprint.GetReference()
        if ref not in PIN_LABELS:
            continue
        box = footprint.GetBoundingBox(False, False)
        pads = sorted(
            ((int(p.GetNumber()), pcbnew.ToMM(p.GetPosition().x)) for p in footprint.Pads() if p.GetNumber())
        )
        rows.append((footprint, pcbnew.ToMM(box.GetCenter().x), pads))

    min_x = min(x for _, _, pads in rows for _, x in pads) - 1.0
    max_x = max(x for _, _, pads in rows for _, x in pads) + 1.0
    for drawing in list(board.GetDrawings()):
        if (
            isinstance(drawing, pcbnew.PCB_TEXT)
            and drawing.GetLayer() == pcbnew.F_SilkS
            and pcbnew.ToMM(drawing.GetPosition().y) > LABEL_REGION_TOP_MM
            and min_x < pcbnew.ToMM(drawing.GetPosition().x) < max_x
        ):
            board.Remove(drawing)

    count = 0
    for footprint, center_x, pads in rows:
        ref = footprint.GetReference()
        field = footprint.Reference()
        field.SetVisible(True)
        field.SetLayer(pcbnew.F_SilkS)
        field.SetTextAngleDegrees(0)
        field.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        field.SetTextSize(pcbnew.VECTOR2I(mm(REF_SIZE_MM), mm(REF_SIZE_MM)))
        field.SetPosition(pcbnew.VECTOR2I(mm(center_x), mm(REF_Y_MM)))

        for (number, x), label in zip(pads, PIN_LABELS[ref]):
            text = pcbnew.PCB_TEXT(board)
            text.SetText(label)
            text.SetLayer(pcbnew.F_SilkS)
            text.SetTextSize(pcbnew.VECTOR2I(mm(PIN_LABEL_SIZE_MM), mm(PIN_LABEL_SIZE_MM)))
            text.SetTextThickness(mm(0.12))
            text.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
            text.SetTextAngleDegrees(90)
            text.SetPosition(pcbnew.VECTOR2I(mm(x), mm(PIN_LABEL_Y_MM)))
            board.Add(text)
            count += 1

    pcbnew.SaveBoard(str(PCB_FILE), board)
    print(f"Added {count} terminal pin labels")


if __name__ == "__main__":
    main()
