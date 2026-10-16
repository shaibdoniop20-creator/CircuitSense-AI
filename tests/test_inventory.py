"""
CircuitSense AI - Component Inventory Test Suite
Tests: Empty detections, multiple component detections, aggregation, confidence filtering.
"""

from services.inventory import InventoryService


def test_empty_detection_results():
    """Test 7: Empty detection list yields zero counts and clean structure."""
    empty_detections = []
    summary = InventoryService.build_inventory(empty_detections, confidence_threshold=0.0)

    assert summary["total_components"] == 0
    assert summary["unique_classes_count"] == 0
    assert summary["overall_average_confidence"] == 0.0
    assert summary["high_confidence_count"] == 0

    # All target classes exist with 0 quantity
    for cls_name in ["integrated_circuit", "microcontroller", "transistor", "capacitor", "connector"]:
        assert cls_name in summary["by_class"]
        assert summary["by_class"][cls_name]["quantity"] == 0


def test_multiple_component_detections_and_aggregation():
    """Test 8 & 9: Multiple component detections including transistors and accurate class aggregation."""
    detections = [
        {"class_name": "integrated_circuit", "confidence": 0.90, "bbox": {"x1": 10, "y1": 10, "x2": 50, "y2": 50}},
        {"class_name": "integrated_circuit", "confidence": 0.80, "bbox": {"x1": 60, "y1": 10, "x2": 100, "y2": 50}},
        {"class_name": "microcontroller", "confidence": 0.95, "bbox": {"x1": 120, "y1": 60, "x2": 220, "y2": 160}},
        {"class_name": "transistor", "confidence": 0.88, "bbox": {"x1": 10, "y1": 50, "x2": 30, "y2": 70}},
        {"class_name": "capacitor", "confidence": 0.70, "bbox": {"x1": 10, "y1": 80, "x2": 30, "y2": 100}},
        {"class_name": "capacitor", "confidence": 0.60, "bbox": {"x1": 40, "y1": 80, "x2": 60, "y2": 100}},
        {"class_name": "connector", "confidence": 0.85, "bbox": {"x1": 200, "y1": 20, "x2": 280, "y2": 60}},
    ]

    summary = InventoryService.build_inventory(detections, confidence_threshold=0.0)

    assert summary["total_components"] == 7
    assert summary["unique_classes_count"] == 5

    # Quantities per class
    assert summary["by_class"]["integrated_circuit"]["quantity"] == 2
    assert summary["by_class"]["microcontroller"]["quantity"] == 1
    assert summary["by_class"]["transistor"]["quantity"] == 1
    assert summary["by_class"]["capacitor"]["quantity"] == 2
    assert summary["by_class"]["connector"]["quantity"] == 1

    # Average confidence checks
    ic_avg = summary["by_class"]["integrated_circuit"]["average_confidence"]
    assert round(ic_avg, 2) == 0.85

    cap_avg = summary["by_class"]["capacitor"]["average_confidence"]
    assert round(cap_avg, 2) == 0.65


def test_low_confidence_filtering():
    """Test 10: Filtering out detections below threshold."""
    detections = [
        {"class_name": "integrated_circuit", "confidence": 0.92, "bbox": {}},
        {"class_name": "integrated_circuit", "confidence": 0.40, "bbox": {}},
        {"class_name": "microcontroller", "confidence": 0.28, "bbox": {}},
        {"class_name": "transistor", "confidence": 0.85, "bbox": {}},
        {"class_name": "capacitor", "confidence": 0.76, "bbox": {}},
    ]

    # Filter with threshold 0.50: should drop the 0.40 and 0.28 detections
    filtered_summary = InventoryService.build_inventory(detections, confidence_threshold=0.50)

    assert filtered_summary["total_components"] == 3
    assert filtered_summary["by_class"]["integrated_circuit"]["quantity"] == 1
    assert filtered_summary["by_class"]["microcontroller"]["quantity"] == 0
    assert filtered_summary["by_class"]["transistor"]["quantity"] == 1
    assert filtered_summary["by_class"]["capacitor"]["quantity"] == 1


def test_reusability_triage_assessment():
    """Test 11: Reusability triage properly separates reusable components (IC, MCU, Transistor, Connector) from degraded ones."""
    detections = [
        {"class_name": "integrated_circuit", "confidence": 0.90, "bbox": {}},
        {"class_name": "microcontroller", "confidence": 0.92, "bbox": {}},
        {"class_name": "transistor", "confidence": 0.86, "bbox": {}},
        {"class_name": "connector", "confidence": 0.88, "bbox": {}},
        {"class_name": "capacitor", "confidence": 0.85, "bbox": {}},
    ]

    summary = InventoryService.build_inventory(detections, confidence_threshold=0.0, board_condition="intact")
    triage = summary["triage_summary"]

    assert triage["total_evaluated"] == 5
    # IC, MCU, Transistor, Connector are reusable
    assert triage["can_reuse_count"] == 4
    # Electrolytic capacitor cannot be reused (dry electrolyte risk)
    assert triage["recycle_only_count"] == 1
    assert triage["salvage_score"] > 70
