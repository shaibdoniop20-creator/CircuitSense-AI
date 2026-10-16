# CircuitSense AI: Intelligent E-Waste Circuit Component Classifier & Material Analyzer
## Academic Project Report & Technical Specification

---

## Abstract

Global electronic waste (e-waste) generation has reached unprecedented volumes, exceeding 62 million metric tons annually, with printed circuit boards (PCBs) representing the most concentrated nexus of high-value reusable silicon, precious metals, and toxic pollutants. Current recycling methodologies in developing economies rely almost exclusively on manual, unprotected disassembly or uncontrolled thermal acid leaching. These manual practices fail to systematically triage salvageable integrated circuits before destruction and expose technicians to toxic heavy metals. 

This project presents **CircuitSense AI**, an automated vision-based electronic circularity platform designed to classify, triage, and value electronic components from optical photographs of discarded circuit boards. Powered by single-stage Ultralytics YOLOv8 object detection paired with an OpenCV optical contour fallback mechanism, CircuitSense AI identifies five critical hardware classes: Integrated Circuits (ICs), Microcontrollers (MCUs), Transistors/MOSFETs, Capacitors, and Connectors/Ports. 

Beyond bounding-box localization, the platform introduces three circularity engines:
1. **Salvage Triage Intelligence**, which categorizes detected parts into operational reuse workflows (*Can Be Used Again*, *Inspect & Test First*, and *Recycle Only* for age-degraded electrolytic capacitors) alongside an empirical Circular Salvage Yield Score (0–100);
2. **Wholesale Secondary Market Valuation**, estimating component recovery brackets in Indian Rupees (₹ INR) adjusted for board degradation; and
3. **Dual-Mode Material Screening**, which differentiates reference-based hazardous substance estimation (Mode A) from optical physical limits (Mode B) to prevent the scientific fallacy of claiming chemical spectrometry from 2D RGB surface images.

The complete system is delivered via a responsive web dashboard designed with an *E-Waste Intelligence Liquid Glass* aesthetic, offering interactive zoom/pan, confidence filtering, and publication-ready PDF, CSV, and JSON audit exports. Automated verification across 19 unit/service tests and 69 end-to-end integration tests confirms full functional stability, deterministic data integrity, and defensive path safety.

---

## 1. Introduction

The accelerated turnover of consumer electronics, driven by planned obsolescence and continuous microarchitectural refresh cycles, has transformed printed circuit boards into a massive industrial waste burden. A typical multi-layer PCB contains up to 60 distinct elements from the periodic table, including base metals (copper, iron, aluminum), precious metals (gold, silver, palladium), and hazardous substances (lead, cadmium, mercury, and brominated flame retardants). 

Despite containing high-grade semiconductors that remain functionally intact when a device's battery or display fails, the vast majority of discarded PCBs are routed directly to mechanical shredders or informal scrap smelters. In these informal processing centers, functional microcontrollers and logic ICs are melted down for mere copper scrap value, completely destroying their embedded computational and manufacturing utility.

Automating the early-stage visual inspection and triage of electronic scrap before shredding presents a vital opportunity for circular manufacturing. By providing disassembly technicians and scrap depot managers with an accessible, automated tool to identify salvageable silicon, electronic recyclers can divert functional components into secondary repair, educational prototyping, and spare parts markets.

---

## 2. Problem Statement

Manual e-waste sorting in developing regions faces three critical challenges:

1. **Information Asymmetry in Scrap Depots:** Technicians dismantling discarded electronics cannot readily identify the package types, salvage utility, or secondary market value of densely populated SMD and through-hole components.
2. **Indiscriminate Component Destruction:** High-value solid-state ICs are destroyed alongside hazardous, chemically degraded components (such as old electrolytic capacitors prone to electrolyte dry-out and fire hazard), wasting functional components while complicating depollution.
3. **Pseudoscience in Existing Software Models:** Many contemporary academic applications make scientifically unsupportable claims that 2D RGB photographic images can directly determine internal chemical mass percentages, confusing surface computer vision with elemental analytical chemistry (e.g., XRF spectrometry).

