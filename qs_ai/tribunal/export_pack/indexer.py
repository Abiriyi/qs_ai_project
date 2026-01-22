# qs_ai/tribunal/export_pack/indexer.py
import pandas as pd


class TribunalIndexGenerator:

    def generate(self, pack):
        rows = []

        for d in pack.documents:
            rows.append({
                "Type": "Document",
                "Reference": d,
            })

        for e in pack.evidence:
            rows.append({
                "Type": "Evidence",
                "Reference": e.ref,
                "Description": e.description,
                "Source": e.source,
            })

        return pd.DataFrame(rows)

    def to_excel(self, pack, path):
        df = self.generate(pack)
        df.to_excel(path, index=False)
