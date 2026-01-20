# qs_ai/contracts/registry.py
from qs_ai.contracts.fidic.entitlement import FIDICContract
from qs_ai.contracts.jct.entitlement import JCTContract
from qs_ai.contracts.nec.compensation_events import NECContract


CONTRACT_REGISTRY = {
    "FIDIC": FIDICContract,
    "JCT": JCTContract,
    "NEC": NECContract,
}


def load_contract(contract_name: str):
    try:
        return CONTRACT_REGISTRY[contract_name]()
    except KeyError:
        raise ValueError(f"Unsupported contract form: {contract_name}")
