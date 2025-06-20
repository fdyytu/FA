// Mock Data Generators
class MockDataGenerator {
    static generateOverviewStats() {
        return {
            total_revenue: Math.floor(Math.random() * 200000000) + 100000000,
            revenue_change: (Math.random() * 30) - 10,
            total_orders: Math.floor(Math.random() * 3000) + 1000,
            orders_change: (Math.random() * 20) - 5,
            conversion_rate: Math.random() * 5 + 1,
            conversion_change: (Math.random() * 4) - 2,
            avg_order_value: Math.floor(Math.random() * 100000) + 50000,
            aov_change: (Math.random() * 15) - 5
        };
    }

    static generateRevenueData(days = 30) {
        const data = [];
        const now = new Date();
        
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date(now);
            date.setDate(date.getDate() - i);
            
            data.push({
                date: date.toISOString().split('T')[0],
                revenue: Math.floor(Math.random() * 5000000) + 1000000
            });
        }
        
        return data;
    }

    static generateOrdersData(days = 30) {
        const data = [];
        const now = new Date();
        
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date(now);
            date.setDate(date.getDate() - i);
            
            const total = Math.floor(Math.random() * 100) + 20;
            const completed = Math.floor(total * 0.8);
            const cancelled = total - completed;
            
            data.push({
                date: date.toISOString().split('T')[0],
                orders: total,
                completed: completed,
                cancelled: cancelled
            });
        }
        
        return data;
    }

    static generateUserGrowthData(days = 30) {
        const data = [];
        const now = new Date();
        
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date(now);
            date.setDate(date.getDate() - i);
            
            data.push({
                date: date.toISOString().split('T')[0],
                new_users: Math.floor(Math.random() * 50) + 5,
                active_users: Math.floor(Math.random() * 200) + 100
            });
        }
        
        return data;
    }

    static generatePaymentMethodsData() {
        return [
            { method: 'QRIS', count: 450, percentage: 35 },
            { method: 'Bank Transfer', count: 380, percentage: 30 },
            { method: 'E-Wallet', count: 320, percentage: 25 },
            { method: 'Credit Card', count: 130, percentage: 10 }
        ];
    }
}

// Legacy compatibility functions
function generateMockOverviewStats() {
    return MockDataGenerator.generateOverviewStats();
}

function generateMockRevenueData(days = 30) {
    return MockDataGenerator.generateRevenueData(days);
}

function generateMockOrdersData(days = 30) {
    return MockDataGenerator.generateOrdersData(days);
}

function generateMockUserGrowthData(days = 30) {
    return MockDataGenerator.generateUserGrowthData(days);
}

function generateMockPaymentMethodsData() {
    return MockDataGenerator.generatePaymentMethodsData();
}
