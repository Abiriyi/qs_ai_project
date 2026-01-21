def determine_status(claimed: float, assessed: float) -> str:
    if abs(claimed - assessed) < 0.01:
        return "Agreed"
    if assessed > 0:
        return "Partly Agreed"
    return "Not Agreed"
