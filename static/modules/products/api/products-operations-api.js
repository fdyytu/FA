// Products Operations API Service
// Maksimal 50 baris per file

class ProductsOperationsApi {
    constructor() {
        this.baseUrl = '/api/v1';
    }

    // Delete product
    async deleteProduct(productId) {
        const response = await apiRequest(`/products/${productId}`, {
            method: 'DELETE'
        });
        return response;
    }

    // Upload stock
    async uploadStock(formData) {
        const response = await apiRequest('/products/upload-stock', {
            method: 'POST',
            body: formData,
            headers: {} // Remove Content-Type to let browser set it for FormData
        });
        return response;
    }

    // Import products
    async importProducts(formData) {
        const response = await apiRequest('/products/import', {
            method: 'POST',
            body: formData,
            headers: {} // Remove Content-Type for FormData
        });
        return response;
    }

    // Bulk operations
    async bulkDelete(productIds) {
        const response = await apiRequest('/products/bulk-delete', {
            method: 'POST',
            body: JSON.stringify({ product_ids: productIds })
        });
        return response;
    }

    // Update product status
    async updateProductStatus(productId, status) {
        const response = await apiRequest(`/products/${productId}/status`, {
            method: 'PATCH',
            body: JSON.stringify({ status: status })
        });
        return response;
    }
}

// Export instance
window.productsOperationsApi = new ProductsOperationsApi();
