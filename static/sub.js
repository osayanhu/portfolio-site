document.addEventListener('DOMContentLoaded', function() {
    var modal = document.getElementById('subscribeModal');
    var span = document.querySelector('.close');
    var closeTimeout;

    // Function to show the modal
    function showModal() {
        modal.style.display = 'block';
        closeTimeout = setTimeout(function() {
            modal.style.display = 'none';
        }, 60000); // Close after 60 seconds
    }

    // Function to reset the close timeout
    function resetCloseTimeout() {
        clearTimeout(closeTimeout);
        closeTimeout = setTimeout(function() {
            modal.style.display = 'none';
        }, 30000); // Reset to close after 30 seconds
    }

    // Show modal after 30 seconds
    if (getCookie('subscribed') != "") {
        setTimeout(showModal, 10000); // Show after 10 seconds
    }

    span.onclick = function() {
        modal.style.display = 'none';
        clearTimeout(closeTimeout);
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
            clearTimeout(closeTimeout);
        }
    }

    var form = document.getElementById('subscribeForm');
    form.onsubmit = function(event) {
        event.preventDefault();

        var name = document.getElementById('name').value;
        var email = document.getElementById('email').value;

        fetch('/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'name': name,
                'email': email
            })
        })
        .then(response => {
            if (response.redirected) {
                // Set the subscribed cookie
                setCookie('subscribed', 'true', 365);
                window.location.href = response.url;
            }
        })
        .catch(error => console.error('Error:', error));
    }

    modal.onmousemove = resetCloseTimeout;
    modal.onkeypress = resetCloseTimeout;

    document.addEventListener('keydown', function(event) {
        if (event.key === 'Delete') {
            showModal();
        }
    });

    window.addEventListener('popstate', function(event) {
        showModal();
    });

    // Function to set a cookie
    function setCookie(name, value, days) {
        const d = new Date();
        d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
        const expires = "expires=" + d.toUTCString();
        document.cookie = name + "=" + value + ";" + expires + ";path=/";
    }

    // Function to get a cookie by name
    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) == ' ') {
                c = c.substring(1, c.length);
            }
            if (c.indexOf(nameEQ) == 0) {
                return c.substring(nameEQ.length, c.length);
            }
        }
        return null;
    }
});
