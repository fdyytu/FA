// Discord Data Service
class DiscordDataService {
    constructor() {
        this.data = {
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
                return data.data || data;
            } else {
                return this.generateMockStats();
            }
        } catch (error) {
            console.error('Error loading Discord stats:', error);
            return this.generateMockStats();
        }
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

    async loadWorlds() {
        try {
            const response = await apiClient.get('/admin/discord/worlds');
            
            if (response && response.ok) {
                const data = await response.json();
                this.data.worlds = data.data || [];
            } else {
                this.data.worlds = this.generateMockWorlds();
            }
            
            return this.data.worlds;
        } catch (error) {
            console.error('Error loading worlds:', error);
            this.data.worlds = this.generateMockWorlds();
            return this.data.worlds;
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

    generateMockBots() {
        return [
            {
                id: 1,
                name: 'PPOB Bot',
                status: 'online',
                uptime: '99.9%',
                commands_count: 1234,
                last_seen: new Date().toISOString()
            },
            {
                id: 2,
                name: 'Support Bot',
                status: 'online',
                uptime: '98.5%',
                commands_count: 567,
                last_seen: new Date().toISOString()
            },
            {
                id: 3,
                name: 'Analytics Bot',
                status: 'maintenance',
                uptime: '95.2%',
                commands_count: 89,
                last_seen: new Date(Date.now() - 3600000).toISOString()
            }
        ];
    }

    generateMockWorlds() {
        return [
            {
                id: 1,
                name: 'BUYWORLD',
                owner: 'ADMIN',
                players: 45,
                status: 'active',
                last_activity: new Date().toISOString()
            },
            {
                id: 2,
                name: 'SHOPWORLD',
                owner: 'MODERATOR',
                players: 23,
                status: 'active',
                last_activity: new Date(Date.now() - 1800000).toISOString()
            }
        ];
    }

    getData() {
        return this.data;
    }
}

// Global Discord data service instance
const discordDataService = new DiscordDataService();
