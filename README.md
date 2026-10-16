# CircuitSense AI 🔬⚡

> **Intelligent E-Waste Circuit Component Classifier & Material Analyzer**  
> *"Detect Smarter. Recover More. Recycle Responsibly."*

![CircuitSense AI Dark Mode](static/images/logo.svg)

---

## 🌟 Overview

**CircuitSense AI** is a vision-based artificial intelligence platform developed for college AI/ML hackathons and electronic circularity workflows. It automates the hazardous, manual sorting of discarded printed circuit boards (PCBs) by detecting, localizing, and inventorying reusable electronic components:

1. **Integrated Circuits (ICs)**
2. **Microcontrollers (MCUs)**
3. **Capacitors**
4. **Connectors & Ports**

### Core Capabilities

- **Optical Localization & Annotation:** High-speed Ultralytics YOLOv8 inference with class-coded bounding boxes, corner accents, and confidence scores.
- **Transparent Wholesale Valuation:** Second-hand salvage pricing bands (Low, High, Midpoint) in Indian Rupees (INR) with board condition coefficients.
- **Defensible Material Analysis:** Two strictly separated modes:
  - **Mode A (Reference-Based Estimation):** Computes hazardous substance mass fractions based on empirical EMPA/UNEP disassembly benchmarks.
  - **Mode B (Insufficient Data Protocol):** Transparently declares when optical RGB imagery alone cannot determine chemical composition without spectrometry.
- **Interactive Results Dashboard:** iOS 27 Liquid Glass dark UI with image comparison (Annotated vs Original vs Side-by-Side Dual), zoom & pan, dynamic confidence slider, and component-level crops inspector.
- **Publication-Grade Exports:** One-click downloads for PDF audit reports, CSV inventory tables, raw JSON detections, and high-resolution annotated images.
- **Persistent SQLite History:** Search, filter, inspect, and safely delete previous board inspections.

---

## 🛠️ Technology Stack

| Domain | Technologies |
| :--- | :--- |
| **Computer Vision & AI** | Ultralytics YOLOv8, PyTorch 2.x, OpenCV, Pillow, NumPy |
| **Backend & Routing** | Python 3.11+, Flask 3.x, Flask-SQLAlchemy 3.x, SQLite |
| **Frontend & UI/UX** | HTML5, CSS3 (iOS 27 Liquid Glass Dark Theme), JavaScript, Chart.js |
| **Report Generation** | ReportLab (PDF Engine), Python CSV Module |
| **Testing & Quality** | PyTest (17 Comprehensive Integration & Unit Tests) |

---

## 🚀 Quickstart for Windows 11 & VS Code

The application is engineered to run on student Windows laptops without requiring CUDA GPUs or high-end servers.

### 1. Prerequisites
- **Operating System:** Windows 10 or Windows 11
- **Python:** Python 3.11, 3.12, 3.13, or 3.14 (Verified and tested on Python 3.14)
- **Editor:** Visual Studio Code

### 2. Create and Activate Virtual Environment

Open PowerShell in the project directory:
```powershell
# Create virtual environment
py -m venv .venv

# If PowerShell script execution is restricted, run:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

*(Or in Windows Command Prompt `cmd.exe`:)*
```cmd
.venv\Scripts\activate.bat
```

### 3. Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run Automated Test Suite
Verify that all 17 integration and unit tests pass:
```powershell
py -m pytest -v
```

### 5. Launch CircuitSense AI
```powershell
py app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📁 Project Directory Structure

