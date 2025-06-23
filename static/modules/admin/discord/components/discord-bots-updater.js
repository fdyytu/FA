// Discord Bots UI Updater
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

// Export functions
window.updateDiscordBots = updateDiscordBots;
window.updateDiscordLogs = updateDiscordLogs;
window.updateDiscordCommands = updateDiscordCommands;
