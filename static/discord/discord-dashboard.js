/**
 * Discord Bot Dashboard JavaScript
 * Mengelola interaksi dashboard dengan backend API
 */

// API Base URL
const API_BASE = '/api/v1/discord';

// Global state
let refreshInterval;
let isLoading = false;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Discord Bot Dashboard initialized');
    refreshData();
    loadActiveConfig();
    startAutoRefresh();
});

/**
 * Refresh bot data from API
 */
async function refreshData() {
    if (isLoading) return;
    
    try {
        isLoading = true;
        showLoading('Memuat data bot...');
        
        const response = await fetch(`${API_BASE}/bot/status`);
        const data = await response.json();
        
        if (data.success) {
            updateUI(data.data);
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
        hideLoading();
    }
}

/**
 * Update UI with bot status data
 */
function updateUI(statusData) {
    // Update status badge
    const statusElement = document.getElementById('botStatus');
    const statusBadge = document.getElementById('botStatusBadge');
    
    const status = statusData.status || 'unknown';
    const isRunning = statusData.is_running || false;
    
    statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    
    // Update status badge
    statusBadge.className = 'ml-2 px-2 py-1 text-xs font-medium rounded-full border';
    if (status === 'online' && isRunning) {
        statusBadge.classList.add('status-online');
        statusBadge.innerHTML = '<i class="fas fa-circle mr-1"></i>Online';
    } else if (status === 'offline' || !isRunning) {
        statusBadge.classList.add('status-offline');
        statusBadge.innerHTML = '<i class="fas fa-circle mr-1"></i>Offline';
    } else {
        statusBadge.classList.add('status-loading');
        statusBadge.innerHTML = '<i class="fas fa-circle mr-1"></i>Loading';
    }
    
    // Update metrics
    document.getElementById('guildCount').textContent = statusData.guilds || 0;
    document.getElementById('userCount').textContent = statusData.users || 0;
    document.getElementById('latency').textContent = (statusData.latency || 0) + 'ms';
    
    // Update bot information
    document.getElementById('botUser').textContent = statusData.user || 'Tidak tersedia';
    document.getElementById('managerInitialized').textContent = statusData.manager_initialized ? 'Ya' : 'Tidak';
    document.getElementById('tokenConfigured').textContent = statusData.token_configured ? 'Ya' : 'Tidak';
    document.getElementById('commandPrefix').textContent = statusData.environment?.command_prefix || '!';
    
    // Update button states
    updateButtonStates(isRunning);
}

/**
 * Update UI when error occurs
 */
function updateUIError() {
    document.getElementById('botStatus').textContent = 'Error';
    const statusBadge = document.getElementById('botStatusBadge');
    statusBadge.className = 'ml-2 px-2 py-1 text-xs font-medium rounded-full border status-offline';
    statusBadge.innerHTML = '<i class="fas fa-exclamation-triangle mr-1"></i>Error';
    
    // Reset metrics
    document.getElementById('guildCount').textContent = '-';
    document.getElementById('userCount').textContent = '-';
    document.getElementById('latency').textContent = '-';
    
    // Reset bot information
    document.getElementById('botUser').textContent = '-';
    document.getElementById('managerInitialized').textContent = '-';
    document.getElementById('tokenConfigured').textContent = '-';
    document.getElementById('commandPrefix').textContent = '-';
    
    // Disable all buttons
    updateButtonStates(false);
}

/**
 * Update button states based on bot status
 */
function updateButtonStates(isRunning) {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const restartBtn = document.getElementById('restartBtn');
    const sendBtn = document.getElementById('sendBtn');
    
    // Check if elements exist before updating
    if (startBtn) startBtn.disabled = isRunning;
    if (stopBtn) stopBtn.disabled = !isRunning;
    if (restartBtn) restartBtn.disabled = false; // Always allow restart
    if (sendBtn) sendBtn.disabled = !isRunning;
}

/**
 * Start Discord bot
 */
async function startBot() {
    try {
        showLoading('Menjalankan bot...');
        
        const response = await fetch(`${API_BASE}/bot/start`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Bot berhasil dijalankan', 'success');
            setTimeout(refreshData, 2000); // Refresh after 2 seconds
        } else {
            throw new Error(data.detail || data.message || 'Gagal menjalankan bot');
        }
        
    } catch (error) {
        console.error('Error starting bot:', error);
        showToast('Gagal menjalankan bot: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Stop Discord bot
 */
async function stopBot() {
    try {
        showLoading('Menghentikan bot...');
        
        const response = await fetch(`${API_BASE}/bot/stop`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Bot berhasil dihentikan', 'success');
            setTimeout(refreshData, 2000); // Refresh after 2 seconds
        } else {
            throw new Error(data.detail || data.message || 'Gagal menghentikan bot');
        }
        
    } catch (error) {
        console.error('Error stopping bot:', error);
        showToast('Gagal menghentikan bot: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Restart Discord bot
 */
async function restartBot() {
    try {
        showLoading('Merestart bot...');
        
        const response = await fetch(`${API_BASE}/bot/restart`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Bot berhasil direstart', 'success');
            setTimeout(refreshData, 3000); // Refresh after 3 seconds
        } else {
            throw new Error(data.detail || data.message || 'Gagal merestart bot');
        }
        
    } catch (error) {
        console.error('Error restarting bot:', error);
        showToast('Gagal merestart bot: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Test Discord configuration
 */
async function testDiscordConfig() {
    const token = document.getElementById('discordToken').value;
    const guildId = document.getElementById('guildId').value;
    
    if (!token) {
        showToast('Discord token harus diisi', 'warning');
        return;
    }
    
    try {
        showLoading('Testing Discord configuration...');
        
        const response = await fetch(`${API_BASE}/discord/config/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token: token,
                guild_id: guildId || null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showConfigStatus('success', 'Token valid dan bot berhasil terhubung!');
            showToast('Konfigurasi Discord valid', 'success');
        } else {
            showConfigStatus('error', data.message || 'Token tidak valid');
            showToast('Konfigurasi Discord tidak valid: ' + (data.message || 'Unknown error'), 'error');
        }
        
    } catch (error) {
        console.error('Error testing Discord config:', error);
        showConfigStatus('error', 'Error testing configuration');
        showToast('Error testing configuration: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Save Discord configuration
 */
async function saveDiscordConfig() {
    const name = document.getElementById('configName').value;
    const token = document.getElementById('discordToken').value;
    const guildId = document.getElementById('guildId').value;
    const commandPrefix = document.getElementById('commandPrefix').value;
    
    if (!name || !token) {
        showToast('Nama konfigurasi dan token harus diisi', 'warning');
        return;
    }
    
    try {
        showLoading('Menyimpan konfigurasi...');
        
        const response = await fetch(`${API_BASE}/discord/config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                token: token,
                guild_id: guildId || null,
                command_prefix: commandPrefix || '!',
                is_active: true
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showConfigStatus('success', 'Konfigurasi berhasil disimpan!');
            showToast('Konfigurasi Discord berhasil disimpan', 'success');
            
            // Clear sensitive data
            document.getElementById('discordToken').value = '';
            
            // Refresh bot status
            setTimeout(refreshData, 1000);
        } else {
            throw new Error(data.detail || data.message || 'Gagal menyimpan konfigurasi');
        }
        
    } catch (error) {
        console.error('Error saving Discord config:', error);
        showConfigStatus('error', 'Gagal menyimpan konfigurasi');
        showToast('Gagal menyimpan konfigurasi: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Load active Discord configuration
 */
async function loadActiveConfig() {
    try {
        const response = await fetch(`${API_BASE}/discord/config/active`);
        const data = await response.json();
        
        if (data.success && data.data) {
            const config = data.data;
            document.getElementById('configName').value = config.name || '';
            document.getElementById('guildId').value = config.guild_id || '';
            document.getElementById('commandPrefix').value = config.command_prefix || '!';
            
            showConfigStatus('info', `Konfigurasi aktif: ${config.name}`);
        }
        
    } catch (error) {
        console.error('Error loading active config:', error);
    }
}

/**
 * Show configuration status
 */
function showConfigStatus(type, message) {
    const statusDiv = document.getElementById('configStatus');
    const statusIcon = document.getElementById('configStatusIcon');
    const statusText = document.getElementById('configStatusText');
    
    // Reset classes
    statusDiv.className = 'rounded-md p-4';
    statusIcon.className = 'fas';
    
    switch (type) {
        case 'success':
            statusDiv.classList.add('bg-green-50');
            statusIcon.classList.add('fa-check-circle', 'text-green-400');
            statusText.className = 'text-sm font-medium text-green-800';
            break;
        case 'error':
            statusDiv.classList.add('bg-red-50');
            statusIcon.classList.add('fa-exclamation-circle', 'text-red-400');
            statusText.className = 'text-sm font-medium text-red-800';
            break;
        case 'info':
            statusDiv.classList.add('bg-blue-50');
            statusIcon.classList.add('fa-info-circle', 'text-blue-400');
            statusText.className = 'text-sm font-medium text-blue-800';
            break;
        default:
            statusDiv.classList.add('bg-gray-50');
            statusIcon.classList.add('fa-info-circle', 'text-gray-400');
            statusText.className = 'text-sm font-medium text-gray-800';
    }
    
    statusText.textContent = message;
    statusDiv.classList.remove('hidden');
}

/**
 * Start Discord bot
 */
async function startBot() {
    try {
        showLoading('Memulai bot...');
        
        const response = await fetch(`${API_BASE}/bot/start`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Bot berhasil dimulai', 'success');
            setTimeout(refreshData, 2000); // Refresh after 2 seconds
        } else {
            throw new Error(data.detail || data.message || 'Gagal memulai bot');
        }
        
    } catch (error) {
        console.error('Error starting bot:', error);
        showToast('Gagal memulai bot: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Stop Discord bot
 */
async function stopBot() {
    try {
        showLoading('Menghentikan bot...');
        
        const response = await fetch(`${API_BASE}/bot/stop`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Bot berhasil dihentikan', 'success');
            setTimeout(refreshData, 2000); // Refresh after 2 seconds
        } else {
            throw new Error(data.detail || data.message || 'Gagal menghentikan bot');
        }
        
    } catch (error) {
        console.error('Error stopping bot:', error);
        showToast('Gagal menghentikan bot: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Restart Discord bot
 */
async function restartBot() {
    try {
        showLoading('Merestart bot...');
        
        const response = await fetch(`${API_BASE}/bot/restart`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Bot berhasil direstart', 'success');
            setTimeout(refreshData, 3000); // Refresh after 3 seconds
        } else {
            throw new Error(data.detail || data.message || 'Gagal merestart bot');
        }
        
    } catch (error) {
        console.error('Error restarting bot:', error);
        showToast('Gagal merestart bot: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Test Discord configuration
 */
async function testDiscordConfig() {
    const token = document.getElementById('discordToken').value;
    const guildId = document.getElementById('guildId').value;
    
    if (!token) {
        showToast('Discord Bot Token harus diisi', 'warning');
        return;
    }
    
    try {
        showLoading('Testing koneksi Discord...');
        
        const response = await fetch(`${API_BASE}/config/test-token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token: token,
                guild_id: guildId || null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showConfigStatus('Token valid dan bot berhasil terhubung!', 'success');
            showToast('Koneksi Discord berhasil!', 'success');
        } else {
            throw new Error(data.detail || data.message || 'Token tidak valid');
        }
        
    } catch (error) {
        console.error('Error testing Discord config:', error);
        showConfigStatus('Error: ' + error.message, 'error');
        showToast('Gagal test koneksi: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Save Discord configuration
 */
async function saveDiscordConfig() {
    const configName = document.getElementById('configName').value;
    const token = document.getElementById('discordToken').value;
    const guildId = document.getElementById('guildId').value;
    const commandPrefix = document.getElementById('commandPrefix').value;
    
    if (!configName || !token) {
        showToast('Nama konfigurasi dan Discord Bot Token harus diisi', 'warning');
        return;
    }
    
    try {
        showLoading('Menyimpan konfigurasi...');
        
        const response = await fetch(`${API_BASE}/config/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: configName,
                token: token,
                guild_id: guildId || null,
                command_prefix: commandPrefix || '!',
                is_active: true
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showConfigStatus('Konfigurasi berhasil disimpan!', 'success');
            showToast('Konfigurasi Discord berhasil disimpan!', 'success');
            
            // Clear sensitive data
            document.getElementById('discordToken').value = '';
            
            // Refresh data to show new config
            setTimeout(refreshData, 1000);
        } else {
            throw new Error(data.detail || data.message || 'Gagal menyimpan konfigurasi');
        }
        
    } catch (error) {
        console.error('Error saving Discord config:', error);
        showConfigStatus('Error: ' + error.message, 'error');
        showToast('Gagal menyimpan konfigurasi: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Send message to Discord channel
 */
async function sendMessage() {
    const channelId = document.getElementById('channelId').value;
    const messageText = document.getElementById('messageText').value;
    
    if (!channelId || !messageText) {
        showToast('Channel ID dan pesan harus diisi', 'warning');
        return;
    }
    
    try {
        showLoading('Mengirim pesan...');
        
        const response = await fetch(`${API_BASE}/bot/send-message?channel_id=${channelId}&message=${encodeURIComponent(messageText)}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Pesan berhasil dikirim', 'success');
            document.getElementById('messageText').value = ''; // Clear message
        } else {
            throw new Error(data.detail || data.message || 'Gagal mengirim pesan');
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        showToast('Gagal mengirim pesan: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Show loading overlay
 */
function showLoading(text = 'Loading...') {
    document.getElementById('loadingText').textContent = text;
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    
    let bgColor, textColor, icon;
    switch (type) {
        case 'success':
            bgColor = 'bg-green-500';
            textColor = 'text-white';
            icon = 'fas fa-check-circle';
            break;
        case 'error':
            bgColor = 'bg-red-500';
            textColor = 'text-white';
            icon = 'fas fa-exclamation-circle';
            break;
        case 'warning':
            bgColor = 'bg-yellow-500';
            textColor = 'text-white';
            icon = 'fas fa-exclamation-triangle';
            break;
        default:
            bgColor = 'bg-blue-500';
            textColor = 'text-white';
            icon = 'fas fa-info-circle';
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
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 300);
        }
    }, 5000);
}

/**
 * Update last update time
 */
function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('id-ID');
    document.getElementById('lastUpdateTime').textContent = timeString;
}

/**
 * Start auto refresh
 */
function startAutoRefresh() {
    // Refresh every 30 seconds
    refreshInterval = setInterval(refreshData, 30000);
}

/**
 * Stop auto refresh
 */
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Handle page visibility change to pause/resume auto refresh
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
        refreshData(); // Refresh immediately when page becomes visible
    }
});
