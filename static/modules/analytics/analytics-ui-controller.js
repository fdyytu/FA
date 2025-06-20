// Analytics UI Controller
class AnalyticsUIController {
    constructor() {
        this.elements = {};
        this.initElements();
    }

    initElements() {
        this.elements = {
            // Overview stats elements
            totalRevenue: document.getElementById('totalRevenue'),
            revenueChange: document.getElementById('revenueChange'),
            totalOrders: document.getElementById('totalOrders'),
            ordersChange: document.getElementById('ordersChange'),
            conversionRate: document.getElementById('conversionRate'),
            conversionChange: document.getElementById('conversionChange'),
            avgOrderValue: document.getElementById('avgOrderValue'),
            aovChange: document.getElementById('aovChange'),
            
            // Date range selector
            dateRangeSelector: document.getElementById('dateRangeSelector'),
            
            // Refresh buttons
            refreshButtons: document.querySelectorAll('[id^="refresh"]')
        };
    }

    updateOverviewStats(stats) {
        if (this.elements.totalRevenue) {
            this.elements.totalRevenue.textContent = Formatters.formatCurrency(stats.total_revenue || 0);
        }
        
        if (this.elements.revenueChange) {
            UIUtils.updateChangeIndicator(this.elements.revenueChange, stats.revenue_change || 0);
        }
        
        if (this.elements.totalOrders) {
            this.elements.totalOrders.textContent = Formatters.formatNumber(stats.total_orders || 0);
        }
        
        if (this.elements.ordersChange) {
            UIUtils.updateChangeIndicator(this.elements.ordersChange, stats.orders_change || 0);
        }
        
        if (this.elements.conversionRate) {
            this.elements.conversionRate.textContent = `${(stats.conversion_rate || 0).toFixed(1)}%`;
        }
        
        if (this.elements.conversionChange) {
            UIUtils.updateChangeIndicator(this.elements.conversionChange, stats.conversion_change || 0);
        }
        
        if (this.elements.avgOrderValue) {
            this.elements.avgOrderValue.textContent = Formatters.formatCurrency(stats.avg_order_value || 0);
        }
        
        if (this.elements.aovChange) {
            UIUtils.updateChangeIndicator(this.elements.aovChange, stats.aov_change || 0);
        }
    }

    initEventListeners() {
        // Date range selector
        if (this.elements.dateRangeSelector) {
            this.elements.dateRangeSelector.addEventListener('change', (e) => {
                const days = parseInt(e.target.value);
                analyticsDataService.setDateRange(days);
                this.refreshAnalytics();
            });
        }

        // Refresh buttons
        this.elements.refreshButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.refreshSection(button.id);
            });
        });

        // Export button
        const exportButton = document.getElementById('exportAnalytics');
        if (exportButton) {
            exportButton.addEventListener('click', () => {
                this.exportAnalytics();
            });
        }
    }

    async refreshAnalytics() {
        UIUtils.showLoading(true);
        
        try {
            const [overviewStats, chartData] = await Promise.all([
                analyticsDataService.loadOverviewStats(),
                analyticsDataService.loadChartData()
            ]);
            
            this.updateOverviewStats(overviewStats);
            this.updateCharts(chartData);
            
            UIUtils.showToast('Dashboard analytics berhasil diperbarui', 'success', 3000);
        } catch (error) {
            console.error('Error refreshing analytics:', error);
            UIUtils.showToast('Gagal memperbarui dashboard analytics', 'error');
        } finally {
            UIUtils.showLoading(false);
        }
    }

    updateCharts(data) {
        if (data.revenue && data.revenue.data) {
            analyticsCharts.createRevenueChart(data.revenue.data);
        }
        
        if (data.orders && data.orders.data) {
            analyticsCharts.createOrdersChart(data.orders.data);
        }
    }

    async refreshSection(buttonId) {
        const button = document.getElementById(buttonId);
        if (button) {
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>Refreshing...';
            button.disabled = true;
            
            try {
                // Handle specific section refresh logic here
                await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
                UIUtils.showToast('Data berhasil diperbarui', 'success', 2000);
            } catch (error) {
                UIUtils.showToast('Gagal memperbarui data', 'error');
            } finally {
                button.innerHTML = originalText;
                button.disabled = false;
            }
        }
    }

    exportAnalytics() {
        const exportData = {
            overview: analyticsDataService.getData(),
            date_range: analyticsDataService.getDateRange(),
            exported_at: new Date().toISOString()
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `analytics-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        UIUtils.showToast('Data analytics berhasil diekspor', 'success');
    }
}

// Global analytics UI controller instance
const analyticsUIController = new AnalyticsUIController();
