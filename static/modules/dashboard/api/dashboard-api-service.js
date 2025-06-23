// Dashboard API Service
class DashboardApiService {
    constructor() {
        this.token = localStorage.getItem('adminToken');
        this.apiBaseUrl = '/api/v1/admin';
    }

    async getOverviewStats() {
        const response = await fetch(`${this.apiBaseUrl}/dashboard/stats/overview`, {
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    async getRecentTransactions() {
        const response = await fetch(`${this.apiBaseUrl}/dashboard/`, {
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }
}

// Export untuk digunakan di modul lain
window.DashboardApiService = DashboardApiService;
