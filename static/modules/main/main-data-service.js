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
            const response = await apiClient.get('/admin/stats');
            
            if (response && response.ok) {
                const data = await response.json();
                this.data.stats = data.data || data;
            } else {
                this.data.stats = this.generateMockStats();
            }
            return this.data.stats;
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
            this.data.stats = this.generateMockStats();
            return this.data.stats;
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
            } else {
                this.data.recentTransactions = this.generateMockTransactions();
            }
            return this.data.recentTransactions;
        } catch (error) {
            console.error('Error loading recent transactions:', error);
            this.data.recentTransactions = this.generateMockTransactions();
            return this.data.recentTransactions;
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
            const response = await apiClient.get('/admin/charts/data');
            
            if (response && response.ok) {
                const data = await response.json();
                this.data.chartData = data.data || data;
            } else {
                this.data.chartData = this.generateMockChartData();
            }
            return this.data.chartData;
        } catch (error) {
            console.error('Error loading chart data:', error);
            this.data.chartData = this.generateMockChartData();
            return this.data.chartData;
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
