from pathlib import Path

import pcbnew


PCB_FILE = Path(__file__).resolve().parent / "Alarm Panel.kicad_pcb"
CAPACITORS = {
    "C1": ("680 uF / 18 V", "12V CAP"),
    "C2": ("470 uF / 10 V", "5V CAP"),
    "C3": ("470 uF / 10 V", "3V3 CAP"),
}


def mm(value):
    return pcbnew.FromMM(value)


def vector(x_mm, y_mm):
    return pcbnew.VECTOR2I(mm(x_mm), mm(y_mm))


def main():
    board = pcbnew.LoadBoard(str(PCB_FILE))
    footprints = {footprint.GetReference(): footprint for footprint in board.GetFootprints()}

    for reference, (value, _) in CAPACITORS.items():
        if reference not in footprints:
            raise RuntimeError(f"Could not find {reference} on the PCB")
        footprints[reference].SetValue(value)

    rail_names = {rail_name for _, rail_name in CAPACITORS.values()}
    for drawing in list(board.GetDrawings()):
        if (
            isinstance(drawing, pcbnew.PCB_TEXT)
            and drawing.GetLayer() == pcbnew.F_SilkS
            and drawing.GetText() in rail_names
        ):
            board.Remove(drawing)

    for reference, (_, rail_name) in CAPACITORS.items():
        footprint = footprints[reference]
        position = footprint.GetPosition()
        label = pcbnew.PCB_TEXT(board)
        label.SetText(rail_name)
        label.SetPosition(vector(pcbnew.ToMM(position.x), pcbnew.ToMM(position.y) + 7.3))
        label.SetLayer(pcbnew.F_SilkS)
        label.SetTextSize(vector(0.8, 0.8))
        label.SetTextThickness(mm(0.12))
        board.Add(label)

    pcbnew.SaveBoard(str(PCB_FILE), board)
    print("Updated capacitor values and rail silkscreen labels without changing placements.")
    for reference, (value, rail_name) in CAPACITORS.items():
        print(f"{reference}: {value}, silkscreen {rail_name}")


if __name__ == "__main__":
    main()
