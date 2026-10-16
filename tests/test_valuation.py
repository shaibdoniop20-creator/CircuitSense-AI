"""
CircuitSense AI - Valuation Engine Test Suite
Tests: Pricing catalogue matching, low/high/midpoint ranges, condition multipliers, missing data.
"""

from services.valuation import ValuationService
from services.inventory import InventoryService


def test_valuation_calculation_ranges_and_condition():
    """Test 12: Low, high, and midpoint valuation calculations with condition adjustment."""
    val_service = ValuationService()

    # 2 ICs and 1 MCU
    detections = [
        {"class_name": "integrated_circuit", "confidence": 0.85},
        {"class_name": "integrated_circuit", "confidence": 0.88},
        {"class_name": "microcontroller", "confidence": 0.92},
    ]

    inventory_summary = InventoryService.build_inventory(detections)

    # Intact condition (multiplier 1.0)
    val_intact = val_service.calculate_valuation(inventory_summary, board_condition="intact")

    assert val_intact["total_reusable_components"] == 3
    assert val_intact["total_low"] > 0
    assert val_intact["total_high"] > val_intact["total_low"]
    assert val_intact["total_mid"] == round((val_intact["total_low"] + val_intact["total_high"]) / 2, 2)
    assert len(val_intact["breakdown"]) == 2

    # Damaged condition (multiplier 0.40)
    val_damaged = val_service.calculate_valuation(inventory_summary, board_condition="damaged")

    assert val_damaged["condition_factor"] == 0.40
    assert val_damaged["total_low"] < val_intact["total_low"]
    assert val_damaged["total_high"] < val_intact["total_high"]


def test_missing_pricing_data_handling():
    """Test 11: Unsupported or unknown component categories are safely quarantined."""
    val_service = ValuationService()

    # Inventory with a non-catalogued class
    fake_inventory = {
        "by_class": {
            "unsupported_vacuum_tube": {
                "class_name": "unsupported_vacuum_tube",
                "display_name": "Vacuum Tube",
                "quantity": 2,
                "average_confidence": 0.75
            }
        }
    }

    val_result = val_service.calculate_valuation(fake_inventory, board_condition="intact")

    assert val_result["total_low"] == 0.0
    assert val_result["total_high"] == 0.0
    assert len(val_result["unpriced_components"]) == 1
    assert val_result["unpriced_components"][0]["class_name"] == "unsupported_vacuum_tube"


def test_salvageable_vs_scrap_split():
    """Test: Distinguish reusable component value from capacitor scrap recycling."""
    val_service = ValuationService()
    detections = [
        {"class_name": "microcontroller", "confidence": 0.90},
        {"class_name": "capacitor", "confidence": 0.85},
    ]
    inventory = InventoryService.build_inventory(detections)
    val = val_service.calculate_valuation(inventory, board_condition="intact")

    assert val["salvageable_mid"] > 0
    assert val["recycle_scrap_mid"] > 0
    assert round(val["salvageable_mid"] + val["recycle_scrap_mid"], 2) == val["total_mid"]
