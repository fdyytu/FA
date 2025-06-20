// Shared Authentication Service
class SharedAuthService {
    constructor() {
        this.API_BASE_URL = '/api/v1';
    }

    // Check authentication
    checkAuth() {
        const token = localStorage.getItem('adminToken');
        if (!token) {
            window.location.href = 'login_android.html';
            return false;
        }
        return token;
    }

    // Logout functionality
    async logout() {
        const token = localStorage.getItem('adminToken');
        
        if (token) {
            try {
                await fetch(`${this.API_BASE_URL}/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
            } catch (error) {
                console.error('Logout error:', error);
            }
        }
        
        localStorage.removeItem('adminToken');
        window.location.href = 'login_android.html';
    }

    // Initialize logout functionality
    initLogout() {
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }
    }
}

// Export for use in other modules
window.SharedAuthService = SharedAuthService;
