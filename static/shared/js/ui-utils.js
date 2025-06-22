// UI Utilities
class UIUtils {
    static showLoading(show = true) {
        const loader = document.getElementById('loadingOverlay') || 
                      document.getElementById('loadingSpinner') || 
                      document.querySelector('.loading-spinner');
        
        if (loader) {
            if (show) {
                loader.classList.remove('hidden');
            } else {
                loader.classList.add('hidden');
            }
        }
    }

    static showToast(message, type = 'info', duration = 3000) {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.toast-notification');
        existingToasts.forEach(toast => toast.remove());

        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas ${this.getToastIcon(type)}"></i>
                <span>${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, duration);
    }

    static getToastIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    static checkAuth() {
        const token = localStorage.getItem('adminToken');
        if (!token) {
            window.location.href = '../login_android.html';
            return null;
        }
        return token;
    }

    static updateChangeIndicator(element, change) {
        if (!element) return;
        
        const isPositive = change >= 0;
        const icon = isPositive ? 'fa-arrow-up' : 'fa-arrow-down';
        const sign = isPositive ? '+' : '';
        const colorClass = isPositive ? 'text-green-600' : 'text-red-600';
        
        element.innerHTML = `
            <span class="${colorClass}">
                <i class="fas ${icon} mr-1"></i>
                ${sign}${parseFloat(change).toFixed(1)}%
            </span>
        `;
    }
}

// Legacy compatibility functions
function showLoading(show = true) {
    UIUtils.showLoading(show);
}

function showToast(message, type = 'info', duration = 3000) {
    UIUtils.showToast(message, type, duration);
}

function checkAuth() {
    return UIUtils.checkAuth();
}

function updateChangeIndicator(element, change) {
    UIUtils.updateChangeIndicator(element, change);
}
