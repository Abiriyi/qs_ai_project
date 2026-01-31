class EvidenceStore:
    def __init__(self):
        self._records = []

    def append(self, record):
        self._records.append(record)

    def all(self):
        return list(self._records)
