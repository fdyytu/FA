// Android Dashboard Chart Manager
class AndroidChartManager {
    constructor() {
        this.transactionChart = null;
        this.categoryChart = null;
    }

    // Initialize all charts
    initCharts() {
        this.initTransactionChart();
        this.initCategoryChart();
    }

    // Initialize transaction chart
    initTransactionChart() {
        const ctx = document.getElementById('transactionChart').getContext('2d');
        
        this.transactionChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'],
                datasets: [{
                    label: 'Transaksi',
                    data: [120, 190, 300, 500, 200, 300, 450],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
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
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Initialize category chart
    initCategoryChart() {
        const ctx = document.getElementById('categoryChart').getContext('2d');
        
        this.categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Pulsa', 'Token PLN', 'Paket Data', 'BPJS', 'Lainnya'],
                datasets: [{
                    data: [35, 25, 20, 15, 5],
                    backgroundColor: [
                        '#3b82f6',
                        '#10b981',
                        '#8b5cf6',
                        '#f59e0b',
                        '#ef4444'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    // Destroy charts
    destroyCharts() {
        if (this.transactionChart) {
            this.transactionChart.destroy();
        }
        if (this.categoryChart) {
            this.categoryChart.destroy();
        }
    }
}

// Export for use in other modules
window.AndroidChartManager = AndroidChartManager;
