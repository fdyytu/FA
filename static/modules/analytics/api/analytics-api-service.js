// Analytics API Service
// Menangani semua komunikasi API untuk analytics

class AnalyticsApiService {
    constructor() {
        this.baseUrl = '/dashboard/stats';
    }

    // Load overview statistics
    async loadOverviewStats() {
        try {
            const response = await apiRequest(`${this.baseUrl}/overview`);
            
            if (response && response.ok) {
                const data = await response.json();
                return data.data || data;
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading overview stats:', error);
            return {
                total_revenue: 0,
                revenue_change: 0,
                total_orders: 0,
                orders_change: 0,
                conversion_rate: 0,
                conversion_change: 0,
                avg_order_value: 0,
                aov_change: 0
            };
        }
    }

    // Load chart data
    async loadChartData() {
        try {
            const [revenueResponse, transactionResponse] = await Promise.all([
                apiRequest(`${this.baseUrl}/revenue?period=daily`),
                apiRequest(`${this.baseUrl}/transactions`)
            ]);
            
            return {
                revenue: revenueResponse && revenueResponse.ok ? 
                    await revenueResponse.json() : { data: [] },
                transactions: transactionResponse && transactionResponse.ok ? 
                    await transactionResponse.json() : { data: [] },
                userGrowth: { data: [] },
                paymentMethods: { data: [] }
            };
        } catch (error) {
            console.error('Error loading chart data:', error);
            return {
                revenue: { data: [] },
                transactions: { data: [] },
                userGrowth: { data: [] },
                paymentMethods: { data: [] }
            };
        }
    }

    // Load top products
    async loadTopProducts() {
        try {
            const response = await apiRequest(`${this.baseUrl}/products`);
            
            if (response && response.ok) {
                const data = await response.json();
                return data.data?.top_products || [];
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading top products:', error);
            return [];
        }
    }

    // Load recent activity
    async loadRecentActivity() {
        try {
            const response = await apiRequest('/dashboard/recent-activities?limit=10');
            
            if (response && response.ok) {
                const data = await response.json();
                return data.data?.activities || [];
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading recent activity:', error);
            return [];
        }
    }

    // Load performance metrics
    async loadPerformanceMetrics() {
        try {
            const response = await apiRequest(`${this.baseUrl}/performance`);
            
            if (response && response.ok) {
                const data = await response.json();
                return data.data || {};
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading performance metrics:', error);
            return {};
        }
    }

    // Load geographic data
    async loadGeographicData() {
        try {
            const response = await apiRequest(`${this.baseUrl}/geographic`);
            
            if (response && response.ok) {
                const data = await response.json();
                return data.data?.countries || [];
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading geographic data:', error);
            return [];
        }
    }
}

// Export instance
window.analyticsApiService = new AnalyticsApiService();
