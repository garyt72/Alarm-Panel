from pathlib import Path

import pcbnew

from project_paths import PROJECT_DIR

PCB_DIR = PROJECT_DIR
FOOTPRINT_LIBRARY = PCB_DIR / "footprints" / "AlarmPanel_THT.pretty"
STANDARD_FOOTPRINTS = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")
OUTPUT_FILE = PCB_DIR / "Alarm Panel.kicad_pcb"

BOARD_WIDTH_MM = 110.0
BOARD_HEIGHT_MM = 80.0
BOARD_EDGE_INSET_MM = 2.0
TERMINAL_ROW_Y_MM = BOARD_HEIGHT_MM - 3.2
TERMINAL_BODY_GAP_MM = 1.75
ESP32_HEADER_PIN_X_OFFSET_MM = 17.78
ESP32_HEADER_EDGE_CENTER_INSET_MM = 2.0
ESP32_CENTER_X_MM = BOARD_WIDTH_MM - ESP32_HEADER_PIN_X_OFFSET_MM - ESP32_HEADER_EDGE_CENTER_INSET_MM
ESP32_CENTER_Y_MM = 49.9
W5500_PIN1_X_MM = BOARD_WIDTH_MM - 52.3
W5500_PIN1_Y_MM = 19.09
RJ45_NOTCH_CLEARANCE_MM = 1.0


def mm(value):
    return pcbnew.FromMM(value)


def vector(x_mm, y_mm):
    return pcbnew.VECTOR2I(mm(x_mm), mm(y_mm))


def add_edge_segment(board, start, end):
    edge = pcbnew.PCB_SHAPE(board)
    edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
    edge.SetStart(vector(*start))
    edge.SetEnd(vector(*end))
    edge.SetLayer(pcbnew.Edge_Cuts)
    edge.SetWidth(mm(0.05))
    board.Add(edge)


def load_footprint(name, reference, value, x_mm, y_mm):
    footprint = pcbnew.FootprintLoad(str(FOOTPRINT_LIBRARY), name)
    if footprint is None:
        raise RuntimeError(f"Could not load footprint {name}")
    footprint.SetReference(reference)
    footprint.SetValue(value)
    footprint.SetPosition(vector(x_mm, y_mm))
    return footprint


def load_standard_footprint(library, name, reference, value, x_mm, y_mm):
    library_path = STANDARD_FOOTPRINTS / f"{library}.pretty"
    footprint = pcbnew.FootprintLoad(str(library_path), name)
    if footprint is None:
        raise RuntimeError(f"Could not load standard footprint {library}:{name}")
    footprint.SetReference(reference)
    footprint.SetValue(value)
    footprint.SetPosition(vector(x_mm, y_mm))
    return footprint


def add_outline(board):
    notch_left = BOARD_WIDTH_MM - (52.3 - 34.0) - RJ45_NOTCH_CLEARANCE_MM
    notch_top = W5500_PIN1_Y_MM - 9.69 - RJ45_NOTCH_CLEARANCE_MM
    notch_bottom = W5500_PIN1_Y_MM + 6.51 + RJ45_NOTCH_CLEARANCE_MM
    outline_points = [
        (0.0, 0.0),
        (BOARD_WIDTH_MM, 0.0),
        (BOARD_WIDTH_MM, notch_top),
        (notch_left, notch_top),
        (notch_left, notch_bottom),
        (BOARD_WIDTH_MM, notch_bottom),
        (BOARD_WIDTH_MM, BOARD_HEIGHT_MM),
        (0.0, BOARD_HEIGHT_MM),
    ]
    for index, start in enumerate(outline_points):
        end = outline_points[(index + 1) % len(outline_points)]
        add_edge_segment(board, start, end)


def add_mounting_holes(board):
    hole_positions = [
        ("H1", BOARD_EDGE_INSET_MM, BOARD_EDGE_INSET_MM),
        ("H2", BOARD_WIDTH_MM - BOARD_EDGE_INSET_MM, BOARD_EDGE_INSET_MM),
        ("H3", BOARD_WIDTH_MM - BOARD_EDGE_INSET_MM, BOARD_HEIGHT_MM - BOARD_EDGE_INSET_MM),
        ("H4", BOARD_EDGE_INSET_MM, BOARD_HEIGHT_MM - BOARD_EDGE_INSET_MM),
    ]
    for reference, x_mm, y_mm in hole_positions:
        hole = load_footprint(
            "MountingHole_NPTH_2.0mm",
            reference,
            "2.0 mm NPTH",
            x_mm,
            y_mm,
        )
        board.Add(hole)


