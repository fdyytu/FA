// Shared JavaScript functions for all dashboard components
const API_BASE_URL = '/api/v1/admin';

// Authentication functions
function checkAuth() {
    const token = localStorage.getItem('adminToken');
    if (!token) {
        window.location.href = 'login_android.html';
        return false;
    }
    return token;
}

function logout() {
    const token = localStorage.getItem('adminToken');
    
    if (token) {
        fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        }).catch(error => {
            console.error('Logout error:', error);
        });
    }
    
    localStorage.removeItem('adminToken');
    window.location.href = 'login_android.html';
}

// Mobile menu functionality
function initMobileMenu() {
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
        closeBtn.addEventListener('click', closeMobileMenu);
    }
    
    if (overlay) {
        overlay.addEventListener('click', closeMobileMenu);
    }

    function closeMobileMenu() {
        sidebar.classList.add('sidebar-hidden');
        overlay.classList.add('hidden');
    }
}

// Navigation functionality
function initNavigation() {
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

// Logout functionality
function initLogout() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
}

// Loading overlay functions
function showLoading(show = true) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        if (show) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }
}

function hideLoading() {
    showLoading(false);
}

// Toast notification system
function showToast(message, type = 'info', duration = 5000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} p-4 rounded-lg shadow-lg`;
    
    const icon = getToastIcon(type);
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

function getToastIcon(type) {
    switch (type) {
        case 'success': return 'fas fa-check-circle';
        case 'error': return 'fas fa-exclamation-circle';
        case 'warning': return 'fas fa-exclamation-triangle';
        case 'info': return 'fas fa-info-circle';
        default: return 'fas fa-info-circle';
    }
}

// API helper functions
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('adminToken');
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, mergedOptions);
        
        if (response.status === 401) {
            logout();
            return null;
        }
        
        return response;
    } catch (error) {
        console.error('API request error:', error);
        showToast('Terjadi kesalahan koneksi', 'error');
        return null;
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0
    }).format(amount);
}

// Format number
function formatNumber(number) {
    return new Intl.NumberFormat('id-ID').format(number);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('id-ID', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// Format relative time
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Baru saja';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} menit lalu`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} jam lalu`;
    } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days} hari lalu`;
    }
}

// Status badge helper
function getStatusBadge(status) {
    const statusClasses = {
        'active': 'status-active',
        'inactive': 'status-inactive',
        'maintenance': 'status-maintenance',
        'pending': 'status-pending',
        'success': 'status-success',
        'failed': 'status-failed'
    };
    
    const statusTexts = {
        'active': 'Aktif',
        'inactive': 'Tidak Aktif',
        'maintenance': 'Maintenance',
        'pending': 'Pending',
        'success': 'Berhasil',
        'failed': 'Gagal'
    };
    
    const statusIcons = {
        'active': 'fas fa-check',
        'inactive': 'fas fa-times',
        'maintenance': 'fas fa-exclamation-triangle',
        'pending': 'fas fa-clock',
        'success': 'fas fa-check',
        'failed': 'fas fa-times'
    };
    
    const className = statusClasses[status] || 'status-inactive';
    const text = statusTexts[status] || status;
    const icon = statusIcons[status] || 'fas fa-question';
    
    return `
        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${className}">
            <i class="${icon} mr-1"></i>
            ${text}
        </span>
    `;
}

// Modal helper functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^(\+62|62|0)8[1-9][0-9]{6,9}$/;
    return re.test(phone);
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Local storage helpers
function setLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

function getLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error('Error reading from localStorage:', error);
        return defaultValue;
    }
}

// Initialize common functionality
function initSharedComponents() {
    checkAuth();
    initMobileMenu();
    initNavigation();
    initLogout();
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initSharedComponents);

// Export functions for use in other modules
window.DashboardShared = {
    checkAuth,
    logout,
    showLoading,
    hideLoading,
    showToast,
    apiRequest,
    formatCurrency,
    formatNumber,
    formatDate,
    formatRelativeTime,
    getStatusBadge,
    openModal,
    closeModal,
    validateEmail,
    validatePhone,
    debounce,
    setLocalStorage,
    getLocalStorage
};
