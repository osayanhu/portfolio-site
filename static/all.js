document.addEventListener("scroll", function () {
    const sections = document.querySelectorAll("section");
    const dots = document.querySelectorAll(".dot");

    let currentIndex = sections.length;

    sections.forEach((section, index) => {
        const sectionTop = section.getBoundingClientRect().top;
        if (sectionTop <= window.innerHeight / 2) {
            currentIndex = index;
        }
    });

    dots.forEach((dot, index) => {
        if (index === currentIndex) {
            dot.classList.add("active");
        } else {
            dot.classList.remove("active");
        }
    });
});

// Smooth scroll to section on dot click
const dots = document.querySelectorAll(".dot");

dots.forEach(dot => {
    dot.addEventListener("click", function () {
        const target = document.querySelector(`.${dot.getAttribute('data-target')}`);
        target.scrollIntoView({ behavior: "smooth" });
    });
});