def add_bottom_terminal_row(board):
    row = [
        ("J11", "TerminalBlock_1x02_P2.54mm_Body5.60x6.40mm", 5.60),
        ("J2", "TerminalBlock_1x03_P2.54mm_Body8.15x6.40mm", 8.15),
        ("J3", "TerminalBlock_1x03_P2.54mm_Body8.15x6.40mm", 8.15),
        ("J4", "TerminalBlock_1x03_P2.54mm_Body8.15x6.40mm", 8.15),
        ("J5", "TerminalBlock_1x03_P2.54mm_Body8.15x6.40mm", 8.15),
        ("J6", "TerminalBlock_1x03_P2.54mm_Body8.15x6.40mm", 8.15),
        ("J7", "TerminalBlock_1x03_P2.54mm_Body8.15x6.40mm", 8.15),
        ("J12", "TerminalBlock_1x02_P2.54mm_Body5.60x6.40mm", 5.60),
    ]
    total_width = sum(body_width for _, _, body_width in row)
    total_width += TERMINAL_BODY_GAP_MM * (len(row) - 1)
    left_edge = (BOARD_WIDTH_MM - total_width) / 2.0

    cursor = left_edge
    for reference, footprint_name, body_width in row:
        if "1x03" in footprint_name:
            pin1_offset_x = 1.535
        else:
            pin1_offset_x = 1.53
        footprint = load_footprint(
            footprint_name,
            reference,
            reference,
            cursor + pin1_offset_x,
            TERMINAL_ROW_Y_MM,
        )
        if reference == "J11":
            footprint.Reference().SetPosition(vector(6.0, TERMINAL_ROW_Y_MM - 4.5))
        elif reference == "J12":
            footprint.Reference().SetPosition(vector(84.0, TERMINAL_ROW_Y_MM - 4.5))
        elif reference == "J4":
            footprint.Reference().SetPosition(vector(44.5, TERMINAL_ROW_Y_MM - 4.5))
        elif reference == "J5":
            footprint.Reference().SetPosition(vector(54.4, TERMINAL_ROW_Y_MM - 4.5))
        elif reference == "J6":
            footprint.Reference().SetPosition(vector(64.3, TERMINAL_ROW_Y_MM - 4.5))
        elif reference == "J7":
            footprint.Reference().SetPosition(vector(74.2, TERMINAL_ROW_Y_MM - 4.5))
        board.Add(footprint)
        cursor += body_width + TERMINAL_BODY_GAP_MM


def add_esp32_carrier(board):
    footprint = load_footprint(
        "ESP32_OLED_2x15_P2.54mm_Row27.94mm",
        "J9",
        "ESP32 OLED carrier sockets (27.94 mm standard row pitch)",
        ESP32_CENTER_X_MM,
        ESP32_CENTER_Y_MM,
    )
    footprint.SetOrientationDegrees(180)
    board.Add(footprint)


def add_w5500_module(board):
    footprint = load_footprint(
        "W5500_2x5_P2.54mm_Module55.1x28.1mm",
        "J10",
        "W5500 module (drawing-based outline)",
        W5500_PIN1_X_MM,
        W5500_PIN1_Y_MM,
    )
    footprint.Reference().SetPosition(vector(58.0, 2.0))
    board.Add(footprint)


