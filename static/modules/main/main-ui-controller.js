// Main Dashboard UI Controller
class MainDashboardUIController {
    constructor() {
        this.elements = {};
        this.charts = {};
        this.initElements();
    }

    initElements() {
        this.elements = {
            totalRevenue: document.getElementById('totalRevenue'),
            totalTransactions: document.getElementById('totalTransactions'),
            totalUsers: document.getElementById('totalUsers'),
            totalProducts: document.getElementById('totalProducts'),
            recentTransactions: document.getElementById('recentTransactions'),
            transactionChart: document.getElementById('transactionChart'),
            categoryChart: document.getElementById('categoryChart')
        };
    }

    updateStatsCards(stats) {
        if (this.elements.totalRevenue) {
            this.elements.totalRevenue.textContent = Formatters.formatCurrency(stats.total_revenue || 0);
        }
        
        if (this.elements.totalTransactions) {
            this.elements.totalTransactions.textContent = Formatters.formatNumber(stats.total_transactions || 0);
        }
        
        if (this.elements.totalUsers) {
            this.elements.totalUsers.textContent = Formatters.formatNumber(stats.total_users || 0);
        }
        
        if (this.elements.totalProducts) {
            this.elements.totalProducts.textContent = Formatters.formatNumber(stats.total_products || 0);
        }
    }

    renderRecentTransactions(transactions) {
        if (!this.elements.recentTransactions) return;
        
        if (!transactions || transactions.length === 0) {
            this.elements.recentTransactions.innerHTML = '<p class="text-gray-500 text-center py-4">Tidak ada transaksi terbaru</p>';
            return;
        }
        
        this.elements.recentTransactions.innerHTML = transactions.map(transaction => `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div class="flex items-center">
                    <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                        <i class="fas fa-user text-white text-sm"></i>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm font-medium text-gray-900">${transaction.user || transaction.username || 'Unknown User'}</p>
                        <p class="text-xs text-gray-500">${transaction.product || transaction.product_name || 'Unknown Product'}</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-sm font-medium text-gray-900">${Formatters.formatCurrency(transaction.amount)}</p>
                    <div class="flex items-center justify-end mt-1">
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${transaction.status === 'success' ? 'bg-green-100 text-green-800' : transaction.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}">
                            <i class="fas ${transaction.status === 'success' ? 'fa-check' : transaction.status === 'pending' ? 'fa-clock' : 'fa-times'} mr-1"></i>
                            ${transaction.status === 'success' ? 'Berhasil' : transaction.status === 'pending' ? 'Pending' : 'Gagal'}
                        </span>
                    </div>
                    <p class="text-xs text-gray-400 mt-1">${Formatters.formatRelativeTime(transaction.created_at)}</p>
                </div>
            </div>
        `).join('');
    }

    initCharts(chartData) {
        this.initTransactionChart(chartData.revenue);
        this.initCategoryChart(chartData.orders);
    }

    initTransactionChart(data) {
        if (!this.elements.transactionChart) return;
        
        const ctx = this.elements.transactionChart.getContext('2d');
        this.charts.transaction = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                datasets: [{
                    label: 'Revenue',
                    data: data,
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    initCategoryChart(data) {
        if (!this.elements.categoryChart) return;
        
        const ctx = this.elements.categoryChart.getContext('2d');
        this.charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Electronics', 'Clothing', 'Books', 'Home'],
                datasets: [{
                    data: data,
                    backgroundColor: [
                        'rgb(59, 130, 246)',
                        'rgb(16, 185, 129)',
                        'rgb(245, 158, 11)',
                        'rgb(239, 68, 68)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

// Export class untuk digunakan oleh module bridge
window.MainDashboardUIController = MainDashboardUIController;

const mainDashboardUIController = new MainDashboardUIController();
