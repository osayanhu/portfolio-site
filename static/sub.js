document.addEventListener('DOMContentLoaded', function() {
    var modal = document.getElementById('subscribeModal');
    var icon = document.getElementById('subscribeIcon');
    var span = document.querySelector('.close');
    var closeTimeout;

    function showModal() {
        modal.style.display = 'block';

        // Set a timeout to close the modal after 30 seconds if no interaction
        closeTimeout = setTimeout(function() {
            modal.style.display = 'none';
        }, 40000);
    }

    function resetCloseTimeout() {
        clearTimeout(closeTimeout);
        closeTimeout = setTimeout(function() {
            modal.style.display = 'none';
        }, 30000);
    }

    // Show modal after 30 seconds
    setTimeout(showModal, 10000); // 30,000 milliseconds = 30 seconds


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
                window.location.href = response.url;
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Reset the close timeout on any interaction within the modal
    modal.onmousemove = resetCloseTimeout;
    modal.onkeypress = resetCloseTimeout;

    // Show modal when delete key is pressed
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Delete') {
            showModal();
        }
    });

    // Show modal when back button is pressed
    window.addEventListener('popstate', function(event) {
        showModal();
    });
});
