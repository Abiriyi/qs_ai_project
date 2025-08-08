# parse_section.py

DEFAULT_CEILING_HEIGHT_MM = 3300

# Wall finish logic based on room type
ROOM_FINISHES = {
    "kitchen": {"wall": ("Tiles up to 2100mm", 2100)},
    "bath": {"wall": ("Tiles up to 2100mm", 2100)},
    "toilet": {"wall": ("Tiles up to 2100mm", 2100)},
    "wc": {"wall": ("Tiles up to 2100mm", 2100)},
    "store": {"wall": ("Paint", DEFAULT_CEILING_HEIGHT_MM)},
    "bedroom": {"wall": ("Paint", DEFAULT_CEILING_HEIGHT_MM)},
    "living": {"wall": ("Paint", DEFAULT_CEILING_HEIGHT_MM)},
    "passage": {"wall": ("Paint", DEFAULT_CEILING_HEIGHT_MM)},
    "dining": {"wall": ("Paint", DEFAULT_CEILING_HEIGHT_MM)},
    "foyer": {"wall": ("Paint", DEFAULT_CEILING_HEIGHT_MM)},
    "madam": {"wall": ("Paint", DEFAULT_CEILING_HEIGHT_MM)},
    "master": {"wall": ("Paint", DEFAULT_CEILING_HEIGHT_MM)},
    "ent.": {"wall": ("Paint", DEFAULT_CEILING_HEIGHT_MM)},
}

def get_wall_finish(room_name: str):
    name = room_name.lower()
    for keyword, spec in ROOM_FINISHES.items():
        if keyword in name:
            return spec["wall"]
    return ("Paint", DEFAULT_CEILING_HEIGHT_MM)  # Default fallback
