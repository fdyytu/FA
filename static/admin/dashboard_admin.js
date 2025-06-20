// Dashboard Admin JavaScript
// API Configuration
const API_BASE_URL = '/api/v1/admin';

// Global variables
let revenueChart = null;
let transactionChart = null;
let dashboardData = {};

// DOM Elements
const sidebar = document.getElementById('sidebar');
const mobileMenuOverlay = document.getElementById('mobileMenuOverlay');
const openSidebarBtn = document.getElementById('openSidebar');
const closeSidebarBtn = document.getElementById('closeSidebar');
const logoutBtn = document.getElementById('logoutBtn');
const profileBtn = document.getElementById('profileBtn');
const notificationBtn = document.getElementById('notificationBtn');
const notificationModal = document.getElementById('notificationModal');
const closeNotificationModal = document.getElementById('closeNotificationModal');
const fabBtn = document.getElementById('fabBtn');
const loadingOverlay = document.getElementById('loadingOverlay');

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    loadDashboardData();
    setupCharts();
    startRealTimeUpdates();
});

function initializeDashboard() {
    // Check authentication
    const token = localStorage.getItem('adminToken');
    if (!token) {
        window.location.href = '../admin_login.html';
        return;
    }

    // Load admin data
    const adminData = JSON.parse(localStorage.getItem('adminData') || '{}');
    if (adminData.username) {
        document.getElementById('adminName').textContent = adminData.username;
        document.getElementById('welcomeAdminName').textContent = adminData.username;
    }
}

function setupEventListeners() {
    // Sidebar controls
    openSidebarBtn?.addEventListener('click', openSidebar);
    closeSidebarBtn?.addEventListener('click', closeSidebar);
    mobileMenuOverlay?.addEventListener('click', closeSidebar);

    // Logout
    logoutBtn?.addEventListener('click', handleLogout);

    // Profile
    profileBtn?.addEventListener('click', showProfile);

    // Notifications
    notificationBtn?.addEventListener('click', showNotifications);
    closeNotificationModal?.addEventListener('click', hideNotifications);

    // FAB
    fabBtn?.addEventListener('click', showQuickActions);

    // Chart period changes
    document.getElementById('revenueChartPeriod')?.addEventListener('change', updateRevenueChart);
    document.getElementById('transactionChartPeriod')?.addEventListener('change', updateTransactionChart);

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);

    // Window resize
    window.addEventListener('resize', handleWindowResize);
}

function openSidebar() {
    sidebar?.classList.remove('sidebar-hidden');
    mobileMenuOverlay?.classList.remove('hidden');
}

function closeSidebar() {
    sidebar?.classList.add('sidebar-hidden');
    mobileMenuOverlay?.classList.add('hidden');
}

function handleLogout() {
    if (confirm('Apakah Anda yakin ingin logout?')) {
        // Clear local storage
        localStorage.removeItem('adminToken');
        localStorage.removeItem('adminData');
        
        // Redirect to login
        window.location.href = '../admin_login.html';
    }
}

function showProfile() {
    // TODO: Implement profile modal
    alert('Fitur profil akan segera tersedia');
}

function showNotifications() {
    loadNotifications();
    notificationModal?.classList.remove('hidden');
}

function hideNotifications() {
    notificationModal?.classList.add('hidden');
}

function showQuickActions() {
    // TODO: Implement quick actions menu
    alert('Menu aksi cepat akan segera tersedia');
}

