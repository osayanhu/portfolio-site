document.addEventListener('DOMContentLoaded', function() {
    // Get the modal
    var modal = document.getElementById('subscribeModal');

    // Get the icon that opens the modal
    var icon = document.getElementById('subscribeIcon');

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName('close')[0];

    // When the user clicks the icon, open the modal
    icon.onclick = function() {
        modal.style.display = 'block';
    }

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = 'none';
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }

    // Handle form submission
    var form = document.getElementById('subscribeForm');
    form.onsubmit = function(event) {
        event.preventDefault();
        // Add your form submission code here, e.g., an AJAX request to subscribe the user
        alert('Subscribed!');
        modal.style.display = 'none';
    }
});
