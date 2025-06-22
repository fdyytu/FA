// Dashboard Discord functionality
let bots = [];
let worlds = [];
let recentCommands = [];
let botLogs = [];

// Initialize Discord dashboard
async function initDiscordDashboard() {
    const token = checkAuth();
    if (!token) return;

    showLoading(true);
    
    try {
        await Promise.all([
            loadDiscordStats(),
            loadBots(),
            loadWorlds(),
            loadRecentCommands(),
            loadBotLogs()
        ]);
        
        initEventListeners();
        showToast('Dashboard Discord berhasil dimuat', 'success', 3000);
    } catch (error) {
        console.error('Error loading Discord dashboard:', error);
        showToast('Gagal memuat data Discord', 'error');
    } finally {
        showLoading(false);
    }
}

// Load Discord statistics
async function loadDiscordStats() {
    try {
        const response = await apiRequest('/api/v1/discord/analytics/stats');
        
        if (response && response.ok) {
            const data = await response.json();
            updateDiscordStats(data.data || data);
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
    } catch (error) {
        console.error('Error loading Discord stats:', error);
        showError('Gagal memuat statistik Discord');
        updateDiscordStats({
            total_bots: 0,
            discord_users: 0,
            live_products: 0,
            commands_today: 0
        });
    }
}

// Update Discord statistics cards
function updateDiscordStats(stats) {
    const elements = {
        totalBots: document.getElementById('totalBots'),
        discordUsers: document.getElementById('discordUsers'),
        liveProducts: document.getElementById('liveProducts'),
        commandsToday: document.getElementById('commandsToday')
    };
    
    if (elements.totalBots) {
        elements.totalBots.textContent = formatNumber(stats.total_bots || 0);
    }
    
    if (elements.discordUsers) {
        elements.discordUsers.textContent = formatNumber(stats.discord_users || 0);
    }
    
    if (elements.liveProducts) {
        elements.liveProducts.textContent = formatNumber(stats.live_products || 0);
    }
    
    if (elements.commandsToday) {
        elements.commandsToday.textContent = formatNumber(stats.commands_today || 0);
    }
}

// Load bots
async function loadBots() {
    try {
        const response = await apiRequest('/api/v1/discord/config/bots');
        
        if (response && response.ok) {
            const data = await response.json();
            bots = data.data || [];
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
        
        renderBotsList();
        updateBotOptions();
        
    } catch (error) {
        console.error('Error loading bots:', error);
        bots = [];
        renderBotsList();
        updateBotOptions();
    }
}

// Render bots list
function renderBotsList() {
    const container = document.getElementById('botsList');
    if (!container) return;
    
    container.innerHTML = bots.map(bot => `
        <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <div class="flex items-center">
                <div class="w-12 h-12 bg-gradient-to-r from-purple-500 to-blue-600 rounded-full flex items-center justify-center">
                    <i class="fab fa-discord text-white text-lg"></i>
                </div>
                <div class="ml-4">
                    <h4 class="text-sm font-medium text-gray-900">${bot.name}</h4>
                    <p class="text-xs text-gray-500">Prefix: ${bot.prefix} | Uptime: ${bot.uptime || '0m'}</p>
                    <div class="flex items-center mt-1">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${bot.status === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                            <span class="w-1.5 h-1.5 ${bot.status === 'online' ? 'bg-green-400' : 'bg-red-400'} rounded-full mr-1"></span>
                            ${bot.status === 'online' ? 'Online' : 'Offline'}
                        </span>
                        <span class="ml-2 text-xs text-gray-500">${bot.commands_count || 0} commands</span>
                    </div>
                </div>
            </div>
            <div class="flex space-x-2">
                <button onclick="toggleBot(${bot.id})" class="text-sm ${bot.status === 'online' ? 'text-red-600 hover:text-red-800' : 'text-green-600 hover:text-green-800'}" title="${bot.status === 'online' ? 'Stop Bot' : 'Start Bot'}">
                    <i class="fas ${bot.status === 'online' ? 'fa-stop' : 'fa-play'}"></i>
                </button>
                <button onclick="editBot(${bot.id})" class="text-blue-600 hover:text-blue-800" title="Edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="deleteBot(${bot.id})" class="text-red-600 hover:text-red-800" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// Load worlds
async function loadWorlds() {
    try {
        const response = await apiRequest('/api/v1/discord/config/worlds');
        
        if (response && response.ok) {
            const data = await response.json();
            worlds = data.data || [];
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
        
        renderWorldsList();
        
    } catch (error) {
        console.error('Error loading worlds:', error);
        worlds = [];
        renderWorldsList();
    }
}

// Render worlds list
function renderWorldsList() {
    const container = document.getElementById('worldsList');
    container.innerHTML = worlds.map(world => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div class="flex items-center">
                <div class="ml-3">
                    <h4 class="text-sm font-medium text-gray-900">${world.name}</h4>
                    <p class="text-xs text-gray-500">Owner: ${world.owner}</p>
                    <p class="text-xs text-gray-400">Bot: ${world.bot_name || 'Unknown'}</p>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                ${getStatusBadge(world.is_active ? 'active' : 'inactive')}
                <button onclick="editWorld(${world.id})" class="text-blue-600">
                    <i class="fas fa-edit text-xs"></i>
                </button>
                <button onclick="deleteWorld(${world.id})" class="text-red-600">
                    <i class="fas fa-trash text-xs"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// Load recent commands
async function loadRecentCommands() {
    try {
        const response = await apiRequest('/api/v1/discord/monitoring/commands/recent?limit=5');
        
        if (response && response.ok) {
            const data = await response.json();
            recentCommands = data.data?.commands || [];
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
        
        renderRecentCommands();
        
    } catch (error) {
        console.error('Error loading recent commands:', error);
        recentCommands = [];
        renderRecentCommands();
    }
}

// Render recent commands
function renderRecentCommands() {
    const container = document.getElementById('recentCommands');
    if (!container) return;
    
    container.innerHTML = recentCommands.map(cmd => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div class="flex items-center">
                <div class="w-8 h-8 ${cmd.success ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'} rounded-full flex items-center justify-center">
                    <i class="fas ${cmd.success ? 'fa-check' : 'fa-times'} text-xs"></i>
                </div>
                <div class="ml-3">
                    <p class="text-sm font-medium text-gray-900">${cmd.command_name || cmd.command}</p>
                    <p class="text-xs text-gray-500">by ${cmd.user_id || cmd.user}</p>
                </div>
            </div>
            <div class="text-right">
                <p class="text-xs text-gray-400">${cmd.execution_time || '0ms'}</p>
                <p class="text-xs text-gray-500">${new Date(cmd.timestamp).toLocaleTimeString()}</p>
            </div>
        </div>
    `).join('');
}

// Load bot logs
async function loadBotLogs() {
    try {
        const response = await apiRequest('/api/v1/discord/monitoring/logs?limit=10');
        
        if (response && response.ok) {
            const data = await response.json();
            botLogs = data.data?.logs || [];
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
        
        renderBotLogs();
        
    } catch (error) {
        console.error('Error loading bot logs:', error);
        botLogs = [];
        renderBotLogs();
    }
}

// Render bot logs
function renderBotLogs() {
    const container = document.getElementById('botLogs');
    if (!container) return;
    
    container.innerHTML = botLogs.map(log => `
        <div class="flex items-start space-x-2 text-xs">
            <span class="text-gray-400 font-mono">${new Date(log.timestamp).toLocaleTimeString()}</span>
            <span class="px-2 py-0.5 rounded text-xs font-medium ${getLogTypeClass(log.level || log.type)}">
                ${(log.level || log.type || 'INFO').toUpperCase()}
            </span>
            <span class="text-gray-700 flex-1">${log.message}</span>
        </div>
    `).join('');
}

// Get log type CSS class
function getLogTypeClass(type) {
    const lowerType = (type || 'info').toLowerCase();
    switch (lowerType) {
        case 'info': return 'bg-blue-100 text-blue-800';
        case 'warning': return 'bg-yellow-100 text-yellow-800';
        case 'error': return 'bg-red-100 text-red-800';
        case 'success': return 'bg-green-100 text-green-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}

// Initialize event listeners
function initEventListeners() {
    // Buttons
    const addBotBtn = document.getElementById('addBotBtn');
    const addWorldBtn = document.getElementById('addWorldBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    const refreshBotsBtn = document.getElementById('refreshBotsBtn');
    const clearLogsBtn = document.getElementById('clearLogsBtn');
    
    if (addBotBtn) {
        addBotBtn.addEventListener('click', () => openBotModal());
    }
    
    if (addWorldBtn) {
        addWorldBtn.addEventListener('click', () => openWorldModal());
    }
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshDiscordDashboard);
    }
    
    if (refreshBotsBtn) {
        refreshBotsBtn.addEventListener('click', loadBots);
    }
    
    if (clearLogsBtn) {
        clearLogsBtn.addEventListener('click', clearBotLogs);
    }
    
    // Modal event listeners
    initModalEventListeners();
}

// Initialize modal event listeners
function initModalEventListeners() {
    // Bot modal
    const botForm = document.getElementById('botForm');
    const cancelBotBtn = document.getElementById('cancelBotBtn');
    
    if (botForm) {
        botForm.addEventListener('submit', handleBotSubmit);
    }
    
    if (cancelBotBtn) {
        cancelBotBtn.addEventListener('click', () => closeModal('botModal'));
    }
    
    // World modal
    const worldForm = document.getElementById('worldForm');
    const cancelWorldBtn = document.getElementById('cancelWorldBtn');
    
    if (worldForm) {
        worldForm.addEventListener('submit', handleWorldSubmit);
    }
    
    if (cancelWorldBtn) {
        cancelWorldBtn.addEventListener('click', () => closeModal('worldModal'));
    }
}

// Open bot modal
function openBotModal(botId = null) {
    const modal = document.getElementById('botModal');
    const modalTitle = document.getElementById('botModalTitle');
    const form = document.getElementById('botForm');
    
    if (!modal || !form) return;
    
    // Reset form
    form.reset();
    
    if (botId) {
        // Edit mode
        const bot = bots.find(b => b.id === botId);
        if (bot) {
            modalTitle.textContent = 'Edit Bot';
            populateBotForm(bot);
        }
    } else {
        // Add mode
        modalTitle.textContent = 'Tambah Bot';
    }
    
    openModal('botModal');
}

// Populate bot form
function populateBotForm(bot) {
    const fields = {
        botId: bot.id,
        botName: bot.name,
        botToken: bot.token,
        botPrefix: bot.prefix,
        botGuild: bot.guild_id,
        botDescription: bot.description,
        botActive: bot.is_active,
        botAutoStart: bot.auto_start
    };
    
    Object.entries(fields).forEach(([fieldId, value]) => {
        const element = document.getElementById(fieldId);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = value;
            } else {
                element.value = value || '';
            }
        }
    });
}

// Handle bot form submission
async function handleBotSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const botData = Object.fromEntries(formData.entries());
    
    // Convert checkboxes
    botData.is_active = formData.has('is_active');
    botData.auto_start = formData.has('auto_start');
    
    showLoading(true);
    
    try {
        const isEdit = botData.id;
        const endpoint = isEdit ? `/discord/bots/${botData.id}` : '/discord/bots';
        const method = isEdit ? 'PUT' : 'POST';
        
        const response = await apiRequest(endpoint, {
            method: method,
            body: JSON.stringify(botData)
        });
        
        if (response && response.ok) {
            showToast(`Bot berhasil ${isEdit ? 'diperbarui' : 'ditambahkan'}`, 'success');
            closeModal('botModal');
            await loadBots();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal menyimpan bot', 'error');
        }
    } catch (error) {
        console.error('Error saving bot:', error);
        showToast('Terjadi kesalahan saat menyimpan bot', 'error');
    } finally {
        showLoading(false);
    }
}

// Open world modal
function openWorldModal(worldId = null) {
    const modal = document.getElementById('worldModal');
    const modalTitle = document.getElementById('worldModalTitle');
    const form = document.getElementById('worldForm');
    
    if (!modal || !form) return;
    
    // Reset form
    form.reset();
    
    if (worldId) {
        // Edit mode
        const world = worlds.find(w => w.id === worldId);
        if (world) {
            modalTitle.textContent = 'Edit World';
            populateWorldForm(world);
        }
    } else {
        // Add mode
        modalTitle.textContent = 'Tambah World';
    }
    
    openModal('worldModal');
}

// Update bot options in world form
function updateBotOptions() {
    const select = document.getElementById('worldBot');
    if (!select) return;
    
    const currentValue = select.value;
    select.innerHTML = '<option value="">Pilih Bot</option>' + 
        bots.map(bot => `<option value="${bot.id}">${bot.name}</option>`).join('');
    
    if (currentValue) {
        select.value = currentValue;
    }
}

// Populate world form
function populateWorldForm(world) {
    const fields = {
        worldId: world.id,
        worldName: world.name,
        worldOwner: world.owner,
        worldBot: world.bot_id,
        worldActive: world.is_active
    };
    
    Object.entries(fields).forEach(([fieldId, value]) => {
        const element = document.getElementById(fieldId);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = value;
            } else {
                element.value = value || '';
            }
        }
    });
}

