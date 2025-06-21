// Dashboard analytics functionality
let charts = {};
let analyticsData = {};
let currentDateRange = 30;

// Initialize analytics dashboard
async function initAnalyticsDashboard() {
    const token = checkAuth();
    if (!token) return;

    showLoading(true);
    
    try {
        await Promise.all([
            loadOverviewStats(),
            loadChartData(),
            loadTopProducts(),
            loadRecentActivity(),
            loadPerformanceMetrics(),
            loadGeographicData()
        ]);
        
        initCharts();
        initEventListeners();
        showToast('Dashboard analytics berhasil dimuat', 'success', 3000);
    } catch (error) {
        console.error('Error loading analytics dashboard:', error);
        showToast('Gagal memuat data analytics', 'error');
    } finally {
        showLoading(false);
    }
}

// Load overview statistics
async function loadOverviewStats() {
    try {
        const response = await apiRequest(`/dashboard/stats/overview`);
        
        if (response && response.ok) {
            const data = await response.json();
            updateOverviewStats(data.data || data);
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
    } catch (error) {
        console.error('Error loading overview stats:', error);
        showError('Gagal memuat statistik overview');
        updateOverviewStats({
            total_revenue: 0,
            revenue_change: 0,
            total_orders: 0,
            orders_change: 0,
            conversion_rate: 0,
            conversion_change: 0,
            avg_order_value: 0,
            aov_change: 0
        });
    }
}



// Update overview statistics cards
function updateOverviewStats(stats) {
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
        updateChangeIndicator(elements.revenueChange, stats.revenue_change || 0);
    }
    
    if (elements.totalOrders) {
        elements.totalOrders.textContent = formatNumber(stats.total_orders || 0);
    }
    
    if (elements.ordersChange) {
        updateChangeIndicator(elements.ordersChange, stats.orders_change || 0);
    }
    
    if (elements.conversionRate) {
        elements.conversionRate.textContent = `${(stats.conversion_rate || 0).toFixed(1)}%`;
    }
    
    if (elements.conversionChange) {
        updateChangeIndicator(elements.conversionChange, stats.conversion_change || 0);
    }
    
    if (elements.avgOrderValue) {
        elements.avgOrderValue.textContent = formatCurrency(stats.avg_order_value || 0);
    }
    
    if (elements.aovChange) {
        updateChangeIndicator(elements.aovChange, stats.aov_change || 0);
    }
}

// Update change indicator
function updateChangeIndicator(element, change) {
    const isPositive = change >= 0;
    const icon = isPositive ? 'fa-arrow-up' : 'fa-arrow-down';
    const sign = isPositive ? '+' : '';
    
    element.innerHTML = `
        <i class="fas ${icon} mr-1"></i>
        ${sign}${change.toFixed(1)}%
    `;
}

// Load chart data
async function loadChartData() {
    try {
        const [revenueResponse, transactionResponse] = await Promise.all([
            apiRequest(`/dashboard/stats/revenue?period=daily`),
            apiRequest(`/dashboard/stats/transactions`)
        ]);
        
        analyticsData.revenue = revenueResponse && revenueResponse.ok ? 
            await revenueResponse.json() : { data: [] };
        
        analyticsData.transactions = transactionResponse && transactionResponse.ok ? 
            await transactionResponse.json() : { data: [] };
        
        // Set empty data for other charts until real endpoints are available
        analyticsData.userGrowth = { data: [] };
        analyticsData.paymentMethods = { data: [] };
        
    } catch (error) {
        console.error('Error loading chart data:', error);
        analyticsData = {
            revenue: { data: [] },
            transactions: { data: [] },
            userGrowth: { data: [] },
            paymentMethods: { data: [] }
        };
    }
}



// Initialize charts
function initCharts() {
    initRevenueChart();
    initOrdersChart();
    initUserGrowthChart();
    initPaymentMethodsChart();
}

