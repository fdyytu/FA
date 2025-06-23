// Analytics Data Service
class AnalyticsDataService {
    constructor() {
        this.currentDateRange = 30;
        this.data = {};
    }

    async loadOverviewStats() {
        try {
            const response = await apiClient.get(`/analytics/overview?days=${this.currentDateRange}`);
            
            if (response && response.ok) {
                const data = await response.json();
                return data.data || data;
            } else {
                return {
                    totalRevenue: 0,
                    totalOrders: 0,
                    conversionRate: 0,
                    avgOrderValue: 0
                };
            }
        } catch (error) {
            console.error('Error loading overview stats:', error);
            return {
                totalRevenue: 0,
                totalOrders: 0,
                conversionRate: 0,
                avgOrderValue: 0
            };
        }
    }

    async loadChartData() {
        try {
            const [revenueResponse, ordersResponse, userGrowthResponse, paymentMethodsResponse] = await Promise.all([
                apiClient.get(`/analytics/revenue?days=${this.currentDateRange}`),
                apiClient.get(`/analytics/orders?days=${this.currentDateRange}`),
                apiClient.get(`/analytics/user-growth?days=${this.currentDateRange}`),
                apiClient.get(`/analytics/payment-methods?days=${this.currentDateRange}`)
            ]);
            
            this.data.revenue = revenueResponse && revenueResponse.ok ? 
                await revenueResponse.json() : { data: [] };
            
            this.data.orders = ordersResponse && ordersResponse.ok ? 
                await ordersResponse.json() : { data: [] };
            
            this.data.userGrowth = userGrowthResponse && userGrowthResponse.ok ? 
                await userGrowthResponse.json() : { data: [] };
            
            this.data.paymentMethods = paymentMethodsResponse && paymentMethodsResponse.ok ? 
                await paymentMethodsResponse.json() : { data: [] };
            
            return this.data;
        } catch (error) {
            console.error('Error loading chart data:', error);
            this.data = {
                revenue: { data: [] },
                orders: { data: [] },
                userGrowth: { data: [] },
                paymentMethods: { data: [] }
            };
            return this.data;
        }
    }

    setDateRange(days) {
        this.currentDateRange = days;
    }

    getDateRange() {
        return this.currentDateRange;
    }

    getData() {
        return this.data;
    }
}

// Global analytics data service instance
const analyticsDataService = new AnalyticsDataService();
