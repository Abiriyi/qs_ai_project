from qs_ai.dispute.methodology_registry import METHODOLOGIES

def form_opinion(facts, methodology_key):
    if methodology_key not in METHODOLOGIES:
        raise ValueError("Unsupported methodology")

    return {
        "opinion": f"Assessment carried out using {methodology_key}",
        "methodology": methodology_key,
        "assumptions": ["Records provided are complete"],
        "confidence_level": 0.75,
    }
