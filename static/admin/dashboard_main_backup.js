// Dashboard Main JavaScript
class DashboardManager {
    constructor() {
        this.token = localStorage.getItem('adminToken');
        this.apiBaseUrl = '/api/v1/admin';
        this.init();
    }

    async init() {
        // Check authentication
        if (!this.token) {
            window.location.href = 'admin_login.html';
            return;
        }

        // Load dashboard data
        await this.loadDashboardData();
        
        // Setup refresh interval (every 30 seconds)
        setInterval(() => this.loadDashboardData(), 30000);
    }

    async loadDashboardData() {
        try {
            await Promise.all([
                this.loadOverviewStats(),
                this.loadRecentTransactions(),
                this.loadTransactionTrends()
            ]);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data. Please refresh the page.');
        }
    }

    async loadOverviewStats() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/dashboard/stats/overview`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.updateStatsCards(data.data);
        } catch (error) {
            console.error('Error loading overview stats:', error);
            throw error;
        }
    }

    async loadRecentTransactions() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/dashboard/`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.updateTransactionTrends(data.transaction_trends);
        } catch (error) {
            console.error('Error loading recent transactions:', error);
            throw error;
        }
    }

    async loadTransactionTrends() {
        // This will be loaded as part of loadRecentTransactions
        // Keeping this method for future separate implementation if needed
    }

    updateStatsCards(stats) {
        // Update Total Users
        const totalUsersElement = document.getElementById('totalUsers');
        if (totalUsersElement) {
            totalUsersElement.textContent = this.formatNumber(stats.total_users || 0);
        }

        // Update Total Transactions
        const totalTransactionsElement = document.getElementById('totalTransactions');
        if (totalTransactionsElement) {
            totalTransactionsElement.textContent = this.formatNumber(stats.total_transactions || 0);
        }

        // Update Total Products (using active users as proxy since we don't have products endpoint)
        const totalProductsElement = document.getElementById('totalProducts');
        if (totalProductsElement) {
            totalProductsElement.textContent = this.formatNumber(stats.active_users || 0);
        }

        // Update Total Revenue
        const totalRevenueElement = document.getElementById('totalRevenue');
        if (totalRevenueElement) {
            totalRevenueElement.textContent = this.formatCurrency(stats.total_revenue || 0);
        }

        console.log('Stats updated:', stats);
    }

    updateTransactionTrends(trends) {
        if (!trends || !Array.isArray(trends)) {
            console.warn('No transaction trends data available');
            return;
        }

        // Update transaction chart
        this.updateTransactionChart(trends);
        console.log('Transaction trends updated:', trends);
    }

    updateTransactionChart(trends) {
        const ctx = document.getElementById('transactionChart');
        if (!ctx) return;

        const labels = trends.map(trend => {
            const date = new Date(trend.date);
            return date.toLocaleDateString('id-ID', { month: 'short', day: 'numeric' });
        });

        const data = trends.map(trend => trend.count || 0);
        const amounts = trends.map(trend => trend.amount || 0);

        // Destroy existing chart if it exists
        if (window.transactionChart) {
            window.transactionChart.destroy();
        }

        window.transactionChart = new Chart(ctx, {
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

    formatNumber(num) {
        return new Intl.NumberFormat('id-ID').format(num);
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }

    showError(message) {
        // Create or update error notification
        let errorDiv = document.getElementById('dashboard-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'dashboard-error';
            errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
            document.body.appendChild(errorDiv);
        }
        
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';

        // Auto hide after 5 seconds
        setTimeout(() => {
            if (errorDiv) {
                errorDiv.style.display = 'none';
            }
        }, 5000);
    }

    showSuccess(message) {
        // Create or update success notification
        let successDiv = document.getElementById('dashboard-success');
        if (!successDiv) {
            successDiv = document.createElement('div');
            successDiv.id = 'dashboard-success';
            successDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
            document.body.appendChild(successDiv);
        }
        
        successDiv.textContent = message;
        successDiv.style.display = 'block';

        // Auto hide after 3 seconds
        setTimeout(() => {
            if (successDiv) {
                successDiv.style.display = 'none';
            }
        }, 3000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.dashboardManager = new DashboardManager();
});

// Add logout functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add logout button if it doesn't exist
    const sidebar = document.querySelector('.sidebar nav');
    if (sidebar && !document.getElementById('logoutBtn')) {
        const logoutLink = document.createElement('a');
        logoutLink.href = '#';
        logoutLink.id = 'logoutBtn';
        logoutLink.className = 'nav-item';
        logoutLink.innerHTML = '<i class="fas fa-sign-out-alt mr-3"></i>Logout';
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            localStorage.removeItem('adminToken');
            window.location.href = 'admin_login.html';
        });
        sidebar.appendChild(logoutLink);
    }
});
