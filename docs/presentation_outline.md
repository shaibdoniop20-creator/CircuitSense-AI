# CircuitSense AI: College Presentation Outline & Slide Deck Plan

This document provides a slide-by-slide guide for presenting **CircuitSense AI: Intelligent E-Waste Circuit Component Classifier & Material Analyzer** for an academic project evaluation, capstone defense, or technical seminar (10–12 slides, ~10–15 minutes presentation).

---

## Slide 1: Title & Team Details
- **Slide Title:** CircuitSense AI: Intelligent E-Waste Circuit Component Classifier & Material Analyzer
- **Subtitle:** An Automated Computer Vision Platform for PCB Component Localization, Salvage Triage, and Secondary Market Valuation
- **Bullet Points:**
  - Academic Year: 2026
  - Department: `[Insert Department, e.g., Department of Computer Science & Engineering]`
  - Institution: `[Insert Institution / College Name]`
- **Placeholders:**
  - **Student Name 1:** `[Student 1 Name]` | **USN:** `[Student 1 USN]`
  - **Student Name 2:** `[Student 2 Name]` | **USN:** `[Student 2 USN]`
  - **Student Name 3:** `[Student 3 Name]` | **USN:** `[Student 3 USN]`
  - **Student Name 4:** `[Student 4 Name]` | **USN:** `[Student 4 USN]`
  - **Project Guide:** `[Guide Name, Designation, Department]`
- **Suggested Visuals:** CircuitSense AI vector branding logo with a dark liquid-glass background accent.

---

## Slide 2: Introduction
- **Slide Title:** Introduction to the E-Waste Crisis
- **Bullet Points:**
  - Global e-waste generation exceeds 62 million metric tons annually, with printed circuit boards (PCBs) being the most concentrated resource stream.
  - PCBs contain high concentrations of base metals (copper, tin), precious metals (gold, silver, palladium), and hazardous elements (lead, mercury, cadmium).
  - Millions of discarded circuit boards contain functionally intact microcontrollers and logic chips that are destroyed prematurely during bulk shredding.
  - Early-stage automated optical inspection can divert functional chips into secondary repair and prototyping before destructive processing.
- **Suggested Visuals:** Photograph or infographic contrasting a discarded PCB versus urban mining material recovery streams.

---

## Slide 3: Problem Statement
- **Slide Title:** Challenges in Current E-Waste Sorting
- **Bullet Points:**
  - **Manual, Hazardous Sorting:** Scrap depot workers sort circuit boards by hand without optical assistance, leading to low sorting throughput and toxic lead exposure.
  - **Lack of Salvage Intelligence:** Technicians cannot easily identify whether a component is a reusable logic chip or an age-degraded capacitor.
  - **Destructive Melting:** High-value microcontrollers worth hundreds of rupees are melted down for mere copper scrap value.
  - **Misleading AI Claims:** Prior academic projects claim 2D cameras can measure chemical ppm directly, misleading recyclers.
- **Suggested Visuals:** Comparison matrix highlighting manual inspection bottlenecks vs. automated sorting.

---

## Slide 4: Project Objectives
- **Slide Title:** Project Objectives
- **Bullet Points:**
  - **Real-Time Localization:** Localize and classify five hardware component classes (ICs, MCUs, Transistors, Capacitors, Connectors) from single PCB images.
  - **Operational Salvage Triage:** Categorize detected parts into *Can Be Used Again*, *Inspect & Test First*, and *Recycle Only* (e.g. aged electrolytic capacitors).
  - **Secondary Valuation (INR):** Calculate wholesale recovery value brackets in Indian Rupees (₹) adjusted for board condition.
  - **Defensible Material Screening:** Implement empirical reference screening (Mode A) and honest physical limitation notices (Mode B).
  - **Accessible Local-First Architecture:** Run efficiently on student Windows laptops without requiring cloud servers or dedicated GPUs.
- **Suggested Visuals:** Flow diagram connecting PCB photograph $\rightarrow$ Detection $\rightarrow$ Triage $\rightarrow$ Valuation $\rightarrow$ PDF Report.

---

## Slide 5: Existing vs. Proposed System
- **Slide Title:** Comparative Evaluation
- **Bullet Points:**
  - **Industrial AOI Systems:** High accuracy but cost $50,000–$250,000 and require pristine CAD files; cannot handle dirty e-waste.
  - **Manual Sorting:** Inexpensive but hazardous, subjective, and slow.
  - **Generic Cloud Vision:** Lacks PCB hardware semantics.
  - **CircuitSense AI (Proposed):**
    - Free, local-first web deployment.
    - Custom YOLOv8 neural network paired with OpenCV optical fallback.
    - Domain-aware triage separating solid-state silicon from degraded capacitors.
    - Transparent Indian market salvage pricing catalogue.
- **Suggested Visuals:** 4-column comparison table comparing Cost, Speed, Accuracy, and Domain Intelligence.

---

## Slide 6: System Architecture & Data Flow
- **Slide Title:** System Architecture
- **Bullet Points:**
  - **Client Viewport:** Vanilla HTML5, CSS3 (*E-Waste Intelligence Liquid Glass*), and ES6 JavaScript.
  - **Application Controller:** Flask 3.1 WSGI router with parameterized SQLite persistence.
  - **Computer Vision Core:** Ultralytics YOLOv8 PyTorch model with automated OpenCV contour fallback.
  - **Circularity Engines:** Reusability Service, Valuation Service, and Material Analysis Service.
  - **Export Pipelines:** Vector PDF report generation via ReportLab, CSV inventory, and RESTful JSON.
