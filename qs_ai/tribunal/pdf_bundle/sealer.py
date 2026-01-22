# qs_ai/tribunal/pdf_bundle/sealer.py
import hashlib


class PdfBundleSealer:

    def seal(self, pdf_path):
        sha = hashlib.sha256()

        with open(pdf_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)

        return sha.hexdigest()
