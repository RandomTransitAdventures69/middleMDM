// middleMDM - Control Room Interface JavaScript
// Subtle interactions, no flashy animations

document.addEventListener('DOMContentLoaded', function() {
    // Add active class to current nav item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath || 
            (currentPath.startsWith(link.getAttribute('href')) && link.getAttribute('href') !== '/dashboard/')) {
            link.classList.add('active');
        }
    });
    
    // Add LED indicators to status
    const statusElements = document.querySelectorAll('.status-badge, .status-text');
    statusElements.forEach(el => {
        if (el.textContent.toLowerCase().includes('online')) {
            el.classList.add('status-online');
            if (!el.querySelector('.status-led')) {
                const indicator = document.createElement('span');
                indicator.className = 'status-indicator status-online';
                indicator.innerHTML = '<span class="status-led"></span><span class="status-text">ONLINE</span>';
                el.replaceWith(indicator);
            }
        } else if (el.textContent.toLowerCase().includes('offline')) {
            el.classList.add('status-offline');
            if (!el.querySelector('.status-led')) {
                const indicator = document.createElement('span');
                indicator.className = 'status-indicator status-offline';
                indicator.innerHTML = '<span class="status-led"></span><span class="status-text">OFFLINE</span>';
                el.replaceWith(indicator);
            }
        }
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0.7';
        }, 4000);
        setTimeout(() => {
            alert.style.display = 'none';
        }, 6000);
    });
    
    // Add confirmation to destructive actions
    const deleteLinks = document.querySelectorAll('a[href*="delete"], button[data-action="delete"]');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('CONFIRM: This action cannot be undone. Proceed?')) {
                e.preventDefault();
            }
        });
    });
});
