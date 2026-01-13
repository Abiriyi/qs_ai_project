def enforce_qs_review(items, threshold=0.6):
    flagged = [
        it for it in items
        if it.get("Confidence", 1.0) < threshold
    ]

    if flagged:
        raise RuntimeError(
            "QS REVIEW REQUIRED for items: " +
            ", ".join(it["ItemCode"] for it in flagged)
        )