// Handle world form submission
async function handleWorldSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const worldData = Object.fromEntries(formData.entries());
    
    worldData.is_active = formData.has('is_active');
    worldData.bot_id = parseInt(worldData.bot_id);
    
    const isEdit = worldData.id;
    const endpoint = isEdit ? `/admin/discord/worlds/${worldData.id}` : '/admin/discord/worlds';
    const method = isEdit ? 'PUT' : 'POST';
    
    const response = await apiRequest(endpoint, {
        method: method,
        body: JSON.stringify(worldData)
    });
}

// Toggle bot status
async function toggleBot(botId) {
    const bot = bots.find(b => b.id === botId);
    if (!bot) return;
    
    const action = bot.status === 'online' ? 'stop' : 'start';
    
    showLoading(true);
    
    try {
        const response = await apiRequest(`/admin/discord/bots/${botId}/${action}`, {
            method: 'POST'
        });
        
        if (response && response.ok) {
            showToast(`Bot berhasil ${action === 'start' ? 'dijalankan' : 'dihentikan'}`, 'success');
            await loadBots();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || `Gagal ${action} bot`, 'error');
        }
    } catch (error) {
        console.error(`Error ${action} bot:`, error);
        showToast(`Terjadi kesalahan saat ${action} bot`, 'error');
    } finally {
        showLoading(false);
    }
}

