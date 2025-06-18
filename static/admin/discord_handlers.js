// Discord data handlers
async function loadDiscordStats() {
    try {
        // Get all Discord data in parallel with error handling
        const [logsResponse, commandsResponse, botsResponse] = await Promise.all([
            apiRequest('/discord/logs?limit=10').catch(() => ({ data: { logs: [] } })),
            apiRequest('/discord/commands/recent?limit=5').catch(() => ({ data: { commands: [] } })),
            apiRequest('/discord/bots').catch(() => ({ data: { bots: [] } }))
        ]);
        
        // Update UI with available data
        if (logsResponse && logsResponse.data) {
            updateDiscordLogs(logsResponse.data.logs || []);
        }
        
        if (commandsResponse && commandsResponse.data) {
            updateDiscordCommands(commandsResponse.data.commands || []);
        }
        
        if (botsResponse && botsResponse.data) {
            updateDiscordBots(botsResponse.data.bots || []);
        }
        
        // Remove error states if any
        document.querySelectorAll('.discord-section').forEach(section => {
            section.classList.remove('error');
        });
        
    } catch (error) {
        console.error('Error loading Discord stats:', error);
        showToast('Beberapa data Discord tidak dapat dimuat', 'warning');
        
        // Add error state to sections
        document.querySelectorAll('.discord-section').forEach(section => {
            section.classList.add('error');
        });
    }
}

function updateDiscordBots(bots) {
    const container = document.getElementById('discordBots');
    if (!container) return;
    
    if (bots.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center py-4">Tidak ada bot yang aktif</p>';
        return;
    }
    
    container.innerHTML = bots.map(bot => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-2">
            <div>
                <h4 class="font-medium">${bot.name || 'Unnamed Bot'}</h4>
                <p class="text-sm text-gray-500">Guild ID: ${bot.guild_id || 'N/A'}</p>
            </div>
            <span class="px-2 py-1 rounded text-sm ${bot.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                ${bot.status || 'unknown'}
            </span>
        </div>
    `).join('');
}

function updateDiscordLogs(logs) {
    const container = document.getElementById('discordLogs');
    if (!container) return;
    
    if (!logs || logs.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center py-4">Tidak ada log terbaru</p>';
        return;
    }
    
    container.innerHTML = logs.map(log => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-2">
            <div>
                <p class="text-sm">${log.message || 'No message'}</p>
                <p class="text-xs text-gray-500">${formatDate(log.created_at) || 'Unknown time'}</p>
            </div>
            <span class="px-2 py-1 rounded text-sm ${getLogLevelClass(log.level || 'info')}">
                ${log.level || 'info'}
            </span>
        </div>
    `).join('');
}

function updateDiscordCommands(commands) {
    const container = document.getElementById('discordCommands');
    if (!container) return;
    
    if (!commands || commands.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center py-4">Tidak ada command terbaru</p>';
        return;
    }
    
    container.innerHTML = commands.map(cmd => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-2">
            <div>
                <p class="text-sm font-medium">${cmd.command || 'Unknown command'}</p>
                <p class="text-xs text-gray-500">
                    ${cmd.user || 'Unknown user'} - ${formatDate(cmd.created_at) || 'Unknown time'}
                </p>
            </div>
            <span class="px-2 py-1 rounded text-sm ${cmd.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                ${cmd.success ? 'Success' : 'Failed'}
            </span>
        </div>
    `).join('');
}

function getLogLevelClass(level) {
    switch (level.toLowerCase()) {
        case 'error':
            return 'bg-red-100 text-red-800';
        case 'warning':
            return 'bg-yellow-100 text-yellow-800';
        case 'info':
            return 'bg-blue-100 text-blue-800';
        case 'debug':
            return 'bg-gray-100 text-gray-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
}

// Export functions
window.loadDiscordStats = loadDiscordStats;
window.updateDiscordBots = updateDiscordBots;
window.updateDiscordLogs = updateDiscordLogs;
window.updateDiscordCommands = updateDiscordCommands;
