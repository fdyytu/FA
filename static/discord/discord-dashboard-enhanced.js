/**
 * Enhanced Discord Bot Dashboard JavaScript
 * Mengintegrasikan semua fitur Discord yang sudah diimplementasikan
 */

// API Base URL
const API_BASE = '/api/v1';

// Global state
let refreshInterval;
let isLoading = false;
let websocket = null;
let currentTab = 'overview';

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Enhanced Discord Bot Dashboard initialized');
    refreshData();
    loadFeatures();
    startAutoRefresh();
    initializeWebSocket();
});

/**
 * Tab Management
 */
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active', 'border-indigo-500', 'text-indigo-600');
        btn.classList.add('border-transparent', 'text-gray-500');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.remove('hidden');
    
    // Add active class to selected button
    event.target.classList.add('active', 'border-indigo-500', 'text-indigo-600');
    event.target.classList.remove('border-transparent', 'text-gray-500');
    
    currentTab = tabName;
    
    // Load tab-specific content
    loadTabContent(tabName);
}

/**
 * Load content for specific tab
 */
async function loadTabContent(tabName) {
    try {
        switch(tabName) {
            case 'monitoring':
                await loadMonitoringData();
                break;
            case 'commands':
                await loadCommandLogs();
                break;
            case 'bulk':
                await loadBulkOperations();
                break;
            case 'security':
                await loadSecurityData();
                break;
        }
    } catch (error) {
        console.error(`Error loading ${tabName} content:`, error);
        showToast(`Gagal memuat data ${tabName}`, 'error');
    }
}

/**
 * Refresh dashboard overview data
 */
async function refreshData() {
    if (isLoading) return;
    
    try {
        isLoading = true;
        
        // Load dashboard overview
        const response = await fetch(`${API_BASE}/discord/dashboard/overview`);
        const data = await response.json();
        
        if (data.success) {
            updateOverviewUI(data.data);
            updateLastUpdateTime();
            showToast('Data berhasil dimuat', 'success');
        } else {
            throw new Error(data.message || 'Gagal memuat data');
        }
        
    } catch (error) {
        console.error('Error refreshing data:', error);
        showToast('Gagal memuat data: ' + error.message, 'error');
        updateUIError();
    } finally {
        isLoading = false;
    }
}

/**
 * Load available features
 */
async function loadFeatures() {
    try {
        const response = await fetch(`${API_BASE}/discord/dashboard/features`);
        const data = await response.json();
        
        if (data.success) {
            updateFeaturesUI(data.data);
        }
    } catch (error) {
        console.error('Error loading features:', error);
    }
}

/**
 * Update overview UI with data
 */
function updateOverviewUI(data) {
    // Update bot status
    const botStatus = data.bot_status;
    document.getElementById('botStatus').textContent = botStatus.status || 'Unknown';
    
    const statusBadge = document.getElementById('botStatusBadge');
    statusBadge.className = 'ml-2 px-2 py-1 text-xs font-medium rounded-full border';
    
    if (botStatus.is_healthy) {
        statusBadge.classList.add('status-online');
        statusBadge.innerHTML = '<i class="fas fa-circle mr-1"></i>Online';
    } else {
        statusBadge.classList.add('status-offline');
        statusBadge.innerHTML = '<i class="fas fa-circle mr-1"></i>Offline';
    }
    
    // Update metrics
    document.getElementById('commandsToday').textContent = data.recent_commands?.length || 0;
    document.getElementById('systemHealth').textContent = botStatus.is_healthy ? 'Good' : 'Poor';
}

/**
 * Update features UI
 */
function updateFeaturesUI(data) {
    document.getElementById('activeFeatures').textContent = 
        `${data.active_features}/${data.total_features}`;
}

/**
 * Load monitoring data
 */
async function loadMonitoringData() {
    try {
        const response = await fetch(`${API_BASE}/discord/monitoring/health`);
        const data = await response.json();
        
        const content = document.getElementById('monitoring-content');
        content.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h3 class="font-semibold mb-2">System Metrics</h3>
                    <div class="space-y-2">
                        <div class="flex justify-between">
                            <span>CPU Usage:</span>
                            <span class="font-mono">${data.data?.cpu_usage || 'N/A'}%</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Memory Usage:</span>
                            <span class="font-mono">${data.data?.memory_usage || 'N/A'}%</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Uptime:</span>
                            <span class="font-mono">${data.data?.uptime || 'N/A'}</span>
                        </div>
                    </div>
                </div>
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h3 class="font-semibold mb-2">Bot Health</h3>
                    <div class="space-y-2">
                        <div class="flex justify-between">
                            <span>Status:</span>
                            <span class="font-mono ${data.data?.is_healthy ? 'text-green-600' : 'text-red-600'}">
                                ${data.data?.is_healthy ? 'Healthy' : 'Unhealthy'}
                            </span>
                        </div>
                        <div class="flex justify-between">
                            <span>Latency:</span>
                            <span class="font-mono">${data.data?.latency || 'N/A'}ms</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        document.getElementById('monitoring-content').innerHTML = 
            '<p class="text-red-600">Error loading monitoring data</p>';
    }
}

