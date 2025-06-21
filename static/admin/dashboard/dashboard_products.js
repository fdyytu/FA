// Dashboard products functionality
let currentPage = 1;
let itemsPerPage = 10;
let totalItems = 0;
let products = [];
let filteredProducts = [];

// Initialize products dashboard
async function initProductsDashboard() {
    const token = checkAuth();
    if (!token) return;

    showLoading(true);
    
    try {
        await Promise.all([
            loadProductStats(),
            loadProducts()
        ]);
        
        initEventListeners();
        showToast('Dashboard produk berhasil dimuat', 'success', 3000);
    } catch (error) {
        console.error('Error loading products dashboard:', error);
        showToast('Gagal memuat data produk', 'error');
    } finally {
        showLoading(false);
    }
}

// Load product statistics
async function loadProductStats() {
    try {
        const response = await apiRequest('/api/v1/admin/dashboard/stats/products');
        
        if (response && response.ok) {
            const data = await response.json();
            updateProductStats(data.data || data);
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
    } catch (error) {
        console.error('Error loading product stats:', error);
        showError('Gagal memuat statistik produk');
        updateProductStats({
            total_products: 0,
            active_products: 0,
            low_stock_products: 0,
            total_categories: 0
        });
    }
}

// Update product statistics cards
function updateProductStats(stats) {
    const elements = {
        totalProducts: document.getElementById('totalProducts'),
        activeProducts: document.getElementById('activeProducts'),
        lowStockProducts: document.getElementById('lowStockProducts'),
        totalCategories: document.getElementById('totalCategories')
    };
    
    if (elements.totalProducts) {
        elements.totalProducts.textContent = formatNumber(stats.total_products || 0);
    }
    
    if (elements.activeProducts) {
        elements.activeProducts.textContent = formatNumber(stats.active_products || 0);
    }
    
    if (elements.lowStockProducts) {
        elements.lowStockProducts.textContent = formatNumber(stats.low_stock_products || 0);
    }
    
    if (elements.totalCategories) {
        elements.totalCategories.textContent = formatNumber(stats.total_categories || 0);
    }
}

// Load products
async function loadProducts() {
    const loadingElement = document.getElementById('loadingProducts');
    const tableContainer = document.getElementById('productsTableContainer');
    
    if (loadingElement) loadingElement.classList.remove('hidden');
    if (tableContainer) tableContainer.classList.add('hidden');
    
    try {
        const response = await apiRequest('/api/v1/products');
        
        if (response && response.ok) {
            const data = await response.json();
            products = data.data || [];
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
        
        filteredProducts = [...products];
        totalItems = filteredProducts.length;
        renderProductsTable();
        updatePagination();
        
    } catch (error) {
        console.error('Error loading products:', error);
        products = [];
        filteredProducts = [];
        totalItems = 0;
        renderProductsTable();
        updatePagination();
    } finally {
        if (loadingElement) loadingElement.classList.add('hidden');
        if (tableContainer) tableContainer.classList.remove('hidden');
    }
}

// Render products table
function renderProductsTable() {
    const tbody = document.getElementById('productsTableBody');
    if (!tbody) return;
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageProducts = filteredProducts.slice(startIndex, endIndex);
    
    tbody.innerHTML = pageProducts.map(product => `
        <tr class="table-row">
            <td class="px-6 py-4 whitespace-nowrap">
                <input type="checkbox" class="product-checkbox rounded border-gray-300" value="${product.id}">
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                        <div class="h-10 w-10 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                            <i class="fas fa-box text-white text-sm"></i>
                        </div>
                    </div>
                    <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">${product.name}</div>
                        <div class="text-sm text-gray-500">${product.code}</div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    ${product.category.replace('_', ' ').toUpperCase()}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">${formatCurrency(product.price)}</div>
                ${product.price_wl ? `<div class="text-xs text-gray-500">WL: ${formatCurrency(product.price_wl)}</div>` : ''}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">${formatNumber(product.stock_quantity)}</div>
                ${product.stock_quantity < 10 ? '<div class="text-xs text-red-500">Stok rendah</div>' : ''}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${getStatusBadge(product.status)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                    <button onclick="editProduct(${product.id})" class="text-blue-600 hover:text-blue-900" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="uploadStock(${product.id})" class="text-green-600 hover:text-green-900" title="Upload Stock">
                        <i class="fas fa-upload"></i>
                    </button>
                    <button onclick="deleteProduct(${product.id})" class="text-red-600 hover:text-red-900" title="Hapus">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    updateTableInfo();
}

// Update table pagination info
function updateTableInfo() {
    const showingFrom = document.getElementById('showingFrom');
    const showingTo = document.getElementById('showingTo');
    const totalItemsElement = document.getElementById('totalItems');
    
    const startIndex = (currentPage - 1) * itemsPerPage + 1;
    const endIndex = Math.min(currentPage * itemsPerPage, totalItems);
    
    if (showingFrom) showingFrom.textContent = startIndex;
    if (showingTo) showingTo.textContent = endIndex;
    if (totalItemsElement) totalItemsElement.textContent = totalItems;
}

// Update pagination
function updatePagination() {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const pageNumbers = document.getElementById('pageNumbers');
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    
    // Update prev/next buttons
    if (prevBtn) {
        prevBtn.disabled = currentPage === 1;
        prevBtn.onclick = () => {
            if (currentPage > 1) {
                currentPage--;
                renderProductsTable();
                updatePagination();
            }
        };
    }
    
    if (nextBtn) {
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.onclick = () => {
            if (currentPage < totalPages) {
                currentPage++;
                renderProductsTable();
                updatePagination();
            }
        };
    }
    
    // Generate page numbers
    if (pageNumbers) {
        let paginationHTML = '';
        const maxVisiblePages = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage < maxVisiblePages - 1) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <button onclick="goToPage(${i})" 
                        class="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 ${i === currentPage ? 'bg-blue-500 text-white border-blue-500' : ''}">
                    ${i}
                </button>
            `;
        }
        
        pageNumbers.innerHTML = paginationHTML;
    }
}

// Go to specific page
function goToPage(page) {
    currentPage = page;
    renderProductsTable();
    updatePagination();
}

// Filter products
function filterProducts() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const categoryFilter = document.getElementById('categoryFilter')?.value || '';
    const statusFilter = document.getElementById('statusFilter')?.value || '';
    
    filteredProducts = products.filter(product => {
        const matchesSearch = !searchTerm || 
            product.name.toLowerCase().includes(searchTerm) ||
            product.code.toLowerCase().includes(searchTerm) ||
            product.provider.toLowerCase().includes(searchTerm);
            
        const matchesCategory = !categoryFilter || product.category === categoryFilter;
        const matchesStatus = !statusFilter || product.status === statusFilter;
        
        return matchesSearch && matchesCategory && matchesStatus;
    });
    
    totalItems = filteredProducts.length;
    currentPage = 1;
    renderProductsTable();
    updatePagination();
}

