def assess_agreement(claimant, respondent, tolerance=0.01):
    """
    Determines agreement status and agreed value if possible.
    """
    if abs(claimant - respondent) <= tolerance:
        return "Agreed", round((claimant + respondent) / 2, 2), None

    midpoint = round((claimant + respondent) / 2, 2)

    return (
        "Narrowed",
        midpoint,
        "Difference in measurement methodology"
    )