/**
 * Load command logs
 */
async function loadCommandLogs() {
    try {
        const response = await fetch(`${API_BASE}/discord/logs/recent?limit=20`);
        const data = await response.json();
        
        const content = document.getElementById('commands-content');
        if (data.success && data.data?.length > 0) {
            const logsHtml = data.data.map(log => `
                <div class="border-b border-gray-200 py-3">
                    <div class="flex justify-between items-start">
                        <div>
                            <span class="font-mono text-sm bg-gray-100 px-2 py-1 rounded">${log.command}</span>
                            <span class="text-gray-600 ml-2">by ${log.user_id}</span>
                        </div>
                        <div class="text-sm text-gray-500">
                            ${new Date(log.timestamp).toLocaleString('id-ID')}
                        </div>
                    </div>
                    <div class="mt-1 text-sm text-gray-600">
                        Channel: ${log.channel_id} | 
                        Status: <span class="${log.success ? 'text-green-600' : 'text-red-600'}">
                            ${log.success ? 'Success' : 'Failed'}
                        </span>
                    </div>
                </div>
            `).join('');
            
            content.innerHTML = `
                <div class="mb-4">
                    <h3 class="font-semibold">Recent Commands</h3>
                </div>
                <div class="max-h-96 overflow-y-auto">
                    ${logsHtml}
                </div>
            `;
        } else {
            content.innerHTML = '<p class="text-gray-600">No command logs available</p>';
        }
    } catch (error) {
        document.getElementById('commands-content').innerHTML = 
            '<p class="text-red-600">Error loading command logs</p>';
    }
}

/**
 * Load bulk operations
 */
async function loadBulkOperations() {
    const content = document.getElementById('bulk-content');
    content.innerHTML = `
        <div class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h3 class="font-semibold mb-4">Bulk Bot Operations</h3>
                    <div class="space-y-3">
                        <button onclick="bulkStartBots()" class="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                            <i class="fas fa-play mr-2"></i>Start All Bots
                        </button>
                        <button onclick="bulkStopBots()" class="w-full bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
                            <i class="fas fa-stop mr-2"></i>Stop All Bots
                        </button>
                        <button onclick="bulkRestartBots()" class="w-full bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700">
                            <i class="fas fa-redo mr-2"></i>Restart All Bots
                        </button>
                    </div>
                </div>
                
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h3 class="font-semibold mb-4">Bulk Messaging</h3>
                    <div class="space-y-3">
                        <textarea id="bulkMessage" placeholder="Enter message to send to all bots..." 
                                  class="w-full p-2 border rounded-md" rows="3"></textarea>
                        <button onclick="sendBulkMessage()" class="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                            <i class="fas fa-paper-plane mr-2"></i>Send to All Bots
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="bg-gray-50 p-4 rounded-lg">
                <h3 class="font-semibold mb-4">Stock Display Management</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <button onclick="toggleAllStockDisplay(true)" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                        <i class="fas fa-eye mr-2"></i>Show All Stock
                    </button>
                    <button onclick="toggleAllStockDisplay(false)" class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
                        <i class="fas fa-eye-slash mr-2"></i>Hide All Stock
                    </button>
                    <button onclick="refreshStockDisplay()" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                        <i class="fas fa-sync mr-2"></i>Refresh Stock
                    </button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Load security data
 */
async function loadSecurityData() {
    try {
        const response = await fetch(`${API_BASE}/discord/audit/logs?limit=20`);
        const data = await response.json();
        
        const content = document.getElementById('security-content');
        content.innerHTML = `
            <div class="space-y-6">
                <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <h3 class="font-semibold text-yellow-800 mb-2">Security Status</h3>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                            <span class="text-yellow-700">Authentication:</span>
                            <span class="font-mono text-green-600 ml-2">Active</span>
                        </div>
                        <div>
                            <span class="text-yellow-700">Rate Limiting:</span>
                            <span class="font-mono text-green-600 ml-2">Active</span>
                        </div>
                        <div>
                            <span class="text-yellow-700">Audit Logging:</span>
                            <span class="font-mono text-green-600 ml-2">Active</span>
                        </div>
                    </div>
                </div>
                
                <div>
                    <h3 class="font-semibold mb-4">Recent Audit Logs</h3>
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <p class="text-gray-600">Audit logs will be displayed here when available</p>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        document.getElementById('security-content').innerHTML = 
            '<p class="text-red-600">Error loading security data</p>';
    }
}

/**
 * Bulk Operations Functions
 */
