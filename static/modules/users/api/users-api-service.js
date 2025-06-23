// Users API Service
// Menangani semua komunikasi API untuk users

class UsersApiService {
    constructor() {
        this.baseUrl = '/api/v1';
    }

    // Load user statistics
    async loadUserStats() {
        try {
            const response = await apiRequest(`${this.baseUrl}/admin/dashboard/stats/users`);
            
            if (response && response.ok) {
                const data = await response.json();
                return data.data || data;
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading user stats:', error);
            return {
                total_users: 0,
                active_users: 0,
                premium_users: 0,
                new_users_today: 0
            };
        }
    }

    // Load users list
    async loadUsers() {
        try {
            const response = await apiRequest(`${this.baseUrl}/users`);
            
            if (response && response.ok) {
                const data = await response.json();
                return data.data || [];
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading users:', error);
            return [];
        }
    }

    // Update user status
    async updateUserStatus(userId, status) {
        try {
            const response = await apiRequest(`${this.baseUrl}/users/${userId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status })
            });
            
            if (response && response.ok) {
                return await response.json();
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error updating user status:', error);
            throw error;
        }
    }

    // Delete user
    async deleteUser(userId) {
        try {
            const response = await apiRequest(`${this.baseUrl}/users/${userId}`, {
                method: 'DELETE'
            });
            
            if (response && response.ok) {
                return await response.json();
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            throw error;
        }
    }

    // Get user details
    async getUserDetails(userId) {
        try {
            const response = await apiRequest(`${this.baseUrl}/users/${userId}`);
            
            if (response && response.ok) {
                return await response.json();
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error getting user details:', error);
            throw error;
        }
    }

    // Update user
    async updateUser(userId, userData) {
        try {
            const response = await apiRequest(`${this.baseUrl}/users/${userId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });
            
            if (response && response.ok) {
                return await response.json();
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error updating user:', error);
            throw error;
        }
    }

    // Search users
    async searchUsers(query) {
        try {
            const response = await apiRequest(`${this.baseUrl}/users/search?q=${encodeURIComponent(query)}`);
            
            if (response && response.ok) {
                const data = await response.json();
                return data.data || [];
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error searching users:', error);
            return [];
        }
    }
}

// Export instance
window.usersApiService = new UsersApiService();
