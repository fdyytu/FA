// Discord Bot Utilities
// Maksimal 50 baris per modul

class DiscordBotUtils {
    // Get bot status info
    static getBotStatusInfo(bot) {
        const isOnline = bot.status === 'online';
        return {
            statusClass: isOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
            dotClass: isOnline ? 'bg-green-400' : 'bg-red-400',
            statusText: isOnline ? 'Online' : 'Offline',
            buttonClass: isOnline ? 'text-red-600 hover:text-red-800' : 'text-green-600 hover:text-green-800',
            buttonIcon: isOnline ? 'fa-stop' : 'fa-play',
            buttonTitle: isOnline ? 'Stop Bot' : 'Start Bot'
        };
    }

    // Update bot options in select elements
    static updateBotOptions(bots) {
        const selects = document.querySelectorAll('select[data-bot-select]');
        selects.forEach(select => {
            const currentValue = select.value;
            select.innerHTML = '<option value="">Pilih Bot</option>' + 
                bots.map(bot => `<option value="${bot.id}" ${bot.id == currentValue ? 'selected' : ''}>${bot.name}</option>`).join('');
        });
    }

    // Format bot uptime
    static formatUptime(uptime) {
        if (!uptime) return '0m';
        const minutes = Math.floor(uptime / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `${days}d ${hours % 24}h`;
        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        return `${minutes}m`;
    }
}

// Export for global use
window.getBotStatusInfo = DiscordBotUtils.getBotStatusInfo;
window.updateBotOptions = DiscordBotUtils.updateBotOptions;
