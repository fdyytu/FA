// Discord API Service - Koneksi API Discord
// Maksimal 50 baris per modul

class DiscordApiService {
    constructor() {
        this.baseUrl = '/discord';
    }

    // Load Discord statistics
    async loadStats() {
        try {
            const response = await apiRequest(`${this.baseUrl}/analytics/stats`);
            if (response && response.ok) {
                const data = await response.json();
                return data.data || data;
            }
            throw new Error(`API Error: ${response.status}`);
        } catch (error) {
            console.error('Error loading Discord stats:', error);
            throw error;
        }
    }

    // Load bots
    async loadBots() {
        try {
            const response = await apiRequest(`${this.baseUrl}/config/bots`);
            if (response && response.ok) {
                const data = await response.json();
                return data.data || [];
            }
            throw new Error(`API Error: ${response.status}`);
        } catch (error) {
            console.error('Error loading bots:', error);
            throw error;
        }
    }

    // Load worlds
    async loadWorlds() {
        try {
            const response = await apiRequest(`${this.baseUrl}/config/worlds`);
            if (response && response.ok) {
                const data = await response.json();
                return data.data || [];
            }
            throw new Error(`API Error: ${response.status}`);
        } catch (error) {
            console.error('Error loading worlds:', error);
            throw error;
        }
    }
}

// Export instance
const discordApiService = new DiscordApiService();
