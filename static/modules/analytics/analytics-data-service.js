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
                return MockDataGenerator.generateOverviewStats();
            }
        } catch (error) {
            console.error('Error loading overview stats:', error);
            return MockDataGenerator.generateOverviewStats();
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
                await revenueResponse.json() : { data: MockDataGenerator.generateRevenueData(this.currentDateRange) };
            
            this.data.orders = ordersResponse && ordersResponse.ok ? 
                await ordersResponse.json() : { data: MockDataGenerator.generateOrdersData(this.currentDateRange) };
            
            this.data.userGrowth = userGrowthResponse && userGrowthResponse.ok ? 
                await userGrowthResponse.json() : { data: MockDataGenerator.generateUserGrowthData(this.currentDateRange) };
            
            this.data.paymentMethods = paymentMethodsResponse && paymentMethodsResponse.ok ? 
                await paymentMethodsResponse.json() : { data: MockDataGenerator.generatePaymentMethodsData() };
            
            return this.data;
        } catch (error) {
            console.error('Error loading chart data:', error);
            this.data = {
                revenue: { data: MockDataGenerator.generateRevenueData(this.currentDateRange) },
                orders: { data: MockDataGenerator.generateOrdersData(this.currentDateRange) },
                userGrowth: { data: MockDataGenerator.generateUserGrowthData(this.currentDateRange) },
                paymentMethods: { data: MockDataGenerator.generatePaymentMethodsData() }
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
