// Transaction Chart Component
// Maksimal 50 baris per file

class TransactionChart {
    constructor() {
        this.chart = null;
    }

    async init() {
        const canvas = document.getElementById('transactionChart');
        if (!canvas) return;
        
        this.destroy();
        const ctx = canvas.getContext('2d');
        
        try {
            const chartData = await ChartsAPIService.getTransactionData();
            
            this.chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartData.labels,
                    datasets: [{
                        label: 'Transaksi',
                        data: chartData.data,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#3b82f6',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }]
                },
                options: ChartsConfig.getTransactionChartOptions()
            });
            
        } catch (error) {
            console.error('Error initializing transaction chart:', error);
        }
    }

    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}
