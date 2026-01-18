from dataclasses import dataclass

@dataclass(frozen=True)
class InterimCertificate:
    certificate_id: str
    valuation_id: str
    gross_value: float
    retention_amount: float
    net_payable: float
