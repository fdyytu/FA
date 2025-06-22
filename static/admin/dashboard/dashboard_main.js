// Dashboard main functionality

// Initialize dashboard
async function initDashboard() {
    const token = checkAuth();
    if (!token) return;

    showLoading(true);
    
    try {
        await Promise.all([
            loadDashboardStats(),
            loadRecentTransactions(),
            initCharts()
        ]);
        
        showToast('Dashboard berhasil dimuat', 'success', 3000);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showToast('Gagal memuat data dashboard', 'error');
    } finally {
        showLoading(false);
    }
}

// Load dashboard statistics
async function loadDashboardStats() {
    try {
        const response = await apiRequest('/admin/stats/');
        if (!response || !response.data) {
            throw new Error('Invalid response format');
        }
        updateStatsCards(response.data);
        
        // Hapus kelas error jika sebelumnya ada error
        document.querySelectorAll('.stat-card').forEach(card => {
            card.classList.remove('error');
        });
    } catch (error) {
        console.error('Error loading stats:', error);
        showToast('Gagal memuat statistik dashboard', 'error');
        
        // Tambahkan visual indicator untuk error
        document.querySelectorAll('.stat-card').forEach(card => {
            card.classList.add('error');
        });
        
        // Set nilai 0 untuk semua stats
        updateStatsCards({
            total_users: 0,
            total_transactions: 0,
            total_products: 0,
            total_revenue: 0
        });
    }
}

// Update stats cards
function updateStatsCards(stats) {
    const elements = {
        totalUsers: document.getElementById('totalUsers'),
        totalTransactions: document.getElementById('totalTransactions'),
        totalProducts: document.getElementById('totalProducts'),
        totalRevenue: document.getElementById('totalRevenue')
    };
    
    if (elements.totalUsers) {
        elements.totalUsers.textContent = formatNumber(stats.total_users || 0);
    }
    
    if (elements.totalTransactions) {
        elements.totalTransactions.textContent = formatNumber(stats.total_transactions || 0);
    }
    
    if (elements.totalProducts) {
        elements.totalProducts.textContent = formatNumber(stats.total_products || 0);
    }
    
    if (elements.totalRevenue) {
        elements.totalRevenue.textContent = formatCurrency(stats.total_revenue || 0).replace('IDR', 'Rp');
    }
}

// Load recent transactions
async function loadRecentTransactions() {
    const container = document.getElementById('recentTransactions');
    if (!container) return;
    
    try {
        const data = await apiRequest('/admin/transactions/recent?limit=5');
        const transactions = data.data || [];
        
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
                    <p class="text-sm font-medium text-gray-900">${formatCurrency(tx.amount)}</p>
                    <div class="flex items-center justify-end mt-1">
                        ${getStatusBadge(tx.status)}
                    </div>
                    <p class="text-xs text-gray-400 mt-1">${formatRelativeTime(tx.created_at)}</p>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading recent transactions:', error);
        container.innerHTML = '<p class="text-gray-500 text-center py-4">Gagal memuat transaksi terbaru</p>';
    }
}

// Refresh dashboard data
async function refreshDashboard() {
    showLoading(true);
    try {
        await Promise.all([
            loadDashboardStats(),
            loadRecentTransactions(),
            initCharts()
        ]);
        showToast('Dashboard berhasil diperbarui', 'success', 3000);
    } catch (error) {
        showToast('Gagal memperbarui dashboard', 'error');
    } finally {
        showLoading(false);
    }
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Use bridge initialization if available, fallback to original
    if (window.DashboardBridge) {
        initDashboardWithBridge();
        loadDiscordStatsWithBridge();
    } else {
        initDashboard();
        if (window.loadDiscordStats) {
            loadDiscordStats();
        }
    }
    
    initFloatingActionButton();
    
    // Auto-refresh setiap 15 detik using bridge
    setInterval(() => {
        if (window.DashboardBridge && window.DashboardBridge.isInitialized) {
            refreshDashboardWithBridge();
            loadDiscordStatsWithBridge();
        } else {
            refreshDashboard();
            if (window.loadDiscordStats) {
                loadDiscordStats();
            }
        }
    }, 15 * 1000);
});

// Module Bridge Integration Functions
async function loadDashboardStatsWithBridge() {
    try {
        if (window.DashboardBridge && window.DashboardBridge.isInitialized) {
            console.log('📊 Loading dashboard stats via module bridge...');
            await window.DashboardBridge.loadDashboardStats();
        } else {
            console.log('📊 Loading dashboard stats via fallback...');
            await loadDashboardStats();
        }
    } catch (error) {
        console.error('Error loading dashboard stats via bridge:', error);
        // Fallback to original implementation
        await loadDashboardStats();
    }
}

async function loadDiscordStatsWithBridge() {
    try {
        if (window.DashboardBridge && window.DashboardBridge.isInitialized) {
            console.log('🤖 Loading Discord stats via module bridge...');
            await window.DashboardBridge.loadDiscordStats();
        } else {
            console.log('🤖 Loading Discord stats via fallback...');
            if (window.loadDiscordStats) {
                await window.loadDiscordStats();
            }
        }
    } catch (error) {
        console.error('Error loading Discord stats via bridge:', error);
        // Fallback to original implementation
        if (window.loadDiscordStats) {
            await window.loadDiscordStats();
        }
    }
}

async function refreshDashboardWithBridge() {
    showLoading(true);
    try {
        if (window.DashboardBridge && window.DashboardBridge.isInitialized) {
            console.log('🔄 Refreshing dashboard via module bridge...');
            await window.DashboardBridge.refreshDashboard();
        } else {
            console.log('🔄 Refreshing dashboard via fallback...');
            await Promise.all([
                loadDashboardStats(),
                loadRecentTransactions(),
                initCharts()
            ]);
        }
        showToast('Dashboard berhasil diperbarui', 'success', 3000);
    } catch (error) {
        showToast('Gagal memperbarui dashboard', 'error');
    } finally {
        showLoading(false);
    }
}

// Enhanced initialization with module bridge
async function initDashboardWithBridge() {
    const token = checkAuth();
    if (!token) return;

    showLoading(true);
    
    try {
        // Wait for module bridge to initialize
        if (window.DashboardBridge && !window.DashboardBridge.isInitialized) {
            console.log('⏳ Waiting for module bridge to initialize...');
            await new Promise(resolve => {
                const checkBridge = setInterval(() => {
                    if (window.DashboardBridge && window.DashboardBridge.isInitialized) {
                        clearInterval(checkBridge);
                        resolve();
                    }
                }, 100);
                
                // Timeout after 5 seconds
                setTimeout(() => {
                    clearInterval(checkBridge);
                    resolve();
                }, 5000);
            });
        }

        await Promise.all([
            loadDashboardStatsWithBridge(),
            loadRecentTransactions(),
            initCharts()
        ]);
        
        showToast('Dashboard berhasil dimuat', 'success', 3000);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showToast('Gagal memuat data dashboard', 'error');
    } finally {
        showLoading(false);
    }
}

// Cleanup charts when page unloads
window.addEventListener('beforeunload', () => {
    cleanupCharts();
});
