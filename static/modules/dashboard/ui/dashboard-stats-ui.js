// Dashboard Stats UI Components
class DashboardStatsUI {
    constructor() {
        this.formatters = {
            number: (num) => new Intl.NumberFormat('id-ID').format(num),
            currency: (amount) => new Intl.NumberFormat('id-ID', {
                style: 'currency',
                currency: 'IDR',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(amount)
        };
    }

    updateStatsCards(stats) {
        // Update Total Users
        const totalUsersElement = document.getElementById('totalUsers');
        if (totalUsersElement) {
            totalUsersElement.textContent = this.formatters.number(stats.total_users || 0);
        }

        // Update Total Transactions
        const totalTransactionsElement = document.getElementById('totalTransactions');
        if (totalTransactionsElement) {
            totalTransactionsElement.textContent = this.formatters.number(stats.total_transactions || 0);
        }

        // Update Total Products
        const totalProductsElement = document.getElementById('totalProducts');
        if (totalProductsElement) {
            totalProductsElement.textContent = this.formatters.number(stats.active_users || 0);
        }

        // Update Total Revenue
        const totalRevenueElement = document.getElementById('totalRevenue');
        if (totalRevenueElement) {
            totalRevenueElement.textContent = this.formatters.currency(stats.total_revenue || 0);
        }

        console.log('Stats updated:', stats);
    }
}

// Export untuk digunakan di modul lain
window.DashboardStatsUI = DashboardStatsUI;
