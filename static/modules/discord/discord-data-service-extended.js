// Discord Data Service
class DiscordDataService {
    constructor() {
        this.data = {
            stats: {},
            bots: [],
            worlds: [],
            recentCommands: [],
            botLogs: []
        };
    }

    async loadDiscordStats() {
        try {
            const response = await apiClient.get('/admin/discord/stats');
            
            if (response && response.ok) {
                const data = await response.json();
                this.data.stats = data.data || data;
            } else {
                this.data.stats = this.generateMockStats();
            }
            return this.data.stats;
        } catch (error) {
            console.error('Error loading Discord stats:', error);
            this.data.stats = this.generateMockStats();
            return this.data.stats;
        }
    }

    generateMockStats() {
        return {
            total_bots: 3,
            discord_users: 2450,
            live_products: 156,
            commands_today: 1234
        };
    }

    async loadBots() {
        try {
            const response = await apiClient.get('/admin/discord/bots');
            
            if (response && response.ok) {
                const data = await response.json();
                this.data.bots = data.data || [];
            } else {
                this.data.bots = this.generateMockBots();
            }
            return this.data.bots;
        } catch (error) {
            console.error('Error loading bots:', error);
            this.data.bots = this.generateMockBots();
            return this.data.bots;
        }
    }

    generateMockBots() {
        return [
            { id: 1, name: 'Bot Utama', status: 'online', commands_count: 1234 },
            { id: 2, name: 'Bot Backup', status: 'offline', commands_count: 567 },
            { id: 3, name: 'Bot Test', status: 'online', commands_count: 89 }
        ];
    }
}

const discordDataService = new DiscordDataService();
