# qs_ai/tribunal/export_pack/hash_manifest.py
import hashlib
import json
from pathlib import Path


class HashManifestGenerator:

    def hash_file(self, path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            h.update(f.read())
        return h.hexdigest()

    def generate(self, files, output_path):
        manifest = {}

        for f in files:
            manifest[f] = self.hash_file(f)

        Path(output_path).write_text(
            json.dumps(manifest, indent=2)
        )

        return output_path
