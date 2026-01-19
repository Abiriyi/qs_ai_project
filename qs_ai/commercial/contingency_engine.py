# qs_ai/commercial/contingency_engine.py
def calculate_contingency(risks):
    return round(
        sum(r.probability * r.cost_impact for r in risks),
        2
    )
