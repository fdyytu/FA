// Category Chart Component
// Maksimal 50 baris per file

class CategoryChart {
    constructor() {
        this.chart = null;
    }

    async init() {
        const canvas = document.getElementById('categoryChart');
        if (!canvas) return;
        
        this.destroy();
        const ctx = canvas.getContext('2d');
        
        try {
            const chartData = await ChartsAPIService.getCategoryData();
            
            this.chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: chartData.labels,
                    datasets: [{
                        data: chartData.data,
                        backgroundColor: [
                            '#3b82f6',
                            '#10b981',
                            '#8b5cf6',
                            '#f59e0b',
                            '#ef4444'
                        ],
                        borderWidth: 0,
                        hoverOffset: 4
                    }]
                },
                options: ChartsConfig.getCategoryChartOptions()
            });
            
        } catch (error) {
            console.error('Error initializing category chart:', error);
        }
    }

    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}
