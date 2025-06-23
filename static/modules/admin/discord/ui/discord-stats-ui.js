// Discord Statistics UI Components
// Maksimal 50 baris per modul

class DiscordStatsUI {
    constructor() {
        this.elements = {
            totalBots: document.getElementById('totalBots'),
            discordUsers: document.getElementById('discordUsers'),
            liveProducts: document.getElementById('liveProducts'),
            commandsToday: document.getElementById('commandsToday')
        };
    }

    // Update Discord statistics cards
    updateStats(stats) {
        if (this.elements.totalBots) {
            this.elements.totalBots.textContent = formatNumber(stats.total_bots || 0);
        }
        if (this.elements.discordUsers) {
            this.elements.discordUsers.textContent = formatNumber(stats.discord_users || 0);
        }
        if (this.elements.liveProducts) {
            this.elements.liveProducts.textContent = formatNumber(stats.live_products || 0);
        }
        if (this.elements.commandsToday) {
            this.elements.commandsToday.textContent = formatNumber(stats.commands_today || 0);
        }
    }

    // Show default stats on error
    showDefaultStats() {
        this.updateStats({
            total_bots: 0,
            discord_users: 0,
            live_products: 0,
            commands_today: 0
        });
    }
}

// Export instance
const discordStatsUI = new DiscordStatsUI();
