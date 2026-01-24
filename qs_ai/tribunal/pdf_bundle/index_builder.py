# qs_ai/tribunal/pdf_bundle/index_builder.py

class IndexBuilder:
    def __init__(self):
        self.entries = []

    def register(self, title: str):
        self.entries.append(title)