// Edit bot
function editBot(botId) {
    openBotModal(botId);
}

// Delete bot
async function deleteBot(botId) {
    if (!confirm('Apakah Anda yakin ingin menghapus bot ini?')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await apiRequest(`/admin/discord/bots/${botId}`, {
            method: 'DELETE'
        });
        
        if (response && response.ok) {
            showToast('Bot berhasil dihapus', 'success');
            await loadBots();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal menghapus bot', 'error');
        }
    } catch (error) {
        console.error('Error deleting bot:', error);
        showToast('Terjadi kesalahan saat menghapus bot', 'error');
    } finally {
        showLoading(false);
    }
}

// Edit world
function editWorld(worldId) {
    openWorldModal(worldId);
}

// Delete world
async function deleteWorld(worldId) {
    if (!confirm('Apakah Anda yakin ingin menghapus world ini?')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await apiRequest(`/admin/discord/worlds/${worldId}`, {
            method: 'DELETE'
        });
        
        if (response && response.ok) {
            showToast('World berhasil dihapus', 'success');
            await loadWorlds();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal menghapus world', 'error');
        }
    } catch (error) {
        console.error('Error deleting world:', error);
        showToast('Terjadi kesalahan saat menghapus world', 'error');
    } finally {
        showLoading(false);
    }
}

