// Android Dashboard UI Service
// Maksimal 50 baris per file

class AndroidUIService {
    static updateStatsCards(stats) {
        document.getElementById('totalUsers').textContent = stats.total_users?.toLocaleString() || '0';
        document.getElementById('totalTransactions').textContent = stats.total_transactions?.toLocaleString() || '0';
        document.getElementById('totalProducts').textContent = stats.total_products?.toLocaleString() || '0';
        
        const revenue = stats.total_revenue || 0;
        document.getElementById('totalRevenue').textContent = 'Rp ' + (revenue / 1000000).toFixed(1) + 'M';
    }

    static renderRecentTransactions(transactions) {
        const container = document.getElementById('recentTransactions');
        
        if (transactions.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">Tidak ada transaksi terbaru</p>';
            return;
        }
        
        container.innerHTML = transactions.map(tx => `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center">
                    <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                        <i class="fas fa-exchange-alt text-white text-sm"></i>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm font-medium text-gray-900">${tx.description || 'Transaksi'}</p>
                        <p class="text-xs text-gray-500">${this.formatDate(tx.created_at)}</p>
                    </div>
                </div>
                <div class="text-right">
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        ${tx.type || 'transaction'}
                    </span>
                </div>
            </div>
        `).join('');
    }

    static formatDate(dateString) {
        if (!dateString) return 'Tidak diketahui';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'Baru saja';
        if (diffMins < 60) return `${diffMins} menit lalu`;
        if (diffHours < 24) return `${diffHours} jam lalu`;
        if (diffDays < 7) return `${diffDays} hari lalu`;
        
        return date.toLocaleDateString('id-ID');
    }
}

window.AndroidUIService = AndroidUIService;
