// Products API Service
// Maksimal 50 baris per file

class ProductsApiService {
    constructor() {
        this.baseUrl = '/api/v1';
    }

    // Load product statistics
    async loadProductStats() {
        try {
            const response = await apiRequest('/api/v1/admin/dashboard/stats/products');
            
            if (response && response.ok) {
                const data = await response.json();
                return data.data || data;
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading product stats:', error);
            throw error;
        }
    }

    // Load products
    async loadProducts() {
        try {
            const response = await apiRequest('/api/v1/products');
            
            if (response && response.ok) {
                const data = await response.json();
                return data.data || [];
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading products:', error);
            throw error;
        }
    }

    // Save product (create or update)
    async saveProduct(productData) {
        const isEdit = productData.id;
        const endpoint = isEdit ? `/products/${productData.id}` : '/products';
        const method = isEdit ? 'PUT' : 'POST';
        
        const response = await apiRequest(endpoint, {
            method: method,
            body: JSON.stringify(productData)
        });
        
        return response;
    }
}

// Export instance
window.productsApiService = new ProductsApiService();
