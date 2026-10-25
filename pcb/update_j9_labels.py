from pathlib import Path
import math

import pcbnew

from add_pin_labels import J9_CARRIER_NAMES, label_text, placement


PCB_FILE = Path(__file__).resolve().parent / "Alarm Panel.kicad_pcb"
LEGACY_J9_LABEL_ROWS_MM = (38.5, 61.0)


def mm(value):
    return pcbnew.FromMM(value)


def to_mm(value):
    return pcbnew.ToMM(value)


def local_to_board(footprint, x_mm, y_mm):
    angle = math.radians(footprint.GetOrientationDegrees())
    origin = footprint.GetPosition()
    x0, y0 = to_mm(origin.x), to_mm(origin.y)
    return (
        x0 + x_mm * math.cos(angle) + y_mm * math.sin(angle),
        y0 - x_mm * math.sin(angle) + y_mm * math.cos(angle),
    )


def add_segment(footprint, layer, start, end, width_mm):
    shape = pcbnew.PCB_SHAPE(footprint)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetLayer(layer)
    shape.SetWidth(mm(width_mm))
    shape.SetStart(pcbnew.VECTOR2I(mm(start[0]), mm(start[1])))
    shape.SetEnd(pcbnew.VECTOR2I(mm(end[0]), mm(end[1])))
    footprint.Add(shape)


def add_antenna_callout(footprint):
    graphics = list(footprint.GraphicalItems())
    existing = [
        item for item in graphics
        if isinstance(item, pcbnew.PCB_TEXT)
        and item.GetLayer() == pcbnew.F_Fab
        and item.GetText() == "Antenna"
    ]
    if existing:
        return

    corners_local = [(-29.0, -9.5), (-21.0, -9.5), (-21.0, 8.5), (-29.0, 8.5)]
    corners = [local_to_board(footprint, *corner) for corner in corners_local]
    for start, end in zip(corners, corners[1:] + corners[:1]):
        add_segment(footprint, pcbnew.F_Fab, start, end, 0.1)

    text = pcbnew.PCB_TEXT(footprint)
    text.SetText("Antenna")
    text.SetLayer(pcbnew.F_Fab)
    text.SetTextSize(pcbnew.VECTOR2I(mm(2.0), mm(2.0)))
    text.SetTextThickness(mm(0.1))
    text.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    text.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_BOTTOM)
    text.SetTextAngleDegrees((footprint.GetOrientationDegrees() + 90) % 360)
    x, y = local_to_board(footprint, -24.5, 5.5)
    text.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    footprint.Add(text)


def main():
    board = pcbnew.LoadBoard(str(PCB_FILE))
    footprint = next(item for item in board.GetFootprints() if item.GetReference() == "J9")
    pads = {
        pad.GetNumber(): (to_mm(pad.GetPosition().x), to_mm(pad.GetPosition().y))
        for pad in footprint.Pads()
        if pad.GetNumber() in J9_CARRIER_NAMES
    }
    footprint_labels = [
        item for item in footprint.GraphicalItems()
        if isinstance(item, pcbnew.PCB_TEXT)
        and item.GetLayer() == pcbnew.F_SilkS
    ]
    moved = 0
    for text in footprint_labels:
        x, y = to_mm(text.GetPosition().x), to_mm(text.GetPosition().y)
        number = min(pads, key=lambda item: (x - pads[item][0]) ** 2 + (y - pads[item][1]) ** 2)
        pad_x, pad_y = pads[number]
        if (x - pad_x) ** 2 + (y - pad_y) ** 2 > 16:
            continue
        position = text.GetPosition()
        text.SetText(label_text("J9", number))
        text.SetPosition(pcbnew.VECTOR2I(mm(pad_x), position.y))
        moved += 1

    add_antenna_callout(footprint)
    pcbnew.SaveBoard(str(PCB_FILE), board)
    print(f"Aligned {moved} J9 footprint-attached labels to their pad X coordinates; Y positions and text formatting were preserved.")


if __name__ == "__main__":
    main()