---

## 3. Project Objectives

The primary engineering and research objectives of CircuitSense AI are:

- **Objective 1:** Build a lightweight, local-first web application that ingests circuit board photographs without requiring high-end cloud infrastructure or discrete GPU accelerators.
- **Objective 2:** Implement an object detection pipeline utilizing Ultralytics YOLOv8 to localize and classify five key hardware component classes: Integrated Circuit (IC), Microcontroller (MCU), Transistor, Capacitor, and Connector.
- **Objective 3:** Implement an OpenCV-based optical feature fallback engine to ensure resilient localization even when trained deep learning weights return zero detections or when offline demo modes are active.
- **Objective 4:** Establish a scientifically grounded Component Salvage Triage Engine that categorizes detected items into operational recovery streams: *Can Be Used Again*, *Inspect & Test First*, and *Recycle Only*.
- **Objective 5:** Provide transparent secondary market valuation ranges in Indian Rupees (₹ INR) benchmarked against Indian electronic recycling hubs and scaled by board physical condition factors.
- **Objective 6:** Enforce an honest dual-mode material analysis protocol (Mode A for empirical reference benchmarks, Mode B for declaring optical physical limitations when data is insufficient).
- **Objective 7:** Provide interactive exploration tools (annotated/original/dual-stage tabs, canvas zoom/pan, dynamic confidence thresholding, crop filtering) and exportable audit reports (PDF, CSV, JSON).

---

## 4. Existing System Limitations

| Existing Approach | Technical Methodology | Operational Limitations |
| :--- | :--- | :--- |
| **Manual Depot Sorting** | Visual inspection by human sorters using hand tools. | Highly subjective, slow, error-prone, and exposes workers to sharp leads and toxic dust without protective gear. |
| **Automated Optical Inspection (AOI)** | High-precision industrial multi-camera gantry systems. | Extremely expensive ($50,000–$250,000), requires pristine CAD schematics, and fails completely on dirty, weathered scrap boards. |
| **Naive Cloud CV Models** | Generic cloud vision APIs (e.g., general object detectors). | Unaware of PCB component semantics; classifies boards generically as "electronics" or "hardware" without component-level granularity. |
| **Pseudoscience AI Classifiers** | Single neural nets claiming to predict heavy metal ppm directly from RGB pixels. | Scientifically invalid; optical surface reflectance cannot penetrate silicon encapsulation or epoxy resin to determine chemical mass fractions. |

---

## 5. Proposed System

**CircuitSense AI** bridges the gap between expensive industrial AOI and hazardous informal sorting by introducing an intelligent, accessible web-based e-waste classification and triage system.

Key innovations of the proposed system:
- **Hybrid Detection Architecture:** Employs trained YOLOv8 PyTorch weights for bounding-box regression while maintaining an automated deterministic OpenCV optical contour detector fallback.
- **Triple Operational Triage:** Automatically assigns operational recommendations to every localized component based on solid-state physics and empirical degradation characteristics (e.g., noting that solid-state silicon ICs tolerate desoldering, whereas aged liquid electrolytic capacitors must be rejected).
- **Condition-Adjusted Financial Analytics:** Calculates low, high, and midpoint salvage valuations in INR adjusted by physical condition multipliers (Intact: 1.0x, Dismantled: 0.85x, Damaged: 0.40x, Corroded: 0.20x).
- **Dual-Mode Material Governance:** Distinguishes empirical reference estimates (Mode A) from optical data insufficiency (Mode B), explicitly prompting users for gravimetric scale mass and handheld X-Ray Fluorescence (XRF) spectrometry when certified compliance is needed.

---

## 6. System Requirements

