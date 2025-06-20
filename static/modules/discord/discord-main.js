// Discord Main Controller
class DiscordMainController {
    constructor() {
        this.dataService = new DiscordDataService();
        this.uiController = new DiscordUIController();
        this.botManager = new DiscordBotManager(this.dataService, this.uiController);
    }

    async initDiscordDashboard() {
        const token = localStorage.getItem('authToken');
        if (!token) {
            window.location.href = '/login';
            return;
        }

        UIUtils.showLoading(true);
        
        try {
            await Promise.all([
                this.loadDiscordStats(),
                this.loadBots(),
                this.loadWorlds(),
                this.loadRecentCommands(),
                this.loadBotLogs()
            ]);
            
            this.initEventListeners();
            UIUtils.showToast('Dashboard Discord berhasil dimuat', 'success', 3000);
        } catch (error) {
            console.error('Error loading Discord dashboard:', error);
            UIUtils.showToast('Gagal memuat data Discord', 'error');
        } finally {
            UIUtils.showLoading(false);
        }
    }

    async loadDiscordStats() {
        const stats = await this.dataService.loadDiscordStats();
        this.uiController.updateDiscordStats(stats);
    }

    async loadBots() {
        await this.botManager.loadAndRenderBots();
    }

    async loadWorlds() {
        // Implementation for worlds loading
        console.log('Loading worlds...');
    }

    async loadRecentCommands() {
        // Implementation for recent commands loading
        console.log('Loading recent commands...');
    }

    async loadBotLogs() {
        // Implementation for bot logs loading
        console.log('Loading bot logs...');
    }

    initEventListeners() {
        // Add event listeners for Discord dashboard
        console.log('Discord event listeners initialized');
    }
}

// Global instance
const discordMainController = new DiscordMainController();
