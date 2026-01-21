def collect_evidence(issue_seed):
    """
    Returns list of references supporting an issue.
    """
    refs = []

    if issue_seed.get("boq_item"):
        refs.append(f"BoQ Item: {issue_seed['boq_item']}")

    if issue_seed.get("drawing"):
        refs.append(f"Drawing: {issue_seed['drawing']}")

    if issue_seed.get("approval_id"):
        refs.append(f"QS Approval: {issue_seed['approval_id']}")

    if issue_seed.get("variation_id"):
        refs.append(f"Variation: {issue_seed['variation_id']}")

    return refs
