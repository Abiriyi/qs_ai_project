from qs_ai.qs_override.models import QSOverrideRecord
from qs_ai.qs_override.exceptions import (
    InvalidOverrideError,
    PermissionDeniedError,
)

ALLOWED_ROLES = {"QS", "Senior QS", "Associate", "Partner"}


class QSOverrideService:
    def __init__(self, storage_backend):
        """
        storage_backend must implement:
        - save_override(record)
        - list_overrides(boq_item_code)
        """
        self.storage = storage_backend

    def submit_override(
        self,
        *,
        boq_item_code: str,
        description: str,
        base_quantity: float,
        overridden_quantity: float,
        unit: str,
        reason: str,
        created_by: str,
        created_role: str,
        technical_basis: str | None = None,
    ) -> QSOverrideRecord:
        # -------- Authority check --------
        if created_role not in ALLOWED_ROLES:
            raise PermissionDeniedError(
                f"Role '{created_role}' not permitted to issue overrides"
            )

        # -------- Validation --------
        if base_quantity < 0 or overridden_quantity < 0:
            raise InvalidOverrideError("Quantities cannot be negative")

        if abs(overridden_quantity - base_quantity) < 1e-6:
            raise InvalidOverrideError("Override must change the quantity")

        if not reason or len(reason.strip()) < 10:
            raise InvalidOverrideError(
                "QS justification must be explicit and professional"
            )

        # -------- Record creation --------
        record = QSOverrideRecord(
            boq_item_code=boq_item_code,
            description=description,
            base_quantity=round(base_quantity, 6),
            overridden_quantity=round(overridden_quantity, 6),
            unit=unit,
            reason=reason.strip(),
            technical_basis=technical_basis,
            created_by=created_by,
            created_role=created_role,
        )

        # -------- Persistence --------
        self.storage.save_override(record)

        return record
