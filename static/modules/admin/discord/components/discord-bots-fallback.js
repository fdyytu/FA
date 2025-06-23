// Discord Bots Fallback Methods
// Maksimal 50 baris per modul

// Add fallback method to DiscordBotsList
if (typeof discordBotsList !== 'undefined') {
    discordBotsList.getDefaultStatusInfo = function(bot) {
        const isOnline = bot.status === 'online';
        return {
            statusClass: isOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
            dotClass: isOnline ? 'bg-green-400' : 'bg-red-400',
            statusText: isOnline ? 'Online' : 'Offline',
            buttonClass: isOnline ? 'text-red-600 hover:text-red-800' : 'text-green-600 hover:text-green-800',
            buttonIcon: isOnline ? 'fa-stop' : 'fa-play',
            buttonTitle: isOnline ? 'Stop Bot' : 'Start Bot'
        };
    };
}

// Global fallback functions
window.getDefaultStatusInfo = function(bot) {
    const isOnline = bot.status === 'online';
    return {
        statusClass: isOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
        dotClass: isOnline ? 'bg-green-400' : 'bg-red-400',
        statusText: isOnline ? 'Online' : 'Offline',
        buttonClass: isOnline ? 'text-red-600 hover:text-red-800' : 'text-green-600 hover:text-green-800',
        buttonIcon: isOnline ? 'fa-stop' : 'fa-play',
        buttonTitle: isOnline ? 'Stop Bot' : 'Start Bot'
    };
};

// Ensure getBotStatusInfo exists
if (!window.getBotStatusInfo) {
    window.getBotStatusInfo = window.getDefaultStatusInfo;
}
