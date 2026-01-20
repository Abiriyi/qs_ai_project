def assess_cross_exam_risk(opinion):
    risks = []

    if opinion["confidence_level"] < 0.6:
        risks.append("Low confidence opinion")

    if "Total Cost" in opinion["methodology"]:
        risks.append("Methodology vulnerable to challenge")

    return risks
