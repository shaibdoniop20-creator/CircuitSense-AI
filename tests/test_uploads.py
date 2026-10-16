"""
CircuitSense AI - Uploads & Image Processing Test Suite
Tests: Valid upload, unsupported type, corrupted image, oversized/undersized image.
"""

import io
from pathlib import Path
from PIL import Image
from werkzeug.datastructures import FileStorage

from services.image_processor import ImageProcessor
from config import Config


def test_valid_image_upload(tmp_path):
    """Test 1: Valid image upload validation and orientation handling."""
    # Create valid synthetic RGB image in memory
    img = Image.new("RGB", (320, 240), color=(50, 120, 60))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)

    file_storage = FileStorage(
        stream=buffer,
        filename="test_circuit.jpg",
        content_type="image/jpeg"
    )

    dest_path = tmp_path / "valid_saved.jpg"
    is_valid, err_msg, meta = ImageProcessor.validate_and_save_upload(file_storage, dest_path)

    assert is_valid is True
    assert err_msg is None
    assert meta is not None
    assert meta["width"] == 320
    assert meta["height"] == 240
    assert dest_path.exists()


def test_unsupported_file_type(tmp_path):
    """Test 2: Rejection of unsupported file types."""
    buffer = io.BytesIO(b"%PDF-1.4 Fake PDF Content")
    file_storage = FileStorage(
        stream=buffer,
        filename="document.pdf",
        content_type="application/pdf"
    )

    dest_path = tmp_path / "should_not_save.pdf"
    is_valid, err_msg, meta = ImageProcessor.validate_and_save_upload(file_storage, dest_path)

    assert is_valid is False
    assert "Unsupported file type" in err_msg
    assert meta is None
    assert not dest_path.exists()


def test_corrupted_image(tmp_path):
    """Test 3: Rejection of corrupted image data with valid extension."""
    buffer = io.BytesIO(b"Not a real jpeg file binary header garbage data")
    file_storage = FileStorage(
        stream=buffer,
        filename="corrupted.jpg",
        content_type="image/jpeg"
    )

    dest_path = tmp_path / "corrupted_saved.jpg"
    is_valid, err_msg, meta = ImageProcessor.validate_and_save_upload(file_storage, dest_path)

    assert is_valid is False
    assert "Invalid or corrupted image" in err_msg
    assert not dest_path.exists()


def test_undersized_image(tmp_path):
    """Test 4: Rejection of images that are too small to resolve components."""
    # 10x10 is below the 32x32 minimum resolution threshold
    tiny_img = Image.new("RGB", (10, 10), color=(10, 10, 10))
    buffer = io.BytesIO()
    tiny_img.save(buffer, format="PNG")
    buffer.seek(0)

    file_storage = FileStorage(
        stream=buffer,
        filename="tiny.png",
        content_type="image/png"
    )

    dest_path = tmp_path / "tiny_saved.png"
    is_valid, err_msg, meta = ImageProcessor.validate_and_save_upload(file_storage, dest_path)

    assert is_valid is False
    assert "too small" in err_msg
    assert not dest_path.exists()
