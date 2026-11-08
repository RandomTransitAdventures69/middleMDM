// middleMDM - UI helpers
document.addEventListener('DOMContentLoaded', function() {
    // Active nav item
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href') || '';
        if (href === currentPath || (href !== '/dashboard/' && currentPath.startsWith(href + '/')) || (href === '/dashboard/' && currentPath === '/dashboard/')) {
            link.classList.add('active');
        }
    });

    // Confirm disruptive actions
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', function(e) {
            const msg = el.getAttribute('data-confirm') || 'Are you sure? This action may affect a device.';
            if (!confirm(msg)) e.preventDefault();
        });
    });

    // Auto-dismiss success/info alerts (not errors/warnings)
    document.querySelectorAll('.alert-success, .alert-info').forEach(alert => {
        setTimeout(() => { alert.style.opacity = '0'; alert.style.transition = 'opacity 0.3s'; }, 5000);
        setTimeout(() => { alert.remove(); }, 5400);
    });

    // Client-side table search (for pages that opt in)
    const searchInput = document.querySelector('[data-table-search]');
    if (searchInput) {
        const tableId = searchInput.getAttribute('data-table-search');
        const table = document.getElementById(tableId);
        if (table) {
            searchInput.addEventListener('input', function() {
                const q = this.value.toLowerCase();
                table.querySelectorAll('tbody tr[data-search]').forEach(row => {
                    row.style.display = row.getAttribute('data-search').toLowerCase().includes(q) ? '' : 'none';
                });
            });
        }
    }
});
