// Main Dashboard API Service
// Maksimal 50 baris per file

class MainAPIService {
    static async loadDashboardStats() {
        try {
            const response = await APIService.apiRequest('/admin/stats/');
            if (!response || !response.data) {
                throw new Error('Invalid response format');
            }
            return response.data;
        } catch (error) {
            console.error('Error loading stats:', error);
            NotificationService.showToast('Gagal memuat statistik dashboard', 'error');
            
            // Return default empty values
            return {
                total_users: 0,
                total_transactions: 0,
                total_products: 0,
                total_revenue: 0
            };
        }
    }

    static async loadRecentTransactions() {
        try {
            const data = await APIService.apiRequest('/admin/transactions/recent?limit=5');
            return data.data || [];
        } catch (error) {
            console.error('Error loading recent transactions:', error);
            return [];
        }
    }

    static async refreshDashboard() {
        try {
            const [stats, transactions] = await Promise.all([
                this.loadDashboardStats(),
                this.loadRecentTransactions()
            ]);
            
            return { stats, transactions };
        } catch (error) {
            console.error('Error refreshing dashboard:', error);
            throw error;
        }
    }
}

window.MainAPIService = MainAPIService;
