# CircuitSense AI - Machine Learning Training & Integration Guide

A complete, beginner-friendly guide for training and integrating custom Ultralytics YOLOv8 models for Printed Circuit Board (PCB) component localization.

---

## 1. Computer Vision & YOLO Architecture

### Why YOLO for PCB Sorting?
Manual inspection of dismantled electronic modules is bottlenecked by the tiny footprint, dense clustering, and visual variability of surface-mount devices (SMD) and through-hole components. 

**YOLO (You Only Look Once)** frames detection as a single regression problem, passing the image through the convolutional backbone once to simultaneously predict:
1. **Bounding box coordinates** (`x_center`, `y_center`, `width`, `height`).
2. **Class probabilities** for target components:
   - `integrated_circuit` (ICs)
   - `microcontroller` (MCUs)
   - `capacitor` (Radial electrolytic, tantalum, ceramic)
   - `connector` (Headers, USB/HDMI, terminal blocks)
3. **Objectness confidence scores**.

This single-stage architecture yields millisecond inference latencies suitable for real-time sorting conveyors and local laptop execution without requiring high-end server GPUs.

---

## 2. Dataset Sourcing & Ethical Guidelines

### Open-Access Datasets
1. **Roboflow Universe PCB Datasets:** Search for "PCB Defect & Component Detection" or "E-Waste Circuit Boards".
2. **Kaggle PCB Datasets:** "Synthetic & Real PCB Component Detection".
3. **Self-Collected Hackathon Photography:** Dismantled consumer electronics, routers, motherboards, and power supplies.

> [!IMPORTANT]
> **Data Integrity:** Only use datasets licensed for academic and open-source research. Do not scrape copyrighted industrial CAD schematics without authorization.

---

## 3. Data Annotation & YOLO Format

### Tools
- **Roboflow Annotate** (Web-based, collaborative)
- **CVAT (Computer Vision Annotation Tool)** (Self-hosted or web)
- **LabelImg** (Local desktop tool)

### Class ID Mapping
Ensure your annotations map exactly to our target classes:
- `0`: `integrated_circuit`
- `1`: `microcontroller`
- `2`: `capacitor`
- `3`: `connector`

### Label Format (.txt)
Each corresponding image has a `.txt` file with one row per detected component:
```text
<class_id> <x_center_norm> <y_center_norm> <width_norm> <height_norm>
```
Example (`001_pcb.txt`):
```text
0 0.452 0.381 0.125 0.098
1 0.620 0.512 0.180 0.180
2 0.210 0.740 0.055 0.075
3 0.890 0.210 0.080 0.140
```

---

## 4. Train, Validation & Test Splitting (No Data Leakage)

Split your annotated images across directories:
- **Train (70%):** Model weights optimization.
- **Validation (20%):** Hyperparameter tuning and checkpoint selection (`best.pt`).
- **Test (10%):** Unseen benchmark evaluation.

> [!CAUTION]
> **Avoid Data Leakage:** Never split crops of the same physical circuit board across both train and validation sets! Variations in lighting or rotation of the same board must stay in the same split.

Directory Layout:
```
dataset/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    ├── val/
    └── test/
```

---

## 5. Dataset Configuration YAML (`pcb_dataset.yaml`)

Create `pcb_dataset.yaml`:
```yaml
# CircuitSense AI - PCB Component Dataset Configuration
path: ./dataset  # Dataset root directory
train: images/train
val: images/val
test: images/test

names:
  0: integrated_circuit
  1: microcontroller
  2: capacitor
  3: connector
```

---

## 6. Training with Ultralytics YOLOv8

### Option A: Command Line Interface (CLI)
```bash
# Nano architecture (Recommended for student Windows laptops without discrete GPU)
yolo detect train model=yolov8n.pt data=pcb_dataset.yaml epochs=50 imgsz=640 batch=16 workers=2

# Small architecture (If Nvidia GPU with CUDA is available)
yolo detect train model=yolov8s.pt data=pcb_dataset.yaml epochs=75 imgsz=640 batch=16 device=0
```

### Option B: Built-in Training Pipeline Script (`scripts/train_pcb_model.py`)
CircuitSense AI includes an automated end-to-end training script:

```bash
# 1. Rapid test / demo training on sample PCB specimens (CPU verified)
python scripts/train_pcb_model.py --demo-train

# 2. Full production training on your annotated dataset
python scripts/train_pcb_model.py --data dataset/pcb_dataset.yaml --epochs 50 --batch 8 --device cpu

# 3. If Nvidia GPU with CUDA is available
python scripts/train_pcb_model.py --data dataset/pcb_dataset.yaml --epochs 75 --batch 16 --device 0
```

The script automatically executes Ultralytics YOLOv8 training, computes validation benchmarks (mAP@50, Precision, Recall), and installs the resulting `best.pt` directly into `models/best.pt`.


---

## 7. Model Evaluation Metrics

When training completes, inspect the metrics in `runs/detect/circuitsense_yolov8n/`:

- **Precision (P):** $\frac{\text{True Positives}}{\text{True Positives} + \text{False Positives}}$ (How many detected ICs are actually ICs).
- **Recall (R):** $\frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$ (How many actual ICs on the board were detected).
- **mAP@50:** Mean Average Precision at IoU threshold 0.50 (Primary benchmark).
- **mAP@50-95:** Average precision across IoU thresholds from 0.50 to 0.95.

### Inspecting Errors
- **Confusion Matrix:** `runs/detect/circuitsense_yolov8n/confusion_matrix.png`
- **False Positives:** Check if connectors with pin holes are falsely classified as ICs.
- **Missed Detections:** Check if tiny 0402/0603 SMD capacitors were missed due to low input image resolution.

---

## 8. Connecting Trained Weights to CircuitSense AI

Once training finishes, copy the generated `best.pt`:
```bash
copy runs\detect\circuitsense_yolov8n\weights\best.pt models\best.pt
```

Start the application:
```bash
py app.py
```
CircuitSense AI automatically validates the model file, detects the configured PCB classes, and shifts from **Demo Mode** to **Verified Production YOLO Mode**!

---

## 9. Testing on Hackathon Unseen Benchmark Images

To validate your model on the 10 unseen hackathon circuit boards:
1. Open the CircuitSense AI web dashboard at `http://127.0.0.1:5000/analyze`.
2. Upload each unseen test image.
3. Review bounding box placement, confidence distributions, and component counts.
4. Export the comprehensive PDF audit report for presentation to hackathon judges.
