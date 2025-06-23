// Charts API Service
// Maksimal 50 baris per file

class ChartsAPIService {
    static async getTransactionData() {
        try {
            const data = await apiRequest('/admin/analytics/transactions/weekly');
            if (!data || !data.data) {
                throw new Error('Invalid response format from analytics API');
            }
            
            const apiData = data.data || [];
            return {
                labels: apiData.map(item => item.week || item.start_date || 'Unknown'),
                data: apiData.map(item => item.total_transactions || 0)
            };
        } catch (error) {
            console.error('Error fetching transaction data:', error);
            // Fallback data
            return {
                labels: ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'],
                data: [0, 0, 0, 0, 0, 0, 0]
            };
        }
    }

    static async getCategoryData() {
        try {
            const data = await apiRequest('/admin/analytics/products/categories');
            if (!data || !data.data) {
                throw new Error('Invalid response format from categories API');
            }
            
            const apiData = data.data || [];
            return {
                labels: apiData.map(item => item.category_name || item.name || 'Unknown'),
                data: apiData.map(item => item.total_sales || item.sales || item.revenue || 0)
            };
        } catch (error) {
            console.error('Error fetching category data:', error);
            // Fallback data
            return {
                labels: ['Pulsa', 'Paket Data', 'Token Listrik'],
                data: [1250, 890, 567]
            };
        }
    }
}