// Initialize revenue chart
function initRevenueChart() {
    const ctx = document.getElementById('revenueChart');
    if (!ctx) return;
    
    const data = analyticsData.revenue.data || [];
    
    charts.revenue = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => formatChartDate(item.date)),
            datasets: [{
                label: 'Revenue',
                data: data.map(item => item.revenue),
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Initialize orders chart
function initOrdersChart() {
    const ctx = document.getElementById('ordersChart');
    if (!ctx) return;
    
    const data = analyticsData.orders.data || [];
    
    charts.orders = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => formatChartDate(item.date)),
            datasets: [
                {
                    label: 'Completed',
                    data: data.map(item => item.completed),
                    backgroundColor: 'rgba(34, 197, 94, 0.8)',
                    borderColor: 'rgb(34, 197, 94)',
                    borderWidth: 1
                },
                {
                    label: 'Cancelled',
                    data: data.map(item => item.cancelled),
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    borderColor: 'rgb(239, 68, 68)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    beginAtZero: true
                }
            }
        }
    });
}

// Initialize user growth chart
function initUserGrowthChart() {
    const ctx = document.getElementById('userGrowthChart');
    if (!ctx) return;
    
    const data = analyticsData.userGrowth.data || [];
    
    charts.userGrowth = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => formatChartDate(item.date)),
            datasets: [
                {
                    label: 'New Users',
                    data: data.map(item => item.new_users),
                    borderColor: 'rgb(168, 85, 247)',
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    borderWidth: 2,
                    fill: false
                },
                {
                    label: 'Active Users',
                    data: data.map(item => item.active_users),
                    borderColor: 'rgb(34, 197, 94)',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    borderWidth: 2,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Initialize payment methods chart
function initPaymentMethodsChart() {
    const ctx = document.getElementById('paymentMethodsChart');
    if (!ctx) return;
    
    const data = analyticsData.paymentMethods.data || [];
    
    charts.paymentMethods = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.method),
            datasets: [{
                data: data.map(item => item.count),
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(168, 85, 247, 0.8)',
                    'rgba(251, 146, 60, 0.8)'
                ],
                borderColor: [
                    'rgb(59, 130, 246)',
                    'rgb(34, 197, 94)',
                    'rgb(168, 85, 247)',
                    'rgb(251, 146, 60)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Format chart date
function formatChartDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', { 
        month: 'short', 
        day: 'numeric' 
    });
}

// Load top products
async function loadTopProducts() {
    try {
        const response = await apiRequest(`/dashboard/stats/products`);
        
        if (response && response.ok) {
            const data = await response.json();
            renderTopProducts(data.data?.top_products || []);
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
    } catch (error) {
        console.error('Error loading top products:', error);
        renderTopProducts([]);
    }
}

// Render top products
function renderTopProducts(products) {
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

// Load recent activity
async function loadRecentActivity() {
    try {
        const response = await apiRequest('/dashboard/recent-activities?limit=10');
        
        if (response && response.ok) {
            const data = await response.json();
            renderRecentActivity(data.data?.activities || []);
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
    } catch (error) {
        console.error('Error loading recent activity:', error);
        renderRecentActivity([]);
    }
}

// Render recent activity
function renderRecentActivity(activities) {
    const container = document.getElementById('recentActivity');
    if (!container) return;
    
    container.innerHTML = activities.map(activity => `
        <div class="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
            <div class="w-8 h-8 ${getActivityIconClass(activity.type)} rounded-full flex items-center justify-center">
                <i class="fas ${getActivityIcon(activity.type)} text-white text-xs"></i>
            </div>
            <div class="flex-1">
                <p class="text-sm text-gray-900">${activity.message}</p>
                <p class="text-xs text-gray-500">${formatRelativeTime(activity.time)}</p>
            </div>
        </div>
    `).join('');
}

// Get activity icon class
function getActivityIconClass(type) {
    switch (type) {
        case 'order': return 'bg-blue-500';
        case 'payment': return 'bg-green-500';
        case 'user': return 'bg-purple-500';
        case 'product': return 'bg-orange-500';
        default: return 'bg-gray-500';
    }
}

// Get activity icon
function getActivityIcon(type) {
    switch (type) {
        case 'order': return 'fa-shopping-cart';
        case 'payment': return 'fa-credit-card';
        case 'user': return 'fa-user';
        case 'product': return 'fa-box';
        default: return 'fa-info';
    }
}

// Load performance metrics
async function loadPerformanceMetrics() {
    try {
        const response = await apiRequest(`/dashboard/system-health`);
        
        if (response && response.ok) {
            const data = await response.json();
            renderPerformanceMetrics(data.data || {});
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
    } catch (error) {
        console.error('Error loading performance metrics:', error);
        renderPerformanceMetrics({
            response_time: 0,
            uptime: 0,
            error_rate: 0,
            customer_satisfaction: 0,
            refund_rate: 0
        });
    }
}

// Render performance metrics
function renderPerformanceMetrics(metrics) {
    const container = document.getElementById('performanceMetrics');
    if (!container) return;
    
    const metricsData = [
        { label: 'Response Time', value: `${metrics.response_time}ms`, icon: 'fa-clock', color: 'blue' },
        { label: 'Uptime', value: `${metrics.uptime}%`, icon: 'fa-server', color: 'green' },
        { label: 'Error Rate', value: `${metrics.error_rate}%`, icon: 'fa-exclamation-triangle', color: 'red' },
        { label: 'Customer Satisfaction', value: `${metrics.customer_satisfaction}/5`, icon: 'fa-star', color: 'yellow' },
        { label: 'Refund Rate', value: `${metrics.refund_rate}%`, icon: 'fa-undo', color: 'purple' }
    ];
    
    container.innerHTML = metricsData.map(metric => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div class="flex items-center">
                <div class="w-8 h-8 bg-${metric.color}-500 rounded-lg flex items-center justify-center">
                    <i class="fas ${metric.icon} text-white text-xs"></i>
                </div>
                <span class="ml-3 text-sm font-medium text-gray-900">${metric.label}</span>
            </div>
            <span class="text-sm font-semibold text-gray-900">${metric.value}</span>
        </div>
    `).join('');
}

// Load geographic data
async function loadGeographicData() {
    try {
        // Geographic data endpoint not available yet, skip for now
        renderGeographicData([]);
    } catch (error) {
        console.error('Error loading geographic data:', error);
        renderGeographicData([]);
    }
}

// Render geographic data
function renderGeographicData(data) {
    const container = document.getElementById('geographicData');
    if (!container) return;
    
    container.innerHTML = data.map(item => `
        <div class="flex items-center justify-between">
            <div class="flex items-center">
                <div class="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
                <span class="text-sm text-gray-900">${item.region}</span>
            </div>
            <div class="flex items-center space-x-2">
                <span class="text-sm font-medium text-gray-900">${formatNumber(item.users)}</span>
                <span class="text-xs text-gray-500">(${item.percentage}%)</span>
            </div>
        </div>
    `).join('');
}

// Initialize event listeners
function initEventListeners() {
    // Date range selector
    const dateRangeSelect = document.getElementById('dateRange');
    if (dateRangeSelect) {
        dateRangeSelect.addEventListener('change', handleDateRangeChange);
    }
    
    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshAnalytics);
    }
    
    // Export button
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportAnalytics);
    }
    
    // Chart period buttons
    initChartPeriodButtons();
    
    // Individual refresh buttons
    const refreshButtons = [
        'refreshPaymentMethods',
        'refreshGeographic',
        'refreshActivity',
        'refreshMetrics'
    ];
    
    refreshButtons.forEach(buttonId => {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener('click', () => refreshSection(buttonId));
        }
    });
}

// Initialize chart period buttons
function initChartPeriodButtons() {
    const periodButtons = [
        'revenueDaily', 'revenueWeekly', 'revenueMonthly',
        'ordersDaily', 'ordersWeekly', 'ordersMonthly'
    ];
    
    periodButtons.forEach(buttonId => {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener('click', () => handleChartPeriodChange(buttonId));
        }
    });
}

// Handle date range change
async function handleDateRangeChange(e) {
    currentDateRange = parseInt(e.target.value);
    showLoading(true);
    
    try {
        await Promise.all([
            loadOverviewStats(),
            loadChartData(),
            loadTopProducts(),
            loadPerformanceMetrics(),
            loadGeographicData()
        ]);
        
        updateCharts();
        showToast('Data berhasil diperbarui', 'success', 3000);
    } catch (error) {
        showToast('Gagal memperbarui data', 'error');
    } finally {
        showLoading(false);
    }
}

// Handle chart period change
function handleChartPeriodChange(buttonId) {
    const chartType = buttonId.includes('revenue') ? 'revenue' : 'orders';
    const period = buttonId.includes('Daily') ? 'daily' : 
                  buttonId.includes('Weekly') ? 'weekly' : 'monthly';
    
    // Update active button
    document.querySelectorAll(`[id^="${chartType}"]`).forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(buttonId).classList.add('active');
    
    // Update chart data based on period
    updateChartByPeriod(chartType, period);
}

// Update chart by period
async function updateChartByPeriod(chartType, period) {
    try {
        const response = await apiRequest(`/analytics/${chartType}?days=${currentDateRange}&period=${period}`);
        
        if (response && response.ok) {
            const data = await response.json();
            updateSpecificChart(chartType, data.data);
        }
    } catch (error) {
        console.error(`Error updating ${chartType} chart:`, error);
    }
}

// Update specific chart
function updateSpecificChart(chartType, data) {
    if (!charts[chartType] || !data) return;
    
    charts[chartType].data.labels = data.map(item => formatChartDate(item.date));
    
    if (chartType === 'revenue') {
        charts[chartType].data.datasets[0].data = data.map(item => item.revenue);
    } else if (chartType === 'orders') {
        charts[chartType].data.datasets[0].data = data.map(item => item.completed);
        charts[chartType].data.datasets[1].data = data.map(item => item.cancelled);
    }
    
    charts[chartType].update();
}

// Update all charts
function updateCharts() {
    Object.keys(charts).forEach(chartKey => {
        if (charts[chartKey]) {
            charts[chartKey].destroy();
        }
    });
    
    initCharts();
}

// Refresh analytics
async function refreshAnalytics() {
    showLoading(true);
    
    try {
        await Promise.all([
            loadOverviewStats(),
            loadChartData(),
            loadTopProducts(),
            loadRecentActivity(),
            loadPerformanceMetrics(),
            loadGeographicData()
        ]);
        
        updateCharts();
        showToast('Dashboard analytics berhasil diperbarui', 'success', 3000);
    } catch (error) {
        showToast('Gagal memperbarui dashboard analytics', 'error');
    } finally {
        showLoading(false);
    }
}

// Refresh specific section
async function refreshSection(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>Refreshing...';
    }
    
    try {
        switch (buttonId) {
            case 'refreshPaymentMethods':
                await loadChartData();
                if (charts.paymentMethods) {
                    charts.paymentMethods.destroy();
                    initPaymentMethodsChart();
                }
                break;
            case 'refreshGeographic':
                await loadGeographicData();
                break;
            case 'refreshActivity':
                await loadRecentActivity();
                break;
            case 'refreshMetrics':
                await loadPerformanceMetrics();
                break;
        }
        
        showToast('Data berhasil diperbarui', 'success', 2000);
    } catch (error) {
        showToast('Gagal memperbarui data', 'error');
    } finally {
        if (button) {
            button.innerHTML = '<i class="fas fa-sync-alt mr-1"></i>Refresh';
        }
    }
}

// Export analytics
function exportAnalytics() {
    const exportData = {
        overview: analyticsData,
        date_range: currentDateRange,
        exported_at: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `analytics-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    showToast('Data analytics berhasil diekspor', 'success');
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', () => {
    initAnalyticsDashboard();
    
    // Auto-refresh every 5 minutes
    setInterval(() => {
        loadRecentActivity();
        loadPerformanceMetrics();
    }, 5 * 60 * 1000);
});
