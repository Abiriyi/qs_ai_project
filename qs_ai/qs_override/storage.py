class InMemoryOverrideStore:
    def __init__(self):
        self._records = []

    def save_override(self, record):
        self._records.append(record)

    def list_overrides(self, boq_item_code: str):
        return [
            r for r in self._records
            if r.boq_item_code == boq_item_code
        ]
