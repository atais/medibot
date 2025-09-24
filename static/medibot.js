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

            // Remove hour range inputs if they have default values (0-24)
            const startHourInput = document.getElementById('start_hour');
            const endHourInput = document.getElementById('end_hour');
            if (startHourInput && endHourInput &&
                startHourInput.value == '0' && endHourInput.value == '24') {
                startHourInput.removeAttribute('name');
                endHourInput.removeAttribute('name');
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

    const slider = document.getElementById('hour-range-slider');
    if (slider) {
        var inputFrom = document.getElementById('start_hour');
        var inputTo = document.getElementById('end_hour');

        // Get initial values from the hidden inputs (set by backend)
        var initialFrom = parseInt(inputFrom.value) || 0;
        var initialTo = parseInt(inputTo.value) || 24;

        noUiSlider.create(slider, {
            start: [initialFrom, initialTo],
            connect: true,
            step: 1,
            range: {
                'min': 0,
                'max': 24
            },
            tooltips: [true, true],
            format: {
                to: function (value) {
                    var h = Math.floor(value);
                    return (h < 10 ? '0' : '') + h + ':00';
                },
                from: function (value) {
                    return Number(value.replace(':00', ''));
                }
            }
        });

        slider.noUiSlider.on('update', function (values, handle) {
            inputFrom.value = parseInt(values[0]);
            inputTo.value = parseInt(values[1]);
        });
    }

});

