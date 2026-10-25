"""
CircuitSense AI - Image Processor Service
Validates images, corrects EXIF orientation, generates annotated visualizations with
class-coded bounding boxes, and generates component-level crops for inspection.
"""

import os
import base64
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageOps, ImageFile
import cv2
import numpy as np

from config import Config

logger = logging.getLogger(__name__)

# Allow Pillow to open slightly truncated images if needed
ImageFile.LOAD_TRUNCATED_IMAGES = True


class ImageProcessor:
    """
    Handles image validation, sanitization, annotation rendering,
    and component crop extraction.
    """

    @staticmethod
    def validate_and_save_upload(
        file_storage,
        destination_path: Path
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validates the uploaded file for type, header validity, corruption, and dimensions.
        Saves the sanitized, orientation-corrected image to destination_path.
        Returns: (is_valid, error_message, image_metadata)
        """
        if not file_storage or not file_storage.filename:
            return False, "No file was provided for upload.", None

        filename = file_storage.filename.lower()
        ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
        if ext not in Config.ALLOWED_EXTENSIONS:
            return False, f"Unsupported file type ('.{ext}'). Allowed extensions: {', '.join(Config.ALLOWED_EXTENSIONS)}.", None

        try:
            # Open with Pillow to verify image validity and orientation
            pil_img = Image.open(file_storage.stream)
            pil_img.verify()

            # Rewind stream and re-open to load image data
            file_storage.stream.seek(0)
            pil_img = Image.open(file_storage.stream)

            # Auto-orient based on EXIF tag
            pil_img = ImageOps.exif_transpose(pil_img)

            # Convert RGBA/P/CMYK to RGB
            if pil_img.mode != "RGB":
                pil_img = pil_img.convert("RGB")

            width, height = pil_img.size

            if width < 32 or height < 32:
                return False, f"Image dimensions ({width}x{height}) are too small for component analysis (minimum 32x32).", None

            # Downscale extraordinarily huge images if needed to prevent memory exhaustion
            max_dimension = 3840  # 4K limit
            if width > max_dimension or height > max_dimension:
                pil_img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                width, height = pil_img.size

            # Save clean JPEG to destination
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            pil_img.save(str(destination_path), format="JPEG", quality=92)

            file_size_bytes = destination_path.stat().st_size

            metadata = {
                "width": width,
                "height": height,
                "file_size_bytes": file_size_bytes,
                "file_size_kb": round(file_size_bytes / 1024, 1),
                "file_size_mb": round(file_size_bytes / (1024 * 1024), 2),
                "format": "JPEG"
            }
            return True, None, metadata

        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False, f"Invalid or corrupted image file: {str(e)}", None

    @staticmethod
    def decode_base64_image(
        base64_data: str,
        max_bytes: int = 16 * 1024 * 1024
    ) -> Tuple[bool, Optional[str], Optional[np.ndarray], int, int]:
        """
        Safely decodes a base64 encoded image string (with or without data URL header).
        Validates size, format integrity, and pixel dimensions.
        Returns: (is_valid, error_message, img_bgr, width, height)
        """
        if not base64_data or not isinstance(base64_data, str):
            return False, "No frame data was supplied.", None, 0, 0

        try:
            # Strip data URL prefix if present (e.g., 'data:image/jpeg;base64,')
            if "," in base64_data:
                header, encoded = base64_data.split(",", 1)
            else:
                encoded = base64_data

            # Approximate size check before decoding
            approx_size = (len(encoded) * 3) / 4
            if approx_size > max_bytes:
                return False, f"Frame payload exceeds maximum allowed size ({round(max_bytes / (1024*1024), 1)} MB).", None, 0, 0

            # Decode base64 bytes
            img_bytes = base64.b64decode(encoded)
            if len(img_bytes) == 0:
                return False, "Decoded image buffer is empty (0 bytes).", None, 0, 0

            # Decode into OpenCV BGR numpy array
            np_arr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if img is None:
                return False, "OpenCV failed to decode image frame (corrupted or unsupported format).", None, 0, 0

            h, w = img.shape[:2]
            if w < 32 or h < 32:
                return False, f"Frame dimensions ({w}x{h}) are too small for component analysis (minimum 32x32 px).", None, 0, 0

            if w > 4096 or h > 4096:
                # Downscale large frame for memory efficiency and safety
                max_dim = 1920
                scale = min(max_dim / w, max_dim / h)
                new_w, new_h = int(w * scale), int(h * scale)
                img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                h, w = img.shape[:2]

            return True, None, img, w, h

        except Exception as e:
            logger.error(f"Failed to decode base64 frame: {e}")
            return False, f"Failed to decode image frame: {str(e)}", None, 0, 0

    @staticmethod
    def render_annotated_mat(
        img: np.ndarray,
        detections: List[Dict[str, Any]],
        confidence_filter: float = 0.0
    ) -> np.ndarray:
        """
        Renders clear bounding boxes, glowing badges, class labels, and confidence percentages
        onto an in-memory BGR numpy image.
        Returns: annotated BGR numpy image copy
        """
        if img is None or img.size == 0:
            return img

        annotated = img.copy()
        h, w = annotated.shape[:2]

        # Overlay layer for translucent glass badge backgrounds
        overlay = annotated.copy()

        # Class colors from Config
        class_meta = Config.CLASS_METADATA

        # Line thickness scales with image resolution
        thickness = max(2, int(round(min(w, h) / 360)))
        corner_len = max(12, int(round(min(w, h) / 45)))
        font_scale = max(0.45, min(w, h) / 1100.0)
        font = cv2.FONT_HERSHEY_DUPLEX

        for det in detections:
            conf = det.get("confidence", 0.0)
            if conf < confidence_filter:
                continue

            cls_name = det.get("class_name", "integrated_circuit")
            meta = class_meta.get(cls_name, class_meta.get("integrated_circuit", {}))
            color_bgr = meta.get("bgr_color", (192, 198, 53))

            bbox = det.get("bbox", {})
            x1 = max(0, min(w - 1, int(bbox.get("x1", 0))))
            y1 = max(0, min(h - 1, int(bbox.get("y1", 0))))
            x2 = max(0, min(w - 1, int(bbox.get("x2", 0))))
            y2 = max(0, min(h - 1, int(bbox.get("y2", 0))))

            if x2 <= x1 or y2 <= y1:
                continue

            # Draw semi-transparent bounding box fill
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color_bgr, -1)

            # Draw outer rectangle
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color_bgr, thickness)

            # Draw corner accents for high-tech aesthetic
            # Top-Left
            cv2.line(annotated, (x1, y1), (x1 + min(corner_len, (x2 - x1) // 2), y1), color_bgr, thickness + 2)
            cv2.line(annotated, (x1, y1), (x1, y1 + min(corner_len, (y2 - y1) // 2)), color_bgr, thickness + 2)
            # Top-Right
            cv2.line(annotated, (x2, y1), (x2 - min(corner_len, (x2 - x1) // 2), y1), color_bgr, thickness + 2)
            cv2.line(annotated, (x2, y1), (x2, y1 + min(corner_len, (y2 - y1) // 2)), color_bgr, thickness + 2)
            # Bottom-Left
            cv2.line(annotated, (x1, y2), (x1 + min(corner_len, (x2 - x1) // 2), y2), color_bgr, thickness + 2)
            cv2.line(annotated, (x1, y2), (x1, y2 - min(corner_len, (y2 - y1) // 2)), color_bgr, thickness + 2)
            # Bottom-Right
            cv2.line(annotated, (x2, y2), (x2 - min(corner_len, (x2 - x1) // 2), y2), color_bgr, thickness + 2)
            cv2.line(annotated, (x2, y2), (x2, y2 - min(corner_len, (y2 - y1) // 2)), color_bgr, thickness + 2)

            # Prepare Label Text
            short_name = meta.get("short_name", cls_name.upper())
            conf_str = f"{int(round(conf * 100))}%"
            label = f"{short_name} {conf_str}"

            # Calculate label text size
            (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, 1)

            # Position label badge (above box if space permits, else inside top of box)
            badge_pad_x = 6
            badge_pad_y = 5
            badge_w = text_w + (badge_pad_x * 2)
            badge_h = text_h + baseline + (badge_pad_y * 2)

            label_y1 = y1 - badge_h
            if label_y1 < 0:
                label_y1 = y1

            label_x1 = max(0, min(w - badge_w, x1))
            label_x2 = label_x1 + badge_w
            label_y2 = label_y1 + badge_h

            # Draw solid dark pill badge behind label text for contrast
            cv2.rectangle(annotated, (label_x1, label_y1), (label_x2, label_y2), (23, 25, 29), -1)
            # Thin color accent border for badge
            cv2.rectangle(annotated, (label_x1, label_y1), (label_x2, label_y2), color_bgr, 1)

            # Draw text
            text_x = label_x1 + badge_pad_x
            text_y = label_y2 - baseline - badge_pad_y + 2
            cv2.putText(annotated, label, (text_x, text_y), font, font_scale, (244, 246, 248), 1, cv2.LINE_AA)

        # Blend semi-transparent box highlights (alpha = 0.08)
        alpha = 0.08
        cv2.addWeighted(overlay, alpha, annotated, 1 - alpha, 0, annotated)

        return annotated

    @staticmethod
    def render_annotated_frame_base64(
        img: np.ndarray,
        detections: List[Dict[str, Any]],
        confidence_filter: float = 0.0,
        quality: int = 85
    ) -> str:
        """
        Renders bounding boxes onto an in-memory frame and returns a base64 JPEG data URL.
        Avoids all disk writes for high-speed live camera streams.
        """
        annotated = ImageProcessor.render_annotated_mat(img, detections, confidence_filter)
        success, encoded_buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if not success:
            raise RuntimeError("Failed to encode annotated frame as JPEG.")
        b64_str = base64.b64encode(encoded_buf).decode("utf-8")
        return f"data:image/jpeg;base64,{b64_str}"

    @staticmethod
    def render_annotated_image(
        original_image_path: str,
        output_image_path: str,
        detections: List[Dict[str, Any]],
        confidence_filter: float = 0.0
    ) -> Tuple[str, int, int]:
        """
        Renders clear bounding boxes, glowing badges, class labels, and confidence percentages.
        Guarantees that labels near edges stay within visible image bounds.
        Returns: (output_image_path, width, height)
        """
        img = cv2.imread(original_image_path)
        if img is None:
            raise ValueError(f"Could not load image from '{original_image_path}'")

        h, w = img.shape[:2]
        annotated = ImageProcessor.render_annotated_mat(img, detections, confidence_filter)

        # Save output image
        out_path = Path(output_image_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(out_path), annotated, [cv2.IMWRITE_JPEG_QUALITY, 92])

        return str(out_path), w, h

    @staticmethod
    def generate_component_crops(
        original_image_path: str,
        crops_dir: Path,
        analysis_id: str,
        detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extracts individual component bounding box crops with a slight padding margin,
        saving them to crops_dir so users can zoom in on individual detections.
        Returns updated detections with crop_filename and crop_url.
        """
        img = cv2.imread(original_image_path)
        if img is None:
            return detections

        h, w = img.shape[:2]
        crops_dir.mkdir(parents=True, exist_ok=True)

        for idx, det in enumerate(detections):
            bbox = det.get("bbox", {})
            x1 = bbox.get("x1", 0)
            y1 = bbox.get("y1", 0)
            x2 = bbox.get("x2", 0)
            y2 = bbox.get("y2", 0)

            bw = x2 - x1
            bh = y2 - y1

            if bw <= 0 or bh <= 0:
                continue

            # 12% padding around the bounding box for context
            pad_x = int(bw * 0.12)
            pad_y = int(bh * 0.12)

            crop_x1 = max(0, x1 - pad_x)
            crop_y1 = max(0, y1 - pad_y)
            crop_x2 = min(w, x2 + pad_x)
            crop_y2 = min(h, y2 + pad_y)

            crop_img = img[crop_y1:crop_y2, crop_x1:crop_x2]
            if crop_img.size == 0:
                continue

            crop_filename = f"{analysis_id}_crop_{idx}_{det.get('class_name', 'comp')}.jpg"
            crop_path = crops_dir / crop_filename
            cv2.imwrite(str(crop_path), crop_img, [cv2.IMWRITE_JPEG_QUALITY, 90])

            det["crop_filename"] = crop_filename
            det["crop_url"] = f"/crops/{crop_filename}"
            det["crop_dims"] = {
                "width": crop_img.shape[1],
                "height": crop_img.shape[0]
            }

        return detections