```
Intelligent E-Waste Circuit Component Classifier & Material Analyzer/
├── app.py                      # Main Flask application, SQLite models, & API routes
├── config.py                   # Central configuration, file limits, & class styling
├── requirements.txt            # Python dependencies
├── README.md                   # Installation & operational documentation
├── ML_SETUP.md                 # Complete YOLOv8 training & dataset guide
├── .env.example                # Environment variables template
├── .gitignore                  # Git exclusions for models, uploads, & venv
│
├── models/
│   ├── README.md               # Model weights instructions
│   └── best.pt                 # Active YOLOv8 model weights
│
├── services/
│   ├── __init__.py
│   ├── detector.py             # YOLO inference & transparent Demo Mode fallback
│   ├── image_processor.py      # EXIF correction, CV annotations, & crops
│   ├── inventory.py            # Grouping, counting, & confidence calculations
│   ├── valuation.py            # Second-hand market recovery valuation engine
│   ├── material_analysis.py    # Mode A / Mode B e-waste hazardous analysis
│   └── report_generator.py     # ReportLab PDF generator & CSV exporter
│
├── data/
│   ├── component_prices.json   # Secondary market component pricing catalogue
│   ├── material_references.json# Empirical PCB chemical composition dataset
│   └── sample_circuit.jpg      # Offline test circuit board image
│
├── scripts/
│   ├── generate_sample_model.py # Initializes sample PCB YOLOv8 model weights
│   └── create_sample_pcb_image.py # Generates synthetic PCB image for testing
│
├── uploads/                    # Secure storage for original uploaded photos
├── outputs/                    # Generated annotated output circuit board images
├── crops/                      # Extracted component bounding box crops
├── instance/                   # SQLite database (circuitsense.db)
│
├── templates/
│   ├── base.html               # iOS 27 Liquid Glass base layout & sidebar
│   ├── index.html              # Landing overview with live metrics
│   ├── upload.html             # Drag-and-drop ingestion with live preview
│   ├── results.html            # Interactive analysis dashboard & image viewer
│   ├── history.html            # Audit history search, filters, & deletion
│   ├── inventory.html          # Component catalogue & cumulative chart
│   ├── material_analysis.html  # Scientific methodology & RoHS/WEEE standards
│   ├── about.html              # Technical stack & hackathon mission
│   └── errors/
│       ├── 404.html            # Not found error page
│       └── 500.html            # Processing error page
│
├── static/
│   ├── css/
│   │   └── style.css           # iOS 27 signature liquid glass design system
│   ├── js/
│   │   ├── main.js             # Global menu toggle & notifications
│   │   ├── upload.js           # Client validation & upload progress overlay
│   │   └── results.js          # Interactive zoom, pan, tabs, & confidence filter
│   └── images/
│       └── logo.svg            # CircuitSense AI vector logo
│
└── tests/
    ├── __init__.py
    ├── test_uploads.py         # Image validation, oversized, & corruption tests
    ├── test_inventory.py       # Aggregation, empty states, & confidence filters
    ├── test_valuation.py       # Price ranges, conditions, & unpriced fallbacks
    ├── test_material_analysis.py # Mode A vs Mode B tests
    └── test_routes.py          # End-to-end analysis, exports, 404s, & file cleanup
```

---

## ⚙️ Model Operation Modes

### 1. Verified Production YOLOv8 Mode
- Activated when valid PyTorch weights are placed at `models/best.pt`.
- Uses Ultralytics YOLOv8 neural network inference with PyTorch.
- Bounding boxes, class names, and confidence scores are generated directly by the model.

### 2. Hackathon Demonstration Mode
- Automatically activated if `models/best.pt` is missing or when `CIRCUITSENSE_FORCE_DEMO=true`.
- Visibly labeled as simulated throughout the dashboard to maintain scientific honesty.
- Executes real OpenCV edge/contour localization on the uploaded circuit board photo to identify physical components without fabricating deep learning scores.
- Allows teams and hackathon judges to evaluate the entire pipeline before custom model training is completed.

---

## 🔧 Customizing Reference Data

- **Component Pricing:** Edit `data/component_prices.json` to adjust unit price ranges, add component subtypes, or update condition multipliers.
- **Material References:** Edit `data/material_references.json` to update board mass benchmarks, metal reclamation concentrations, or RoHS regulatory classifications.

---

## 🧪 Automated Testing

Run the test suite at any time:
```powershell
py -m pytest -v
```

The automated test suite verifies 17 critical cases:
1. Valid image upload & dimension validation
2. Unsupported file type rejection (.pdf, .txt)
3. Corrupted image detection
4. Undersized image handling (<32x32)
5. Missing model weights graceful fallback
6. Model detector loading with valid weights
7. Empty detection handling
8. Multiple component detections
9. Component count aggregation & averages
10. Low-confidence detection filtering
11. Missing pricing catalogue data handling
12. Low, high, and midpoint valuation calculations
13. Mode A reference-based material estimation
14. Mode B insufficient data handling
15. Structured CSV inventory export
16. ReportLab PDF report generation
17. Invalid analysis ID handling & safe deletion of files and records

---

## ⚠️ Scientific & Regulatory Disclaimer

CircuitSense AI provides algorithmic visual classification, market estimates, and empirical reference benchmarks for decision support and academic research. Detections do not guarantee functional viability or commercial resale liquidity. Chemical hazardous material percentages are derived from published peer-reviewed studies (EMPA / UNEP) and must not replace certified non-destructive X-ray Fluorescence (XRF) spectrometry or destructive laboratory testing.
