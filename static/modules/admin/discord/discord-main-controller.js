// Discord Main Controller
// Maksimal 50 baris per modul

class DiscordMainController {
    constructor() {
        this.bots = [];
        this.worlds = [];
        this.recentCommands = [];
        this.botLogs = [];
    }

    // Initialize Discord dashboard
    async init() {
        const token = checkAuth();
        if (!token) return;

        if (typeof DiscordUIUtils !== 'undefined') {
            DiscordUIUtils.showLoading(true);
        }
        
        try {
            await Promise.all([
                this.loadStats(),
                this.loadBots(),
                this.loadWorlds(),
                this.loadRecentCommands(),
                this.loadBotLogs()
            ]);
            
            this.initEventListeners();
            if (typeof DiscordUIUtils !== 'undefined') {
                DiscordUIUtils.showToast('Dashboard Discord berhasil dimuat', 'success', 3000);
            }
        } catch (error) {
            console.error('Error loading Discord dashboard:', error);
            if (typeof DiscordUIUtils !== 'undefined') {
                DiscordUIUtils.showToast('Gagal memuat data Discord', 'error');
            }
        } finally {
            if (typeof DiscordUIUtils !== 'undefined') {
                DiscordUIUtils.showLoading(false);
            }
        }
    }

    // Load Discord statistics
    async loadStats() {
        try {
            const stats = await discordApiService.loadStats();
            if (typeof discordStatsUI !== 'undefined') {
                discordStatsUI.updateStats(stats);
            }
        } catch (error) {
            console.error('Error loading Discord stats:', error);
            if (typeof discordStatsUI !== 'undefined') {
                discordStatsUI.showDefaultStats();
            }
        }
    }
}

// Export instance
const discordMainController = new DiscordMainController();
