// UI Utilities Module
// Maksimal 50 baris per file

class UIUtils {
    static getStatusBadge(status) {
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

    static openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
        }
    }

    static closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    }
}

window.UIUtils = UIUtils;
