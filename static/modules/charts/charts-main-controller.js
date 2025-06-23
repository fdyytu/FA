// Charts Main Controller
// Maksimal 50 baris per file

class ChartsMainController {
    constructor() {
        this.transactionChart = new TransactionChart();
        this.categoryChart = new CategoryChart();
    }

    async initCharts() {
        try {
            // Destroy existing charts before creating new ones
            this.destroyCharts();
            
            await Promise.all([
                this.transactionChart.init(),
                this.categoryChart.init()
            ]);
            
            console.log('Charts initialized successfully');
        } catch (error) {
            console.error('Error initializing charts:', error);
        }
    }

    destroyCharts() {
        this.transactionChart.destroy();
        this.categoryChart.destroy();
    }

    // Cleanup charts when page unloads
    cleanup() {
        this.destroyCharts();
    }
}

// Global charts controller instance
let chartsController = null;

// Initialize charts
async function initCharts() {
    if (!chartsController) {
        chartsController = new ChartsMainController();
    }
    await chartsController.initCharts();
}

// Cleanup function for page unload
function cleanupCharts() {
    if (chartsController) {
        chartsController.cleanup();
    }
}
