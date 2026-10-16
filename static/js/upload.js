/**
 * CircuitSense AI - Upload & Ingestion Controller
 * Stitch "Luminescent Precision" Interface Engine
 * Features: Drag-and-drop, client-side validation, dual-pane telemetry sync, 
 * calibration presets, sample-image autofill, and animated processing overlay.
 */

document.addEventListener("DOMContentLoaded", () => {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const browseBtn = document.getElementById("browseBtn");
  const loadSampleBtn = document.getElementById("loadSampleBtn");

  // Viewport & Preview Elements
  const viewportEmptyState = document.getElementById("viewportEmptyState");
  const previewCard = document.getElementById("previewCard");
  const previewImg = document.getElementById("previewImg");
  const previewFilename = document.getElementById("previewFilename");
  const previewMeta = document.getElementById("previewMeta");
  const removeImgBtn = document.getElementById("removeImgBtn");
  const hudCoords = document.getElementById("hudCoords");
  const hudStatus = document.getElementById("hudStatus");

  // Error & Status Elements
  const uploadError = document.getElementById("uploadError");
  const uploadErrorText = document.getElementById("uploadErrorText");
  const submitBtn = document.getElementById("submitBtn");
  const resetBtn = document.getElementById("resetBtn");
  const uploadForm = document.getElementById("uploadForm");

  // Bottom Shelf Elements
  const shelfStatusDot = document.getElementById("shelfStatusDot");
  const shelfStatusText = document.getElementById("shelfStatusText");
  const shelfSpecimenBadge = document.getElementById("shelfSpecimenBadge");

  // Confidence Slider
  const confidenceSlider = document.getElementById("confidenceSlider");
  const confidenceVal = document.getElementById("confidenceVal");

  // Processing Overlay Elements
  const processingOverlay = document.getElementById("processingOverlay");
  const processingStatusText = document.getElementById("processingStatusText");
  const processingProgressBar = document.getElementById("processingProgressBar");

  const MAX_FILE_SIZE_BYTES = 16 * 1024 * 1024; // 16 MB
  const ALLOWED_EXTS = ["jpg", "jpeg", "png", "webp"];

  // Update confidence slider display
  if (confidenceSlider && confidenceVal) {
    confidenceSlider.addEventListener("input", (e) => {
      const pct = Math.round(parseFloat(e.target.value) * 100);
      confidenceVal.textContent = `${pct}%`;
    });
  }

  // Open file browser on browse button click
  if (browseBtn && fileInput) {
    browseBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      fileInput.click();
    });
  }

  // Clicking dropzone opens browser if not clicking child buttons
  if (dropzone && fileInput) {
    dropzone.addEventListener("click", (e) => {
      if (e.target !== browseBtn && !browseBtn.contains(e.target)) {
        fileInput.click();
      }
    });

    dropzone.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        fileInput.click();
      }
    });
  }

  // Load Sample Specimen Autofill
  if (loadSampleBtn && fileInput) {
    loadSampleBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();
      try {
        loadSampleBtn.disabled = true;
        loadSampleBtn.innerHTML = `
          <svg class="liquid-spinner" style="width: 12px; height: 12px; border-width: 2px; display: inline-block; margin-right: 4px;" viewBox="0 0 24 24"></svg>
          Loading...
        `;
        
        const res = await fetch("/static/images/sample_circuit.jpg");
        if (!res.ok) throw new Error("Sample file could not be retrieved");
        const blob = await res.blob();
        const file = new File([blob], "sample_circuit.jpg", { type: "image/jpeg" });

        // Set into fileInput via DataTransfer
        if (window.DataTransfer) {
          const dt = new DataTransfer();
          dt.items.add(file);
          fileInput.files = dt.files;
        }

        handleFileSelected(file);
      } catch (err) {
        console.error("Error loading sample image:", err);
        showError("Could not load sample specimen. Please select an image from your device.");
      } finally {
        loadSampleBtn.disabled = false;
        loadSampleBtn.innerHTML = `
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          Load Demo Specimen
        `;
      }
    });
  }

  // Calibration Presets handler
  const presetButtons = document.querySelectorAll(".calibration-preset-btn");
  presetButtons.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      presetButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      const category = btn.getAttribute("data-category");
      const condition = btn.getAttribute("data-condition");
      const confidence = btn.getAttribute("data-confidence");

      if (category) {
        const catSelect = document.getElementById("boardCategory");
        if (catSelect) catSelect.value = category;
      }
      if (condition) {
        const condSelect = document.getElementById("boardCondition");
        if (condSelect) condSelect.value = condition;
      }
      if (confidence && confidenceSlider) {
        confidenceSlider.value = confidence;
        if (confidenceVal) {
          confidenceVal.textContent = `${Math.round(parseFloat(confidence) * 100)}%`;
        }
      }
    });
  });

  // Drag & drop event handlers
  if (dropzone) {
    ["dragenter", "dragover"].forEach((eventName) => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add("drag-active");
      });
    });

    ["dragleave", "drop"].forEach((eventName) => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove("drag-active");
      });
    });

    dropzone.addEventListener("drop", (e) => {
      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        if (fileInput) {
          fileInput.files = files;
        }
        handleFileSelected(files[0]);
      }
    });
  }

  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFileSelected(e.target.files[0]);
      }
    });
  }

  // Remove / Replace button
  if (removeImgBtn) {
    removeImgBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      clearSelection();
    });
  }

  // Reset button
  if (resetBtn) {
    resetBtn.addEventListener("click", (e) => {
      e.preventDefault();
      clearSelection();
      const boardCat = document.getElementById("boardCategory");
      const boardCond = document.getElementById("boardCondition");
      if (boardCat) boardCat.value = "unknown";
      if (boardCond) boardCond.value = "intact";
      if (confidenceSlider) {
        confidenceSlider.value = 0.25;
        if (confidenceVal) confidenceVal.textContent = "25%";
      }
      presetButtons.forEach((b) => b.classList.remove("active"));
      if (presetButtons.length > 0) presetButtons[0].classList.add("active");
    });
  }

  function showError(msg) {
    if (uploadError && uploadErrorText) {
      uploadErrorText.textContent = msg;
      uploadError.style.display = "flex";
    }
  }

  function hideError() {
    if (uploadError) {
      uploadError.style.display = "none";
    }
  }

  function clearSelection() {
    if (fileInput) fileInput.value = "";
    if (previewCard) previewCard.style.display = "none";
    if (viewportEmptyState) viewportEmptyState.style.display = "flex";
    if (previewImg) previewImg.src = "";
    if (submitBtn) submitBtn.disabled = true;

    if (hudCoords) hudCoords.textContent = "X: 142.4mm / Y: 88.2mm / Z: 12.0mm";
    if (hudStatus) {
      hudStatus.textContent = "CALIBRATION READY";
      hudStatus.style.color = "#4cd7f6";
    }

    if (shelfStatusDot) {
      shelfStatusDot.classList.remove("status-ready");
    }
    if (shelfStatusText) {
      shelfStatusText.textContent = "Awaiting Circuit Specimen";
    }
    if (shelfSpecimenBadge) {
      shelfSpecimenBadge.style.display = "none";
    }

    hideError();
  }

  function handleFileSelected(file) {
    hideError();
    if (!file) return;

    // Validate extension
    const ext = file.name.split(".").pop().toLowerCase();
    if (!ALLOWED_EXTS.includes(ext)) {
      showError(`Unsupported file format ('.${ext}'). Supported formats: JPG, JPEG, PNG, WEBP.`);
      clearSelection();
      return;
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE_BYTES) {
      const mbSize = (file.size / (1024 * 1024)).toFixed(1);
      showError(`File size (${mbSize} MB) exceeds maximum allowed limit of 16 MB.`);
      clearSelection();
      return;
    }

    if (file.size === 0) {
      showError("The selected file is empty (0 bytes). Please select a valid circuit board photograph.");
      clearSelection();
      return;
    }

    // Read and preview file
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        // Validation check for minimum dimensions
        if (img.width < 32 || img.height < 32) {
          showError(`Image dimensions (${img.width}x${img.height}) are too small for component analysis (min 32x32 px).`);
          clearSelection();
          return;
        }

        // Render preview in Specimen Viewport
        if (previewImg) previewImg.src = e.target.result;
        if (previewFilename) previewFilename.textContent = file.name;
        const sizeKb = (file.size / 1024).toFixed(1);
        if (previewMeta) {
          previewMeta.textContent = `${img.width} × ${img.height} px • ${sizeKb} KB • ${ext.toUpperCase()}`;
        }

        if (hudCoords) {
          hudCoords.textContent = `RES: ${img.width}×${img.height} px • Z: 12.0mm`;
        }
        if (hudStatus) {
          hudStatus.textContent = "SPECIMEN CALIBRATED";
          hudStatus.style.color = "#10b981";
        }

        // Update Viewport display
        if (viewportEmptyState) viewportEmptyState.style.display = "none";
        if (previewCard) previewCard.style.display = "block";
        if (submitBtn) submitBtn.disabled = false;

        // Update Bottom Shelf
        if (shelfStatusDot) {
          shelfStatusDot.classList.add("status-ready");
        }
        if (shelfStatusText) {
          shelfStatusText.textContent = "1 Board Specimen Ready";
        }
        if (shelfSpecimenBadge) {
          shelfSpecimenBadge.style.display = "inline-flex";
        }
      };

      img.onerror = () => {
        showError("The selected file is corrupted or could not be decoded as an image.");
        clearSelection();
      };

      img.src = e.target.result;
    };

    reader.onerror = () => {
      showError("Failed to read the selected file from disk.");
      clearSelection();
    };

    reader.readAsDataURL(file);
  }

  // Handle Form Submission with Animated Progress Overlay
  if (uploadForm) {
    uploadForm.addEventListener("submit", (e) => {
      if (submitBtn && submitBtn.disabled) {
        e.preventDefault();
        return;
      }

      // Prevent duplicate submissions
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
          <svg class="liquid-spinner" style="width: 16px; height: 16px; border-width: 2px; margin-right: 8px; display: inline-block;" viewBox="0 0 24 24"></svg>
          Executing Neural Inference...
        `;
      }

      // Show processing modal overlay
      if (processingOverlay) {
        processingOverlay.style.display = "flex";
      }

      // Progress animation simulation
      const steps = [
        { text: "Ingesting optical payload & validating sub-mm dimensions...", progress: 25, delay: 350 },
        { text: "Executing YOLOv8 neural network inference & anchor tensors...", progress: 55, delay: 900 },
        { text: "Extracting component crops & optical bounding reticles...", progress: 80, delay: 1700 },
        { text: "Computing elemental metallurgy yield & circular flow valuation...", progress: 95, delay: 2400 }
      ];

      steps.forEach((step) => {
        setTimeout(() => {
          if (processingStatusText) processingStatusText.textContent = step.text;
          if (processingProgressBar) processingProgressBar.style.width = `${step.progress}%`;
        }, step.delay);
      });
    });
  }
});
