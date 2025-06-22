// Formatting utilities
class Formatters {
    static formatCurrency(amount, currency = 'IDR') {
        if (typeof amount !== 'number') {
            amount = parseFloat(amount) || 0;
        }
        
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }

    static formatNumber(number) {
        if (typeof number !== 'number') {
            number = parseFloat(number) || 0;
        }
        
        return new Intl.NumberFormat('id-ID').format(number);
    }

    static formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        
        return new Intl.DateTimeFormat('id-ID', {
            ...defaultOptions,
            ...options
        }).format(new Date(date));
    }

    static formatChartDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('id-ID', {
            month: 'short',
            day: 'numeric'
        });
    }

    static formatPercentage(value, decimals = 1) {
        return `${parseFloat(value || 0).toFixed(decimals)}%`;
    }

    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    static formatRelativeTime(dateString) {
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
}

// Legacy compatibility functions
function formatCurrency(amount, currency = 'IDR') {
    return Formatters.formatCurrency(amount, currency);
}

function formatNumber(number) {
    return Formatters.formatNumber(number);
}

function formatDate(date, options = {}) {
    return Formatters.formatDate(date, options);
}

function formatChartDate(dateString) {
    return Formatters.formatChartDate(dateString);
}
