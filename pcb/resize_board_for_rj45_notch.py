from pathlib import Path

import pcbnew


PCB_FILE = Path(__file__).resolve().parent / "Alarm Panel.kicad_pcb"
BOARD_WIDTH_MM = 110.0
BOARD_HEIGHT_MM = 80.0
BOARD_EDGE_INSET_MM = 2.0
BOTTOM_TERMINAL_FRONT_MARGIN_MM = 3.2
BOTTOM_TERMINAL_BODY_GAP_MM = 2.0
RJ45_NEAR_EDGE_OFFSET_MM = 34.0
RJ45_RIGHT_EDGE_OFFSET_MM = 52.3
RJ45_TOP_OFFSET_MM = -9.69
RJ45_BOTTOM_OFFSET_MM = 6.51
RJ45_CLEARANCE_MM = 1.0
W5500_MODULE_WIDTH_MM = 55.1
ESP32_HEADER_PIN_X_OFFSET_MM = 17.78
ESP32_HEADER_EDGE_CENTER_INSET_MM = 2.0


def mm(value):
    return pcbnew.FromMM(value)


def vector(x_mm, y_mm):
    return pcbnew.VECTOR2I(mm(x_mm), mm(y_mm))


def footprint_by_reference(board, reference):
    return next(
        (footprint for footprint in board.GetFootprints() if footprint.GetReference() == reference),
        None,
    )


def edge_bounds(board):
    edge_items = [
        item for item in board.GetDrawings()
        if item.GetLayer() == pcbnew.Edge_Cuts
    ]
    if not edge_items:
        raise RuntimeError("Board has no Edge.Cuts outline")
    points = [point for item in edge_items for point in (item.GetStart(), item.GetEnd())]
    return (
        pcbnew.ToMM(min(point.x for point in points)),
        pcbnew.ToMM(min(point.y for point in points)),
        pcbnew.ToMM(max(point.x for point in points)),
        pcbnew.ToMM(max(point.y for point in points)),
    )


def add_edge_segment(board, start, end):
    edge = pcbnew.PCB_SHAPE(board)
    edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
    edge.SetStart(vector(*start))
    edge.SetEnd(vector(*end))
    edge.SetLayer(pcbnew.Edge_Cuts)
    edge.SetWidth(mm(0.05))
    board.Add(edge)


def set_outline(board, left, top, right, bottom, notch_left, notch_top, notch_bottom):
    old_edges = [
        item for item in board.GetDrawings()
        if item.GetLayer() == pcbnew.Edge_Cuts
    ]
    for edge in old_edges:
        board.Remove(edge)

    outline = [
        (left, top),
        (right, top),
        (right, notch_top),
        (notch_left, notch_top),
        (notch_left, notch_bottom),
        (right, notch_bottom),
        (right, bottom),
        (left, bottom),
    ]
    for index, start in enumerate(outline):
        add_edge_segment(board, start, outline[(index + 1) % len(outline)])


def center_bottom_terminal_row(board, left, right):
    references = ["J11", "J2", "J3", "J4", "J5", "J6", "J7", "J12"]
    terminals = []
    total_body_width = 0
    for reference in references:
        footprint = footprint_by_reference(board, reference)
        if footprint is None:
            raise RuntimeError(f"Expected bottom connector {reference}")
        fab_shapes = [
            item for item in footprint.GraphicalItems()
            if isinstance(item, pcbnew.PCB_SHAPE) and item.GetLayer() == pcbnew.F_Fab
        ]
        if not fab_shapes:
            raise RuntimeError(f"No F.Fab body outline found for {reference}")
        body_left = min(item.GetBoundingBox().GetLeft() for item in fab_shapes)
        body_right = max(item.GetBoundingBox().GetRight() for item in fab_shapes)
        body_width = body_right - body_left
        terminals.append((footprint, body_left, body_width))
        total_body_width += body_width

    gap = mm(BOTTOM_TERMINAL_BODY_GAP_MM)
    total_gap_width = gap * (len(terminals) - 1)
    cursor = mm(left) + (mm(right - left) - total_body_width - total_gap_width) // 2

    for footprint, body_left, body_width in terminals:
        position = footprint.GetPosition()
        delta_x = cursor - body_left
        footprint.SetPosition(pcbnew.VECTOR2I(position.x + delta_x, position.y))
        cursor += body_width + gap


