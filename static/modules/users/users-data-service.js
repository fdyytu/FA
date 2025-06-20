// Users Data Service
class UsersDataService {
    constructor() {
        this.data = {
            stats: {},
            users: [],
            currentPage: 1,
            itemsPerPage: 10,
            totalItems: 0
        };
    }

    async loadUserStats() {
        try {
            const response = await apiClient.get('/users/stats');
            
            if (response && response.ok) {
                const data = await response.json();
                this.data.stats = data.data || data;
            } else {
                this.data.stats = this.generateMockStats();
            }
            return this.data.stats;
        } catch (error) {
            console.error('Error loading user stats:', error);
            this.data.stats = this.generateMockStats();
            return this.data.stats;
        }
    }

    generateMockStats() {
        return {
            total_users: 1250,
            active_users: 892,
            premium_users: 156,
            new_users_today: 23
        };
    }

    async loadUsers(page = 1, search = '') {
        try {
            const response = await apiClient.get(`/users?page=${page}&search=${search}&limit=${this.data.itemsPerPage}`);
            
            if (response && response.ok) {
                const data = await response.json();
                this.data.users = data.data || [];
                this.data.totalItems = data.total || 0;
                this.data.currentPage = page;
            } else {
                this.data.users = this.generateMockUsers();
                this.data.totalItems = this.data.users.length;
            }
            return {
                users: this.data.users,
                total: this.data.totalItems,
                currentPage: this.data.currentPage
            };
        } catch (error) {
            console.error('Error loading users:', error);
            this.data.users = this.generateMockUsers();
            this.data.totalItems = this.data.users.length;
            return {
                users: this.data.users,
                total: this.data.totalItems,
                currentPage: this.data.currentPage
            };
        }
    }

    generateMockUsers() {
        return [
            { id: 1, username: 'user1', email: 'user1@example.com', status: 'active', created_at: '2024-01-01' },
            { id: 2, username: 'user2', email: 'user2@example.com', status: 'inactive', created_at: '2024-01-02' }
        ];
    }
}

const usersDataService = new UsersDataService();
