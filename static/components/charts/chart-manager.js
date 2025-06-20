// Chart Manager Component
class ChartManager {
    constructor() {
        this.charts = {};
    }

    createChart(canvasId, config) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.warn(`Canvas element with id "${canvasId}" not found`);
            return null;
        }

        // Destroy existing chart if exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    updateChart(chartId, newData) {
        const chart = this.charts[chartId];
        if (!chart) return false;

        chart.data = newData;
        chart.update();
        return true;
    }

    destroyChart(chartId) {
        if (this.charts[chartId]) {
            this.charts[chartId].destroy();
            delete this.charts[chartId];
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(chartId => {
            this.destroyChart(chartId);
        });
    }

    getChart(chartId) {
        return this.charts[chartId];
    }
}

// Global chart manager instance
const chartManager = new ChartManager();
