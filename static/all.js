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

document.getElementById('timeline').addEventListener('click', function (event) {
    event.preventDefault(); // Prevent default anchor click behavior
    const timeline = document.getElementById('timeline-div');
    const cards = timeline.querySelectorAll('.card');

    // Add the animation class to each card
    cards.forEach(card => card.classList.add('animate-in'));

    // Scroll to the timeline after a short delay to allow the animation to be visible
    setTimeout(() => {
        timeline.scrollIntoView({ behavior: 'smooth' });
    }, 50); // Adjust the delay as needed
});
