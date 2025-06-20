// Analytics Charts Component
class AnalyticsCharts {
    constructor(chartManager) {
        this.chartManager = chartManager;
        this.defaultColors = {
            primary: 'rgb(59, 130, 246)',
            primaryLight: 'rgba(59, 130, 246, 0.1)',
            success: 'rgb(34, 197, 94)',
            successLight: 'rgba(34, 197, 94, 0.1)',
            warning: 'rgb(251, 191, 36)',
            warningLight: 'rgba(251, 191, 36, 0.1)',
            danger: 'rgb(239, 68, 68)',
            dangerLight: 'rgba(239, 68, 68, 0.1)'
        };
    }

    createRevenueChart(data) {
        const config = {
            type: 'line',
            data: {
                labels: data.map(item => formatChartDate(item.date)),
                datasets: [{
                    label: 'Revenue',
                    data: data.map(item => item.revenue),
                    borderColor: this.defaultColors.primary,
                    backgroundColor: this.defaultColors.primaryLight,
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
                }
            }
        };

        return this.chartManager.createChart('revenueChart', config);
    }

    createOrdersChart(data) {
        const config = {
            type: 'bar',
            data: {
                labels: data.map(item => formatChartDate(item.date)),
                datasets: [
                    {
                        label: 'Completed',
                        data: data.map(item => item.completed),
                        backgroundColor: this.defaultColors.success,
                        borderColor: this.defaultColors.success,
                        borderWidth: 1
                    },
                    {
                        label: 'Cancelled',
                        data: data.map(item => item.cancelled),
                        backgroundColor: this.defaultColors.danger,
                        borderColor: this.defaultColors.danger,
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
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
        };

        return this.chartManager.createChart('ordersChart', config);
    }
}

// Global analytics charts instance
const analyticsCharts = new AnalyticsCharts(chartManager);
