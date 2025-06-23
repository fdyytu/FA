// Dashboard Notification Utilities
class DashboardNotifications {
    showError(message) {
        // Create or update error notification
        let errorDiv = document.getElementById('dashboard-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'dashboard-error';
            errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
            document.body.appendChild(errorDiv);
        }
        
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';

        // Auto hide after 5 seconds
        setTimeout(() => {
            if (errorDiv) {
                errorDiv.style.display = 'none';
            }
        }, 5000);
    }

    showSuccess(message) {
        // Create or update success notification
        let successDiv = document.getElementById('dashboard-success');
        if (!successDiv) {
            successDiv = document.createElement('div');
            successDiv.id = 'dashboard-success';
            successDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
            document.body.appendChild(successDiv);
        }
        
        successDiv.textContent = message;
        successDiv.style.display = 'block';

        // Auto hide after 3 seconds
        setTimeout(() => {
            if (successDiv) {
                successDiv.style.display = 'none';
            }
        }, 3000);
    }

    showWarning(message) {
        // Create or update warning notification
        let warningDiv = document.getElementById('dashboard-warning');
        if (!warningDiv) {
            warningDiv = document.createElement('div');
            warningDiv.id = 'dashboard-warning';
            warningDiv.className = 'fixed top-4 right-4 bg-yellow-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
            document.body.appendChild(warningDiv);
        }
        
        warningDiv.textContent = message;
        warningDiv.style.display = 'block';

        // Auto hide after 4 seconds
        setTimeout(() => {
            if (warningDiv) {
                warningDiv.style.display = 'none';
            }
        }, 4000);
    }
}

// Export untuk digunakan di modul lain
window.DashboardNotifications = DashboardNotifications;
