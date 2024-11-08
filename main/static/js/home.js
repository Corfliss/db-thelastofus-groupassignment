// home.js

// Toggle dropdown visibility when button is clicked
document.getElementById("menu-button").addEventListener("click", function() {
    const dropdown = document.getElementById("dropdown");
    const expanded = this.getAttribute("aria-expanded") === "true";
    this.setAttribute("aria-expanded", !expanded);
    dropdown.classList.toggle("hidden");
  });
  
  // Close dropdown if clicked outside
  document.addEventListener("click", function(event) {
    const button = document.getElementById("menu-button");
    const dropdown = document.getElementById("dropdown");
    if (!button.contains(event.target) && !dropdown.contains(event.target)) {
      button.setAttribute("aria-expanded", "false");
      dropdown.classList.add("hidden");
    }
  });