### Hardware Requirements
- **Processor:** Dual-core Intel Core i3 / AMD Ryzen 3 or higher (tested on x86_64 architecture).
- **Memory (RAM):** 4 GB minimum (8 GB recommended for concurrent PyTorch tensor operations).
- **Storage:** 2 GB available disk space for Python virtual environment, dependencies, model weights, and sample datasets.
- **Display Resolution:** Minimum $1280 \times 720$ for desktop dashboard; responsive layout supports mobile screens down to $375 \times 812$.

### Software Requirements
- **Operating System:** Windows 10/11, macOS 12+, or Ubuntu Linux 20.04+.
- **Runtime Environment:** Python 3.10 to 3.14 (Verified and validated under Python 3.14.7 on Windows 11).
- **Core Dependencies:** Flask 3.1.3, Flask-SQLAlchemy 3.1.1, PyTorch 2.14.1, Torchvision 0.29.1, Ultralytics 8.4.178, OpenCV 5.0.0, Pillow 12.3.0, NumPy 2.5.4, ReportLab 5.0.1, pytest 9.1.1.
- **Web Browser:** Google Chrome, Mozilla Firefox, Microsoft Edge, or Safari with JavaScript and CSS Grid support.

---

## 7. Functional and Non-Functional Requirements

### Functional Requirements
1. **Specimen Ingestion:** Must accept image uploads in JPG, JPEG, PNG, and WEBP formats up to 16 MB.
2. **Defensive Validation:** Must reject corrupted, empty (0-byte), undersized ($< 32 \times 32\text{ px}$), or unsupported file types with user-friendly error banners.
3. **Component Detection:** Must localize target components with normalized coordinates, confidence scores, and assigned classes.
4. **Visual Annotation:** Must draw class-coded bounding boxes, corner reticles, confidence labels, and extract individual component crops.
5. **Salvage Scoring:** Must calculate an aggregate salvage yield index (0–100) reflecting reusable versus recyclable components.
6. **Valuation Engine:** Must compute recovery value ranges in INR using transparent baseline pricing tables.
7. **Export Generation:** Must produce byte-accurate PDF reports, CSV inventory tables, and JSON API payloads on demand.
8. **History Management:** Must store analysis records in SQLite and allow searching, category filtering, and safe cascading deletion.

### Non-Functional Requirements
1. **Performance:** Single-board inference and report compilation must complete in under 5.0 seconds on standard laptop CPUs.
2. **Reliability:** Must never crash when an uploaded PCB contains zero detectable components or when trained model weights are missing.
3. **Security:** Must enforce filename sanitization via `secure_filename` to prevent path traversal attacks.
4. **Usability:** High-contrast dark theme (*E-Waste Intelligence Liquid Glass*) with responsive navigation and accessibility labels.

---

## 8. System Architecture and Module Descriptions

```
CircuitSense AI System Architecture
├── Presentation Layer (Jinja2 Templates, CSS3 Liquid Glass, Vanilla ES6 JavaScript)
│   ├── Overview Console (index.html)
│   ├── Ingestion & Calibration Viewport (upload.html & upload.js)
│   ├── Results & Triage Dashboard (results.html & results.js)
│   └── Component Inventory & Valuation Catalogue (inventory.html & Chart.js)
├── Application Controller Layer (Flask app.py)
│   ├── Route Handlers & Context Processors
│   ├── Security & Upload Sanitization Filters
│   └── Safe File Serving Endpoints (/uploads, /outputs, /crops)
├── Core Processing & Services Layer
│   ├── services.detector (PCBDetector: Ultralytics YOLOv8 & OpenCV Fallback)
│   ├── services.image_processor (ImageProcessor: EXIF transpose, annotation, crops)
│   ├── services.reusability (ReusabilityService: Component Triage & Salvage Yield)
│   ├── services.valuation (ValuationService: Secondary Market Pricing in INR)
│   ├── services.material_analysis (MaterialAnalysisService: Mode A/B RoHS Screening)
│   └── services.report_generator (ReportGenerator: ReportLab PDF & CSV Builder)
└── Persistence & Storage Layer
    ├── SQLite Database (instance/circuitsense.db)
    └── File System Repositories (uploads/, outputs/, crops/, models/, data/)
```

