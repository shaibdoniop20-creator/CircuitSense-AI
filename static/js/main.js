/**
 * CircuitSense AI - Global JavaScript
 * Mobile menu toggle, notification toasts, and general UI enhancements.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Mobile Sidebar Toggle
  const mobileBtn = document.getElementById("mobileMenuBtn");
  const sidebar = document.getElementById("appSidebar");

  if (mobileBtn && sidebar) {
    mobileBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener("click", (e) => {
      if (window.innerWidth <= 768 && sidebar.classList.contains("open")) {
        if (!sidebar.contains(e.target) && !mobileBtn.contains(e.target)) {
          sidebar.classList.remove("open");
        }
      }
    });
  }

  // Auto-dismiss alerts after 6 seconds
  const alerts = document.querySelectorAll(".alert-banner");
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.transition = "opacity 0.5s ease";
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 500);
    }, 6000);
  });
});
