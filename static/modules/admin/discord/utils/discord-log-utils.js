// Discord Log Utilities
function getLogLevelClass(level) {
    switch (level.toLowerCase()) {
        case 'error':
            return 'bg-red-100 text-red-800';
        case 'warning':
            return 'bg-yellow-100 text-yellow-800';
        case 'info':
            return 'bg-blue-100 text-blue-800';
        case 'debug':
            return 'bg-gray-100 text-gray-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
}

// Export function
window.getLogLevelClass = getLogLevelClass;
