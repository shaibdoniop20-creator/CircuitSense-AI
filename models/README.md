# CircuitSense AI - Model Weights Directory

This directory stores trained deep learning weights for PCB component detection.

## Expected Weights File

- **Target File Path:** `models/best.pt`
- **Architecture:** Ultralytics YOLOv8 (nano `yolov8n.pt`, small `yolov8s.pt`, or medium `yolov8m.pt`)
- **Target Component Classes:**
  1. `integrated_circuit` (ICs, logic chips, DIP/SOIC packages)
  2. `microcontroller` (MCUs, ARM Cortex, ATmega, microchips)
  3. `capacitor` (Electrolytic canisters, tantalum, ceramic SMD)
  4. `connector` (Pin headers, USB/HDMI ports, terminal blocks)

## How CircuitSense AI Handles Weights

1. **Automatic Detection:**
   When the Flask application starts, it verifies if `models/best.pt` exists and is a valid PyTorch model file with PCB classes.
2. **Demo Mode Fallback:**
   If `models/best.pt` is missing or contains default COCO classes (e.g., person, car), CircuitSense AI automatically activates **Hackathon Demo Mode**.
   - Demo mode is visibly labeled throughout the user interface.
   - It performs OpenCV edge and contour localization over the uploaded PCB image to extract physical component candidates without fabricating false deep learning accuracy scores.
3. **Switching to Real YOLOv8 Inference:**
   Once you train your custom model (see `ML_SETUP.md`), simply copy the resulting `best.pt` into this directory:
   ```bash
   copy runs\detect\train\weights\best.pt models\best.pt
   ```
   Restart the Flask application (`python app.py`), and CircuitSense AI will immediately switch from Demo Mode to Production YOLOv8 Inference!
