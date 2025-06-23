// Discord Data Loader
// Maksimal 50 baris per modul

class DiscordDataLoader {
    // Load bots
    static async loadBots() {
        try {
            const bots = await discordApiService.loadBots();
            if (typeof discordBotsList !== 'undefined') {
                discordBotsList.setBots(bots);
            }
            if (window.updateBotOptions) {
                window.updateBotOptions(bots);
            }
            return bots;
        } catch (error) {
            console.error('Error loading bots:', error);
            if (typeof discordBotsList !== 'undefined') {
                discordBotsList.setBots([]);
            }
            return [];
        }
    }

    // Load worlds
    static async loadWorlds() {
        try {
            const worlds = await discordApiService.loadWorlds();
            if (typeof discordWorldsList !== 'undefined') {
                discordWorldsList.setWorlds(worlds);
            }
            return worlds;
        } catch (error) {
            console.error('Error loading worlds:', error);
            if (typeof discordWorldsList !== 'undefined') {
                discordWorldsList.setWorlds([]);
            }
            return [];
        }
    }

    // Load recent commands
    static async loadRecentCommands() {
        try {
            const commands = await discordMonitoringApi.loadRecentCommands();
            return commands;
        } catch (error) {
            console.error('Error loading recent commands:', error);
            return [];
        }
    }
}

// Export for global use
window.DiscordDataLoader = DiscordDataLoader;
