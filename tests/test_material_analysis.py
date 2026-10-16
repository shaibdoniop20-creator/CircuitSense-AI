"""
CircuitSense AI - Material Analysis Test Suite
Tests: Mode A (Reference-Based Estimation) vs Mode B (Insufficient Data Protocol).
"""

from services.material_analysis import MaterialAnalysisService


def test_material_analysis_mode_a_sufficient_data():
    """Test 13: Mode A reference-based hazardous fraction calculation."""
    mat_service = MaterialAnalysisService()

    # Motherboard category
    res = mat_service.analyze_board_materials(board_category="motherboard", board_mass_grams=600.0)

    assert res["mode"] == "MODE_A_REFERENCE_BASED"
    assert res["can_estimate_percentage"] is True
    assert res["estimated_hazardous_percentage"] is not None
    assert res["estimated_hazardous_percentage"]["typical"] > 0
    assert res["estimated_board_mass_grams"] == 600.0
    assert len(res["hazardous_substances"]) > 0
    assert "valuable_fractions" in res
    assert res["valuable_fractions"]["gold_ppm"] > 0


def test_material_analysis_mode_b_insufficient_data():
    """Test 14: Mode B insufficient data handling for unknown board categories."""
    mat_service = MaterialAnalysisService()

    # Unknown category
    res = mat_service.analyze_board_materials(board_category="unknown")

    assert res["mode"] == "MODE_B_INSUFFICIENT_DATA"
    assert res["can_estimate_percentage"] is False
    assert res["estimated_hazardous_percentage"] is None
    assert "cannot be reliably estimated" in res["notice"]
    assert len(res["required_laboratory_steps"]) > 0
    # Must never invent a percentage
    assert res.get("estimated_hazardous_mass_grams") is None
