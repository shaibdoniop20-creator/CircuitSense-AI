"""
CircuitSense AI - Flask Routes & System Integration Test Suite
Tests: Model loading, demo mode fallback, CSV export, PDF report, invalid ID, analysis deletion.
"""

import io
import json
import pytest
from pathlib import Path
from PIL import Image

from app import app, db, AnalysisRecord
from config import Config
from services.detector import PCBDetector
from services.report_generator import ReportGenerator


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_landing_page(client):
    """Verifies that the landing page renders with branding and actions."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"CircuitSense AI" in res.data
    assert b"Turn Electronic Waste into" in res.data
    assert b"Analyze Circuit Board" in res.data


def test_model_detector_states():
    """Test 5 & 6: Missing weights activates demo mode; valid weights activate model mode."""
    # Test 5: Non-existent weights path
    fake_detector = PCBDetector.__new__(PCBDetector)
    fake_detector.configured_model_path = Path("non_existent_weights.pt")
    fake_detector.target_classes = Config.TARGET_CLASSES
    fake_detector.class_metadata = Config.CLASS_METADATA
    fake_detector._initialize_model()

    status_demo = fake_detector.get_model_status()
    assert status_demo["is_demo"] is True
    assert status_demo["mode"] == "hackathon_demo"

    # Test 6: Real weights file if models/best.pt exists
    real_weights = Path(Config.MODEL_PATH)
    if real_weights.exists():
        real_detector = PCBDetector.__new__(PCBDetector)
        real_detector.configured_model_path = real_weights
        real_detector.target_classes = Config.TARGET_CLASSES
        real_detector.class_metadata = Config.CLASS_METADATA
        real_detector._initialize_model()

        status_real = real_detector.get_model_status()
        assert status_real["is_demo"] is False
        assert status_real["mode"] == "production_trained"


def test_csv_and_pdf_export_generation():
    """Test 15 & 16: Generation of CSV inventory and ReportLab PDF document."""
    mock_analysis_data = {
        "analysis_id": "test-uuid-1234",
        "created_at": "2026-10-16 12:00:00",
        "original_filename": "test_board.jpg",
        "board_category": "motherboard",
        "board_condition": "intact",
        "is_demo": False,
        "total_components": 3,
        "detections": [
            {
                "detection_id": "det_1",
                "class_name": "integrated_circuit",
                "display_name": "Integrated Circuit (IC)",
                "confidence": 0.92,
                "confidence_pct": 92.0,
                "bbox": {"x1": 10, "y1": 10, "x2": 60, "y2": 60},
                "is_simulated": False
            }
        ],
        "inventory_summary": {
            "total_components": 3,
            "overall_average_confidence_pct": 88.5,
            "classes_list": [
                {
                    "class_name": "integrated_circuit",
                    "display_name": "Integrated Circuit (IC)",
                    "quantity": 3,
                    "average_confidence_pct": 88.5
                }
            ]
        },
        "valuation_summary": {
            "total_low": 45.0,
            "total_high": 195.0,
            "total_mid": 120.0,
            "total_reusable_components": 3,
            "breakdown": [
                {
                    "class_name": "integrated_circuit",
                    "display_name": "Integrated Circuit (IC)",
                    "quantity": 3,
                    "unit_low": 15.0,
                    "unit_high": 65.0,
                    "subtotal_low": 45.0,
                    "subtotal_high": 195.0,
                    "subtotal_mid": 120.0
                }
            ]
        },
        "material_analysis": {
            "mode": "MODE_A_REFERENCE_BASED",
            "can_estimate_percentage": True,
            "display_name": "Computer Motherboard",
            "estimated_board_mass_grams": 580,
            "estimated_hazardous_percentage": {"formatted": "2.2% - 5.1% (Typical: 3.6%)", "typical": 3.6},
            "estimated_hazardous_mass_grams": {"formatted": "12.76g - 29.58g"},
            "regulatory_risk": "Moderate-High",
            "hazardous_substances": []
        }
    }

    # Test 15: CSV export
    csv_str = ReportGenerator.generate_inventory_csv(mock_analysis_data)
    assert "CircuitSense AI - Component Inventory Export" in csv_str
    assert "det_1" in csv_str
    assert "integrated_circuit" in csv_str

    # Test 16: PDF export
    pdf_bytes = ReportGenerator.generate_pdf_report(mock_analysis_data, annotated_image_path=None)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500  # Valid PDF binary
    assert pdf_bytes.startswith(b"%PDF")


def test_invalid_analysis_id(client):
    """Test 17: Querying an invalid analysis ID redirects safely with flash message."""
    res = client.get("/results/non-existent-id-99999", follow_redirects=True)
    assert res.status_code == 200
    assert b"was not found" in res.data


def test_analysis_creation_and_safe_deletion(client, tmp_path):
    """Test 18: Full lifecycle - creating analysis record and safely deleting it and files."""
    # Create test image files in storage
    test_stored = Config.UPLOADS_DIR / "test_delete_stored.jpg"
    test_ann = Config.OUTPUTS_DIR / "test_delete_ann.jpg"
    test_crop = Config.CROPS_DIR / "test_delete_comp_0.jpg"

    for p in [test_stored, test_ann, test_crop]:
        p.write_bytes(b"dummy image bytes")

    # Insert database record
    record = AnalysisRecord(
        analysis_id="del-test-uuid-456",
        original_filename="delete_me.jpg",
        stored_filename=test_stored.name,
        annotated_filename=test_ann.name,
        board_category="motherboard",
        board_condition="intact",
        detections_json=json.dumps([{"crop_filename": test_crop.name}])
    )
    with app.app_context():
        db.session.add(record)
        db.session.commit()

        # Verify files exist
        assert test_stored.exists()
        assert test_ann.exists()
        assert test_crop.exists()

    # Trigger POST delete route
    del_res = client.post("/delete/del-test-uuid-456", follow_redirects=True)
    assert del_res.status_code == 200
    assert b"deleted successfully" in del_res.data

    # Verify physical files are deleted
    assert not test_stored.exists()
    assert not test_ann.exists()
    assert not test_crop.exists()

    # Verify record removed from DB
    with app.app_context():
        assert AnalysisRecord.query.filter_by(analysis_id="del-test-uuid-456").first() is None


def test_end_to_end_pcb_analysis(client):
    """Verifies complete end-to-end pipeline: POST /analyze -> DB record -> results -> PDF."""
    sample_img_path = Path("data/sample_circuit.jpg")
    assert sample_img_path.exists(), "Sample circuit image must exist"

    with open(sample_img_path, "rb") as f:
        img_bytes = f.read()

    data = {
        "image": (io.BytesIO(img_bytes), "sample_circuit.jpg"),
        "board_category": "motherboard",
        "board_condition": "intact",
        "confidence": "0.25"
    }

    response = client.post("/analyze", data=data, content_type="multipart/form-data")
    assert response.status_code == 302
    redirect_url = response.headers["Location"]
    assert "/results/" in redirect_url

    analysis_id = redirect_url.split("/results/")[-1]

    # Inspect results page
    results_page = client.get(f"/results/{analysis_id}")
    assert results_page.status_code == 200
    assert b"sample_circuit.jpg" in results_page.data
    assert b"Component Inventory" in results_page.data
    assert b"Estimated Recovery Value" in results_page.data

    # Test PDF download for this real analysis
    pdf_res = client.get(f"/download/report/{analysis_id}")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["Content-Type"] == "application/pdf"
    assert pdf_res.data.startswith(b"%PDF")

    # Test CSV download
    csv_res = client.get(f"/download/csv/{analysis_id}")
    assert csv_res.status_code == 200
    assert b"CircuitSense AI - Component Inventory Export" in csv_res.data

