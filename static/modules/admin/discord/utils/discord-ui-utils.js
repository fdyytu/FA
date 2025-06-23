// Discord UI Utilities
// Maksimal 50 baris per modul

class DiscordUIUtils {
    // Get status badge HTML
    static getStatusBadge(status) {
        const isActive = status === 'active' || status === 'online';
        const colorClass = isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
        const dotClass = isActive ? 'bg-green-400' : 'bg-red-400';
        const text = isActive ? 'Active' : 'Inactive';
        
        return `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${colorClass}">
            <span class="w-1.5 h-1.5 ${dotClass} rounded-full mr-1"></span>
            ${text}
        </span>`;
    }

    // Get log type CSS class
    static getLogTypeClass(type) {
        const lowerType = (type || 'info').toLowerCase();
        switch (lowerType) {
            case 'info': return 'bg-blue-100 text-blue-800';
            case 'warning': return 'bg-yellow-100 text-yellow-800';
            case 'error': return 'bg-red-100 text-red-800';
            case 'success': return 'bg-green-100 text-green-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    }

    // Show loading state
    static showLoading(show = true) {
        if (typeof showLoading === 'function') {
            showLoading(show);
        }
    }

    // Show toast message
    static showToast(message, type = 'info', duration = 3000) {
        if (typeof showToast === 'function') {
            showToast(message, type, duration);
        }
    }
}

// Export for global use
window.getStatusBadge = DiscordUIUtils.getStatusBadge;
window.getLogTypeClass = DiscordUIUtils.getLogTypeClass;
