// Products Data Handler
// Maksimal 50 baris per file

class ProductsDataHandler {
    constructor() {
        this.products = [];
        this.filteredProducts = [];
    }

    // Set products data
    setProducts(products) {
        this.products = products;
        this.filteredProducts = [...products];
    }

    // Get products
    getProducts() {
        return this.products;
    }

    // Get filtered products
    getFilteredProducts() {
        return this.filteredProducts;
    }

    // Filter products
    filterProducts(searchTerm = '', categoryFilter = '', statusFilter = '') {
        this.filteredProducts = this.products.filter(product => {
            const matchesSearch = !searchTerm || 
                product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                product.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
                product.provider.toLowerCase().includes(searchTerm.toLowerCase());
                
            const matchesCategory = !categoryFilter || product.category === categoryFilter;
            const matchesStatus = !statusFilter || product.status === statusFilter;
            
            return matchesSearch && matchesCategory && matchesStatus;
        });
        
        return this.filteredProducts;
    }

    // Get selected products
    getSelectedProducts() {
        const selectedIds = Array.from(document.querySelectorAll('.product-checkbox:checked'))
            .map(checkbox => parseInt(checkbox.value));
        
        return this.products.filter(product => selectedIds.includes(product.id));
    }

    // Find product by ID
    findProductById(productId) {
        return this.products.find(p => p.id === productId);
    }
}

// Export instance
window.productsDataHandler = new ProductsDataHandler();
