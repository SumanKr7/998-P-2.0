document.querySelectorAll(".has-submenu > a").forEach(item => {
  item.addEventListener("click", function(e) {
    if (window.innerWidth < 768) { // Only on mobile
      e.preventDefault();
      let submenu = this.nextElementSibling;
      submenu.style.display = submenu.style.display === "block" ? "none" : "block";
    }
  });
});
