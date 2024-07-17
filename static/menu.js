
document.getElementById('menuIcon').addEventListener('click', function() {
    var navItems = document.getElementById('navItems');
    var menuIcon = document.getElementById('menuIcon')
    if (navItems.classList.contains('active')) {
        menuIcon.classList.add('active')
        navItems.classList.remove('active');
    } else {
        navItems.classList.add('active');
        menuIcon.classList.remove('active')
        setTimeout(function() {
            menuIcon.classList.add('active')
            navItems.classList.remove('active');
        }, 5000); // Close menu after 5 seconds
    }
});

document.addEventListener('click', function(event) {
    var navItems = document.getElementById('navItems');
    var menuIcon = document.getElementById('menuIcon');
    if (!navItems.contains(event.target) && !menuIcon.contains(event.target)) {
        navItems.classList.remove('active');
    }
});

// Prevent click inside the nav-items from triggering the outside click event
document.getElementById('navItems').addEventListener('click', function(event) {
    event.stopPropagation();
});
