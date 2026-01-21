from uuid import uuid4
from qs_ai.commercial.certificate_models import InterimCertificate

from qs_ai.qs_override.approval_guard import require_approval

class CertificateEngine:

    def certify(self, valuation):
        require_approval(valuation, stage="Certification")

        gross = sum(l.value_to_date for l in valuation.lines)
        retention = round(gross * valuation.retention_percent / 100, 2)
        net = round(gross - retention, 2)

        return InterimCertificate(
            certificate_id=str(uuid4()),
            valuation_id=valuation.valuation_id,
            gross_value=gross,
            retention_amount=retention,
            net_payable=net,
        )


