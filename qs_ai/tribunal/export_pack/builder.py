# qs_ai/tribunal/export_pack/builder.py
from uuid import uuid4
from datetime import datetime
from qs_ai.tribunal.export_pack.models import TribunalExportPack


class TribunalPackBuilder:

    def build(
        self,
        contract_reference,
        prepared_by,
        documents,
        evidence,
        hash_manifest_path,
    ):
        return TribunalExportPack(
            pack_id=str(uuid4()),
            contract_reference=contract_reference,
            prepared_at=datetime.utcnow(),
            prepared_by=prepared_by,
            documents=documents,
            evidence=evidence,
            hash_manifest_path=hash_manifest_path,
        )