def main():
    board = pcbnew.LoadBoard(str(PCB_FILE))
    left, top, old_right, old_bottom = edge_bounds(board)
    right = left + BOARD_WIDTH_MM
    bottom = top + BOARD_HEIGHT_MM
    width_delta = right - old_right

    j9 = footprint_by_reference(board, "J9")
    j10 = footprint_by_reference(board, "J10")
    if j9 is None or j10 is None:
        raise RuntimeError("Expected J9 ESP32 and J10 W5500 footprints on the board")

    j10_position = j10.GetPosition()
    j10_y = pcbnew.ToMM(j10_position.y)
    j10.SetPosition(vector(right - RJ45_RIGHT_EDGE_OFFSET_MM, j10_y))

    j9_position = j9.GetPosition()
    j9.SetOrientationDegrees(180)
    j9.SetPosition(vector(
        right - ESP32_HEADER_PIN_X_OFFSET_MM - ESP32_HEADER_EDGE_CENTER_INSET_MM,
        pcbnew.ToMM(j9_position.y),
    ))

    for reference in ("H1", "H2", "H3", "H4"):
        hole = footprint_by_reference(board, reference)
        if hole is None:
            raise RuntimeError(f"Expected mounting-hole footprint {reference}")
        x_mm = left + BOARD_EDGE_INSET_MM if reference in ("H1", "H4") else right - BOARD_EDGE_INSET_MM
        y_mm = top + BOARD_EDGE_INSET_MM if reference in ("H1", "H2") else bottom - BOARD_EDGE_INSET_MM
        hole.SetPosition(vector(x_mm, y_mm))

    for reference in ("C1", "C2", "C3"):
        capacitor = footprint_by_reference(board, reference)
        if capacitor is None:
            raise RuntimeError(f"Expected rail capacitor {reference}")
        position = capacitor.GetPosition()
        capacitor.SetPosition(vector(pcbnew.ToMM(position.x) + width_delta, pcbnew.ToMM(position.y)))

    terminal_y = bottom - BOTTOM_TERMINAL_FRONT_MARGIN_MM
    for reference in ["J11", "J2", "J3", "J4", "J5", "J6", "J7", "J12"]:
        terminal = footprint_by_reference(board, reference)
        position = terminal.GetPosition()
        terminal.SetPosition(vector(pcbnew.ToMM(position.x), terminal_y))
    center_bottom_terminal_row(board, left, right)

    notch_left = right - (RJ45_RIGHT_EDGE_OFFSET_MM - RJ45_NEAR_EDGE_OFFSET_MM) - RJ45_CLEARANCE_MM
    notch_top = j10_y + RJ45_TOP_OFFSET_MM - RJ45_CLEARANCE_MM
    notch_bottom = j10_y + RJ45_BOTTOM_OFFSET_MM + RJ45_CLEARANCE_MM
    set_outline(board, left, top, right, bottom, notch_left, notch_top, notch_bottom)

    pcbnew.SaveBoard(str(PCB_FILE), board)
    print(f"Updated {PCB_FILE}")
    print(f"Board bounds: {left:.2f},{top:.2f} to {right:.2f},{bottom:.2f} mm ({BOARD_WIDTH_MM:g} x {BOARD_HEIGHT_MM:g} mm)")
    print(f"Centered bottom terminal row with {BOTTOM_TERMINAL_BODY_GAP_MM:.1f} mm body gaps.")
    print(f"RJ45 notch: x={notch_left:.2f}..{right:.2f}, y={notch_top:.2f}..{notch_bottom:.2f} mm; 1 mm clearance")
    print(f"Shifted C1-C3 by {width_delta:.2f} mm to absorb the width reduction in the resistor-capacitor gap.")
    print("Preserved all other component placements except right-edge-aligned modules/holes and bottom-edge connectors.")


if __name__ == "__main__":
    main()