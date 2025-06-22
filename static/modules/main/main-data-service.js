// Main Dashboard Data Service
class MainDashboardDataService {
    constructor() {
        this.data = {
            stats: {},
            recentTransactions: [],
            chartData: {}
        };
    }

    async loadDashboardStats() {
        try {
            const response = await apiClient.get('/admin/stats/');
            
            if (response && response.ok) {
                const data = await response.json();
                this.data.stats = data.data || data;
                return this.data.stats;
            } else {
                throw new Error(`API Error: ${response.status} - ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
            throw new Error(`Failed to load dashboard statistics: ${error.message}`);
        }
    }

    generateMockStats() {
        return {
            total_revenue: 125000000,
            total_orders: 1847,
            total_users: 1250,
            total_products: 156
        };
    }

    async loadRecentTransactions() {
        try {
            const response = await apiClient.get('/admin/transactions/recent');
            
            if (response && response.ok) {
                const data = await response.json();
                this.data.recentTransactions = data.data || [];
                return this.data.recentTransactions;
            } else {
                throw new Error(`API Error: ${response.status} - ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error loading recent transactions:', error);
            throw new Error(`Failed to load recent transactions: ${error.message}`);
        }
    }

    generateMockTransactions() {
        return [
            { id: 1, user: 'John Doe', amount: 150000, status: 'completed', date: '2024-01-01' },
            { id: 2, user: 'Jane Smith', amount: 75000, status: 'pending', date: '2024-01-02' }
        ];
    }

    async loadChartData() {
        try {
            const response = await apiClient.get('/admin/dashboard/charts/data');
            
            if (response && response.ok) {
                const data = await response.json();
                this.data.chartData = data.data || data;
                return this.data.chartData;
            } else {
                throw new Error(`API Error: ${response.status} - ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error loading chart data:', error);
            throw new Error(`Failed to load chart data: ${error.message}`);
        }
    }

    generateMockChartData() {
        return {
            revenue: [10, 20, 30, 40, 50, 60, 70],
            orders: [5, 10, 15, 20, 25, 30, 35]
        };
    }
}

const mainDashboardDataService = new MainDashboardDataService();
