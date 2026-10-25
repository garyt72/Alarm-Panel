from pathlib import Path

import pcbnew


PCB_DIR = Path(__file__).resolve().parent
PCB_FILE = PCB_DIR / "Alarm Panel.kicad_pcb"
FOOTPRINT_LIBRARY = PCB_DIR / "footprints" / "AlarmPanel_THT.pretty"

FUSE_CENTER_X_MM = 31.0
FUSE_CENTER_Y_MM = 7.5


def mm(value):
    return pcbnew.FromMM(value)


def vector(x_mm, y_mm):
    return pcbnew.VECTOR2I(mm(x_mm), mm(y_mm))


def main():
    board = pcbnew.LoadBoard(str(PCB_FILE))
    old_footprint = next(
        (item for item in board.GetFootprints() if item.GetReference() == "F1"),
        None,
    )
    if old_footprint is None:
        raise RuntimeError("F1 footprint was not found on the board")

    fuse_holder = pcbnew.FootprintLoad(str(FOOTPRINT_LIBRARY), "FuseHolder_Body24x10_P23.6mm")
    if fuse_holder is None:
        raise RuntimeError("Could not load project-local fuse-holder footprint")

    fuse_holder.SetReference("F1")
    fuse_holder.SetValue("2A time-delay 5x20mm")
    fuse_holder.SetPosition(vector(FUSE_CENTER_X_MM, FUSE_CENTER_Y_MM))
    fuse_holder.Reference().SetPosition(vector(FUSE_CENTER_X_MM, 14.0))

    board.Remove(old_footprint)
    board.Add(fuse_holder)
    pcbnew.SaveBoard(str(PCB_FILE), board)
    print(f"Replaced F1 on {PCB_FILE} with the drawing-based fuse-holder footprint")
    print("Other component placements were preserved.")


if __name__ == "__main__":
    main()
