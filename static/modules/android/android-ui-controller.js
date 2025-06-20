// Android Dashboard UI Controller
class AndroidUIController {
    constructor() {
        this.transactionChart = null;
        this.categoryChart = null;
    }

    // Update stats cards
    updateStatsCards(stats) {
        document.getElementById('totalUsers').textContent = stats.total_users?.toLocaleString() || '1,250';
        document.getElementById('totalTransactions').textContent = stats.total_transactions?.toLocaleString() || '3,420';
        document.getElementById('totalProducts').textContent = stats.total_products?.toLocaleString() || '156';
        
        const revenue = stats.total_revenue || 45000000;
        document.getElementById('totalRevenue').textContent = 'Rp ' + (revenue / 1000000).toFixed(1) + 'M';
    }

    // Load recent transactions
    loadRecentTransactions(transactions) {
        const container = document.getElementById('recentTransactions');
        
        container.innerHTML = transactions.map(tx => `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center">
                    <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                        <i class="fas fa-user text-white text-sm"></i>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm font-medium text-gray-900">${tx.user}</p>
                        <p class="text-xs text-gray-500">${tx.product}</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-sm font-medium text-gray-900">Rp ${tx.amount.toLocaleString()}</p>
                    <div class="flex items-center justify-end">
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${this.getStatusClass(tx.status)}">
                            ${this.getStatusText(tx.status)}
                        </span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Get status class for transaction
    getStatusClass(status) {
        switch (status) {
            case 'success': return 'bg-green-100 text-green-800';
            case 'pending': return 'bg-yellow-100 text-yellow-800';
            case 'failed': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    }

    // Get status text
    getStatusText(status) {
        switch (status) {
            case 'success': return 'Berhasil';
            case 'pending': return 'Pending';
            case 'failed': return 'Gagal';
            default: return 'Unknown';
        }
    }

    // Show/hide loading
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }

    // Show error message
    showError(message) {
        console.error(message);
    }

    // Initialize mobile menu
    initMobileMenu() {
        const openBtn = document.getElementById('openSidebar');
        const closeBtn = document.getElementById('closeSidebar');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobileMenuOverlay');

        openBtn.addEventListener('click', () => {
            sidebar.classList.remove('sidebar-hidden');
            overlay.classList.remove('hidden');
        });

        closeBtn.addEventListener('click', this.closeMobileMenu);
        overlay.addEventListener('click', this.closeMobileMenu);
    }

    closeMobileMenu() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobileMenuOverlay');
        sidebar.classList.add('sidebar-hidden');
        overlay.classList.add('hidden');
    }

    // Initialize navigation
    initNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Remove active class from all items
                navItems.forEach(nav => nav.classList.remove('active'));
                
                // Add active class to clicked item
                item.classList.add('active');
            });
        });
    }
}

// Export for use in other modules
window.AndroidUIController = AndroidUIController;