def add_power_and_siren_components(board):
    barrel_jack = load_standard_footprint(
        "Connector_BarrelJack",
        "BarrelJack_Horizontal",
        "J1",
        "12V_IN",
        14.5,
        29.0,
    )
    board.Add(barrel_jack)

    fuse_holder = load_footprint(
        "FuseHolder_Body24x10_P23.6mm",
        "F1",
        "2A time-delay 5x20mm",
        31.0,
        7.5,
    )
    fuse_holder.Reference().SetPosition(vector(31.0, 14.0))
    board.Add(fuse_holder)

    polarity_diode = load_standard_footprint(
        "Diode_THT",
        "D_DO-201AD_P5.08mm_Vertical_AnodeUp",
        "D1",
        "1N5822 Schottky 3A 40V",
        26.0,
        12.5,
    )
    polarity_diode.Reference().SetPosition(vector(34.0, 12.5))
    board.Add(polarity_diode)

    power_module = load_footprint(
        "PowerModule_1x05_P2.54mm_Body15x20mm",
        "J8",
        "5V power module sockets",
        10.5,
        ESP32_CENTER_Y_MM + 13.97 - 8.0,
    )
    board.Add(power_module)

    capacitor_positions = [
        ("C1", "680 uF / 18 V", "12V CAP", 26.0, 25.0),
        ("C2", "470 uF / 10 V", "5V CAP", 26.0, 40.0),
        ("C3", "470 uF / 10 V", "3V3 CAP", 26.0, 55.0),
    ]
    for reference, value, rail_label, x_mm, y_mm in capacitor_positions:
        capacitor = load_standard_footprint(
            "Capacitor_THT",
            "CP_Radial_D8.0mm_P3.80mm",
            reference,
            value,
            x_mm,
            y_mm,
        )
        capacitor.Reference().SetPosition(vector(x_mm, y_mm - 7.0))
        board.Add(capacitor)
        rail_text = pcbnew.PCB_TEXT(board)
        rail_text.SetText(rail_label)
        rail_text.SetPosition(vector(x_mm, y_mm + 7.5))
        rail_text.SetLayer(pcbnew.F_SilkS)
        rail_text.SetTextSize(vector(0.9, 0.9))
        rail_text.SetTextThickness(mm(0.12))
        board.Add(rail_text)

    mosfet = load_standard_footprint(
        "Package_TO_SOT_THT",
        "TO-220-3_Vertical",
        "Q1",
        "IRFZ44N",
        42.0,
        14.0,
    )
    board.Add(mosfet)

    siren_terminal = load_footprint(
        "TerminalBlock_1x02_P2.54mm_Body5.60x6.40mm",
        "J13",
        "SIREN_OUT",
        47.0,
        3.2,
    )
    siren_terminal.SetOrientationDegrees(180)
    siren_terminal.Reference().SetPosition(vector(48.0, 8.5))
    board.Add(siren_terminal)

    siren_driver = load_standard_footprint(
        "Package_DIP",
        "DIP-8_W7.62mm",
        "U1",
        "TC4420CPA",
        18.0,
        68.5,
    )
    siren_driver.SetOrientationDegrees(270)
    board.Add(siren_driver)

    driver_resistors = [
        ("R5", "10 ohm", 33.0, 44.0),
        ("R6", "10k gate pulldown", 33.0, 52.0),
        ("R7", "10k input pulldown", 33.0, 60.0),
    ]
    for reference, value, x_mm, y_mm in driver_resistors:
        resistor = load_standard_footprint(
            "Resistor_THT",
            "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
            reference,
            value,
            x_mm,
            y_mm,
        )
        board.Add(resistor)

    for reference, value, x_mm in [
        ("C4", "100nF / 25V", 33.0),
        ("C5", "1uF / 25V", 41.0),
    ]:
        capacitor = load_standard_footprint(
            "Capacitor_THT",
            "C_Disc_D5.0mm_W2.5mm_P5.00mm",
            reference,
            value,
            x_mm,
            56.0,
        )
        board.Add(capacitor)

    flyback_diode = load_standard_footprint(
        "Diode_THT",
        "D_DO-201AD_P5.08mm_Vertical_AnodeUp",
        "D2",
        "1N5822 flyback",
        8.5,
        60.0,
    )
    flyback_diode.SetOrientationDegrees(180)
    board.Add(flyback_diode)

    pullup_positions = [
        ("R1", "10k Z7", 35.0),
        ("R2", "10k Z8", 44.5),
        ("R3", "10k Z9", 54.0),
        ("R4", "10k Z10", 63.5),
    ]
    for reference, value, x_mm in pullup_positions:
        resistor = load_standard_footprint(
            "Resistor_THT",
            "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
            reference,
            value,
            22.0,
            x_mm,
        )
        resistor.Reference().SetVisible(False)
        board.Add(resistor)

    pullup_label = pcbnew.PCB_TEXT(board)
    pullup_label.SetText("R1-R4 10k PULL-UPS")
    pullup_label.SetPosition(vector(21.5, 32.0))
    pullup_label.SetLayer(pcbnew.F_SilkS)
    pullup_label.SetTextSize(vector(0.8, 0.8))
    pullup_label.SetTextThickness(mm(0.12))
    board.Add(pullup_label)


def main():
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    add_outline(board)
    add_mounting_holes(board)
    add_bottom_terminal_row(board)
    add_esp32_carrier(board)
    add_w5500_module(board)
    add_power_and_siren_components(board)
    pcbnew.SaveBoard(str(OUTPUT_FILE), board)
    print(f"Created PCB placement baseline: {OUTPUT_FILE}")
    print(f"Board: {BOARD_WIDTH_MM:g} x {BOARD_HEIGHT_MM:g} mm")
    print(f"Bottom row body gap: {TERMINAL_BODY_GAP_MM:g} mm")
    print("Bottom row order: J11, J2, J3, J4, J5, J6, J7, J12")
    print("Placed J9 ESP32 carrier rotated 180 degrees, with D23/EN near the right edge and its antenna beyond the host-board edge.")
    print("J10's W5500 module right edge aligns with the host PCB right edge.")
    print(f"RJ45 cutout: 1.0 mm nominal clearance, x={BOARD_WIDTH_MM - (52.3 - 34.0) - RJ45_NOTCH_CLEARANCE_MM:.2f}..{BOARD_WIDTH_MM:.2f} mm.")
    print("Added host-board clearance holes for the two W5500 RJ45-side mounting holes.")
    print("Placed J1, selected F1 2A time-delay fuse holder, D1 power Schottky, J8, C1-C3, Q1, and J13 in the left-side power/siren area.")
    print("Placed R1-R4 10k pull-ups in the channel between J8 and J9 for GPIO34/35/36/39 zone inputs.")
    print("No tracks or electrical nets are yet imported into the PCB.")


if __name__ == "__main__":
    main()