// Initialize event listeners
function initEventListeners() {
    // Search and filters
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const statusFilter = document.getElementById('statusFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterProducts, 300));
    }
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterProducts);
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', filterProducts);
    }
    
    // Buttons
    const addProductBtn = document.getElementById('addProductBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    const exportBtn = document.getElementById('exportBtn');
    const importBtn = document.getElementById('importBtn');
    
    if (addProductBtn) {
        addProductBtn.addEventListener('click', () => openProductModal());
    }
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshProducts);
    }
    
    if (exportBtn) {
        exportBtn.addEventListener('click', exportProducts);
    }
    
    if (importBtn) {
        importBtn.addEventListener('click', importProducts);
    }
    
    // Modal event listeners
    initModalEventListeners();
    
    // Select all checkbox
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', toggleSelectAll);
    }
}

// Initialize modal event listeners
function initModalEventListeners() {
    // Product modal
    const productForm = document.getElementById('productForm');
    const cancelProductBtn = document.getElementById('cancelProductBtn');
    
    if (productForm) {
        productForm.addEventListener('submit', handleProductSubmit);
    }
    
    if (cancelProductBtn) {
        cancelProductBtn.addEventListener('click', () => closeModal('productModal'));
    }
    
    // Stock modal
    const stockForm = document.getElementById('stockForm');
    const cancelStockBtn = document.getElementById('cancelStockBtn');
    
    if (stockForm) {
        stockForm.addEventListener('submit', handleStockSubmit);
    }
    
    if (cancelStockBtn) {
        cancelStockBtn.addEventListener('click', () => closeModal('stockModal'));
    }
}

// Open product modal
function openProductModal(productId = null) {
    const modal = document.getElementById('productModal');
    const modalTitle = document.getElementById('modalTitle');
    const form = document.getElementById('productForm');
    
    if (!modal || !form) return;
    
    // Reset form
    form.reset();
    
    if (productId) {
        // Edit mode
        const product = products.find(p => p.id === productId);
        if (product) {
            modalTitle.textContent = 'Edit Produk';
            populateProductForm(product);
        }
    } else {
        // Add mode
        modalTitle.textContent = 'Tambah Produk';
    }
    
    openModal('productModal');
}

// Populate product form
function populateProductForm(product) {
    const fields = {
        productId: product.id,
        productName: product.name,
        productCode: product.code,
        productCategory: product.category,
        productProvider: product.provider,
        productPrice: product.price,
        productPriceWL: product.price_wl,
        productStock: product.stock_quantity,
        productDescription: product.description,
        productActive: product.is_active,
        productFeatured: product.is_featured
    };
    
    Object.entries(fields).forEach(([fieldId, value]) => {
        const element = document.getElementById(fieldId);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = value;
            } else {
                element.value = value || '';
            }
        }
    });
}

