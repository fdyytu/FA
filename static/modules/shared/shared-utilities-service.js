// Shared Utilities Service
class SharedUtilitiesService {
    // Format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(amount);
    }

    // Format number
    formatNumber(number) {
        return new Intl.NumberFormat('id-ID').format(number);
    }

    // Format date
    formatDate(dateString) {
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
    formatRelativeTime(dateString) {
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
    getStatusBadge(status) {
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

    // Form validation helpers
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    validatePhone(phone) {
        const re = /^(\+62|62|0)8[1-9][0-9]{6,9}$/;
        return re.test(phone);
    }

    // Debounce function for search
    debounce(func, wait) {
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
    setLocalStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    }

    getLocalStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return defaultValue;
        }
    }
}

// Export for use in other modules
window.SharedUtilitiesService = SharedUtilitiesService;
