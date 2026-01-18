from uuid import uuid4
from qs_ai.commercial.certificate_models import InterimCertificate

class CertificateEngine:

    def certify(self, valuation):
        gross = sum(line.value_to_date for line in valuation.lines)
        retention = round(gross * valuation.retention_percent / 100, 2)
        net = round(gross - retention, 2)

        return InterimCertificate(
            certificate_id=str(uuid4()),
            valuation_id=valuation.valuation_id,
            gross_value=gross,
            retention_amount=retention,
            net_payable=net,
        )