// Handle product form submission
async function handleProductSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const productData = Object.fromEntries(formData.entries());
    
    // Convert checkboxes
    productData.is_active = formData.has('is_active');
    productData.is_featured = formData.has('is_featured');
    
    // Convert numbers
    productData.price = parseFloat(productData.price);
    productData.price_wl = parseFloat(productData.price_wl) || null;
    productData.stock_quantity = parseInt(productData.stock_quantity);
    
    showLoading(true);
    
    try {
        const isEdit = productData.id;
        const endpoint = isEdit ? `/products/${productData.id}` : '/products';
        const method = isEdit ? 'PUT' : 'POST';
        
        const response = await apiRequest(endpoint, {
            method: method,
            body: JSON.stringify(productData)
        });
        
        if (response && response.ok) {
            showToast(`Produk berhasil ${isEdit ? 'diperbarui' : 'ditambahkan'}`, 'success');
            closeModal('productModal');
            await loadProducts();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal menyimpan produk', 'error');
        }
    } catch (error) {
        console.error('Error saving product:', error);
        showToast('Terjadi kesalahan saat menyimpan produk', 'error');
    } finally {
        showLoading(false);
    }
}

// Edit product
function editProduct(productId) {
    openProductModal(productId);
}

// Delete product
async function deleteProduct(productId) {
    if (!confirm('Apakah Anda yakin ingin menghapus produk ini?')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await apiRequest(`/products/${productId}`, {
            method: 'DELETE'
        });
        
        if (response && response.ok) {
            showToast('Produk berhasil dihapus', 'success');
            await loadProducts();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal menghapus produk', 'error');
        }
    } catch (error) {
        console.error('Error deleting product:', error);
        showToast('Terjadi kesalahan saat menghapus produk', 'error');
    } finally {
        showLoading(false);
    }
}

// Upload stock
function uploadStock(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    document.getElementById('stockProductId').value = productId;
    document.getElementById('stockProductName').textContent = product.name;
    
    openModal('stockModal');
}

// Handle stock form submission
async function handleStockSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    
    showLoading(true);
    
    try {
        const response = await apiRequest('/products/upload-stock', {
            method: 'POST',
            body: formData,
            headers: {} // Remove Content-Type to let browser set it for FormData
        });
        
        if (response && response.ok) {
            showToast('Stok berhasil diupload', 'success');
            closeModal('stockModal');
            await loadProducts();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal mengupload stok', 'error');
        }
    } catch (error) {
        console.error('Error uploading stock:', error);
        showToast('Terjadi kesalahan saat mengupload stok', 'error');
    } finally {
        showLoading(false);
    }
}

// Toggle select all
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const productCheckboxes = document.querySelectorAll('.product-checkbox');
    
    productCheckboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
}

// Refresh products
async function refreshProducts() {
    showLoading(true);
    try {
        await Promise.all([
            loadProductStats(),
            loadProducts()
        ]);
        showToast('Data produk berhasil diperbarui', 'success', 3000);
    } catch (error) {
        showToast('Gagal memperbarui data produk', 'error');
    } finally {
        showLoading(false);
    }
}

// Export products
function exportProducts() {
    const selectedProducts = getSelectedProducts();
    const dataToExport = selectedProducts.length > 0 ? selectedProducts : filteredProducts;
    
    const csv = convertToCSV(dataToExport);
    downloadCSV(csv, 'products.csv');
    
    showToast(`${dataToExport.length} produk berhasil diekspor`, 'success');
}

// Import products
function importProducts() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv,.xlsx,.xls';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('file', file);
        
        showLoading(true);
        
        try {
            const response = await apiRequest('/products/import', {
                method: 'POST',
                body: formData,
                headers: {} // Remove Content-Type for FormData
            });
            
            if (response && response.ok) {
                const result = await response.json();
                showToast(`${result.imported_count || 0} produk berhasil diimpor`, 'success');
                await loadProducts();
            } else {
                const errorData = await response.json();
                showToast(errorData.message || 'Gagal mengimpor produk', 'error');
            }
        } catch (error) {
            console.error('Error importing products:', error);
            showToast('Terjadi kesalahan saat mengimpor produk', 'error');
        } finally {
            showLoading(false);
        }
    };
    
    input.click();
}

// Get selected products
function getSelectedProducts() {
    const selectedIds = Array.from(document.querySelectorAll('.product-checkbox:checked'))
        .map(checkbox => parseInt(checkbox.value));
    
    return products.filter(product => selectedIds.includes(product.id));
}

// Convert data to CSV
function convertToCSV(data) {
    if (data.length === 0) return '';
    
    const headers = ['ID', 'Nama', 'Kode', 'Kategori', 'Provider', 'Harga', 'Harga WL', 'Stok', 'Status', 'Aktif', 'Unggulan'];
    const rows = data.map(product => [
        product.id,
        product.name,
        product.code,
        product.category,
        product.provider,
        product.price,
        product.price_wl || '',
        product.stock_quantity,
        product.status,
        product.is_active ? 'Ya' : 'Tidak',
        product.is_featured ? 'Ya' : 'Tidak'
    ]);
    
    const csvContent = [headers, ...rows]
        .map(row => row.map(field => `"${field}"`).join(','))
        .join('\n');
    
    return csvContent;
}

// Download CSV file
function downloadCSV(csvContent, filename) {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', () => {
    initProductsDashboard();
});
