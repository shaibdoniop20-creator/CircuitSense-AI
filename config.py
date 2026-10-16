"""
CircuitSense AI Configuration
Intelligent E-Waste Circuit Component Classifier & Material Analyzer
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    # Flask Core
    SECRET_KEY = os.environ.get("SECRET_KEY", "circuitsense-ai-hackathon-secure-key-2026")
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

    # Storage Paths
    UPLOADS_DIR = BASE_DIR / "uploads"
    OUTPUTS_DIR = BASE_DIR / "outputs"
    CROPS_DIR = BASE_DIR / "crops"
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = BASE_DIR / "models"
    INSTANCE_DIR = BASE_DIR / "instance"

    # SQLite Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{INSTANCE_DIR / 'circuitsense.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security & Upload Validation
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_SIZE_MB", 16)) * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    # YOLOv8 Model Configuration
    MODEL_PATH = Path(os.environ.get("CIRCUITSENSE_MODEL_PATH", str(MODELS_DIR / "best.pt")))
    FORCE_DEMO = os.environ.get("CIRCUITSENSE_FORCE_DEMO", "false").lower() in ("true", "1", "yes")
    DEFAULT_CONFIDENCE = float(os.environ.get("CIRCUITSENSE_DEFAULT_CONFIDENCE", 0.25))
    DEFAULT_IOU = float(os.environ.get("CIRCUITSENSE_DEFAULT_IOU", 0.45))
    CURRENCY = os.environ.get("CIRCUITSENSE_CURRENCY", "INR")
    CURRENCY_SYMBOL = "₹" if CURRENCY == "INR" else "$"

    # Target Component Classes (IC, Microcontroller, Transistor, Capacitor, Connector/Port)
    TARGET_CLASSES = [
        "integrated_circuit",
        "microcontroller",
        "transistor",
        "capacitor",
        "connector"
    ]

    # Human-readable label mappings and color palettes (BGR for OpenCV, Hex for CSS)
    CLASS_METADATA = {
        "integrated_circuit": {
            "display_name": "Integrated Circuit (IC)",
            "short_name": "IC",
            "hex_color": "#00F2FE",       # Apple Electric Cyan
            "bgr_color": (254, 242, 0),   # Cyan BGR
            "rgb_color": (0, 242, 254),
            "description": "Silicon semiconductor chip packaging logic gates, amplifiers, memory, or controllers."
        },
        "microcontroller": {
            "display_name": "Microcontroller (MCU)",
            "short_name": "MCU",
            "hex_color": "#4FACFE",       # Apple Sapphire Blue
            "bgr_color": (254, 172, 79),  # Blue BGR
            "rgb_color": (79, 172, 254),
            "description": "Programmable processing unit containing CPU core, embedded flash, and peripheral controllers."
        },
        "transistor": {
            "display_name": "Transistor / MOSFET",
            "short_name": "Transistor",
            "hex_color": "#B388FF",       # Apple Amethyst Violet
            "bgr_color": (255, 136, 179), # Violet BGR
            "rgb_color": (179, 136, 255),
            "description": "Three-terminal active semiconductor device (BJT/MOSFET) for current switching and power amplification."
        },
        "capacitor": {
            "display_name": "Capacitor",
            "short_name": "Capacitor",
            "hex_color": "#00E676",       # Apple Emerald Green
            "bgr_color": (118, 230, 0),   # Green BGR
            "rgb_color": (0, 230, 118),
            "description": "Passive two-terminal component for capacitive energy storage and voltage rail smoothing."
        },
        "connector": {
            "display_name": "Connector / Port",
            "short_name": "Connector",
            "hex_color": "#FFB300",       # Apple Radiant Amber
            "bgr_color": (0, 179, 255),   # Amber BGR
            "rgb_color": (255, 179, 0),
            "description": "Electro-mechanical interface (USB, HDMI, audio, headers) for signal input/output and power coupling."
        }
    }
