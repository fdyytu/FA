// Discord UI Controller
class DiscordUIController {
    constructor() {
        this.elements = {};
        this.initElements();
    }

    initElements() {
        this.elements = {
            totalBots: document.getElementById('totalBots'),
            discordUsers: document.getElementById('discordUsers'),
            liveProducts: document.getElementById('liveProducts'),
            commandsToday: document.getElementById('commandsToday'),
            botsList: document.getElementById('botsList'),
            worldsList: document.getElementById('worldsList'),
            recentCommandsList: document.getElementById('recentCommandsList'),
            botLogsList: document.getElementById('botLogsList')
        };
    }

    updateDiscordStats(stats) {
        if (this.elements.totalBots) {
            this.elements.totalBots.textContent = Formatters.formatNumber(stats.total_bots || 3);
        }
        
        if (this.elements.discordUsers) {
            this.elements.discordUsers.textContent = Formatters.formatNumber(stats.discord_users || 2450);
        }
        
        if (this.elements.liveProducts) {
            this.elements.liveProducts.textContent = Formatters.formatNumber(stats.live_products || 156);
        }
        
        if (this.elements.commandsToday) {
            this.elements.commandsToday.textContent = Formatters.formatNumber(stats.commands_today || 1234);
        }
    }

    renderBotsList(bots) {
        if (!this.elements.botsList) return;
        
        this.elements.botsList.innerHTML = bots.map(bot => `
            <div class="bg-white p-4 rounded-lg shadow border border-gray-200">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="flex-shrink-0">
                            <i class="fas fa-robot text-2xl text-blue-500"></i>
                        </div>
                        <div>
                            <h3 class="text-sm font-medium text-gray-900">${bot.name}</h3>
                            <div class="flex items-center mt-1">
                                <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${bot.status === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                                    <span class="w-1.5 h-1.5 ${bot.status === 'online' ? 'bg-green-400' : 'bg-red-400'} rounded-full mr-1"></span>
                                    ${bot.status === 'online' ? 'Online' : 'Offline'}
                                </span>
                                <span class="ml-2 text-xs text-gray-500">${bot.commands_count || 0} commands</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }
}

const discordUIController = new DiscordUIController();
