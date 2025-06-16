// Dashboard main functionality
let transactionChart, categoryChart;

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
        const response = await apiRequest('/dashboard/stats');
        
        if (response && response.ok) {
            const data = await response.json();
            updateStatsCards(data.data || data);
        } else {
            // Use mock data if API fails
            updateStatsCards({
                total_users: 1250,
                total_transactions: 3420,
                total_products: 156,
                total_revenue: 45000000,
                discord_bots: 3,
                active_users: 892
            });
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        // Use mock data
        updateStatsCards({
            total_users: 1250,
            total_transactions: 3420,
            total_products: 156,
            total_revenue: 45000000,
            discord_bots: 3,
            active_users: 892
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
        elements.totalUsers.textContent = formatNumber(stats.total_users || 1250);
    }
    
    if (elements.totalTransactions) {
        elements.totalTransactions.textContent = formatNumber(stats.total_transactions || 3420);
    }
    
    if (elements.totalProducts) {
        elements.totalProducts.textContent = formatNumber(stats.total_products || 156);
    }
    
    if (elements.totalRevenue) {
        const revenue = stats.total_revenue || 45000000;
        elements.totalRevenue.textContent = formatCurrency(revenue).replace('IDR', 'Rp');
    }
}

// Load recent transactions
async function loadRecentTransactions() {
    const container = document.getElementById('recentTransactions');
    if (!container) return;
    
    try {
        const response = await apiRequest('/transactions/recent?limit=5');
        let transactions = [];
        
        if (response && response.ok) {
            const data = await response.json();
            transactions = data.data || [];
        }
        
        // Use mock data if no real data
        if (transactions.length === 0) {
            transactions = [
                { 
                    id: 1, 
                    user: 'John Doe', 
                    product: 'Pulsa Telkomsel 50K', 
                    amount: 52000, 
                    status: 'success', 
                    created_at: new Date(Date.now() - 2 * 60 * 1000).toISOString()
                },
                { 
                    id: 2, 
                    user: 'Jane Smith', 
                    product: 'Token PLN 100K', 
                    amount: 102500, 
                    status: 'pending', 
                    created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString()
                },
                { 
                    id: 3, 
                    user: 'Bob Johnson', 
                    product: 'Paket Data XL 5GB', 
                    amount: 65000, 
                    status: 'success', 
                    created_at: new Date(Date.now() - 10 * 60 * 1000).toISOString()
                },
                { 
                    id: 4, 
                    user: 'Alice Brown', 
                    product: 'Pulsa Indosat 25K', 
                    amount: 26500, 
                    status: 'failed', 
                    created_at: new Date(Date.now() - 15 * 60 * 1000).toISOString()
                },
                { 
                    id: 5, 
                    user: 'Charlie Wilson', 
                    product: 'BPJS Kesehatan', 
                    amount: 150000, 
                    status: 'success', 
                    created_at: new Date(Date.now() - 20 * 60 * 1000).toISOString()
                }
            ];
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

// Initialize charts
async function initCharts() {
    await Promise.all([
        initTransactionChart(),
        initCategoryChart()
    ]);
}

// Initialize transaction chart
async function initTransactionChart() {
    const canvas = document.getElementById('transactionChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart if it exists
    if (transactionChart) {
        transactionChart.destroy();
    }
    
    try {
        // Try to load real data
        const response = await apiRequest('/analytics/transactions/weekly');
        let chartData = {
            labels: ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'],
            data: [120, 190, 300, 500, 200, 300, 450]
        };
        
        if (response && response.ok) {
            const data = await response.json();
            if (data.data) {
                chartData = data.data;
            }
        }
        
        transactionChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Transaksi',
                    data: chartData.data,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#3b82f6',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#3b82f6',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#6b7280',
                            font: {
                                size: 12
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#6b7280',
                            font: {
                                size: 12
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
        
    } catch (error) {
        console.error('Error initializing transaction chart:', error);
    }
}

// Initialize category chart
async function initCategoryChart() {
    const canvas = document.getElementById('categoryChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart if it exists
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    try {
        // Try to load real data
        const response = await apiRequest('/analytics/products/categories');
        let chartData = {
            labels: ['Pulsa', 'Token PLN', 'Paket Data', 'BPJS', 'Lainnya'],
            data: [35, 25, 20, 15, 5]
        };
        
        if (response && response.ok) {
            const data = await response.json();
            if (data.data) {
                chartData = data.data;
            }
        }
        
        categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: chartData.labels,
                datasets: [{
                    data: chartData.data,
                    backgroundColor: [
                        '#3b82f6',
                        '#10b981',
                        '#8b5cf6',
                        '#f59e0b',
                        '#ef4444'
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12
                            },
                            color: '#6b7280'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#3b82f6',
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${percentage}%`;
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
        
    } catch (error) {
        console.error('Error initializing category chart:', error);
    }
}

// Refresh dashboard data
async function refreshDashboard() {
    showLoading(true);
    try {
        await initDashboard();
        showToast('Dashboard berhasil diperbarui', 'success', 3000);
    } catch (error) {
        showToast('Gagal memperbarui dashboard', 'error');
    } finally {
        showLoading(false);
    }
}

// Initialize floating action button
function initFloatingActionButton() {
    const fab = document.querySelector('.floating-action-button');
    if (fab) {
        fab.addEventListener('click', () => {
            // Show quick actions menu
            showQuickActionsMenu();
        });
    }
}

// Show quick actions menu
function showQuickActionsMenu() {
    const menu = document.createElement('div');
    menu.className = 'fixed bottom-20 right-6 bg-white rounded-lg shadow-xl p-4 z-50 animate-fade-in';
    menu.innerHTML = `
        <div class="space-y-2">
            <a href="dashboard_products.html" class="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                <i class="fas fa-plus mr-3 text-blue-600"></i>
                Tambah Produk
            </a>
            <a href="dashboard_discord.html" class="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                <i class="fab fa-discord mr-3 text-purple-600"></i>
                Kelola Discord
            </a>
            <a href="dashboard_users.html" class="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                <i class="fas fa-user-plus mr-3 text-green-600"></i>
                Tambah User
            </a>
            <button onclick="refreshDashboard()" class="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg w-full text-left">
                <i class="fas fa-sync-alt mr-3 text-orange-600"></i>
                Refresh Data
            </button>
        </div>
    `;
    
    document.body.appendChild(menu);
    
    // Remove menu when clicking outside
    setTimeout(() => {
        document.addEventListener('click', function removeMenu(e) {
            if (!menu.contains(e.target) && !e.target.closest('.floating-action-button')) {
                menu.remove();
                document.removeEventListener('click', removeMenu);
            }
        });
    }, 100);
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    initFloatingActionButton();
    
    // Auto-refresh every 5 minutes
    setInterval(refreshDashboard, 5 * 60 * 1000);
});

// Cleanup charts when page unloads
window.addEventListener('beforeunload', () => {
    if (transactionChart) {
        transactionChart.destroy();
    }
    if (categoryChart) {
        categoryChart.destroy();
    }
});
