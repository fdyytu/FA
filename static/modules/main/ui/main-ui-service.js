// Main Dashboard UI Service
// Maksimal 50 baris per file

class MainUIService {
    static updateStatsCards(stats) {
        const elements = {
            totalUsers: document.getElementById('totalUsers'),
            totalTransactions: document.getElementById('totalTransactions'),
            totalProducts: document.getElementById('totalProducts'),
            totalRevenue: document.getElementById('totalRevenue')
        };
        
        if (elements.totalUsers) {
            elements.totalUsers.textContent = FormatUtils.formatNumber(stats.total_users || 0);
        }
        
        if (elements.totalTransactions) {
            elements.totalTransactions.textContent = FormatUtils.formatNumber(stats.total_transactions || 0);
        }
        
        if (elements.totalProducts) {
            elements.totalProducts.textContent = FormatUtils.formatNumber(stats.total_products || 0);
        }
        
        if (elements.totalRevenue) {
            elements.totalRevenue.textContent = FormatUtils.formatCurrency(stats.total_revenue || 0).replace('IDR', 'Rp');
        }

        // Remove error class if previously had error
        document.querySelectorAll('.stat-card').forEach(card => {
            card.classList.remove('error');
        });
    }

    static renderRecentTransactions(transactions) {
        const container = document.getElementById('recentTransactions');
        if (!container) return;
        
        if (transactions.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">Tidak ada transaksi terbaru</p>';
            return;
        }
        
        container.innerHTML = transactions.map(tx => `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div class="flex items-center">
                    <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                        <i class="fas fa-user text-white text-sm"></i>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm font-medium text-gray-900">${tx.user || tx.username || 'Unknown User'}</p>
                        <p class="text-xs text-gray-500">${tx.product || tx.product_name || 'Unknown Product'}</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-sm font-medium text-gray-900">${FormatUtils.formatCurrency(tx.amount)}</p>
                    <div class="flex items-center justify-end mt-1">
                        ${UIUtils.getStatusBadge(tx.status)}
                    </div>
                    <p class="text-xs text-gray-400 mt-1">${FormatUtils.formatRelativeTime(tx.created_at)}</p>
                </div>
            </div>
        `).join('');
    }

    static showStatsError() {
        document.querySelectorAll('.stat-card').forEach(card => {
            card.classList.add('error');
        });
    }
}

window.MainUIService = MainUIService;