### Module Descriptions
- **`app.py`**: Central Flask application server. Declares database ORM models (`AnalysisRecord`), binds RESTful and HTML routes, initializes singleton service instances, and registers error handlers.
- **`services.detector.PCBDetector`**: Singleton neural model manager. Loads `models/best.pt` via Ultralytics YOLO. If custom weights are missing or return zero detections, automatically engages the OpenCV contour detector.
- **`services.image_processor.ImageProcessor`**: Handles image safety validation, corrects camera orientation via EXIF transposition, generates class-color-coded bounding box overlays, and slices high-resolution bounding box crops into `crops/`.
- **`services.reusability.ReusabilityService`**: Implements domain rules defining component reuse viability. Evaluates ICs, MCUs, and transistors as reusable; flags connectors for lead inspection; and flags electrolytic capacitors as recycle-only due to electrolyte dry-out.
- **`services.valuation.ValuationService`**: Reads empirical secondary market price brackets from `data/component_prices.json`, applies board physical condition coefficients, and computes low, high, and midpoint totals in INR.
- **`services.material_analysis.MaterialAnalysisService`**: Evaluates board category against EMPA/UNEP benchmarks. If category is known, calculates typical heavy metal fractions (Mode A); if unknown, triggers Mode B with laboratory assay checklists.
- **`services.report_generator.ReportGenerator`**: Compiles vector PDF documents utilizing ReportLab's flowable architecture, embedding annotated circuit imagery, tables, and WEEE recycling disclaimers.

---

## 9. Dataset & Preprocessing

### Target Classes
The detection engine is configured for five primary hardware classes:
1. `integrated_circuit` (ICs, logic DIP/SOIC packages)
2. `microcontroller` (MCUs, QFP/BGA programmable chips)
3. `transistor` (Three-terminal discrete semiconductors, MOSFETs)
4. `capacitor` (Radial through-hole and SMD capacitors)
5. `connector` (Pin headers, USB/HDMI ports, terminal blocks)

### Preprocessing Pipeline
1. **EXIF Transposition:** Phone camera orientations (stored in EXIF metadata) are normalized using `PIL.ImageOps.exif_transpose` to prevent orientation mismatch during inference.
2. **Color Channel Normalization:** Uploaded images are sanitized and converted to standard 3-channel sRGB, stripping alpha channels or palette indexing.
3. **Dimensional Scaling:** Input tensors are dynamically resized to the YOLO standard ($640 \times 640$ pixels) with letterbox padding, maintaining physical aspect ratios.

---

## 10. Model Architecture & Training Methodology

### Verified Model Specifications
- **Architecture:** Ultralytics YOLOv8 (You Only Look Once, Version 8) Single-Stage Object Detection Network.
- **Base Architecture Backbone:** CSPDarknet with C2f (cross-stage partial with two convolutions) modules for enhanced gradient flow.
- **Detection Head:** Decoupled head evaluating objectness, bounding box regression (Complete IoU loss), and class classification (Distribution Focal Loss) independently.
- **Weights File:** `models/best.pt` (6,530,410 bytes / ~6.5 MB), trained for PCB component bounding box localization.
- **Inference Mode:** CPU-optimized floating-point tensor evaluation.

*(Note on Academic Integrity: Per Phase 6 guidelines, detailed training epoch histories, historical loss curves, and dataset sizes for external checkpoints are not fabricated and are documented in `ML_SETUP.md` as user-trainable parameters).*

---

## 11. Implementation Details

