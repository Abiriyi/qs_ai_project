# qs_ai/contracts/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any


class ContractBase(ABC):

    name: str

    @abstractmethod
    def validate_notice(self, event: Dict[str, Any]) -> bool:
        """Was notice given in accordance with the contract?"""
        pass

    @abstractmethod
    def assess_entitlement(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Determine entitlement type and limits"""
        pass

    @abstractmethod
    def applicable_clauses(self, event_type: str) -> list[str]:
        pass
