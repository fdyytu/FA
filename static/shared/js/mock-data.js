// Mock Data Generator untuk Dashboard Admin
const MockDataGenerator = {
    // Generate overview statistics
    generateOverviewStats() {
        return {
            total_revenue: Math.floor(Math.random() * 10000000) + 5000000,
            total_orders: Math.floor(Math.random() * 1000) + 500,
            conversion_rate: (Math.random() * 10 + 5).toFixed(2),
            avg_order_value: Math.floor(Math.random() * 500000) + 100000,
            revenue_change: (Math.random() * 20 - 10).toFixed(1),
            orders_change: (Math.random() * 20 - 10).toFixed(1),
            conversion_change: (Math.random() * 5 - 2.5).toFixed(1),
            aov_change: (Math.random() * 15 - 7.5).toFixed(1)
        };
    },

    // Generate revenue data for charts
    generateRevenueData(days = 30) {
        const data = [];
        const today = new Date();
        
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            
            data.push({
                date: date.toISOString().split('T')[0],
                revenue: Math.floor(Math.random() * 1000000) + 100000,
                orders: Math.floor(Math.random() * 50) + 10
            });
        }
        
        return data;
    },

    // Generate orders data
    generateOrdersData(days = 30) {
        const data = [];
        const today = new Date();
        
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            
            data.push({
                date: date.toISOString().split('T')[0],
                orders: Math.floor(Math.random() * 100) + 20,
                completed: Math.floor(Math.random() * 80) + 15,
                pending: Math.floor(Math.random() * 15) + 3,
                cancelled: Math.floor(Math.random() * 5) + 1
            });
        }
        
        return data;
    },

    // Generate user growth data
    generateUserGrowthData(days = 30) {
        const data = [];
        const today = new Date();
        
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            
            data.push({
                date: date.toISOString().split('T')[0],
                new_users: Math.floor(Math.random() * 50) + 5,
                active_users: Math.floor(Math.random() * 200) + 50,
                returning_users: Math.floor(Math.random() * 100) + 20
            });
        }
        
        return data;
    },

    // Generate payment methods data
    generatePaymentMethodsData() {
        return [
            { method: 'Bank Transfer', count: Math.floor(Math.random() * 500) + 200, percentage: 45 },
            { method: 'E-Wallet', count: Math.floor(Math.random() * 400) + 150, percentage: 35 },
            { method: 'Credit Card', count: Math.floor(Math.random() * 200) + 50, percentage: 15 },
            { method: 'Cash', count: Math.floor(Math.random() * 100) + 20, percentage: 5 }
        ];
    },

    // Generate top products data
    generateTopProductsData(limit = 10) {
        const products = [
            'Pulsa Telkomsel', 'Pulsa XL', 'Pulsa Indosat', 'Pulsa Smartfren',
            'Token PLN', 'Paket Data Telkomsel', 'Paket Data XL', 'Paket Data Indosat',
            'BPJS Kesehatan', 'Tagihan Listrik', 'Air PDAM', 'Internet Indihome'
        ];
        
        const data = [];
        for (let i = 0; i < Math.min(limit, products.length); i++) {
            data.push({
                product_name: products[i],
                sales_count: Math.floor(Math.random() * 1000) + 100,
                revenue: Math.floor(Math.random() * 10000000) + 1000000,
                growth: (Math.random() * 50 - 25).toFixed(1)
            });
        }
        
        return data.sort((a, b) => b.sales_count - a.sales_count);
    },

    // Generate recent transactions
    generateRecentTransactions(limit = 10) {
        const statuses = ['success', 'pending', 'failed'];
        const products = ['Pulsa Telkomsel', 'Token PLN', 'Paket Data XL', 'BPJS Kesehatan'];
        const data = [];
        
        for (let i = 0; i < limit; i++) {
            const date = new Date();
            date.setMinutes(date.getMinutes() - Math.floor(Math.random() * 1440)); // Last 24 hours
            
            data.push({
                id: `TRX${Date.now()}${i}`,
                user_name: `User ${Math.floor(Math.random() * 1000) + 1}`,
                product: products[Math.floor(Math.random() * products.length)],
                amount: Math.floor(Math.random() * 500000) + 10000,
                status: statuses[Math.floor(Math.random() * statuses.length)],
                created_at: date.toISOString()
            });
        }
        
        return data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    },

    // Generate performance metrics
    generatePerformanceMetrics() {
        return {
            response_time: (Math.random() * 500 + 100).toFixed(0) + 'ms',
            uptime: (99 + Math.random()).toFixed(2) + '%',
            error_rate: (Math.random() * 2).toFixed(2) + '%',
            throughput: Math.floor(Math.random() * 1000) + 500 + ' req/min',
            cpu_usage: (Math.random() * 80 + 10).toFixed(1) + '%',
            memory_usage: (Math.random() * 70 + 20).toFixed(1) + '%',
            disk_usage: (Math.random() * 60 + 30).toFixed(1) + '%'
        };
    },

    // Generate user activity data
    generateUserActivity(limit = 20) {
        const activities = [
            'User login', 'Purchase completed', 'Profile updated', 'Password changed',
            'Transaction failed', 'Refund requested', 'Support ticket created'
        ];
        
        const data = [];
        for (let i = 0; i < limit; i++) {
            const date = new Date();
            date.setMinutes(date.getMinutes() - Math.floor(Math.random() * 2880)); // Last 48 hours
            
            data.push({
                id: i + 1,
                user_name: `User ${Math.floor(Math.random() * 1000) + 1}`,
                activity: activities[Math.floor(Math.random() * activities.length)],
                timestamp: date.toISOString(),
                ip_address: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`
            });
        }
        
        return data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    }
};

// Export untuk penggunaan global
window.MockDataGenerator = MockDataGenerator;
