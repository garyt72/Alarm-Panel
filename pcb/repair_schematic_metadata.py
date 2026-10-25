import re
import uuid
from pathlib import Path


PCB_DIR = Path(__file__).resolve().parent
SCHEMATIC = PCB_DIR / "Alarm Panel.kicad_sch"
SYMBOL_LIBRARY_DIR = Path(r"C:\Program Files\KiCad\10.0\share\kicad\symbols")
SYMBOL_ALIASES = {
    "Device:CP": "Device:C_Polarized",
    "Device:Q_NMOS": "Transistor_FET:Q_NMOS_GDS",
}
LIBRARY_CACHE = {}


def tokenize(text):
    pattern = re.compile(r'\s+|;[^\n]*|"(?:\\.|[^"\\])*"|[()]|[^\s()]+')
    return [match.group(0) for match in pattern.finditer(text) if not match.group(0).isspace() and not match.group(0).startswith(";")]


def parse_expr(tokens, index=0):
    if tokens[index] != "(":
        return tokens[index], index + 1
    items = []
    index += 1
    while tokens[index] != ")":
        item, index = parse_expr(tokens, index)
        items.append(item)
    return items, index + 1


def parse(text):
    tokens = tokenize(text)
    expression, next_index = parse_expr(tokens)
    if next_index != len(tokens):
        raise ValueError("Unexpected content after top-level S-expression")
    return expression


def quote(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render(expression, depth=0):
    if isinstance(expression, str):
        return expression
    indent = "  " * depth
    if not any(isinstance(item, list) for item in expression):
        return "(" + " ".join(expression) + ")"
    lines = ["(" + render(expression[0], depth + 1)]
    lines.extend("  " * (depth + 1) + render(item, depth + 1) for item in expression[1:])
    return "\n".join(lines) + "\n" + indent + ")"


def direct_child(expression, name):
    return next((item for item in expression if isinstance(item, list) and item and item[0] == name), None)


def find_all(expression, name):
    found = []
    if isinstance(expression, list):
        if expression and expression[0] == name:
            found.append(expression)
        for item in expression:
            found.extend(find_all(item, name))
    return found


def library_symbol(library_name, symbol_name):
    if library_name not in LIBRARY_CACHE:
        if library_name == "AlarmPanel":
            library_path = PCB_DIR / "symbols" / "AlarmPanel.kicad_sym"
        else:
            library_path = SYMBOL_LIBRARY_DIR / f"{library_name}.kicad_sym"
        LIBRARY_CACHE[library_name] = parse(library_path.read_text(encoding="utf-8"))
        print(f"Loaded {library_name} library", flush=True)
    library = LIBRARY_CACHE[library_name]
    symbol = next(
        item
        for item in library
        if isinstance(item, list)
        and item
        and item[0] == "symbol"
        and len(item) > 1
        and item[1] == quote(symbol_name)
    )
    copied = [item[:] if not isinstance(item, list) else item for item in symbol]
    copied[1] = quote(f"{library_name}:{symbol_name}")
    return copied


def symbol_pin_numbers(symbol_definition):
    numbers = []
    for pin in find_all(symbol_definition, "pin"):
        number = direct_child(pin, "number")
        if number and len(number) > 1 and number[1] not in numbers:
            numbers.append(number[1])
    return numbers


def main():
    print("Repairing schematic metadata", flush=True)
    original = SCHEMATIC.read_text(encoding="utf-8")
    root = parse(original)
    if root[0] != "kicad_sch":
        raise ValueError("Input is not a KiCad schematic")

    existing_uuid = direct_child(root, "uuid")
    schematic_uuid = existing_uuid[1].strip('"') if existing_uuid else str(uuid.uuid4())
    definitions = {}
    instances = []
    root[:] = [
        item for item in root
        if not isinstance(item, list) or not item or item[0] not in {"lib_symbols", "sheet_instances"}
    ]
    for symbol in root:
        if not isinstance(symbol, list) or not symbol or symbol[0] != "symbol":
            continue
        symbol[:] = [
            item for item in symbol
            if not isinstance(item, list) or not item or item[0] not in {"pin", "instances"}
        ]
        lib_id = direct_child(symbol, "lib_id")
        if not lib_id:
            continue
        normalized_lib_id = SYMBOL_ALIASES.get(lib_id[1].strip('"'), lib_id[1].strip('"'))
        lib_id[1] = quote(normalized_lib_id)
        library_name, symbol_name = normalized_lib_id.split(":", 1)
        definitions.setdefault(lib_id[1], library_symbol(library_name, symbol_name))
        reference_property = next(
            item for item in symbol
            if isinstance(item, list) and item[:2] == ["property", quote("Reference")]
        )
        reference = reference_property[2].strip('"')
        unit_expr = direct_child(symbol, "unit")
        unit = unit_expr[1] if unit_expr else "1"
        symbol_uuid = direct_child(symbol, "uuid")[1].strip('"')
        pins = symbol_pin_numbers(definitions[lib_id[1]])
        pin_metadata = [
            ["pin", pin_number, ["uuid", quote(str(uuid.uuid4()))]]
            for pin_number in pins
        ]
        instance_metadata = [
            "instances",
            [
                "project",
                quote("Alarm Panel"),
                [
                    "path",
                    quote(f"/{schematic_uuid}"),
                    ["reference", quote(reference)],
                    ["unit", unit],
                ],
            ],
        ]
        symbol.extend(pin_metadata)
        symbol.append(instance_metadata)
        instances.append((symbol_uuid, reference))
        print(f"Prepared {reference}: {normalized_lib_id}", flush=True)

    if not definitions:
        raise ValueError("No placed symbols found")

    lib_symbols = ["lib_symbols", *definitions.values()]
    if not existing_uuid:
        root.insert(3, ["uuid", quote(schematic_uuid)])
    paper_index = next(
        index for index, item in enumerate(root)
        if isinstance(item, list) and item and item[0] == "paper"
    )
    root.insert(paper_index + 1, lib_symbols)
    root.append(["sheet_instances", ["path", quote("/"), ["page", quote("1")]]])

    SCHEMATIC.write_text(render(root), encoding="utf-8")
    print(f"Embedded {len(definitions)} standard symbol definitions")
    print(f"Added pin UUIDs and instance paths for {len(instances)} placed symbols")
    print(f"Updated {SCHEMATIC}")


if __name__ == "__main__":
    main()