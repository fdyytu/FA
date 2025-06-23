// Discord Monitoring API Service
// Maksimal 50 baris per modul

class DiscordMonitoringApi {
    constructor() {
        this.baseUrl = '/discord/monitoring';
    }

    // Load recent commands
    async loadRecentCommands(limit = 5) {
        try {
            const response = await apiRequest(`${this.baseUrl}/commands/recent?limit=${limit}`);
            if (response && response.ok) {
                const data = await response.json();
                return data.data?.commands || [];
            }
            throw new Error(`API Error: ${response.status}`);
        } catch (error) {
            console.error('Error loading recent commands:', error);
            throw error;
        }
    }

    // Load bot logs
    async loadBotLogs(limit = 10) {
        try {
            const response = await apiRequest(`${this.baseUrl}/logs?limit=${limit}`);
            if (response && response.ok) {
                const data = await response.json();
                return data.data?.logs || [];
            }
            throw new Error(`API Error: ${response.status}`);
        } catch (error) {
            console.error('Error loading bot logs:', error);
            throw error;
        }
    }

    // Clear bot logs
    async clearLogs() {
        try {
            const response = await apiRequest(`${this.baseUrl}/logs`, {
                method: 'DELETE'
            });
            return response && response.ok;
        } catch (error) {
            console.error('Error clearing logs:', error);
            throw error;
        }
    }
}

// Export instance
const discordMonitoringApi = new DiscordMonitoringApi();
