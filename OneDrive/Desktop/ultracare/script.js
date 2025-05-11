// Simple scroll reveal animation
document.addEventListener("DOMContentLoaded", () => {
    const reveals = document.querySelectorAll(".section");
  
    window.addEventListener("scroll", () => {
      const windowHeight = window.innerHeight;
      reveals.forEach((section) => {
        const sectionTop = section.getBoundingClientRect().top;
        if (sectionTop < windowHeight - 100) {
          section.classList.add("visible");
        }
      });
    });
  });
  