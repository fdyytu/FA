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
        const response = await apiRequest('/admin/discord/stats');
        
        if (response && response.ok) {
            const data = await response.json();
            updateDiscordStats(data.data || data);
        } else {
            // Use mock data if API fails
            updateDiscordStats({
                total_bots: 3,
                discord_users: 2450,
                live_products: 156,
                commands_today: 1234
            });
        }
    } catch (error) {
        console.error('Error loading Discord stats:', error);
        // Use mock data
        updateDiscordStats({
            total_bots: 3,
            discord_users: 2450,
            live_products: 156,
            commands_today: 1234
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
        elements.totalBots.textContent = formatNumber(stats.total_bots || 3);
    }
    
    if (elements.discordUsers) {
        elements.discordUsers.textContent = formatNumber(stats.discord_users || 2450);
    }
    
    if (elements.liveProducts) {
        elements.liveProducts.textContent = formatNumber(stats.live_products || 156);
    }
    
    if (elements.commandsToday) {
        elements.commandsToday.textContent = formatNumber(stats.commands_today || 1234);
    }
}

// Load bots
async function loadBots() {
    try {
        const response = await apiRequest('/admin/discord/bots');
        
        if (response && response.ok) {
            const data = await response.json();
            bots = data.data || [];
        } else {
            // Use mock data if API fails
            bots = generateMockBots();
        }
        
        renderBotsList();
        updateBotOptions();
        
    } catch (error) {
        console.error('Error loading bots:', error);
        bots = generateMockBots();
        renderBotsList();
        updateBotOptions();
    }
}

// Generate mock bots data
function generateMockBots() {
    return [
        {
            id: 1,
            name: 'FA Store Bot',
            token: 'MTIzNDU2Nzg5MDEyMzQ1Njc4OTA.XXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXX',
            prefix: '!',
            guild_id: '123456789012345678',
            description: 'Bot utama untuk toko FA',
            is_active: true,
            auto_start: true,
            status: 'online',
            uptime: '2d 14h 32m',
            commands_count: 1234,
            created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
            id: 2,
            name: 'FA Support Bot',
            token: 'MTIzNDU2Nzg5MDEyMzQ1Njc4OTE.YYYYYY.YYYYYYYYYYYYYYYYYYYYYYYYYY',
            prefix: '?',
            guild_id: '123456789012345679',
            description: 'Bot untuk customer support',
            is_active: true,
            auto_start: false,
            status: 'online',
            uptime: '1d 8h 15m',
            commands_count: 567,
            created_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
            id: 3,
            name: 'FA Analytics Bot',
            token: 'MTIzNDU2Nzg5MDEyMzQ1Njc4OTI.ZZZZZZ.ZZZZZZZZZZZZZZZZZZZZZZZZZZ',
            prefix: '#',
            guild_id: '123456789012345680',
            description: 'Bot untuk analytics dan reporting',
            is_active: false,
            auto_start: false,
            status: 'offline',
            uptime: '0m',
            commands_count: 89,
            created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
        }
    ];
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
        const response = await apiRequest('/admin/discord/worlds');
        
        if (response && response.ok) {
            const data = await response.json();
            worlds = data.data || [];
        } else {
            // Use mock data if API fails
            worlds = generateMockWorlds();
        }
        
        renderWorldsList();
        
    } catch (error) {
        console.error('Error loading worlds:', error);
        worlds = generateMockWorlds();
        renderWorldsList();
    }
}

// Generate mock worlds data
function generateMockWorlds() {
    return [
        {
            id: 1,
            name: 'WORLD1',
            owner: 'ADMIN123',
            bot_id: 1,
            bot_name: 'FA Store Bot',
            is_active: true,
            created_at: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
            id: 2,
            name: 'WORLD2',
            owner: 'OWNER456',
            bot_id: 1,
            bot_name: 'FA Store Bot',
            is_active: true,
            created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
            id: 3,
            name: 'TESTWORLD',
            owner: 'TESTER789',
            bot_id: 2,
            bot_name: 'FA Support Bot',
            is_active: false,
            created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString()
        }
    ];
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
        const response = await apiRequest('/admin/discord/commands/recent?limit=5');
        
        if (response && response.ok) {
            const data = await response.json();
            recentCommands = data.data || [];
        } else {
            // Use mock data if API fails
            recentCommands = generateMockCommands();
        }
        
        renderRecentCommands();
        
    } catch (error) {
        console.error('Error loading recent commands:', error);
        recentCommands = generateMockCommands();
        renderRecentCommands();
    }
}

// Generate mock commands data
function generateMockCommands() {
    const commands = ['!buy', '!balance', '!help', '!products', '!status'];
    const users = ['User123', 'Player456', 'Customer789', 'Buyer101', 'Member202'];
    
    return Array.from({length: 5}, (_, i) => ({
        id: i + 1,
        command: commands[Math.floor(Math.random() * commands.length)],
        user: users[Math.floor(Math.random() * users.length)],
        bot_name: 'FA Store Bot',
        success: Math.random() > 0.2,
        executed_at: new Date(Date.now() - Math.random() * 60 * 60 * 1000).toISOString()
    }));
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
                    <p class="text-sm font-medium text-gray-900">${cmd.command}</p>
                    <p class="text-xs text-gray-500">by ${cmd.user}</p>
                </div>
            </div>
            <div class="text-right">
                <p class="text-xs text-gray-400">${formatRelativeTime(cmd.executed_at)}</p>
                <p class="text-xs text-gray-500">${cmd.bot_name}</p>
            </div>
        </div>
    `).join('');
}

// Load bot logs
async function loadBotLogs() {
    try {
        const response = await apiRequest('/admin/discord/logs?limit=10');
        
        if (response && response.ok) {
            const data = await response.json();
            botLogs = data.data || [];
        } else {
            // Use mock data if API fails
            botLogs = generateMockLogs();
        }
        
        renderBotLogs();
        
    } catch (error) {
        console.error('Error loading bot logs:', error);
        botLogs = generateMockLogs();
        renderBotLogs();
    }
}

// Generate mock logs data
function generateMockLogs() {
    const logTypes = ['info', 'warning', 'error', 'success'];
    const messages = [
        'Bot started successfully',
        'Command executed: !buy',
        'User joined server',
        'Payment processed',
        'Connection timeout',
        'Database query completed',
        'Rate limit exceeded',
        'New product added'
    ];
    
    return Array.from({length: 10}, (_, i) => ({
        id: i + 1,
        type: logTypes[Math.floor(Math.random() * logTypes.length)],
        message: messages[Math.floor(Math.random() * messages.length)],
        bot_name: 'FA Store Bot',
        timestamp: new Date(Date.now() - Math.random() * 2 * 60 * 60 * 1000).toISOString()
    }));
}

// Render bot logs
function renderBotLogs() {
    const container = document.getElementById('botLogs');
    if (!container) return;
    
    container.innerHTML = botLogs.map(log => `
        <div class="flex items-start space-x-2 text-xs">
            <span class="text-gray-400 font-mono">${new Date(log.timestamp).toLocaleTimeString()}</span>
            <span class="px-2 py-0.5 rounded text-xs font-medium ${getLogTypeClass(log.type)}">
                ${log.type.toUpperCase()}
            </span>
            <span class="text-gray-700 flex-1">${log.message}</span>
        </div>
    `).join('');
}

// Get log type CSS class
function getLogTypeClass(type) {
    switch (type) {
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

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', () => {
    initDiscordDashboard();
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadRecentCommands();
        loadBotLogs();
    }, 30000);
});
