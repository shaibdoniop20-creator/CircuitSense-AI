/**
 * CircuitSense AI - Results Dashboard Controller
 * Handles image comparison tabs, interactive zoom & pan, client-side confidence filtering,
 * and component crop inspection.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const tabAnnotatedBtn = document.getElementById("tabAnnotatedBtn");
  const tabOriginalBtn = document.getElementById("tabOriginalBtn");
  const tabSideBySideBtn = document.getElementById("tabSideBySideBtn");

  const stageSingleWrap = document.getElementById("stageSingleWrap");
  const stageDualWrap = document.getElementById("stageDualWrap");
  const mainDisplayImg = document.getElementById("mainDisplayImg");

  const zoomInBtn = document.getElementById("zoomInBtn");
  const zoomOutBtn = document.getElementById("zoomOutBtn");
  const zoomResetBtn = document.getElementById("zoomResetBtn");
  const zoomLevelText = document.getElementById("zoomLevelText");

  const filterSlider = document.getElementById("filterSlider");
  const filterValText = document.getElementById("filterValText");
  const visibleCropsCount = document.getElementById("visibleCropsCount");
  const cropsList = document.getElementById("cropsList");
  const cropItems = document.querySelectorAll(".crop-item");

  let currentScale = 1.0;
  const minScale = 0.5;
  const maxScale = 3.5;
  const scaleStep = 0.25;

  let isPanning = false;
  let startX = 0;
  let startY = 0;
  let translateX = 0;
  let translateY = 0;

  // View Mode Switching
  if (tabAnnotatedBtn && tabOriginalBtn && tabSideBySideBtn) {
    tabAnnotatedBtn.addEventListener("click", () => {
      setActiveTab(tabAnnotatedBtn);
      stageSingleWrap.style.display = "flex";
      stageDualWrap.style.display = "none";
      mainDisplayImg.src = mainDisplayImg.getAttribute("data-annotated");
    });

    tabOriginalBtn.addEventListener("click", () => {
      setActiveTab(tabOriginalBtn);
      stageSingleWrap.style.display = "flex";
      stageDualWrap.style.display = "none";
      mainDisplayImg.src = mainDisplayImg.getAttribute("data-original");
    });

    tabSideBySideBtn.addEventListener("click", () => {
      setActiveTab(tabSideBySideBtn);
      stageSingleWrap.style.display = "none";
      stageDualWrap.style.display = "grid";
    });
  }

  function setActiveTab(activeBtn) {
    [tabAnnotatedBtn, tabOriginalBtn, tabSideBySideBtn].forEach((btn) => {
      btn.classList.remove("active");
    });
    activeBtn.classList.add("active");
  }

  // Zoom Handling
  function updateTransform() {
    mainDisplayImg.style.transform = `translate(${translateX}px, ${translateY}px) scale(${currentScale})`;
    if (zoomLevelText) {
      zoomLevelText.textContent = `${Math.round(currentScale * 100)}%`;
    }
  }

  if (zoomInBtn) {
    zoomInBtn.addEventListener("click", () => {
      if (currentScale < maxScale) {
        currentScale = Math.min(maxScale, currentScale + scaleStep);
        updateTransform();
      }
    });
  }

  if (zoomOutBtn) {
    zoomOutBtn.addEventListener("click", () => {
      if (currentScale > minScale) {
        currentScale = Math.max(minScale, currentScale - scaleStep);
        updateTransform();
      }
    });
  }

  if (zoomResetBtn) {
    zoomResetBtn.addEventListener("click", () => {
      currentScale = 1.0;
      translateX = 0;
      translateY = 0;
      updateTransform();
    });
  }

  // Drag-to-Pan on Stage
  if (stageSingleWrap) {
    stageSingleWrap.addEventListener("mousedown", (e) => {
      if (currentScale > 1.0) {
        isPanning = true;
        startX = e.clientX - translateX;
        startY = e.clientY - translateY;
        stageSingleWrap.style.cursor = "grabbing";
      }
    });

    window.addEventListener("mousemove", (e) => {
      if (!isPanning) return;
      translateX = e.clientX - startX;
      translateY = e.clientY - startY;
      updateTransform();
    });

    window.addEventListener("mouseup", () => {
      isPanning = false;
      if (stageSingleWrap) {
        stageSingleWrap.style.cursor = currentScale > 1.0 ? "grab" : "default";
      }
    });
  }

  // Reusability & Class & Confidence Combined Filtering
  let activeReusabilityFilter = "all";
  let activeClassFilter = "all";
  const filterBtns = document.querySelectorAll(".crop-filter-btn");

  function applyCropFilters() {
    const threshold = filterSlider ? parseFloat(filterSlider.value) : 0.0;
    let visibleCount = 0;

    cropItems.forEach((item) => {
      const conf = parseFloat(item.getAttribute("data-confidence") || "0");
      const reusability = item.getAttribute("data-reusability") || "can_reuse";
      const clsName = item.getAttribute("data-class") || "";

      const passesConf = conf >= threshold;
      const passesReusability = (activeReusabilityFilter === "all" || reusability === activeReusabilityFilter);
      const passesClass = (activeClassFilter === "all" || clsName === activeClassFilter);

      if (passesConf && passesReusability && passesClass) {
        item.style.display = "flex";
        visibleCount++;
      } else {
        item.style.display = "none";
      }
    });

    if (visibleCropsCount) {
      visibleCropsCount.textContent = `${visibleCount} Items`;
    }
  }

  filterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      
      const classFilter = btn.getAttribute("data-class-filter");
      if (classFilter) {
        activeClassFilter = classFilter;
        activeReusabilityFilter = "all";
      } else {
        activeClassFilter = "all";
        activeReusabilityFilter = btn.getAttribute("data-filter") || "all";
      }
      applyCropFilters();
    });
  });

  if (filterSlider && filterValText) {
    filterSlider.addEventListener("input", (e) => {
      const threshold = parseFloat(e.target.value);
      const pct = Math.round(threshold * 100);
      filterValText.textContent = `≥ ${pct}%`;
      applyCropFilters();
    });
  }

  // Click on Crop Item to Highlight
  cropItems.forEach((item) => {
    item.addEventListener("click", () => {
      cropItems.forEach((c) => c.classList.remove("highlighted"));
      item.classList.add("highlighted");

      // Auto scroll crop into view in list
      item.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  });
});
