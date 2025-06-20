// Android Dashboard Data Service
class AndroidDataService {
    constructor() {
        this.API_BASE_URL = '/api/v1/admin';
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

    // Load dashboard statistics
    async loadDashboardStats() {
        const token = localStorage.getItem('adminToken');
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/dashboard/stats`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                return data;
            } else {
                // Use mock data if API fails
                return this.getMockStats();
            }
        } catch (error) {
            console.error('Error loading stats:', error);
            return this.getMockStats();
        }
    }

    // Get mock statistics data
    getMockStats() {
        return {
            total_users: 1250,
            total_transactions: 3420,
            total_products: 156,
            total_revenue: 45000000
        };
    }

    // Get mock transactions data
    getMockTransactions() {
        return [
            { id: 1, user: 'John Doe', product: 'Pulsa Telkomsel 50K', amount: 52000, status: 'success', time: '2 menit lalu' },
            { id: 2, user: 'Jane Smith', product: 'Token PLN 100K', amount: 102500, status: 'pending', time: '5 menit lalu' },
            { id: 3, user: 'Bob Johnson', product: 'Paket Data XL 5GB', amount: 65000, status: 'success', time: '10 menit lalu' },
            { id: 4, user: 'Alice Brown', product: 'Pulsa Indosat 25K', amount: 26500, status: 'failed', time: '15 menit lalu' },
            { id: 5, user: 'Charlie Wilson', product: 'BPJS Kesehatan', amount: 150000, status: 'success', time: '20 menit lalu' }
        ];
    }

    // Logout functionality
    async performLogout() {
        const token = localStorage.getItem('adminToken');
        
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
        
        localStorage.removeItem('adminToken');
        window.location.href = 'login_android.html';
    }
}

// Export for use in other modules
window.AndroidDataService = AndroidDataService;
