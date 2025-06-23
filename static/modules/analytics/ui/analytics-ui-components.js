// Analytics UI Components
// Menangani semua komponen UI untuk analytics

class AnalyticsUIComponents {
    constructor() {
        this.charts = {};
    }

    // Update overview statistics cards
    updateOverviewStats(stats) {
        const elements = {
            totalRevenue: document.getElementById('totalRevenue'),
            revenueChange: document.getElementById('revenueChange'),
            totalOrders: document.getElementById('totalOrders'),
            ordersChange: document.getElementById('ordersChange'),
            conversionRate: document.getElementById('conversionRate'),
            conversionChange: document.getElementById('conversionChange'),
            avgOrderValue: document.getElementById('avgOrderValue'),
            aovChange: document.getElementById('aovChange')
        };
        
        if (elements.totalRevenue) {
            elements.totalRevenue.textContent = formatCurrency(stats.total_revenue || 0);
        }
        
        if (elements.revenueChange) {
            this.updateChangeIndicator(elements.revenueChange, stats.revenue_change || 0);
        }
        
        if (elements.totalOrders) {
            elements.totalOrders.textContent = formatNumber(stats.total_orders || 0);
        }
        
        if (elements.ordersChange) {
            this.updateChangeIndicator(elements.ordersChange, stats.orders_change || 0);
        }
        
        if (elements.conversionRate) {
            elements.conversionRate.textContent = `${(stats.conversion_rate || 0).toFixed(1)}%`;
        }
        
        if (elements.conversionChange) {
            this.updateChangeIndicator(elements.conversionChange, stats.conversion_change || 0);
        }
        
        if (elements.avgOrderValue) {
            elements.avgOrderValue.textContent = formatCurrency(stats.avg_order_value || 0);
        }
        
        if (elements.aovChange) {
            this.updateChangeIndicator(elements.aovChange, stats.aov_change || 0);
        }
    }

    // Update change indicator
    updateChangeIndicator(element, change) {
        const isPositive = change >= 0;
        const icon = isPositive ? 'fa-arrow-up' : 'fa-arrow-down';
        const sign = isPositive ? '+' : '';
        
        element.innerHTML = `
            <i class="fas ${icon} mr-1"></i>
            ${sign}${change.toFixed(1)}%
        `;
    }

    // Render top products
    renderTopProducts(products) {
        const container = document.getElementById('topProductsList');
        if (!container) return;
        
        container.innerHTML = products.map((product, index) => `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center">
                    <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                        <span class="text-white text-sm font-bold">${index + 1}</span>
                    </div>
                    <div class="ml-3">
                        <h4 class="text-sm font-medium text-gray-900">${product.name}</h4>
                        <p class="text-xs text-gray-500">${formatNumber(product.sales)} terjual</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-sm font-semibold text-gray-900">${formatCurrency(product.revenue)}</p>
                    <p class="text-xs text-gray-500">Revenue</p>
                </div>
            </div>
        `).join('');
    }

    // Render recent activity
    renderRecentActivity(activities) {
        const container = document.getElementById('recentActivity');
        if (!container) return;
        
        container.innerHTML = activities.map(activity => `
            <div class="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                <div class="w-8 h-8 ${this.getActivityIconClass(activity.type)} rounded-full flex items-center justify-center">
                    <i class="fas ${this.getActivityIcon(activity.type)} text-white text-xs"></i>
                </div>
                <div class="flex-1">
                    <p class="text-sm text-gray-900">${activity.message}</p>
                    <p class="text-xs text-gray-500">${formatRelativeTime(activity.time)}</p>
                </div>
            </div>
        `).join('');
    }

    // Get activity icon class
    getActivityIconClass(type) {
        switch (type) {
            case 'order': return 'bg-blue-500';
            case 'payment': return 'bg-green-500';
            case 'user': return 'bg-purple-500';
            case 'product': return 'bg-orange-500';
            default: return 'bg-gray-500';
        }
    }

    // Get activity icon
    getActivityIcon(type) {
        switch (type) {
            case 'order': return 'fa-shopping-cart';
            case 'payment': return 'fa-credit-card';
            case 'user': return 'fa-user';
            case 'product': return 'fa-box';
            default: return 'fa-info';
        }
    }

    // Render performance metrics
    renderPerformanceMetrics(metrics) {
        const container = document.getElementById('performanceMetrics');
        if (!container) return;
        
        const metricsHtml = Object.entries(metrics).map(([key, value]) => `
            <div class="bg-white p-4 rounded-lg shadow">
                <h4 class="text-sm font-medium text-gray-500">${this.formatMetricName(key)}</h4>
                <p class="text-2xl font-bold text-gray-900">${this.formatMetricValue(key, value)}</p>
            </div>
        `).join('');
        
        container.innerHTML = metricsHtml;
    }

    // Format metric name
    formatMetricName(key) {
        const names = {
            'page_load_time': 'Page Load Time',
            'bounce_rate': 'Bounce Rate',
            'session_duration': 'Avg Session Duration',
            'conversion_rate': 'Conversion Rate'
        };
        return names[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    // Format metric value
    formatMetricValue(key, value) {
        switch (key) {
            case 'page_load_time':
            case 'session_duration':
                return `${value}s`;
            case 'bounce_rate':
            case 'conversion_rate':
                return `${value}%`;
            default:
                return value;
        }
    }
}

// Export instance
window.analyticsUIComponents = new AnalyticsUIComponents();
