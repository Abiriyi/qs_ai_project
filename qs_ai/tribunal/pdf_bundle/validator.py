# qs_ai/tribunal/pdf_bundle/validator.py
class BundleValidator:

    REQUIRED_SECTIONS = {
        "Cover",
        "Table of Contents",
        "Expert Report",
        "Scott Schedule",
    }

    def validate(self, sections):
        titles = {s["title"] for s in sections}
        missing = self.REQUIRED_SECTIONS - titles

        if missing:
            raise RuntimeError(
                f"Bundle missing required sections: {missing}"
            )