- **Suggested Visuals:** High-level architectural block diagram (from `docs/system_architecture.md`).

---

## Slide 7: Technology Stack
- **Slide Title:** Technology Stack & Dependencies
- **Bullet Points:**
  - **Backend:** Python 3.14, Flask 3.1.3, Flask-SQLAlchemy 3.1.1, SQLite.
  - **Vision & AI:** Ultralytics YOLOv8, PyTorch 2.14, OpenCV 5.0, Pillow 12.3, NumPy 2.5.
  - **Reporting & Data:** ReportLab 5.0 (PDF engine), Chart.js 4.4.1 (CDN).
  - **Quality Assurance:** pytest 9.1.1 (19 automated unit/route tests, 69 integration tests).
  - **Zero Heavy Frontend Frameworks:** Native ES6 JavaScript and CSS3 custom properties for fast loading and low memory footprint.
- **Suggested Visuals:** Logos or tech-stack badge grid (Python, Flask, PyTorch, YOLOv8, SQLite, OpenCV, Chart.js).

---

## Slide 8: AI/ML Methodology & Component Classes
- **Slide Title:** YOLOv8 Neural Detection & Target Classes
- **Bullet Points:**
  - **Model Architecture:** Ultralytics YOLOv8 single-stage regression network utilizing CSPDarknet backbone and decoupled detection head.
  - **Component Classes:**
    1. `integrated_circuit` (Electric Cyan): Silicon logic packages, SOIC/DIP.
    2. `microcontroller` (Sapphire Blue): Programmable processing chips.
    3. `transistor` (Amethyst Violet): 3-terminal active switches (BJT, MOSFET).
    4. `capacitor` (Emerald Green): Passive storage components.
    5. `connector` (Radiant Amber): Headers, USB/HDMI interfaces, terminal blocks.
  - **Resilient Fallback:** Automatically switches to OpenCV adaptive thresholding and contour detection if weights return zero detections or demo mode is active.
- **Suggested Visuals:** Diagram showing PCB image overlaid with color-coded bounding boxes for each of the five classes.

---

## Slide 9: Application Demonstration & Screenshots
- **Slide Title:** Live Demonstration & User Interface
- **Bullet Points:**
  - **Ingestion HUD:** Drag-and-drop dropzone with client validation and 1-click "Load Demo Specimen" button.
  - **Results Dashboard:**
    - Segmented controls toggling Annotated, Original, and Side-by-Side Dual View.
    - Canvas zoom (50%–350%) and drag-to-pan inspection.
    - Dynamic confidence threshold filtering slider and individual component crop gallery.
  - **Salvage Intelligence:** Circular Salvage Yield Score gauge (0–100) and actionable operational triage cards.
  - **Inventory & Catalogue:** Chart.js doughnut chart and Indian Rupee valuation catalogue.
- **Suggested Visuals:** High-resolution screenshots of the Upload HUD, Results Dashboard, and Inventory Chart.

---

## Slide 10: Testing & Verified Results
- **Slide Title:** Verification & Experimental Results
- **Bullet Points:**
  - **Automated Unit Tests:** 19/19 pytest test cases passed (100% pass rate).
  - **Comprehensive Integration Suite:** 69/69 test assertions passed across routes, database persistence, and exports.
  - **Real PCB Test Execution:**
    - Physical board tested: $62.8\text{ KB}$ motherboard photograph.
    - Detected 11 components across all 5 classes with average confidence $> 85\%$.
    - Salvage triage: 10 Can Be Used Again (90.9%), 1 Recycle Only (9.1%), Salvage Score: 91/100.
    - Estimated recovery value: ₹451.0 INR.
  - **Defensive Security:** Verified file type filtering, 16 MB size limits, and path traversal sanitization.
- **Suggested Visuals:** Terminal screenshot of `pytest` passing 19/19 and generated PDF report preview.

---

## Slide 11: Limitations & Future Scope
- **Slide Title:** Limitations & Future Scope
- **Bullet Points:**
  - **Current Limitations:**
    - 2D RGB surface images cannot detect chemical composition or internal silicon degradation without spectrometry.
    - Components hidden beneath metal heatsinks or RF shields are optically obscured.
  - **Future Roadmap:**
    - Integration of Optical Character Recognition (OCR) to read IC part numbers (e.g. `STM32`, `NE555`) for live market lookup.
    - Deployment to low-power edge hardware (Raspberry Pi 5 with AI accelerator) for conveyor belt integration.
    - Oblique multi-angle cameras for 3D component height and volume profiling.
- **Suggested Visuals:** Roadmap milestone timeline or concept diagram of an automated edge conveyor sorting unit.

---

## Slide 12: Conclusion & References
- **Slide Title:** Conclusion & Academic References
- **Bullet Points:**
  - CircuitSense AI demonstrates that accessible, local-first artificial intelligence can empower circular electronic waste management.
  - Successfully combines deep learning detection with transparent salvage triage and scientifically defensible material screening.
  - Provides a complete, working platform ready for college evaluation, student hackathons, and circular economy research.
- **Key References:**
  1. *Baldé et al. (2024)*, Global E-Waste Monitor (UNITAR / ITU).
  2. *Jochum & Widmer (2018)*, EMPA E-Waste Characterisation Study.
  3. *Jocher et al. (2023)*, Ultralytics YOLOv8 Documentation.
  4. *CPCB India (2022)*, E-Waste (Management) Rules, Government of India.
- **Suggested Visuals:** "Thank You / Q&A" closing title with repository link and project credits.
