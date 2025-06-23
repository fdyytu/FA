// Analytics Chart Manager
// Menangani semua chart untuk analytics dashboard

class AnalyticsChartManager {
    constructor() {
        this.charts = {};
        this.analyticsData = {};
    }

    // Initialize all charts
    initCharts() {
        this.initRevenueChart();
        this.initTransactionChart();
        this.initUserGrowthChart();
        this.initPaymentMethodsChart();
    }

    // Initialize revenue chart
    initRevenueChart() {
        const ctx = document.getElementById('revenueChart');
        if (!ctx) return;

        const data = this.analyticsData.revenue?.data || [];
        
        this.charts.revenue = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.date || item.label),
                datasets: [{
                    label: 'Revenue',
                    data: data.map(item => item.amount || item.value),
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
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
                }
            }
        });
    }

    // Initialize transaction chart
    initTransactionChart() {
        const ctx = document.getElementById('transactionChart');
        if (!ctx) return;

        const data = this.analyticsData.transactions?.data || [];
        
        this.charts.transaction = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.date || item.label),
                datasets: [{
                    label: 'Transactions',
                    data: data.map(item => item.count || item.value),
                    backgroundColor: 'rgba(34, 197, 94, 0.8)',
                    borderColor: 'rgb(34, 197, 94)',
                    borderWidth: 1
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
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Initialize user growth chart
    initUserGrowthChart() {
        const ctx = document.getElementById('userGrowthChart');
        if (!ctx) return;

        const data = this.analyticsData.userGrowth?.data || [];
        
        this.charts.userGrowth = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.date || item.label),
                datasets: [{
                    label: 'New Users',
                    data: data.map(item => item.users || item.value),
                    borderColor: 'rgb(168, 85, 247)',
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    tension: 0.4,
                    fill: true
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
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Initialize payment methods chart
    initPaymentMethodsChart() {
        const ctx = document.getElementById('paymentMethodsChart');
        if (!ctx) return;

        const data = this.analyticsData.paymentMethods?.data || [];
        
        this.charts.paymentMethods = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(item => item.method || item.label),
                datasets: [{
                    data: data.map(item => item.percentage || item.value),
                    backgroundColor: [
                        'rgb(59, 130, 246)',
                        'rgb(34, 197, 94)',
                        'rgb(168, 85, 247)',
                        'rgb(251, 146, 60)',
                        'rgb(239, 68, 68)'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
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

    // Update chart data
    updateChartData(chartName, newData) {
        if (this.charts[chartName]) {
            const chart = this.charts[chartName];
            
            switch (chartName) {
                case 'revenue':
                    chart.data.labels = newData.map(item => item.date || item.label);
                    chart.data.datasets[0].data = newData.map(item => item.amount || item.value);
                    break;
                case 'transaction':
                    chart.data.labels = newData.map(item => item.date || item.label);
                    chart.data.datasets[0].data = newData.map(item => item.count || item.value);
                    break;
                case 'userGrowth':
                    chart.data.labels = newData.map(item => item.date || item.label);
                    chart.data.datasets[0].data = newData.map(item => item.users || item.value);
                    break;
                case 'paymentMethods':
                    chart.data.labels = newData.map(item => item.method || item.label);
                    chart.data.datasets[0].data = newData.map(item => item.percentage || item.value);
                    break;
            }
            
            chart.update();
        }
    }

    // Update all charts
    updateAllCharts() {
        Object.keys(this.charts).forEach(chartKey => {
            if (this.charts[chartKey]) {
                this.charts[chartKey].destroy();
            }
        });
        
        this.initCharts();
    }

    // Set analytics data
    setAnalyticsData(data) {
        this.analyticsData = data;
    }

    // Destroy all charts
    destroyAllCharts() {
        Object.keys(this.charts).forEach(chartKey => {
            if (this.charts[chartKey]) {
                this.charts[chartKey].destroy();
            }
        });
        this.charts = {};
    }
}

// Export instance
window.analyticsChartManager = new AnalyticsChartManager();
