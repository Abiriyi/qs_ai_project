def compute_quantities(entries, context):
    if not context.confirmed:
        raise RuntimeError("Measurement context not confirmed")
