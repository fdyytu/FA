// Authentication Service Module
// Maksimal 50 baris per file

const API_BASE_URL = '/api/v1';

class AuthService {
    static checkAuth() {
        const token = localStorage.getItem('adminToken');
        if (!token) {
            window.location.href = '/static/admin/login_android.html';
            return false;
        }
        return token;
    }

    static async logout() {
        const token = localStorage.getItem('adminToken');
        
        if (token) {
            try {
                await fetch(`${API_BASE_URL}/auth/logout`, {
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
        window.location.href = '/static/admin/login_android.html';
    }

    static initLogout() {
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', this.logout);
        }
    }
}

// Export untuk digunakan modul lain
window.AuthService = AuthService;
