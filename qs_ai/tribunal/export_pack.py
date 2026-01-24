import json
import zipfile
from pathlib import Path

from qs_ai.tribunal.export_guard import enforce_export_readiness
from qs_ai.tribunal.manifest import build_export_manifest
from qs_ai.tribunal.exceptions import TribunalExportError


class TribunalExportPack:

    def __init__(self, context, output_dir: str):
        self.context = context
        self.output_dir = Path(output_dir)

    def export(self) -> Path:
        """
        Creates a sealed tribunal-ready ZIP export.
        """
        enforce_export_readiness(self.context)

        pack_name = f"Tribunal_Export_Pack_{self.context.case_reference}.zip"
        pack_path = self.output_dir / pack_name

        with zipfile.ZipFile(pack_path, "w", zipfile.ZIP_DEFLATED) as zf:
            self._write_manifest(zf)
            self._write_scott_schedules(zf)
            self._write_joint_statements(zf)
            self._write_claims(zf)
            self._write_evidence(zf)
            self._write_declarations(zf)

        return pack_path

    # -------------------------
    # Internal writers
    # -------------------------

    def _write_manifest(self, zf):
        manifest = build_export_manifest(self.context)
        zf.writestr(
            "00_Export_Manifest.json",
            json.dumps(manifest, indent=2)
        )

    def _write_scott_schedules(self, zf):
        for ss in self.context.scott_schedules:
            zf.write(
                ss.file_path,
                f"02_Scott_Schedules/{Path(ss.file_path).name}"
            )

    def _write_joint_statements(self, zf):
        for js in self.context.joint_statements:
            zf.write(
                js.file_path,
                f"03_Joint_Expert_Statements/{Path(js.file_path).name}"
            )

    def _write_claims(self, zf):
        for claim in self.context.claims:
            zf.write(
                claim.file_path,
                f"04_Claims_Narratives/{Path(claim.file_path).name}"
            )

    def _write_evidence(self, zf):
        for ev in self.context.evidence_items:
            zf.write(
                ev.file_path,
                f"05_Evidence_Bundle/{Path(ev.file_path).name}"
            )

    def _write_declarations(self, zf):
        for dec in self.context.declarations:
            zf.write(
                dec.file_path,
                f"06_Declarations/{Path(dec.file_path).name}"
            )