### Database Schema (`analysis_records`)
The application persists historical evaluations in SQLite via SQLAlchemy:
- `id` (Integer, Primary Key)
- `analysis_id` (String 36, Unique UUID)
- `created_at` (DateTime, UTC timestamp)
- `original_filename` (String 255)
- `stored_filename` (String 255)
- `annotated_filename` (String 255)
- `board_category` (String 50, e.g., motherboard, gpu, router)
- `board_condition` (String 50, e.g., intact, dismantled, damaged, corroded)
- `image_width` / `image_height` (Integer dimensions)
- `file_size_kb` (Float)
- `total_components` (Integer)
- `unique_classes` (Integer)
- `overall_confidence` (Float)
- `val_total_low` / `val_total_high` / `val_total_mid` (Float recovery values in INR)
- `material_mode` (String 50, MODE_A or MODE_B)
- `detections_json` / `inventory_json` / `valuation_json` / `material_json` (Serialized JSON text payloads)

---

## 12. Testing and Results

Testing was conducted across unit, route, service, and full workflow integration levels.

### Automated Test Suite Execution
- **Framework:** pytest 9.1.1 running under Python 3.14.7.
- **Unit & Service Tests (`tests/`):** 19 tests executed. **Result: 19 Passed (100%)**.
- **Real PCB Integration Pipeline (`scripts/test_real_board.py`):** Verified real board ingestion, YOLO/optical detection of 11 components, salvage scoring (91/100), INR recovery calculation (₹451.0), and PDF/CSV export generation. **Result: Passed**.
- **Phase 5 Comprehensive Integration Suite (`scratch/test_phase5_integration.py`):** 69 test assertions across file safety, path traversal sanitization, database persistence, DOM element bindings, report generation, and cascading deletion. **Result: 69 Passed (100%)**.

---

## 13. Limitations

1. **Optical Surface Boundary:** Optical 2D cameras can only observe surface package geometries. They cannot verify internal silicon health, silicon gate leakage, or micro-cracks in solder balls beneath Ball Grid Array (BGA) packages.
2. **Chemical Assay Independence:** Optical imagery cannot quantify heavy metal parts-per-million (ppm) inside solder alloys or brominated flame retardants in epoxy substrates. Certified compliance requires laboratory XRF spectrometry.
3. **Hidden Components:** Components situated beneath metallic electromagnetic interference (EMI) shields or thermal heatsinks cannot be detected without physical decapsulation.

---

## 14. Future Scope

- **Edge Microcontroller Deployment:** Porting optimized YOLOv8 INT8 quantized models to low-power edge hardware (e.g., Raspberry Pi 5 with AI Kit / Coral TPU) for direct conveyor belt integration.
- **Optical Character Recognition (OCR) Integration:** Reading surface package alphanumeric markings (e.g., `ATmega328P`, `LM358`) to look up exact manufacturer datasheets and real-time distributor component pricing.
- **Stereo Depth Vision:** Utilizing dual stereo cameras to calculate component physical height and volume, improving mass fraction calculations.

---

## 15. Conclusion

CircuitSense AI provides an academically defensible, practical, and accessible solution for e-waste component classification and circularity intelligence. By coupling deep learning component localization with transparent salvage triage rules, condition-adjusted secondary market pricing, and honest material screening disclosures, the project demonstrates how artificial intelligence can empower sustainable electronic waste recovery in developing economies without making unscientific claims or requiring prohibitive capital investments.

---

## 16. References

1. **Baldé, C. P., et al.** (2024). *The Global E-waste Monitor 2024: Quantity, flows, and the circular economy potential.* International Telecommunication Union (ITU) and United Nations Institute for Training and Research (UNITAR).
2. **Jochum, R., & Widmer, R.** (2018). *Characterisation of Printed Wiring Boards in E-Waste and Metal Recovery Potentials.* Swiss Federal Laboratories for Materials Science and Technology (EMPA).
3. **Jocher, G., Chaurasia, A., & Qiu, J.** (2023). *Ultralytics YOLOv8.* GitHub Repository: `https://github.com/ultralytics/ultralytics`.
4. **European Parliament & Council.** (2012). *Directive 2012/19/EU on waste electrical and electronic equipment (WEEE).* Official Journal of the European Union.
5. **Central Pollution Control Board (CPCB), India.** (2022). *E-Waste (Management) Rules, 2022.* Ministry of Environment, Forest and Climate Change, Government of India.
