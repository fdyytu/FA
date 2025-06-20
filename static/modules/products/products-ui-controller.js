// Products UI Controller
class ProductsUIController {
    constructor() {
        this.elements = {};
        this.initElements();
    }

    initElements() {
        this.elements = {
            totalProducts: document.getElementById('totalProducts'),
            activeProducts: document.getElementById('activeProducts'),
            outOfStock: document.getElementById('outOfStock'),
            lowStock: document.getElementById('lowStock'),
            productsList: document.getElementById('productsList'),
            pagination: document.getElementById('productsPagination'),
            searchInput: document.getElementById('productsSearch'),
            categoryFilter: document.getElementById('categoryFilter')
        };
    }

    updateProductStats(stats) {
        if (this.elements.totalProducts) {
            this.elements.totalProducts.textContent = Formatters.formatNumber(stats.total_products || 0);
        }
        
        if (this.elements.activeProducts) {
            this.elements.activeProducts.textContent = Formatters.formatNumber(stats.active_products || 0);
        }
        
        if (this.elements.outOfStock) {
            this.elements.outOfStock.textContent = Formatters.formatNumber(stats.out_of_stock || 0);
        }
        
        if (this.elements.lowStock) {
            this.elements.lowStock.textContent = Formatters.formatNumber(stats.low_stock || 0);
        }
    }

    renderProductsList(products) {
        if (!this.elements.productsList) return;
        
        this.elements.productsList.innerHTML = products.map(product => `
            <div class="bg-white rounded-lg shadow-md overflow-hidden">
                <div class="p-4">
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">${product.name}</h3>
                    <p class="text-gray-600 mb-2">Category: ${product.category}</p>
                    <div class="flex justify-between items-center">
                        <span class="text-xl font-bold text-green-600">
                            ${Formatters.formatCurrency(product.price)}
                        </span>
                        <span class="text-sm ${product.stock > 10 ? 'text-green-600' : product.stock > 0 ? 'text-yellow-600' : 'text-red-600'}">
                            Stock: ${product.stock}
                        </span>
                    </div>
                    <div class="mt-3 flex space-x-2">
                        <button onclick="editProduct(${product.id})" class="text-blue-600 hover:text-blue-800">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button onclick="deleteProduct(${product.id})" class="text-red-600 hover:text-red-800">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }
}

const productsUIController = new ProductsUIController();