async function loadDashboardData() {
    showLoading(true);
    
    try {
        const token = localStorage.getItem('adminToken');
        
        // Load overview stats
        const overviewResponse = await fetch(`${API_BASE_URL}/dashboard/stats/overview`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (overviewResponse.ok) {
            const overviewData = await overviewResponse.json();
            updateOverviewStats(overviewData.data);
        }

        // Load recent activities
        const activitiesResponse = await fetch(`${API_BASE_URL}/dashboard/recent-activities?limit=5`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (activitiesResponse.ok) {
            const activitiesData = await activitiesResponse.json();
            updateRecentActivities(activitiesData.data);
        }

        // Load system health
        const healthResponse = await fetch(`${API_BASE_URL}/dashboard/system-health`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (healthResponse.ok) {
            const healthData = await healthResponse.json();
            updateSystemHealth(healthData.data);
        }

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showErrorMessage('Gagal memuat data dashboard');
    } finally {
        showLoading(false);
    }
}

function updateOverviewStats(data) {
    // Update stat cards with animation
    animateCounter('totalUsers', data.total_users || 0);
    animateCounter('totalTransactions', data.total_transactions || 0);
    animateCounter('totalRevenue', formatCurrency(data.total_revenue || 0));
    animateCounter('activeProducts', data.active_products || 0);

    // Update growth percentages
    document.getElementById('usersGrowth').textContent = `+${data.users_growth || 0}%`;
    document.getElementById('transactionsGrowth').textContent = `+${data.transactions_growth || 0}%`;
    document.getElementById('revenueGrowth').textContent = `+${data.revenue_growth || 0}%`;
    document.getElementById('productsCount').textContent = data.product_categories || 0;
}

function updateRecentActivities(activities) {
    const container = document.getElementById('recentActivities');
    if (!container) return;

    if (!activities || activities.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-sm">Tidak ada aktivitas terbaru</p>';
        return;
    }

    container.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">${activity.title}</p>
                    <p class="text-xs text-gray-500 mt-1">${activity.description}</p>
                </div>
                <span class="text-xs text-gray-400">${formatTimeAgo(activity.created_at)}</span>
            </div>
        </div>
    `).join('');
}

function updateSystemHealth(health) {
    // This would update system status indicators
    // For now, we'll keep the static implementation
    console.log('System health:', health);
}

function setupCharts() {
    setupRevenueChart();
    setupTransactionChart();
}

function setupRevenueChart() {
    const ctx = document.getElementById('revenueChart');
    if (!ctx) return;

    revenueChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Revenue',
                data: [12000000, 15000000, 18000000, 14000000, 20000000, 25000000],
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
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            }
        }
    });
}

function setupTransactionChart() {
    const ctx = document.getElementById('transactionChart');
    if (!ctx) return;

    transactionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'],
            datasets: [{
                label: 'Transaksi',
                data: [120, 150, 180, 140, 200, 250, 180],
                backgroundColor: '#10b981',
                borderRadius: 8,
                borderSkipped: false,
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
                    beginAtZero: true
                }
            }
        }
    });
}

async function updateRevenueChart() {
    const period = document.getElementById('revenueChartPeriod').value;
    // TODO: Fetch new data based on period
    console.log('Updating revenue chart for period:', period);
}

async function updateTransactionChart() {
    const period = document.getElementById('transactionChartPeriod').value;
    // TODO: Fetch new data based on period
    console.log('Updating transaction chart for period:', period);
}

async function loadNotifications() {
    try {
        const token = localStorage.getItem('adminToken');
        const response = await fetch(`${API_BASE_URL}/dashboard/alerts`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateNotificationList(data.data);
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

function updateNotificationList(notifications) {
    const container = document.getElementById('notificationList');
    if (!container) return;

    if (!notifications || notifications.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-sm text-center py-4">Tidak ada notifikasi</p>';
        return;
    }

    container.innerHTML = notifications.map(notification => `
        <div class="p-3 bg-gray-50 rounded-lg">
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <i class="fas fa-${getNotificationIcon(notification.type)} text-${getNotificationColor(notification.type)}-500"></i>
                </div>
                <div class="ml-3 flex-1">
                    <p class="text-sm font-medium text-gray-900">${notification.title}</p>
                    <p class="text-xs text-gray-500 mt-1">${notification.message}</p>
                    <p class="text-xs text-gray-400 mt-1">${formatTimeAgo(notification.created_at)}</p>
                </div>
            </div>
        </div>
    `).join('');
}

function startRealTimeUpdates() {
    // Update dashboard data every 5 minutes
    setInterval(() => {
        loadDashboardData();
    }, 5 * 60 * 1000);

    // Update time displays every minute
    setInterval(() => {
        updateTimeDisplays();
    }, 60 * 1000);
}

function updateTimeDisplays() {
    // Update any time-based displays
    const timeElements = document.querySelectorAll('[data-time]');
    timeElements.forEach(element => {
        const timestamp = element.getAttribute('data-time');
        element.textContent = formatTimeAgo(timestamp);
    });
}

function handleKeyboardShortcuts(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[placeholder="Cari..."]');
        searchInput?.focus();
    }

    // Escape to close modals
    if (e.key === 'Escape') {
        hideNotifications();
    }
}

function handleWindowResize() {
    // Auto-close sidebar on mobile when window is resized to desktop
    if (window.innerWidth >= 1024) {
        closeSidebar();
    }
}

// Utility functions
function animateCounter(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const startValue = 0;
    const duration = 2000;
    const startTime = performance.now();

    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
        
        if (typeof targetValue === 'string') {
            element.textContent = targetValue;
        } else {
            element.textContent = currentValue.toLocaleString('id-ID');
        }

        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }

    requestAnimationFrame(updateCounter);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatTimeAgo(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInSeconds = Math.floor((now - time) / 1000);

    if (diffInSeconds < 60) {
        return 'Baru saja';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} menit yang lalu`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} jam yang lalu`;
    } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days} hari yang lalu`;
    }
}

function getNotificationIcon(type) {
    const icons = {
        'info': 'info-circle',
        'warning': 'exclamation-triangle',
        'error': 'exclamation-circle',
        'success': 'check-circle'
    };
    return icons[type] || 'bell';
}

function getNotificationColor(type) {
    const colors = {
        'info': 'blue',
        'warning': 'yellow',
        'error': 'red',
        'success': 'green'
    };
    return colors[type] || 'gray';
}

function showLoading(show) {
    if (show) {
        loadingOverlay?.classList.remove('hidden');
    } else {
        loadingOverlay?.classList.add('hidden');
    }
}

function showErrorMessage(message) {
    // TODO: Implement toast notification system
    console.error(message);
    alert(message);
}

function showSuccessMessage(message) {
    // TODO: Implement toast notification system
    console.log(message);
}

// Export functions for global access
window.dashboardAdmin = {
    loadDashboardData,
    updateRevenueChart,
    updateTransactionChart,
    showNotifications,
    hideNotifications
};
