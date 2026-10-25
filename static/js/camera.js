/**
 * CircuitSense AI - Live Camera Vision & Real-Time YOLOv8 Detection Controller
 * Seamlessly integrates local webcam / USB inspection optics with the trained
 * YOLOv8 neural network backend.
 *
 * Features:
 * - HTML5 MediaDevices camera streaming with front/back/USB device selection
 * - Permission & error handling with HTTPS / localhost diagnostics
 * - Frame freezing & capture workflow
 * - Real-time component inference via /api/detect-frame
 * - Continuous live detection loop with controlled throttling and concurrency locking
 * - Glassmorphic canvas overlay with corner reticles and class-colored bounding badges
 * - Instant handoff to persistent full-board valuation and metallurgy reporting
 * - Leak-free stream lifecycle with automatic track disposal
 */

document.addEventListener("DOMContentLoaded", () => {
  // Mode Switcher Elements
  const modeUploadBtn = document.getElementById("modeUploadBtn");
  const modeCameraBtn = document.getElementById("modeCameraBtn");
  const uploadModeSection = document.getElementById("uploadModeSection");
  const cameraModeSection = document.getElementById("cameraModeSection");

  // Viewport & Stream Elements
  const cameraViewport = document.getElementById("cameraViewport");
  const cameraVideo = document.getElementById("cameraVideo");
  const cameraCanvas = document.getElementById("cameraCanvas");
  const cameraCapturedImg = document.getElementById("cameraCapturedImg");
  const cameraScanline = document.getElementById("cameraScanline");
  const cameraStandbyState = document.getElementById("cameraStandbyState");
  const cameraLiveDot = document.getElementById("cameraLiveDot");
  const cameraTagTitle = document.getElementById("cameraTagTitle");
  const cameraStatusPill = document.getElementById("cameraStatusPill");
  const cameraResBadge = document.getElementById("cameraResBadge");
  const frozenFrameBadge = document.getElementById("frozenFrameBadge");

  // Error Banner Elements
  const cameraErrorBanner = document.getElementById("cameraErrorBanner");
  const cameraErrorTitle = document.getElementById("cameraErrorTitle");
  const cameraErrorMessage = document.getElementById("cameraErrorMessage");
  const retryCameraBtn = document.getElementById("retryCameraBtn");

  // Device Selection Elements
  const cameraDeviceSelect = document.getElementById("cameraDeviceSelect");
  const switchCameraBtn = document.getElementById("switchCameraBtn");

  // Action Buttons
  const standbyStartBtn = document.getElementById("standbyStartBtn");
  const startCameraBtn = document.getElementById("startCameraBtn");
  const stopCameraBtn = document.getElementById("stopCameraBtn");
  const captureFrameBtn = document.getElementById("captureFrameBtn");
  const resumeFeedBtn = document.getElementById("resumeFeedBtn");
  const detectFrameBtn = document.getElementById("detectFrameBtn");
  const analyzeCapturedFrameBtn = document.getElementById("analyzeCapturedFrameBtn");

  // Continuous Detection Controls
  const continuousDetectToggle = document.getElementById("continuousDetectToggle");
  const detectionIntervalSlider = document.getElementById("detectionIntervalSlider");
  const intervalValText = document.getElementById("intervalValText");

  // Real-Time Telemetry Displays
  const cameraTotalComponentsVal = document.getElementById("cameraTotalComponentsVal");
  const cameraUniqueClassesSub = document.getElementById("cameraUniqueClassesSub");
  const cameraInferenceMsVal = document.getElementById("cameraInferenceMsVal");
  const cameraLastUpdateSub = document.getElementById("cameraLastUpdateSub");
  const cameraAvgConfVal = document.getElementById("cameraAvgConfVal");
  const cameraSalvageScoreBadge = document.getElementById("cameraSalvageScoreBadge");
  const triageReusableCount = document.getElementById("triageReusableCount");
  const triageTestCount = document.getElementById("triageTestCount");
  const triageScrapCount = document.getElementById("triageScrapCount");

  // Class Tally Counter Elements
  const countIC = document.getElementById("countIC");
  const countMCU = document.getElementById("countMCU");
  const countTransistor = document.getElementById("countTransistor");
  const countCapacitor = document.getElementById("countCapacitor");
  const countConnector = document.getElementById("countConnector");

  const tallyIC = document.getElementById("tallyIC");
  const tallyMCU = document.getElementById("tallyMCU");
  const tallyTransistor = document.getElementById("tallyTransistor");
  const tallyCapacitor = document.getElementById("tallyCapacitor");
  const tallyConnector = document.getElementById("tallyConnector");

  // Common Form Config References
  const confidenceSlider = document.getElementById("confidenceSlider");
  const boardCondition = document.getElementById("boardCondition");
  const boardCategory = document.getElementById("boardCategory");
  const cameraFramePayload = document.getElementById("cameraFramePayload");
  const uploadForm = document.getElementById("uploadForm");
  const processingOverlay = document.getElementById("processingOverlay");

  // Internal Camera Controller State
  let mediaStream = null;
  let isStreaming = false;
  let isFrozen = false;
  let currentFrozenBase64 = null;
  let isProcessingFrame = false;
  let continuousTimer = null;
  let isContinuousActive = false;
  let availableVideoDevices = [];
  let currentDeviceIndex = 0;

  // PCB Component Color Scheme (Matches Backend Config.CLASS_METADATA)
  const CLASS_COLORS = {
    integrated_circuit: { hex: "#00F2FE", label: "IC" },
    microcontroller: { hex: "#4FACFE", label: "MCU" },
    transistor: { hex: "#B388FF", label: "Transistor" },
    capacitor: { hex: "#00E676", label: "Capacitor" },
    connector: { hex: "#FFB300", label: "Connector" },
    resistor: { hex: "#FF5252", label: "Resistor" },
    diode: { hex: "#FF4081", label: "Diode" },
    led: { hex: "#E040FB", label: "LED" },
    switch: { hex: "#64FFDA", label: "Switch" },
    inductor: { hex: "#7C4DFF", label: "Inductor" }
  };

  // =========================================================================
  // 1. MODE SWITCHING (MODE A: UPLOAD vs MODE B: LIVE CAMERA)
  // =========================================================================

  function setIngestionMode(mode) {
    if (mode === "camera") {
      if (modeUploadBtn) {
        modeUploadBtn.classList.remove("active");
        modeUploadBtn.setAttribute("aria-selected", "false");
      }
      if (modeCameraBtn) {
        modeCameraBtn.classList.add("active");
        modeCameraBtn.setAttribute("aria-selected", "true");
      }
      if (uploadModeSection) uploadModeSection.style.display = "none";
      if (cameraModeSection) cameraModeSection.style.display = "block";

      // Refresh camera devices list on entering camera mode
      enumerateCameraDevices();

      // Update URL query parameter silently
      const url = new URL(window.location);
      url.searchParams.set("mode", "camera");
      window.history.replaceState({}, "", url);
    } else {
      // Switching to Upload mode: safely terminate camera stream
      stopCameraStream();

      if (modeCameraBtn) {
        modeCameraBtn.classList.remove("active");
        modeCameraBtn.setAttribute("aria-selected", "false");
      }
      if (modeUploadBtn) {
        modeUploadBtn.classList.add("active");
        modeUploadBtn.setAttribute("aria-selected", "true");
      }
      if (cameraModeSection) cameraModeSection.style.display = "none";
      if (uploadModeSection) uploadModeSection.style.display = "block";

      // Update URL query parameter silently
      const url = new URL(window.location);
      url.searchParams.delete("mode");
      window.history.replaceState({}, "", url);
    }
  }

  if (modeUploadBtn) {
    modeUploadBtn.addEventListener("click", () => setIngestionMode("upload"));
  }
  if (modeCameraBtn) {
    modeCameraBtn.addEventListener("click", () => setIngestionMode("camera"));
  }

  // Check initial mode from URL (e.g. ?mode=camera)
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("mode") === "camera") {
    setIngestionMode("camera");
  }

  // =========================================================================
  // 2. DEVICE ENUMERATION & SELECTION
  // =========================================================================

  async function enumerateCameraDevices() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
      console.warn("navigator.mediaDevices.enumerateDevices is not supported.");
      return;
    }

    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      availableVideoDevices = devices.filter((d) => d.kind === "videoinput");

      if (cameraDeviceSelect) {
        cameraDeviceSelect.innerHTML = "";

        if (availableVideoDevices.length === 0) {
          const opt = document.createElement("option");
          opt.value = "";
          opt.textContent = "Default Camera / Built-in Webcam";
          cameraDeviceSelect.appendChild(opt);
        } else {
          availableVideoDevices.forEach((device, idx) => {
            const opt = document.createElement("option");
            opt.value = device.deviceId;
            opt.textContent = device.label || `Optical Camera ${idx + 1}`;
            cameraDeviceSelect.appendChild(opt);
          });
        }
      }
    } catch (err) {
      console.warn("Failed to enumerate video devices:", err);
    }
  }

  // Listen for device connects / disconnects (e.g. USB inspection camera plugged in)
  if (navigator.mediaDevices && navigator.mediaDevices.addEventListener) {
    navigator.mediaDevices.addEventListener("devicechange", () => {
      enumerateCameraDevices();
    });
  }

  if (cameraDeviceSelect) {
    cameraDeviceSelect.addEventListener("change", () => {
      if (isStreaming) {
        // Restart stream with the newly chosen device
        startCameraStream(cameraDeviceSelect.value);
      }
    });
  }

  if (switchCameraBtn) {
    switchCameraBtn.addEventListener("click", () => {
      if (availableVideoDevices.length <= 1) {
        alert("Only one video device detected on this workstation.");
        return;
      }
      currentDeviceIndex = (currentDeviceIndex + 1) % availableVideoDevices.length;
      const targetDevice = availableVideoDevices[currentDeviceIndex];
      if (cameraDeviceSelect && targetDevice) {
        cameraDeviceSelect.value = targetDevice.deviceId;
      }
      if (isStreaming && targetDevice) {
        startCameraStream(targetDevice.deviceId);
      }
    });
  }

  // =========================================================================
  // 3. CAMERA STREAM LIFECYCLE (START / STOP / RESUME)
  // =========================================================================

  function showCameraError(title, message) {
    if (cameraErrorBanner) {
      if (cameraErrorTitle) cameraErrorTitle.textContent = title;
      if (cameraErrorMessage) cameraErrorMessage.textContent = message;
      cameraErrorBanner.style.display = "flex";
    }
    if (cameraStatusPill) {
      cameraStatusPill.textContent = "Error";
      cameraStatusPill.className = "cal-pill cal-danger";
    }
  }

  function hideCameraError() {
    if (cameraErrorBanner) {
      cameraErrorBanner.style.display = "none";
    }
  }

  async function startCameraStream(preferredDeviceId = null) {
    hideCameraError();

    // Check mediaDevices support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      showCameraError(
        "Camera API Not Supported",
        "Your browser does not support the HTML5 MediaDevices API, or the page is running in an insecure context. Please access via localhost (http://127.0.0.1:5000) or HTTPS."
      );
      return;
    }

    // Stop existing stream if currently running
    if (mediaStream) {
      mediaStream.getTracks().forEach((track) => track.stop());
      mediaStream = null;
    }

    const deviceId = preferredDeviceId || (cameraDeviceSelect ? cameraDeviceSelect.value : null);

    const constraints = {
      audio: false,
      video: {
        width: { ideal: 1920 },
        height: { ideal: 1080 }
      }
    };

    if (deviceId && deviceId !== "") {
      constraints.video.deviceId = { exact: deviceId };
    }

    try {
      if (startCameraBtn) {
        startCameraBtn.disabled = true;
        startCameraBtn.innerHTML = `
          <svg class="liquid-spinner" style="width: 14px; height: 14px; border-width: 2px; margin-right: 6px; display: inline-block;" viewBox="0 0 24 24"></svg>
          Initializing...
        `;
      }

      mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      cameraVideo.srcObject = mediaStream;

      // Wait for video metadata to play
      await new Promise((resolve) => {
        cameraVideo.onloadedmetadata = () => {
          cameraVideo.play();
          resolve();
        };
      });

      isStreaming = true;
      isFrozen = false;
      currentFrozenBase64 = null;

      // Update UI displays
      if (cameraStandbyState) cameraStandbyState.style.display = "none";
      if (cameraCapturedImg) cameraCapturedImg.style.display = "none";
      if (cameraVideo) cameraVideo.style.display = "block";
      if (cameraCanvas) cameraCanvas.style.display = "block";
      if (frozenFrameBadge) frozenFrameBadge.classList.remove("active");

      if (startCameraBtn) {
        startCameraBtn.style.display = "none";
        startCameraBtn.disabled = false;
      }
      if (stopCameraBtn) stopCameraBtn.style.display = "inline-flex";
      if (captureFrameBtn) {
        captureFrameBtn.disabled = false;
        captureFrameBtn.style.display = "inline-flex";
      }
      if (resumeFeedBtn) resumeFeedBtn.style.display = "none";
      if (detectFrameBtn) detectFrameBtn.disabled = false;
      if (continuousDetectToggle) continuousDetectToggle.disabled = false;

      if (cameraLiveDot) cameraLiveDot.style.display = "inline-block";
      if (cameraStatusPill) {
        cameraStatusPill.textContent = "Live Stream Active";
        cameraStatusPill.className = "cal-pill cal-emerald";
      }
      if (cameraResBadge) {
        cameraResBadge.textContent = `${cameraVideo.videoWidth || 1280}×${cameraVideo.videoHeight || 720}`;
        cameraResBadge.style.display = "inline-flex";
      }

      // Re-enumerate to get friendly device names now that permission was granted
      await enumerateCameraDevices();

      // Sync canvas dimensions
      resizeOverlayCanvas();
    } catch (err) {
      console.error("Camera access error:", err);
      let errorTitle = "Camera Access Denied";
      let errorMsg = "Unable to start optical video stream.";

      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        errorTitle = "Camera Permission Denied";
        errorMsg = "Browser camera access was blocked. Please click the lock or camera icon in your address bar to allow camera access for this application.";
      } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
        errorTitle = "No Camera Detected";
        errorMsg = "No physical optical camera or USB video sensor was detected on this computer. Please connect a webcam and click Retry.";
      } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
        errorTitle = "Camera In Use by Another App";
        errorMsg = "Your webcam hardware is currently locked by another program (such as Zoom, Teams, or another browser tab). Please close conflicting apps and retry.";
      } else if (err.name === "OverconstrainedError") {
        // Fall back to unconstrained video request
        try {
          mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
          cameraVideo.srcObject = mediaStream;
          cameraVideo.play();
          isStreaming = true;
          return;
        } catch (fallbackErr) {
          errorTitle = "Constraint Error";
          errorMsg = fallbackErr.message;
        }
      } else {
        errorMsg = err.message || "An unexpected error prevented camera startup.";
      }

      showCameraError(errorTitle, errorMsg);
      stopCameraStream();
    } finally {
      if (startCameraBtn) {
        startCameraBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          Start Camera
        `;
        startCameraBtn.disabled = false;
      }
    }
  }

  function stopCameraStream() {
    // Stop continuous detection loop if active
    stopContinuousDetection();

    if (mediaStream) {
      mediaStream.getTracks().forEach((track) => track.stop());
      mediaStream = null;
    }

    if (cameraVideo) {
      cameraVideo.pause();
      cameraVideo.srcObject = null;
      cameraVideo.style.display = "none";
    }

    isStreaming = false;
    isFrozen = false;
    currentFrozenBase64 = null;

    // Reset Viewport UI
    if (cameraStandbyState) cameraStandbyState.style.display = "flex";
    if (cameraCapturedImg) cameraCapturedImg.style.display = "none";
    if (cameraCanvas) {
      const ctx = cameraCanvas.getContext("2d");
      ctx.clearRect(0, 0, cameraCanvas.width, cameraCanvas.height);
      cameraCanvas.style.display = "none";
    }
    if (frozenFrameBadge) frozenFrameBadge.classList.remove("active");

    // Reset Buttons
    if (startCameraBtn) {
      startCameraBtn.style.display = "inline-flex";
      startCameraBtn.disabled = false;
    }
    if (stopCameraBtn) stopCameraBtn.style.display = "none";
    if (captureFrameBtn) {
      captureFrameBtn.style.display = "inline-flex";
      captureFrameBtn.disabled = true;
    }
    if (resumeFeedBtn) resumeFeedBtn.style.display = "none";
    if (detectFrameBtn) detectFrameBtn.disabled = true;
    if (analyzeCapturedFrameBtn) analyzeCapturedFrameBtn.disabled = true;
    if (continuousDetectToggle) {
      continuousDetectToggle.checked = false;
      continuousDetectToggle.disabled = true;
    }

    if (cameraLiveDot) cameraLiveDot.style.display = "none";
    if (cameraStatusPill) {
      cameraStatusPill.textContent = "Standby";
      cameraStatusPill.className = "cal-pill";
    }
    if (cameraResBadge) cameraResBadge.style.display = "none";
  }

  function resizeOverlayCanvas() {
    if (!cameraCanvas || !cameraVideo) return;
    const w = cameraVideo.videoWidth || 1280;
    const h = cameraVideo.videoHeight || 720;
    cameraCanvas.width = w;
    cameraCanvas.height = h;
  }

  window.addEventListener("resize", resizeOverlayCanvas);

  // Hook camera lifecycle buttons
  if (standbyStartBtn) standbyStartBtn.addEventListener("click", () => startCameraStream());
  if (startCameraBtn) startCameraBtn.addEventListener("click", () => startCameraStream());
  if (stopCameraBtn) stopCameraBtn.addEventListener("click", stopCameraStream);
  if (retryCameraBtn) retryCameraBtn.addEventListener("click", () => startCameraStream());

  // Safe window unload cleanup
  window.addEventListener("beforeunload", stopCameraStream);
  window.addEventListener("pagehide", stopCameraStream);

  // =========================================================================
  // 4. FRAME FREEZE & CAPTURE
  // =========================================================================

  function getFrameAsBase64() {
    if (isFrozen && currentFrozenBase64) {
      return currentFrozenBase64;
    }

    if (!cameraVideo || cameraVideo.readyState < 2) {
      return null;
    }

    const captureCanvas = document.createElement("canvas");
    const w = cameraVideo.videoWidth || 1280;
    const h = cameraVideo.videoHeight || 720;
    captureCanvas.width = w;
    captureCanvas.height = h;

    const ctx = captureCanvas.getContext("2d");
    ctx.drawImage(cameraVideo, 0, 0, w, h);
    return captureCanvas.toDataURL("image/jpeg", 0.92);
  }

  function freezeFrame() {
    if (!isStreaming) return;

    const base64 = getFrameAsBase64();
    if (!base64) return;

    currentFrozenBase64 = base64;
    isFrozen = true;

    // Display frozen frame
    if (cameraCapturedImg) {
      cameraCapturedImg.src = base64;
      cameraCapturedImg.style.display = "block";
    }
    if (cameraVideo) cameraVideo.style.display = "none";
    if (frozenFrameBadge) frozenFrameBadge.classList.add("active");

    if (captureFrameBtn) captureFrameBtn.style.display = "none";
    if (resumeFeedBtn) resumeFeedBtn.style.display = "inline-flex";
    if (analyzeCapturedFrameBtn) analyzeCapturedFrameBtn.disabled = false;

    // Save into hidden input for full analysis if triggered
    if (cameraFramePayload) cameraFramePayload.value = base64;

    if (cameraStatusPill) {
      cameraStatusPill.textContent = "Frame Frozen";
      cameraStatusPill.className = "cal-pill cal-amber";
    }
  }

  function resumeLiveFeed() {
    if (!isStreaming) return;

    isFrozen = false;
    currentFrozenBase64 = null;

    if (cameraCapturedImg) cameraCapturedImg.style.display = "none";
    if (cameraVideo) {
      cameraVideo.style.display = "block";
      cameraVideo.play();
    }
    if (frozenFrameBadge) frozenFrameBadge.classList.remove("active");

    if (captureFrameBtn) captureFrameBtn.style.display = "inline-flex";
    if (resumeFeedBtn) resumeFeedBtn.style.display = "none";

    // Clear overlay canvas
    if (cameraCanvas) {
      const ctx = cameraCanvas.getContext("2d");
      ctx.clearRect(0, 0, cameraCanvas.width, cameraCanvas.height);
    }

    if (cameraStatusPill) {
      cameraStatusPill.textContent = "Live Stream Active";
      cameraStatusPill.className = "cal-pill cal-emerald";
    }
  }

  if (captureFrameBtn) captureFrameBtn.addEventListener("click", freezeFrame);
  if (resumeFeedBtn) resumeFeedBtn.addEventListener("click", resumeLiveFeed);

  // =========================================================================
  // 5. YOLOv8 LIVE INFERENCE & OVERLAY RENDERING
  // =========================================================================

  function renderDetectionsOnCanvas(detections, frameWidth, frameHeight) {
    if (!cameraCanvas) return;
    const ctx = cameraCanvas.getContext("2d");
    ctx.clearRect(0, 0, cameraCanvas.width, cameraCanvas.height);

    if (!detections || detections.length === 0) return;

    // Line scaling
    const minDim = Math.min(cameraCanvas.width, cameraCanvas.height);
    const lineWidth = Math.max(2, Math.round(minDim / 360));
    const cornerLen = Math.max(12, Math.round(minDim / 45));
    const fontSize = Math.max(11, Math.round(minDim / 45));

    ctx.font = `600 ${fontSize}px 'JetBrains Mono', monospace`;

    detections.forEach((det) => {
      const bbox = det.bbox || {};
      const x1 = Math.round(bbox.x1 || 0);
      const y1 = Math.round(bbox.y1 || 0);
      const x2 = Math.round(bbox.x2 || 0);
      const y2 = Math.round(bbox.y2 || 0);
      const bw = x2 - x1;
      const bh = y2 - y1;

      if (bw <= 0 || bh <= 0) return;

      const clsName = det.class_name || "integrated_circuit";
      const colorInfo = CLASS_COLORS[clsName] || { hex: "#00F2FE", label: clsName.toUpperCase() };
      const colorHex = colorInfo.hex;
      const confPct = Math.round((det.confidence || 0) * 100);

      // Semi-transparent box fill
      ctx.fillStyle = colorHex + "1A"; // ~10% opacity
      ctx.fillRect(x1, y1, bw, bh);

      // Outer rectangle stroke
      ctx.strokeStyle = colorHex;
      ctx.lineWidth = lineWidth;
      ctx.strokeRect(x1, y1, bw, bh);

      // High-tech corner brackets
      ctx.lineWidth = lineWidth + 2;
      const cLenX = Math.min(cornerLen, Math.floor(bw / 2));
      const cLenY = Math.min(cornerLen, Math.floor(bh / 2));

      // Top-Left
      ctx.beginPath();
      ctx.moveTo(x1, y1 + cLenY);
      ctx.lineTo(x1, y1);
      ctx.lineTo(x1 + cLenX, y1);
      ctx.stroke();

      // Top-Right
      ctx.beginPath();
      ctx.moveTo(x2 - cLenX, y1);
      ctx.lineTo(x2, y1);
      ctx.lineTo(x2, y1 + cLenY);
      ctx.stroke();

      // Bottom-Left
      ctx.beginPath();
      ctx.moveTo(x1, y2 - cLenY);
      ctx.lineTo(x1, y2);
      ctx.lineTo(x1 + cLenX, y2);
      ctx.stroke();

      // Bottom-Right
      ctx.beginPath();
      ctx.moveTo(x2 - cLenX, y2);
      ctx.lineTo(x2, y2);
      ctx.lineTo(x2, y2 - cLenY);
      ctx.stroke();

      // Label Badge
      const shortName = colorInfo.label;
      const labelText = `${shortName} ${confPct}%`;
      const textMetrics = ctx.measureText(labelText);
      const padX = 6;
      const padY = 4;
      const badgeW = textMetrics.width + padX * 2;
      const badgeH = fontSize + padY * 2;

      let badgeY = y1 - badgeH;
      if (badgeY < 0) badgeY = y1;
      let badgeX = Math.max(0, Math.min(cameraCanvas.width - badgeW, x1));

      // Badge pill background (Light Liquid Glass Badge)
      ctx.fillStyle = "rgba(255, 255, 255, 0.94)";
      ctx.fillRect(badgeX, badgeY, badgeW, badgeH);

      // Badge border accent
      ctx.strokeStyle = colorHex;
      ctx.lineWidth = 1.5;
      ctx.strokeRect(badgeX, badgeY, badgeW, badgeH);

      // Label Text (Crisp Dark Charcoal)
      ctx.fillStyle = "#1D1E22";
      ctx.fillText(labelText, badgeX + padX, badgeY + badgeH - padY);
    });
  }

  function updateTelemetryUI(data) {
    if (!data) return;

    // Total components and latency
    if (cameraTotalComponentsVal) cameraTotalComponentsVal.textContent = data.total_components ?? 0;
    if (cameraUniqueClassesSub) cameraUniqueClassesSub.textContent = `${data.unique_classes ?? 0} Classes`;
    if (cameraInferenceMsVal) cameraInferenceMsVal.textContent = `${data.inference_ms ?? 0} ms`;
    if (cameraAvgConfVal) cameraAvgConfVal.textContent = `${data.overall_confidence_pct ?? 0}%`;

    const now = new Date();
    if (cameraLastUpdateSub) {
      cameraLastUpdateSub.textContent = `At ${now.toTimeString().split(" ")[0]}`;
    }

    // Class Tally Counters
    const counts = data.component_counts || {};
    const icQty = counts.integrated_circuit || 0;
    const mcuQty = counts.microcontroller || 0;
    const transQty = counts.transistor || 0;
    const capQty = counts.capacitor || 0;
    const connQty = counts.connector || 0;

    if (countIC) countIC.textContent = icQty;
    if (countMCU) countMCU.textContent = mcuQty;
    if (countTransistor) countTransistor.textContent = transQty;
    if (countCapacitor) countCapacitor.textContent = capQty;
    if (countConnector) countConnector.textContent = connQty;

    // Highlight active cards
    if (tallyIC) tallyIC.classList.toggle("has-detections", icQty > 0);
    if (tallyMCU) tallyMCU.classList.toggle("has-detections", mcuQty > 0);
    if (tallyTransistor) tallyTransistor.classList.toggle("has-detections", transQty > 0);
    if (tallyCapacitor) tallyCapacitor.classList.toggle("has-detections", capQty > 0);
    if (tallyConnector) tallyConnector.classList.toggle("has-detections", connQty > 0);

    // Triage Summary Snapshot
    const triage = data.triage_summary || {};
    if (triageReusableCount) triageReusableCount.textContent = triage.can_reuse_count || 0;
    if (triageTestCount) triageTestCount.textContent = triage.needs_testing_count || 0;
    if (triageScrapCount) triageScrapCount.textContent = triage.recycle_only_count || 0;

    if (cameraSalvageScoreBadge) {
      const score = triage.salvage_score ?? 75;
      cameraSalvageScoreBadge.textContent = `Yield: ${score}/100`;
    }
  }

  async function detectCurrentFrame(isSilent = false) {
    if (isProcessingFrame) return; // Prevent concurrent inference requests
    if (!isStreaming) return;

    const frameBase64 = getFrameAsBase64();
    if (!frameBase64) return;

    isProcessingFrame = true;

    if (!isSilent) {
      if (detectFrameBtn) {
        detectFrameBtn.disabled = true;
        detectFrameBtn.innerHTML = `
          <svg class="liquid-spinner" style="width: 14px; height: 14px; border-width: 2px; margin-right: 6px; display: inline-block;" viewBox="0 0 24 24"></svg>
          Inferring...
        `;
      }
      if (cameraStatusPill) {
        cameraStatusPill.textContent = "Inferring...";
        cameraStatusPill.className = "cal-pill cal-cyan";
      }
    }

    try {
      const confThreshold = parseFloat(confidenceSlider ? confidenceSlider.value : 0.25);
      const cond = boardCondition ? boardCondition.value : "intact";
      const cat = boardCategory ? boardCategory.value : "unknown";

      const response = await fetch("/api/detect-frame", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          frame: frameBase64,
          confidence: confThreshold,
          board_condition: cond,
          board_category: cat,
          return_annotated: true
        })
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.message || `Server error ${response.status}`);
      }

      const data = await response.json();

      // Render bounding boxes on overlay canvas
      renderDetectionsOnCanvas(data.detections || [], data.frame_dims?.width, data.frame_dims?.height);

      // If user froze the frame, also display the backend's high-res annotated image directly
      if (isFrozen && data.annotated_frame && cameraCapturedImg) {
        cameraCapturedImg.src = data.annotated_frame;
      }

      // Update telemetry readout and tally counts
      updateTelemetryUI(data);

      // Store in hidden payload for full analysis action
      if (cameraFramePayload) {
        cameraFramePayload.value = frameBase64;
      }
      if (analyzeCapturedFrameBtn) {
        analyzeCapturedFrameBtn.disabled = false;
      }

      if (!isSilent && cameraStatusPill) {
        cameraStatusPill.textContent = isFrozen ? "Frozen • Inferred" : "Live Stream Active";
        cameraStatusPill.className = isFrozen ? "cal-pill cal-amber" : "cal-pill cal-emerald";
      }
    } catch (err) {
      console.error("Frame detection failed:", err);
      if (!isSilent) {
        alert(`Inference failed: ${err.message}`);
        if (cameraStatusPill) {
          cameraStatusPill.textContent = "Inference Failed";
          cameraStatusPill.className = "cal-pill cal-danger";
        }
      }
    } finally {
      isProcessingFrame = false;
      if (!isSilent && detectFrameBtn) {
        detectFrameBtn.disabled = false;
        detectFrameBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="2" x2="12" y2="22"/>
            <line x1="2" y1="12" x2="22" y2="12"/>
          </svg>
          Detect Components
        `;
      }
    }
  }

  if (detectFrameBtn) {
    detectFrameBtn.addEventListener("click", () => detectCurrentFrame(false));
  }

  // =========================================================================
  // 6. CONTINUOUS LIVE DETECTION MODE
  // =========================================================================

  function startContinuousDetection() {
    isContinuousActive = true;
    if (cameraScanline) cameraScanline.classList.add("scanning");

    async function loop() {
      if (!isContinuousActive) return;

      if (isStreaming && !isFrozen && !isProcessingFrame) {
        await detectCurrentFrame(true);
      }

      if (isContinuousActive) {
        const intervalSec = parseFloat(detectionIntervalSlider ? detectionIntervalSlider.value : 1.0);
        const delayMs = Math.max(400, Math.round(intervalSec * 1000));
        continuousTimer = setTimeout(loop, delayMs);
      }
    }

    loop();
  }

  function stopContinuousDetection() {
    isContinuousActive = false;
    if (continuousTimer) {
      clearTimeout(continuousTimer);
      continuousTimer = null;
    }
    if (cameraScanline) cameraScanline.classList.remove("scanning");
    if (continuousDetectToggle) continuousDetectToggle.checked = false;
  }

  if (continuousDetectToggle) {
    continuousDetectToggle.addEventListener("change", (e) => {
      if (e.target.checked) {
        if (!isStreaming) {
          startCameraStream().then(() => startContinuousDetection());
        } else {
          startContinuousDetection();
        }
      } else {
        stopContinuousDetection();
      }
    });
  }

  if (detectionIntervalSlider && intervalValText) {
    detectionIntervalSlider.addEventListener("input", (e) => {
      intervalValText.textContent = `${parseFloat(e.target.value).toFixed(1)}s`;
    });
  }

  // =========================================================================
  // 7. FULL ANALYSIS SUBMISSION FROM LIVE CAMERA
  // =========================================================================

  if (analyzeCapturedFrameBtn) {
    analyzeCapturedFrameBtn.addEventListener("click", () => {
      let frameBase64 = currentFrozenBase64;
      if (!frameBase64 && isStreaming) {
        frameBase64 = getFrameAsBase64();
      }

      if (!frameBase64) {
        alert("Please start the camera and capture a frame first.");
        return;
      }

      if (cameraFramePayload) {
        cameraFramePayload.value = frameBase64;
      }

      // Stop camera before redirecting to prevent resource leak
      stopCameraStream();

      // Show processing progress modal
      if (processingOverlay) {
        processingOverlay.style.display = "flex";
      }

      // Trigger animated progress step text
      const statusText = document.getElementById("processingStatusText");
      const progBar = document.getElementById("processingProgressBar");
      if (statusText) statusText.textContent = "Ingesting camera frame & validating substrate...";
      if (progBar) progBar.style.width = "35%";

      // Submit form
      if (uploadForm) {
        uploadForm.submit();
      }
    });
  }
});
