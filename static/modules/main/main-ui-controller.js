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
            totalOrders: document.getElementById('totalOrders'),
            totalUsers: document.getElementById('totalUsers'),
            totalProducts: document.getElementById('totalProducts'),
            recentTransactionsList: document.getElementById('recentTransactionsList'),
            transactionChart: document.getElementById('transactionChart'),
            categoryChart: document.getElementById('categoryChart')
        };
    }

    updateStatsCards(stats) {
        if (this.elements.totalRevenue) {
            this.elements.totalRevenue.textContent = Formatters.formatCurrency(stats.total_revenue || 0);
        }
        
        if (this.elements.totalOrders) {
            this.elements.totalOrders.textContent = Formatters.formatNumber(stats.total_orders || 0);
        }
        
        if (this.elements.totalUsers) {
            this.elements.totalUsers.textContent = Formatters.formatNumber(stats.total_users || 0);
        }
        
        if (this.elements.totalProducts) {
            this.elements.totalProducts.textContent = Formatters.formatNumber(stats.total_products || 0);
        }
    }

    renderRecentTransactions(transactions) {
        if (!this.elements.recentTransactionsList) return;
        
        this.elements.recentTransactionsList.innerHTML = transactions.map(transaction => `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    #${transaction.id}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${transaction.user}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${Formatters.formatCurrency(transaction.amount)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${transaction.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}">
                        ${transaction.status}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${Formatters.formatDate(transaction.date)}
                </td>
            </tr>
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

const mainDashboardUIController = new MainDashboardUIController();
