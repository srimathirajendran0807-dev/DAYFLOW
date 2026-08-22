// DAYFLOW - small UI helpers (no framework dependency)

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after a few seconds
    document.querySelectorAll('.alert').forEach(function (alertEl) {
        setTimeout(function () {
            var alert = bootstrap.Alert.getOrCreateInstance(alertEl);
            if (alert) alert.close();
        }, 5000);
    });

    // Confirm before checking out (irreversible for the day)
    document.querySelectorAll('form[action*="check-out"]').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!confirm('Are you sure you want to check out now?')) {
                e.preventDefault();
            }
        });
    });

    // Client-side guard: leave "to date" cannot be before "from date"
    var fromDate = document.querySelector('input[name="from_date"]');
    var toDate = document.querySelector('input[name="to_date"]');
    if (fromDate && toDate) {
        fromDate.addEventListener('change', function () {
            toDate.min = fromDate.value;
        });
    }
});
