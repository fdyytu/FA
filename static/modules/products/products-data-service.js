// Products Data Service
class ProductsDataService {
    constructor() {
        this.data = {
            stats: {},
            products: [],
            categories: [],
            currentPage: 1,
            itemsPerPage: 12,
            totalItems: 0
        };
    }

    async loadProductStats() {
        try {
            const response = await apiClient.get('/products/stats');
            
            if (response && response.ok) {
                const data = await response.json();
                this.data.stats = data.data || data;
            } else {
                this.data.stats = this.generateMockStats();
            }
            return this.data.stats;
        } catch (error) {
            console.error('Error loading product stats:', error);
            this.data.stats = this.generateMockStats();
            return this.data.stats;
        }
    }

    generateMockStats() {
        return {
            total_products: 156,
            active_products: 142,
            out_of_stock: 8,
            low_stock: 6
        };
    }

    async loadProducts(page = 1, search = '', category = '') {
        try {
            const params = new URLSearchParams({
                page: page,
                limit: this.data.itemsPerPage,
                search: search,
                category: category
            });
            
            const response = await apiClient.get(`/products?${params}`);
            
            if (response && response.ok) {
                const data = await response.json();
                this.data.products = data.data || [];
                this.data.totalItems = data.total || 0;
                this.data.currentPage = page;
            } else {
                this.data.products = this.generateMockProducts();
                this.data.totalItems = this.data.products.length;
            }
            return {
                products: this.data.products,
                total: this.data.totalItems,
                currentPage: this.data.currentPage
            };
        } catch (error) {
            console.error('Error loading products:', error);
            this.data.products = this.generateMockProducts();
            this.data.totalItems = this.data.products.length;
            return {
                products: this.data.products,
                total: this.data.totalItems,
                currentPage: this.data.currentPage
            };
        }
    }

    generateMockProducts() {
        return [
            { id: 1, name: 'Product 1', price: 50000, stock: 10, category: 'Electronics' },
            { id: 2, name: 'Product 2', price: 75000, stock: 5, category: 'Clothing' }
        ];
    }
}

const productsDataService = new ProductsDataService();