async function bulkStartBots() {
    try {
        const response = await fetch(`${API_BASE}/discord/bulk/start`, { method: 'POST' });
        const data = await response.json();
        showToast(data.success ? 'Bulk start initiated' : 'Failed to start bots', 
                 data.success ? 'success' : 'error');
    } catch (error) {
        showToast('Error starting bots: ' + error.message, 'error');
    }
}

async function bulkStopBots() {
    try {
        const response = await fetch(`${API_BASE}/discord/bulk/stop`, { method: 'POST' });
        const data = await response.json();
        showToast(data.success ? 'Bulk stop initiated' : 'Failed to stop bots', 
                 data.success ? 'success' : 'error');
    } catch (error) {
        showToast('Error stopping bots: ' + error.message, 'error');
    }
}

async function sendBulkMessage() {
    const message = document.getElementById('bulkMessage').value;
    if (!message.trim()) {
        showToast('Please enter a message', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/discord/bulk/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();
        showToast(data.success ? 'Bulk message sent' : 'Failed to send message', 
                 data.success ? 'success' : 'error');
        if (data.success) {
            document.getElementById('bulkMessage').value = '';
        }
    } catch (error) {
        showToast('Error sending message: ' + error.message, 'error');
    }
}

/**
 * Stock Management Functions
 */
async function toggleStockDisplay() {
    try {
        const response = await fetch(`${API_BASE}/discord/stock/toggle`, { method: 'POST' });
        const data = await response.json();
        showToast(data.success ? 'Stock display toggled' : 'Failed to toggle stock display', 
                 data.success ? 'success' : 'error');
    } catch (error) {
        showToast('Error toggling stock display: ' + error.message, 'error');
    }
}

async function toggleAllStockDisplay(show) {
    try {
        const response = await fetch(`${API_BASE}/discord/stock/bulk/${show ? 'show' : 'hide'}`, 
                                   { method: 'POST' });
        const data = await response.json();
        showToast(data.success ? `Stock display ${show ? 'shown' : 'hidden'} for all` : 'Operation failed', 
                 data.success ? 'success' : 'error');
    } catch (error) {
        showToast('Error updating stock display: ' + error.message, 'error');
    }
}

/**
 * WebSocket Functions
 */
function initializeWebSocket() {
    try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/discord`;
        
        websocket = new WebSocket(wsUrl);
        
        websocket.onopen = function() {
            console.log('WebSocket connected');
            showToast('Real-time updates connected', 'success');
        };
        
        websocket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
        
        websocket.onclose = function() {
            console.log('WebSocket disconnected');
            setTimeout(initializeWebSocket, 5000); // Reconnect after 5 seconds
        };
        
        websocket.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
    } catch (error) {
        console.error('Error initializing WebSocket:', error);
    }
}

function handleWebSocketMessage(data) {
    switch(data.type) {
        case 'bot_status_update':
            updateBotStatus(data.data);
            break;
        case 'command_log':
            if (currentTab === 'commands') {
                loadCommandLogs();
            }
            break;
        case 'system_alert':
            showToast(data.message, 'warning');
            break;
    }
}

function connectWebSocket() {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        showToast('WebSocket already connected', 'info');
    } else {
        initializeWebSocket();
    }
}

/**
 * Utility Functions
 */
function updateUIError() {
    document.getElementById('botStatus').textContent = 'Error';
    const statusBadge = document.getElementById('botStatusBadge');
    statusBadge.className = 'ml-2 px-2 py-1 text-xs font-medium rounded-full border status-offline';
    statusBadge.innerHTML = '<i class="fas fa-exclamation-triangle mr-1"></i>Error';
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    
    let bgColor, textColor, icon;
    switch (type) {
        case 'success':
            bgColor = 'bg-green-500'; textColor = 'text-white'; icon = 'fas fa-check-circle';
            break;
        case 'error':
            bgColor = 'bg-red-500'; textColor = 'text-white'; icon = 'fas fa-exclamation-circle';
            break;
        case 'warning':
            bgColor = 'bg-yellow-500'; textColor = 'text-white'; icon = 'fas fa-exclamation-triangle';
            break;
        default:
            bgColor = 'bg-blue-500'; textColor = 'text-white'; icon = 'fas fa-info-circle';
    }
    
    toast.className = `${bgColor} ${textColor} px-4 py-3 rounded-lg shadow-lg flex items-center space-x-2 transform transition-all duration-300 translate-x-full`;
    toast.innerHTML = `
        <i class="${icon}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="ml-2 text-white hover:text-gray-200">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    toastContainer.appendChild(toast);
    setTimeout(() => toast.classList.remove('translate-x-full'), 100);
    setTimeout(() => {
        if (toast.parentElement) {
            toast.classList.add('translate-x-full');
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

function updateLastUpdateTime() {
    const now = new Date();
    document.getElementById('lastUpdateTime').textContent = now.toLocaleTimeString('id-ID');
}

function startAutoRefresh() {
    refreshInterval = setInterval(refreshData, 30000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Handle page visibility change
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
        refreshData();
    }
});
