// Android Dashboard API Service
// Maksimal 50 baris per file

const API_BASE_URL = '/api/v1/admin';

class AndroidAPIService {
    static async loadDashboardStats() {
        const token = localStorage.getItem('adminToken');
        
        try {
            const response = await fetch(`${API_BASE_URL}/dashboard/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.stats) {
                    return data.stats;
                } else {
                    throw new Error('Invalid response format');
                }
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
            // Return default empty values
            return {
                total_users: 0,
                total_transactions: 0,
                total_products: 0,
                total_revenue: 0
            };
        }
    }

    static async loadRecentTransactions() {
        const token = localStorage.getItem('adminToken');
        
        try {
            const response = await fetch(`${API_BASE_URL}/dashboard/recent-activities`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.data?.activities || [];
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading recent transactions:', error);
            return [];
        }
    }
}

window.AndroidAPIService = AndroidAPIService;