// Clear bot logs
async function clearBotLogs() {
    if (!confirm('Apakah Anda yakin ingin menghapus semua log?')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await apiRequest('/admin/discord/logs', {
            method: 'DELETE'
        });
        
        if (response && response.ok) {
            showToast('Log berhasil dihapus', 'success');
            await loadBotLogs();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal menghapus log', 'error');
        }
    } catch (error) {
        console.error('Error clearing logs:', error);
        showToast('Terjadi kesalahan saat menghapus log', 'error');
    } finally {
        showLoading(false);
    }
}

// Refresh Discord dashboard
async function refreshDiscordDashboard() {
    showLoading(true);
    try {
        await Promise.all([
            loadDiscordStats(),
            loadBots(),
            loadWorlds(),
            loadRecentCommands(),
            loadBotLogs()
        ]);
        showToast('Dashboard Discord berhasil diperbarui', 'success', 3000);
    } catch (error) {
        showToast('Gagal memperbarui dashboard Discord', 'error');
    } finally {
        showLoading(false);
    }
}

// Discord Module Bridge Integration
async function initDiscordDashboardWithBridge() {
    const token = checkAuth();
    if (!token) return;

    showLoading(true);
    
    try {
        // Wait for module bridge to initialize
        if (window.DashboardBridge && !window.DashboardBridge.isInitialized) {
            console.log('⏳ Waiting for Discord module bridge to initialize...');
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

        // Load Discord modules if available
        if (window.DashboardBridge && window.DashboardBridge.isInitialized) {
            console.log('🤖 Loading Discord modules via bridge...');
            await window.DashboardBridge.loadDiscordModules();
        }

        await Promise.all([
            loadDiscordStatsWithBridge(),
            loadBots(),
            loadWorlds(),
            loadRecentCommands(),
            loadBotLogs()
        ]);
        
        initEventListeners();
        showToast('Dashboard Discord berhasil dimuat', 'success', 3000);
    } catch (error) {
        console.error('Error loading Discord dashboard:', error);
        showToast('Gagal memuat data Discord', 'error');
    } finally {
        showLoading(false);
    }
}

async function loadDiscordStatsWithBridge() {
    try {
        if (window.DashboardBridge && window.DashboardBridge.isInitialized) {
            console.log('📊 Loading Discord stats via module bridge...');
            await window.DashboardBridge.loadDiscordStats();
        } else {
            console.log('📊 Loading Discord stats via fallback...');
            await loadDiscordStats();
        }
    } catch (error) {
        console.error('Error loading Discord stats via bridge:', error);
        // Fallback to original implementation
        await loadDiscordStats();
    }
}

async function refreshDiscordDashboardWithBridge() {
    showLoading(true);
    try {
        if (window.DashboardBridge && window.DashboardBridge.isInitialized) {
            console.log('🔄 Refreshing Discord dashboard via module bridge...');
            
            // Use bridge if Discord module is loaded
            const discordInstance = window.DashboardBridge.getModuleInstance('discord');
            if (discordInstance) {
                await Promise.all([
                    discordInstance.loadDiscordStats(),
                    discordInstance.loadBots(),
                    loadWorlds(),
                    loadRecentCommands(),
                    loadBotLogs()
                ]);
            } else {
                // Fallback to mixed approach
                await Promise.all([
                    loadDiscordStatsWithBridge(),
                    loadBots(),
                    loadWorlds(),
                    loadRecentCommands(),
                    loadBotLogs()
                ]);
            }
        } else {
            console.log('🔄 Refreshing Discord dashboard via fallback...');
            await refreshDiscordDashboard();
        }
        showToast('Dashboard Discord berhasil diperbarui', 'success', 3000);
    } catch (error) {
        showToast('Gagal memperbarui dashboard Discord', 'error');
    } finally {
        showLoading(false);
    }
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Use bridge initialization if available, fallback to original
    if (window.DashboardBridge) {
        initDiscordDashboardWithBridge();
    } else {
        initDiscordDashboard();
    }
    
    // Auto-refresh every 30 seconds using bridge
    setInterval(() => {
        if (window.DashboardBridge && window.DashboardBridge.isInitialized) {
            loadDiscordStatsWithBridge();
            loadRecentCommands();
            loadBotLogs();
        } else {
            loadRecentCommands();
            loadBotLogs();
        }
    }, 30000);
});
