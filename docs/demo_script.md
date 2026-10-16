# CircuitSense AI: 3–5 Minute Live Demonstration Script

This script provides a concise, step-by-step demonstration walkthrough for presenting **CircuitSense AI** to evaluators, faculty judges, or technical review panels. Total running time: approximately 3.5 to 5.0 minutes.

---

## Preparation (Before the Presentation Begins)

1. Open PowerShell or Terminal in the project root:
   ```powershell
   cd "c:\Users\irfan\project\CircuitSense AI"
   .\.venv\Scripts\Activate.ps1
   python app.py
   ```
2. Open a web browser (Chrome or Edge) at `http://127.0.0.1:5000`.
3. Have the browser window maximized and set to 100% zoom.

---

## Step 1: System Overview & Architecture Introduction (0:00 – 0:45)

**Action:** Display the Overview page at `http://127.0.0.1:5000/`.

**Speaker Script:**
> *"Respected evaluators, this is **CircuitSense AI**, an intelligent e-waste circuit component classifier and material circularity analyzer. 
> 
> Printed circuit boards are packed with valuable, reusable semiconductors like microcontrollers and logic ICs, but in informal e-waste depots, they are typically sorted by hand or melted down for copper scrap. 
> 
> CircuitSense AI was engineered to automate this triage. Notice on the sidebar that our custom **YOLOv8 Neural Vision engine is online**, running entirely locally on this laptop without needing external cloud APIs. The dashboard shows aggregate statistics from past inspections, including total components detected, average confidence scores, and estimated secondary market recovery value in Indian Rupees."*

---

## Step 2: Specimen Ingestion & Calibration (0:45 – 1:30)

**Action:** Click the **"Analyze Circuit Board"** button in the top navigation or click **"New Analysis"** in the sidebar to open `http://127.0.0.1:5000/analyze`.

**Speaker Script:**
> *"Let's navigate to the New Analysis console. Here we see the **Specimen Viewport and Ingestion HUD**. The dropzone accepts standard circuit board photographs up to 16 megabytes and performs client-side validation to reject corrupted or undersized files.
> 
> For our demonstration, I will click **'Load Demo Specimen'**. This immediately loads a high-resolution motherboard photograph into the viewport. 
> 
> Notice how the telemetry HUD automatically detects the resolution—$800 \times 600$ pixels—and updates the calibration status to **'SPECIMEN CALIBRATED'**. 
> 
> On the right, technicians can select the circuit board category—we will select **'Motherboard'**—and specify the physical condition—**'Intact'**. We can also calibrate the detection confidence threshold using this slider. Let's set it to 30% and click **'Analyze Specimen'**."*

---

## Step 3: Neural Inference & Live Results Breakdown (1:30 – 2:45)

**Action:** Click the **"Analyze Specimen"** button. The animated modal overlay appears with progress milestones, then redirects to `/results/<analysis_id>`.

**Speaker Script:**
> *"When we submit, the application executes our single-stage YOLOv8 network. If trained weights return zero detections or in demo mode, our deterministic OpenCV optical feature detector acts as a reliable fallback so components are always localized.
> 
> Here on the **Results Dashboard**, we have complete telemetry:
> 1. **Top Metrics Bento Grid:** Our model detected 11 components across 5 distinct hardware classes, with an average confidence score of 87%.
> 2. **Component Reusability & Salvage Triage:** Notice this circular gauge showing an **overall Salvage Yield Score of 91/100**. Our system triaged 10 components as **'Can Be Used Again'**—these are solid-state silicon ICs, microcontrollers, and pin headers that can safely be desoldered for repair or education. 
> 3. **Critical Triage Rule:** Notice that 1 component is explicitly marked **'Cannot Be Used Again (Recycle Only)'**. That is an electrolytic capacitor. In circular electronics, liquid capacitors degrade and dry out over 3 to 8 years, creating fire and short-circuit hazards. CircuitSense AI automatically flags them to be routed to metal scrap recycling rather than reused."*

---

## Step 4: Interactive Inspection, Filters & Exports (2:45 – 3:45)

**Action:** Interact with the viewer controls:
1. Click the **"Original"** tab $\rightarrow$ original image appears.
2. Click the **"Side-by-Side"** tab $\rightarrow$ dual-stage comparison appears.
3. Switch back to **"Annotated"**.
4. Click **Zoom In (+)** twice $\rightarrow$ zoom level displays 150%. Drag the image with the mouse to demonstrate panning. Click **Reset**.
5. Adjust the **Confidence Filter** slider $\rightarrow$ observe low-confidence crops filter out.
6. Click the **"PDF Report"** button in the header $\rightarrow$ open the downloaded PDF report.

**Speaker Script:**
> *"The Results dashboard allows technicians to inspect localized hardware in detail:
> - We can toggle between the **Annotated view**, the **Original image**, and a **Side-by-Side dual view** for direct visual comparison.
> - We can zoom into dense regions up to 350% and pan across the board to inspect fine soldering leads.
> - We can dynamically filter component crops by confidence threshold or class. Clicking any crop highlights the specific component.
> 
> Furthermore, with one click, we can generate this **Audit-Ready PDF Report**. It embeds the annotated circuit board, full triage breakdown, and WEEE compliance guidelines, ready to hand over to depot supervisors or scrap buyers. We also provide full CSV and JSON exports."*

---

## Step 5: Inventory Dashboard & Honest Limitations (3:45 – 5:00)

**Action:** Click **"Component Inventory"** in the sidebar to open `http://127.0.0.1:5000/inventory`.

**Speaker Script:**
> *"Finally, let us look at the **Component Inventory & Valuation Catalogue**.
> 
> Here, our system aggregates detections across all scanned boards. This Chart.js doughnut chart visualizes the class distribution ratio, showing the exact proportion of ICs, MCUs, transistors, capacitors, and connectors across our scrap inventory.
> 
> Below the chart is our **Wholesale Salvage Pricing Catalogue**, quoting realistic secondary market price brackets in Indian Rupees benchmarked against recycling hubs like Mayapuri.
> 
> **To conclude with honest academic transparency regarding our system limitations:**
> - CircuitSense AI uses 2D surface optical RGB photography. It cannot look through metal heatsinks or detect chemical concentrations inside internal solder alloys without physical laboratory spectrometry like XRF. That is why our Material Analysis engine provides Mode B notices when data is insufficient.
> - In future work, we plan to integrate Optical Character Recognition to read chip part numbers for live market lookup and deploy to Raspberry Pi edge hardware.
> 
> Thank you, and we are now ready for your questions."*
