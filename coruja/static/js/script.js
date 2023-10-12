const closeButtons = document.querySelectorAll('[data-dismiss="alert"]');
closeButtons.forEach(function(button) {
    button.addEventListener('click', function() {
        button.parentElement.style.display = 'none';
    });
});
