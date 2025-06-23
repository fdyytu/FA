// Discord Bots List Component
// Maksimal 50 baris per modul

class DiscordBotsList {
    constructor() {
        this.container = document.getElementById('botsList');
        this.bots = [];
    }

    // Set bots data
    setBots(bots) {
        this.bots = bots || [];
        this.render();
    }

    // Render bots list
    render() {
        if (!this.container) return;
        this.container.innerHTML = this.bots.map(bot => this.renderBotItem(bot)).join('');
    }

    // Render single bot item
    renderBotItem(bot) {
        const statusInfo = window.getBotStatusInfo ? window.getBotStatusInfo(bot) : this.getDefaultStatusInfo(bot);
        return `<div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <div class="flex items-center">
                <div class="w-12 h-12 bg-gradient-to-r from-purple-500 to-blue-600 rounded-full flex items-center justify-center">
                    <i class="fab fa-discord text-white text-lg"></i>
                </div>
                <div class="ml-4">
                    <h4 class="text-sm font-medium text-gray-900">${bot.name}</h4>
                    <p class="text-xs text-gray-500">Prefix: ${bot.prefix} | Uptime: ${bot.uptime || '0m'}</p>
                    <div class="flex items-center mt-1">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusInfo.statusClass}">
                            <span class="w-1.5 h-1.5 ${statusInfo.dotClass} rounded-full mr-1"></span>
                            ${statusInfo.statusText}
                        </span>
                        <span class="ml-2 text-xs text-gray-500">${bot.commands_count || 0} commands</span>
                    </div>
                </div>
            </div>
            <div class="flex space-x-2">
                <button onclick="toggleBot(${bot.id})" class="text-sm ${statusInfo.buttonClass}" title="${statusInfo.buttonTitle}">
                    <i class="fas ${statusInfo.buttonIcon}"></i>
                </button>
                <button onclick="editBot(${bot.id})" class="text-blue-600 hover:text-blue-800" title="Edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="deleteBot(${bot.id})" class="text-red-600 hover:text-red-800" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>`;
    }
}

// Export instance
const discordBotsList = new DiscordBotsList();
