from boq_generator import aggregate_parsed_entries, compute_quantities_from_geometry, _build_full_item_list, get_rate_from_library, DEFAULT_RATE, pd, defaultdict
def populate_besmm4_from_parsed(parsed_entries, context, location="Kaduna", include_empty=True):

    agg = aggregate_parsed_entries(parsed_entries)
    computed = compute_quantities_from_geometry(agg, context=context)
    items = _build_full_item_list(include_empty=include_empty)

    # Canonical lookup
    canonical_to_items = defaultdict(list)
    for it in items:
        canonical_to_items[(it["Canonical"] or it["Description"]).lower()].append(it)

    # ---------------- Mapping computed quantities ----------------
    for canonical_key, res in computed.items():
        qty = res.get("quantity", 0.0)
        just = res.get("justification", "")
        confidence = res.get("confidence", 1.0)

        if canonical_key in canonical_to_items:
            for it in canonical_to_items[canonical_key]:
                it["Quantity"] = round(float(qty), 4)
                it["Justification"] = just
                it["Confidence"] = confidence

                if confidence >= 0.85:
                    it["Status"] = "OK"
                elif confidence >= 0.60:
                    it["Status"] = "REVIEW"
                else:
                    it["Status"] = "REVIEW_REQUIRED"

        else:
            # Fuzzy fallback
            for can_k, its in canonical_to_items.items():
                if canonical_key in can_k or can_k in canonical_key:
                    for it in its:
                        it["Quantity"] = round(float(qty), 4)
                        it["Justification"] = just
                        it["Confidence"] = confidence
                        it["Status"] = "REVIEW"
                    break

    # ---------------- Rate & amount ----------------
    for it in items:
        rate = get_rate_from_library(
            it["Canonical"],
            it["Description"],
            it["Unit"],
            location=location
        ) or DEFAULT_RATE

        it["Rate"] = float(rate)
        it["Amount"] = round(it["Quantity"] * it["Rate"], 2)

    return pd.DataFrame(items)

