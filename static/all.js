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

$(document).ready(function () {
    var wh = $(window).height(); // Get window height

    // Create waypoints for each skill card
    $('.skill-card').each(function () {
        var skillCard = $(this); // Reference to the current skill card

        // Create a waypoint for the 'enter' event
        new Waypoint({
            element: this,
            handler: function (direction) {
                // Restart animation when entering the viewport
                skillCard.css('animationPlayState', 'running');
            },
            offset: wh - 50 // Trigger when the bottom of the element is within 50px of the viewport
        });

        // Create a waypoint for the 'leave' event
        new Waypoint({
            element: this,
            handler: function (direction) {
                // Pause animation when leaving the viewport
                skillCard.css('animationPlayState', 'paused');
            },
            offset: 'bottom-in-view' // Trigger when the top of the element leaves the viewport
        });
    });
});
