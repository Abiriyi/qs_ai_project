# qs_ai/tribunal/export_pack/renderer.py
import shutil
from pathlib import Path


class TribunalPackRenderer:

    def render(self, pack, output_dir):
        base = Path(output_dir) / f"Tribunal_Pack_{pack.pack_id}"
        base.mkdir(parents=True, exist_ok=True)

        for doc in pack.documents:
            shutil.copy(doc, base / Path(doc).name)

        for ev in pack.evidence:
            shutil.copy(ev.file_path, base / Path(ev.file_path).name)

        shutil.copy(pack.hash_manifest_path, base / "hash_manifest.json")

        return base
