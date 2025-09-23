document.addEventListener('DOMContentLoaded', function () {

    // Set up login show/hide password
    const passwordInput = document.getElementById('password');
    const toggleBtn = document.getElementById('togglePassword');
    const toggleIcon = document.getElementById('togglePasswordIcon');
    if (passwordInput && toggleBtn && toggleIcon) {
        toggleBtn.addEventListener('click', function () {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleIcon.classList.remove('bi-eye');
                toggleIcon.classList.add('bi-eye-slash');
            } else {
                passwordInput.type = 'password';
                toggleIcon.classList.remove('bi-eye-slash');
                toggleIcon.classList.add('bi-eye');
            }
        });
    }

    // Set up datepicker for start_time
    const startTimeInput = document.getElementById('start_time');
    if (startTimeInput) {
        $(startTimeInput).datepicker({
            format: 'yyyy-mm-dd',
            language: 'pl',
            autoclose: true,
            todayHighlight: true
        });
        // Set default value to start_time from URL if present, otherwise today
        const urlParams = new URLSearchParams(window.location.search);
        const startTimeParam = urlParams.get('start_time');
        if (startTimeParam) {
            startTimeInput.value = startTimeParam;
            $(startTimeInput).datepicker('update', startTimeParam);
        } else if (!startTimeInput.value) {
            const today = new Date();
            const yyyy = today.getFullYear();
            const mm = String(today.getMonth() + 1).padStart(2, '0');
            const dd = String(today.getDate()).padStart(2, '0');
            const todayStr = `${yyyy}-${mm}-${dd}`;
            startTimeInput.value = todayStr;
            $(startTimeInput).datepicker('update', todayStr);
        }
    }

    // Set up datepicker for end_time
    const endTimeInput = document.getElementById('end_time');
    if (endTimeInput) {
        $(endTimeInput).datepicker({
            format: 'yyyy-mm-dd',
            language: 'pl',
            autoclose: true,
            clearBtn: true,
            toggleActive: true,
            todayHighlight: true
        });
        // Set default value to end_time from URL if present
        const urlParams = new URLSearchParams(window.location.search);
        const endTimeParam = urlParams.get('end_time');
        if (endTimeParam) {
            endTimeInput.value = endTimeParam;
            $(endTimeInput).datepicker('update', endTimeParam);
        }
    }

    // Remove empty end_time from form before submit
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function (e) {
            const endTimeInput = document.getElementById('end_time');
            if (endTimeInput && !endTimeInput.value) {
                endTimeInput.removeAttribute('name');
            }
        });
    }

    // Attach js-loading-overlay to form submit (only if valid)
    function showLoadingOverlay() {
        if (!window.jsLoadingOverlayActive) {
            window.jsLoadingOverlayActive = true;
            window.JsLoadingOverlay.show({
                'backgroundColor': '#000',
                'opacity': 0.5,
                'spinnerIcon': 'ball-spin-clockwise',
                'spinnerColor': '#fff',
                'spinnerSize': '2x',
                'overlayIDName': 'js-loading-overlay',
                'offsetTop': 0,
                'offsetLeft': 0,
                'overlayZIndex': 9998
            });
        }
    }

    function hideLoadingOverlay() {
        window.JsLoadingOverlay.hide();
        window.jsLoadingOverlayActive = false;
    }

    // Attach to all forms: show overlay only if form is valid
    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (form.checkValidity()) {
                showLoadingOverlay();
            }
        });
    });
    // Attach to all anchor buttons (e.g., .btn-success, .btn-outline-primary, etc.)
    document.querySelectorAll('a.btn').forEach(function (a) {
        a.addEventListener('click', function (e) {
            showLoadingOverlay();
        });
    });

    // Also, hide overlay on pageshow event (for bfcache/back-forward cache)
    window.addEventListener('pageshow', function (event) {
        hideLoadingOverlay();
    });
});

