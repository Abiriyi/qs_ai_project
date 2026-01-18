import pytest
from datetime import date
from qs_ai.commercial.valuation_engine import ValuationEngine
from qs_ai.commercial.valuation_models import ValuationLine

def test_overvaluation_blocked():
    engine = ValuationEngine()

    lines = [
        ValuationLine(
            boq_item_id="B1",
            tender_quantity=10,
            executed_quantity_to_date=12,
            unit_rate=100,
        )
    ]

    with pytest.raises(ValueError):
        engine.create_valuation(
            snapshot_id="SNAP-1",
            valuation_no=1,
            prepared_by="QS",
            valuation_date=date.today(),
            lines=lines,
            retention_percent=5,
        )
