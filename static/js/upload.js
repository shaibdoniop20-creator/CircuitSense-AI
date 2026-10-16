/**
 * CircuitSense AI - Upload & Ingestion Controller
 * Drag-and-drop, client-side validation, image preview, and animated processing overlay.
 */

document.addEventListener("DOMContentLoaded", () => {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const browseBtn = document.getElementById("browseBtn");
  const previewCard = document.getElementById("previewCard");
  const previewImg = document.getElementById("previewImg");
  const previewFilename = document.getElementById("previewFilename");
  const previewMeta = document.getElementById("previewMeta");
  const removeImgBtn = document.getElementById("removeImgBtn");
  const uploadError = document.getElementById("uploadError");
  const uploadErrorText = document.getElementById("uploadErrorText");
  const submitBtn = document.getElementById("submitBtn");
  const resetBtn = document.getElementById("resetBtn");
  const uploadForm = document.getElementById("uploadForm");

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
    browseBtn.addEventListener("click", () => fileInput.click());
  }

  // Clicking dropzone opens browser if empty
  if (dropzone && fileInput) {
    dropzone.addEventListener("click", (e) => {
      if (e.target !== browseBtn) {
        fileInput.click();
      }
    });
  }

  // Drag & drop handlers
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
      handleFileSelected(files[0]);
    }
  });

  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFileSelected(e.target.files[0]);
      }
    });
  }

  // Remove button
  if (removeImgBtn) {
    removeImgBtn.addEventListener("click", () => {
      clearSelection();
    });
  }

  // Reset button
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      clearSelection();
      document.getElementById("boardCategory").value = "unknown";
      document.getElementById("boardCondition").value = "intact";
      if (confidenceSlider) {
        confidenceSlider.value = 0.25;
        confidenceVal.textContent = "25%";
      }
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
    fileInput.value = "";
    previewCard.style.display = "none";
    dropzone.style.display = "flex";
    previewImg.src = "";
    submitBtn.disabled = true;
    hideError();
  }

  function handleFileSelected(file) {
    hideError();

    if (!file) return;

    // Validate extension
    const ext = file.name.split(".").pop().toLowerCase();
    if (!ALLOWED_EXTS.includes(ext)) {
      showError(`Unsupported file format ('.${ext}'). Please select a JPG, JPEG, PNG, or WEBP image.`);
      clearSelection();
      return;
    }

    // Validate size
    if (file.size > MAX_FILE_SIZE_BYTES) {
      const mbSize = (file.size / (1024 * 1024)).toFixed(1);
      showError(`File size (${mbSize} MB) exceeds the maximum allowed limit of 16 MB.`);
      clearSelection();
      return;
    }

    if (file.size === 0) {
      showError("The selected file is empty (0 bytes). Please select a valid circuit board photograph.");
      clearSelection();
      return;
    }

    // Read and preview
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        // Validation check for minimum dimensions
        if (img.width < 32 || img.height < 32) {
          showError(`Image dimensions (${img.width}x${img.height}) are too small for component analysis.`);
          clearSelection();
          return;
        }

        // Display preview
        previewImg.src = e.target.result;
        previewFilename.textContent = file.name;
        const sizeKb = (file.size / 1024).toFixed(1);
        previewMeta.textContent = `${img.width} × ${img.height} px • ${sizeKb} KB • ${ext.toUpperCase()}`;

        dropzone.style.display = "none";
        previewCard.style.display = "block";
        submitBtn.disabled = false;
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
      if (submitBtn.disabled) {
        e.preventDefault();
        return;
      }

      // Prevent duplicate submissions
      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <svg class="liquid-spinner" style="width: 18px; height: 18px; border-width: 2px; margin-right: 6px;" viewBox="0 0 24 24"></svg>
        Processing...
      `;

      // Show processing overlay
      if (processingOverlay) {
        processingOverlay.style.display = "flex";
      }

      // Progress animation simulation
      const steps = [
        { text: "Ingesting image & validating dimensions...", progress: 25, delay: 400 },
        { text: "Executing YOLOv8 neural network inference...", progress: 55, delay: 1000 },
        { text: "Extracting component crops & bounding boxes...", progress: 80, delay: 1800 },
        { text: "Computing wholesale valuation & material metrics...", progress: 95, delay: 2600 }
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
