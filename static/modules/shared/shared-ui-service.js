// Shared UI Utilities Service
class SharedUIService {
    constructor() {
        this.API_BASE_URL = '/api/v1';
    }

    // Mobile menu functionality
    initMobileMenu() {
        const openBtn = document.getElementById('openSidebar');
        const closeBtn = document.getElementById('closeSidebar');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobileMenuOverlay');

        if (openBtn) {
            openBtn.addEventListener('click', () => {
                sidebar.classList.remove('sidebar-hidden');
                overlay.classList.remove('hidden');
            });
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', this.closeMobileMenu);
        }
        
        if (overlay) {
            overlay.addEventListener('click', this.closeMobileMenu);
        }
    }

    closeMobileMenu() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobileMenuOverlay');
        sidebar.classList.add('sidebar-hidden');
        overlay.classList.add('hidden');
    }

    // Navigation functionality
    initNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        const currentPage = window.location.pathname.split('/').pop();
        
        navItems.forEach(item => {
            // Set active state based on current page
            const href = item.getAttribute('href');
            if (href && href === currentPage) {
                item.classList.add('active');
            }
            
            item.addEventListener('click', (e) => {
                // Don't prevent default for actual navigation
                if (item.tagName === 'A' && item.getAttribute('href')) {
                    return;
                }
                
                e.preventDefault();
                
                // Remove active class from all items
                navItems.forEach(nav => nav.classList.remove('active'));
                
                // Add active class to clicked item
                item.classList.add('active');
            });
        });
    }

    // Loading overlay functions
    showLoading(show = true) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            if (show) {
                overlay.classList.remove('hidden');
            } else {
                overlay.classList.add('hidden');
            }
        }
    }

    hideLoading() {
        this.showLoading(false);
    }

    // Toast notification system
    showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} p-4 rounded-lg shadow-lg`;
        
        const icon = this.getToastIcon(type);
        toast.innerHTML = `
            <div class="flex items-center">
                <i class="${icon} mr-3"></i>
                <span>${message}</span>
                <button class="ml-auto text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, duration);
    }

    getToastIcon(type) {
        switch (type) {
            case 'success': return 'fas fa-check-circle';
            case 'error': return 'fas fa-exclamation-circle';
            case 'warning': return 'fas fa-exclamation-triangle';
            case 'info': return 'fas fa-info-circle';
            default: return 'fas fa-info-circle';
        }
    }

    // Modal helper functions
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    }
}

// Export for use in other modules
window.SharedUIService = SharedUIService;
