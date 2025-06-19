const API_BASE_URL = '/api/v1/admin';
let transactionChart, categoryChart;

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('adminToken');
    if (!token) {
        window.location.href = 'login_android.html';
        return false;
    }
    return token;
}

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
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Gagal memuat data dashboard');
    } finally {
        showLoading(false);
    }
}

// Load dashboard statistics
async function loadDashboardStats() {
    const token = localStorage.getItem('adminToken');
    
    try {
        const response = await fetch(`${API_BASE_URL}/dashboard/stats`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateStatsCards(data);
        } else {
            // Use mock data if API fails
            updateStatsCards({
                total_users: 1250,
                total_transactions: 3420,
                total_products: 156,
                total_revenue: 45000000
            });
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        // Use mock data
        updateStatsCards({
            total_users: 1250,
            total_transactions: 3420,
            total_products: 156,
            total_revenue: 45000000
        });
    }
}

// Update stats cards
function updateStatsCards(stats) {
    document.getElementById('totalUsers').textContent = stats.total_users?.toLocaleString() || '1,250';
    document.getElementById('totalTransactions').textContent = stats.total_transactions?.toLocaleString() || '3,420';
    document.getElementById('totalProducts').textContent = stats.total_products?.toLocaleString() || '156';
    
    const revenue = stats.total_revenue || 45000000;
    document.getElementById('totalRevenue').textContent = 'Rp ' + (revenue / 1000000).toFixed(1) + 'M';
}

// Load recent transactions
async function loadRecentTransactions() {
    const container = document.getElementById('recentTransactions');
    
    // Mock data for demonstration
    const transactions = [
        { id: 1, user: 'John Doe', product: 'Pulsa Telkomsel 50K', amount: 52000, status: 'success', time: '2 menit lalu' },
        { id: 2, user: 'Jane Smith', product: 'Token PLN 100K', amount: 102500, status: 'pending', time: '5 menit lalu' },
        { id: 3, user: 'Bob Johnson', product: 'Paket Data XL 5GB', amount: 65000, status: 'success', time: '10 menit lalu' },
        { id: 4, user: 'Alice Brown', product: 'Pulsa Indosat 25K', amount: 26500, status: 'failed', time: '15 menit lalu' },
        { id: 5, user: 'Charlie Wilson', product: 'BPJS Kesehatan', amount: 150000, status: 'success', time: '20 menit lalu' }
    ];
    
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
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusClass(tx.status)}">
                        ${getStatusText(tx.status)}
                    </span>
                </div>
            </div>
        </div>
    `).join('');
}

// Get status class for transaction
function getStatusClass(status) {
    switch (status) {
        case 'success': return 'bg-green-100 text-green-800';
        case 'pending': return 'bg-yellow-100 text-yellow-800';
        case 'failed': return 'bg-red-100 text-red-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}

// Get status text
function getStatusText(status) {
    switch (status) {
        case 'success': return 'Berhasil';
        case 'pending': return 'Pending';
        case 'failed': return 'Gagal';
        default: return 'Unknown';
    }
}

// Initialize charts
function initCharts() {
    initTransactionChart();
    initCategoryChart();
}

// Initialize transaction chart
function initTransactionChart() {
    const ctx = document.getElementById('transactionChart').getContext('2d');
    
    transactionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'],
            datasets: [{
                label: 'Transaksi',
                data: [120, 190, 300, 500, 200, 300, 450],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Initialize category chart
function initCategoryChart() {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Pulsa', 'Token PLN', 'Paket Data', 'BPJS', 'Lainnya'],
            datasets: [{
                data: [35, 25, 20, 15, 5],
                backgroundColor: [
                    '#3b82f6',
                    '#10b981',
                    '#8b5cf6',
                    '#f59e0b',
                    '#ef4444'
                ],
                borderWidth: 0
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
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

// Show/hide loading
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

// Show error message
function showError(message) {
    // You can implement a toast notification here
    console.error(message);
}

// Mobile menu functionality
function initMobileMenu() {
    const openBtn = document.getElementById('openSidebar');
    const closeBtn = document.getElementById('closeSidebar');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobileMenuOverlay');

    openBtn.addEventListener('click', () => {
        sidebar.classList.remove('sidebar-hidden');
        overlay.classList.remove('hidden');
    });

    closeBtn.addEventListener('click', closeMobileMenu);
    overlay.addEventListener('click', closeMobileMenu);

    function closeMobileMenu() {
        sidebar.classList.add('sidebar-hidden');
        overlay.classList.add('hidden');
    }
}

// Navigation functionality
function initNavigation() {
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

// Logout functionality
function initLogout() {
    document.getElementById('logoutBtn').addEventListener('click', async () => {
        const token = localStorage.getItem('adminToken');
        
        try {
            await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        } catch (error) {
            console.error('Logout error:', error);
        }
        
        localStorage.removeItem('adminToken');
        window.location.href = 'login_android.html';
    });
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    initMobileMenu();
    initNavigation();
    initLogout();
});
