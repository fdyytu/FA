// Mock Data untuk testing dan development
class MockDataService {
    constructor() {
        this.mockEnabled = false; // Set to true untuk menggunakan mock data
    }

    // Mock dashboard stats
    getMockDashboardStats() {
        return {
            total_users: 1250,
            total_transactions: 3420,
            total_products: 156,
            total_revenue: 45000000
        };
    }

    // Mock Discord stats
    getMockDiscordStats() {
        return {
            total_bots: 5,
            discord_users: 2340,
            live_products: 89,
            commands_today: 1234
        };
    }

    // Mock recent transactions
    getMockRecentTransactions() {
        return [
            {
                id: 1,
                user: 'John Doe',
                username: 'johndoe',
                product: 'Mobile Legends Diamonds',
                product_name: 'Mobile Legends Diamonds',
                amount: 50000,
                status: 'success',
                created_at: new Date(Date.now() - 1000 * 60 * 5).toISOString() // 5 minutes ago
            },
            {
                id: 2,
                user: 'Jane Smith',
                username: 'janesmith',
                product: 'Free Fire Diamonds',
                product_name: 'Free Fire Diamonds',
                amount: 25000,
                status: 'pending',
                created_at: new Date(Date.now() - 1000 * 60 * 15).toISOString() // 15 minutes ago
            },
            {
                id: 3,
                user: 'Bob Wilson',
                username: 'bobwilson',
                product: 'PUBG UC',
                product_name: 'PUBG UC',
                amount: 75000,
                status: 'success',
                created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString() // 30 minutes ago
            }
        ];
    }

    // Mock Discord bots
    getMockDiscordBots() {
        return [
            {
                id: 1,
                name: 'FA Bot Main',
                prefix: '!',
                token: 'hidden',
                status: 'online',
                uptime: '2h 30m',
                commands_count: 45,
                is_active: true,
                auto_start: true
            },
            {
                id: 2,
                name: 'FA Bot Secondary',
                prefix: '$',
                token: 'hidden',
                status: 'offline',
                uptime: '0m',
                commands_count: 12,
                is_active: false,
                auto_start: false
            }
        ];
    }

    // Mock Discord worlds
    getMockDiscordWorlds() {
        return [
            {
                id: 1,
                name: 'WORLD1',
                owner: 'ADMIN',
                bot_id: 1,
                is_active: true
            },
            {
                id: 2,
                name: 'WORLD2',
                owner: 'MODERATOR',
                bot_id: 1,
                is_active: true
            }
        ];
    }

    // Mock recent commands
    getMockRecentCommands() {
        return [
            {
                id: 1,
                command: '!buy diamonds',
                user: 'user123',
                bot: 'FA Bot Main',
                timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
                status: 'success'
            },
            {
                id: 2,
                command: '!balance',
                user: 'user456',
                bot: 'FA Bot Main',
                timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
                status: 'success'
            }
        ];
    }

    // Mock bot logs
    getMockBotLogs() {
        return [
            {
                id: 1,
                level: 'INFO',
                message: 'Bot started successfully',
                bot: 'FA Bot Main',
                timestamp: new Date(Date.now() - 1000 * 60 * 10).toISOString()
            },
            {
                id: 2,
                level: 'ERROR',
                message: 'Failed to connect to database',
                bot: 'FA Bot Secondary',
                timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString()
            }
        ];
    }

    // Check if mock is enabled
    isMockEnabled() {
        return this.mockEnabled || localStorage.getItem('useMockData') === 'true';
    }

    // Enable/disable mock data
    setMockEnabled(enabled) {
        this.mockEnabled = enabled;
        localStorage.setItem('useMockData', enabled.toString());
    }

    // Generic mock response wrapper
    createMockResponse(data, delay = 100) {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    ok: true,
                    status: 200,
                    data: data,
                    json: () => Promise.resolve({ data: data })
                });
            }, delay);
        });
    }
}

// Global instance
const mockDataService = new MockDataService();

// Export untuk penggunaan global
window.MockDataService = MockDataService;
window.mockDataService = mockDataService;
