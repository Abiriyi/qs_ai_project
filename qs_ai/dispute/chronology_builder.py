def build_chronology(events):
    return sorted(events, key=lambda e: e["date"])
