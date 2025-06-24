// Dashboard Authentication Utilities
class DashboardAuth {
    constructor() {
        this.token = localStorage.getItem('adminToken');
    }

    checkAuthentication() {
        if (!this.token) {
            window.location.href = '../login_android.html';
            return false;
        }
        return true;
    }

    logout() {
        localStorage.removeItem('adminToken');
        window.location.href = '../login_android.html';
    }

    setupLogoutButton() {
        // Add logout button if it doesn't exist
        const sidebar = document.querySelector('.sidebar nav');
        if (sidebar && !document.getElementById('logoutBtn')) {
            const logoutLink = document.createElement('a');
            logoutLink.href = '#';
            logoutLink.id = 'logoutBtn';
            logoutLink.className = 'nav-item';
            logoutLink.innerHTML = '<i class="fas fa-sign-out-alt mr-3"></i>Logout';
            logoutLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.logout();
            });
            sidebar.appendChild(logoutLink);
        }
    }

    getToken() {
        return this.token;
    }

    updateToken(newToken) {
        this.token = newToken;
        localStorage.setItem('adminToken', newToken);
    }
}

// Export untuk digunakan di modul lain
window.DashboardAuth = DashboardAuth;
