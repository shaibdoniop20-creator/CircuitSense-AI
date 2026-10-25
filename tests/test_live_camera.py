"""
Tests for Live Camera YOLOv8 Detection API and Frame Ingestion Routes.
Tests:
- GET /api/model-status
- POST /api/detect-frame (valid base64 frame, structured JSON response, annotated image)
- POST /api/detect-frame error handling (missing frame, invalid frame, too small)
- POST /analyze with base64 camera_frame (full pipeline persistence and redirect)
"""

import base64
import io
from pathlib import Path
import pytest
from PIL import Image

from app import app, db, AnalysisRecord
from config import Config


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


@pytest.fixture
def sample_image_base64():
    """Finds an existing sample image or creates a synthetic circuit board image."""
    uploads_dir = Path("uploads")
    sample_images = list(uploads_dir.glob("*.jpeg")) + list(uploads_dir.glob("*.jpg"))
    if sample_images:
        with open(sample_images[0], "rb") as f:
            raw = f.read()
    else:
        # Create a 640x480 test image
        img = Image.new("RGB", (640, 480), color=(30, 80, 50))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        raw = buf.getvalue()
    
    b64_str = base64.b64encode(raw).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"


def test_api_model_status(client):
    """Test /api/model-status returns 200 and expected metadata."""
    res = client.get("/api/model-status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "model_status" in data
    assert "target_classes" in data
    assert "integrated_circuit" in data["target_classes"]
    assert "microcontroller" in data["target_classes"]


def test_api_detect_frame_valid(client, sample_image_base64):
    """Test /api/detect-frame with valid base64 frame returns detections, counts, and annotated frame."""
    res = client.post(
        "/api/detect-frame",
        json={
            "frame": sample_image_base64,
            "confidence": 0.20,
            "board_condition": "intact",
            "return_annotated": True
        }
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "inference_ms" in data
    assert "detections" in data
    assert isinstance(data["detections"], list)
    assert "component_counts" in data
    assert "total_components" in data
    assert "unique_classes" in data
    assert "overall_confidence" in data
    assert "triage_summary" in data
    assert "annotated_frame" in data
    assert data["annotated_frame"].startswith("data:image/jpeg;base64,")
    assert "frame_dims" in data
    assert data["frame_dims"]["width"] >= 32
    assert data["frame_dims"]["height"] >= 32


def test_api_detect_frame_missing_frame(client):
    """Test /api/detect-frame returns 400 when frame is omitted."""
    res = client.post("/api/detect-frame", json={})
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "No frame" in data["message"]


def test_api_detect_frame_invalid_base64(client):
    """Test /api/detect-frame returns 400 for corrupted base64 string."""
    res = client.post(
        "/api/detect-frame",
        json={"frame": "data:image/jpeg;base64,not_valid_base64_data!!!"}
    )
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"


def test_api_detect_frame_too_small(client):
    """Test /api/detect-frame rejects tiny images (<32x32)."""
    tiny_img = Image.new("RGB", (16, 16), color="red")
    buf = io.BytesIO()
    tiny_img.save(buf, format="JPEG")
    tiny_b64 = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

    res = client.post("/api/detect-frame", json={"frame": tiny_b64})
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "too small" in data["message"]


def test_analyze_camera_frame_full_pipeline(client, sample_image_base64):
    """Test POST /analyze with base64 camera_frame saves record and returns redirect."""
    res = client.post(
        "/analyze",
        json={
            "camera_frame": sample_image_base64,
            "board_category": "motherboard",
            "board_condition": "intact",
            "confidence": 0.25
        }
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "analysis_id" in data
    assert "redirect_url" in data

    # Verify database record was saved
    with app.app_context():
        record = AnalysisRecord.query.filter_by(analysis_id=data["analysis_id"]).first()
        assert record is not None
        assert record.board_category == "motherboard"
        assert record.total_components >= 0
        assert (Config.UPLOADS_DIR / record.stored_filename).exists()
        assert (Config.OUTPUTS_DIR / record.annotated_filename).exists()
