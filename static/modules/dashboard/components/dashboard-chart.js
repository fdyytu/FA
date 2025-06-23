// Dashboard Chart Component
class DashboardChart {
    constructor() {
        this.chart = null;
    }

    updateTransactionChart(trends) {
        const ctx = document.getElementById('transactionChart');
        if (!ctx) return;

        const labels = trends.map(trend => {
            const date = new Date(trend.date);
            return date.toLocaleDateString('id-ID', { month: 'short', day: 'numeric' });
        });

        const data = trends.map(trend => trend.count || 0);

        // Destroy existing chart if it exists
        if (this.chart) {
            this.chart.destroy();
        }

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Transaction Count',
                    data: data,
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
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }

    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// Export untuk digunakan di modul lain
window.DashboardChart = DashboardChart;
