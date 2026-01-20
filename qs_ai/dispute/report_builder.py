def build_expert_report(facts, opinions, mode):
    return {
        "expert_role": mode.value,
        "facts": facts,
        "opinions": opinions,
        "statement_of_truth": (
            "I confirm that this report represents my true and professional opinion."
        ),
    }
