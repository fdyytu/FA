const API_BASE_URL = '/api/v1/product-admin';
let currentProducts = [];
let editingProductId = null;

// Check authentication on page load
window.addEventListener('load', function() {
    const token = localStorage.getItem('adminToken');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    // Load initial data
    loadProducts();
});

// Logout functionality
document.getElementById('logoutBtn').addEventListener('click', function() {
    localStorage.removeItem('adminToken');
    window.location.href = 'login.html';
});

// Modal controls
document.getElementById('addProductBtn').addEventListener('click', function() {
    openProductModal();
});

document.getElementById('closeModal').addEventListener('click', closeProductModal);
document.getElementById('cancelBtn').addEventListener('click', closeProductModal);
document.getElementById('closeStockModal').addEventListener('click', closeStockModal);
document.getElementById('cancelStockBtn').addEventListener('click', closeStockModal);

// Refresh button
document.getElementById('refreshBtn').addEventListener('click', function() {
    loadProducts();
});

// Product form submission
document.getElementById('productForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    await saveProduct();
});

// Stock form submission
document.getElementById('stockForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    await uploadStock();
});

// API Helper function
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('adminToken');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    const defaultOptions = {
        headers: {
            'Authorization': `Bearer ${token}`,
            ...options.headers
        }
    };
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...defaultOptions,
        ...options
    });
    
    if (response.status === 401) {
        localStorage.removeItem('adminToken');
        window.location.href = 'login.html';
        return;
    }
    
    return response;
}

// Load products
async function loadProducts() {
    showLoading(true);
    
    try {
        const response = await apiCall('/products');
        const data = await response.json();
        
        if (response.ok && data.success) {
            currentProducts = data.data;
            renderProductsTable();
        } else {
            showMessage('Error loading products: ' + (data.message || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error loading products:', error);
        showMessage('Terjadi kesalahan saat memuat produk', 'error');
    } finally {
        showLoading(false);
    }
}

// Render products table
function renderProductsTable() {
    const tbody = document.getElementById('productsTableBody');
    const noProducts = document.getElementById('noProducts');
    const productsTable = document.getElementById('productsTable');
    
    if (currentProducts.length === 0) {
        productsTable.classList.add('hidden');
        noProducts.classList.remove('hidden');
        return;
    }
    
    productsTable.classList.remove('hidden');
    noProducts.classList.add('hidden');
    
    tbody.innerHTML = currentProducts.map(product => `
        <tr>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">${product.name}</div>
                <div class="text-sm text-gray-500">${product.description || '-'}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${product.code}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                Rp ${formatNumber(product.price)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    product.total_stock > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }">
                    ${product.total_stock || 0} item
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    product.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }">
                    ${product.is_active ? 'Aktif' : 'Nonaktif'}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <button 
                    onclick="openStockModal(${product.id}, '${product.name}')"
                    class="text-green-600 hover:text-green-900"
                    title="Upload Stock"
                >
                    <i class="fas fa-upload"></i>
                </button>
                <button 
                    onclick="editProduct(${product.id})"
                    class="text-indigo-600 hover:text-indigo-900"
                    title="Edit"
                >
                    <i class="fas fa-edit"></i>
                </button>
                <button 
                    onclick="deleteProduct(${product.id}, '${product.name}')"
                    class="text-red-600 hover:text-red-900"
                    title="Hapus"
                >
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Open product modal
function openProductModal(product = null) {
    const modal = document.getElementById('productModal');
    const modalTitle = document.getElementById('modalTitle');
    const form = document.getElementById('productForm');
    
    if (product) {
        modalTitle.textContent = 'Edit Produk';
        editingProductId = product.id;
        
        // Fill form with product data
        document.getElementById('productId').value = product.id;
        document.getElementById('productName').value = product.name;
        document.getElementById('productCode').value = product.code;
        document.getElementById('productPrice').value = product.price;
        document.getElementById('productDescription').value = product.description || '';
        document.getElementById('productActive').checked = product.is_active;
    } else {
        modalTitle.textContent = 'Tambah Produk';
        editingProductId = null;
        form.reset();
        document.getElementById('productActive').checked = true;
    }
    
    modal.classList.remove('hidden');
}

// Close product modal
function closeProductModal() {
    document.getElementById('productModal').classList.add('hidden');
    document.getElementById('productForm').reset();
    editingProductId = null;
}

// Save product
async function saveProduct() {
    const formData = new FormData(document.getElementById('productForm'));
    const productData = {
        name: formData.get('name'),
        code: formData.get('code'),
        price: parseFloat(formData.get('price')),
        description: formData.get('description') || null,
        is_active: document.getElementById('productActive').checked
    };
    
    try {
        let response;
        if (editingProductId) {
            // Update existing product
            response = await apiCall(`/products/${editingProductId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(productData)
            });
        } else {
            // Create new product
            response = await apiCall('/products', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(productData)
            });
        }
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showMessage(data.message, 'success');
            closeProductModal();
            loadProducts();
        } else {
            showMessage(data.message || 'Gagal menyimpan produk', 'error');
        }
    } catch (error) {
        console.error('Error saving product:', error);
        showMessage('Terjadi kesalahan saat menyimpan produk', 'error');
    }
}

// Edit product
function editProduct(productId) {
    const product = currentProducts.find(p => p.id === productId);
    if (product) {
        openProductModal(product);
    }
}

// Delete product
async function deleteProduct(productId, productName) {
    if (!confirm(`Apakah Anda yakin ingin menghapus produk "${productName}"?`)) {
        return;
    }
    
    try {
        const response = await apiCall(`/products/${productId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showMessage(data.message, 'success');
            loadProducts();
        } else {
            showMessage(data.message || 'Gagal menghapus produk', 'error');
        }
    } catch (error) {
        console.error('Error deleting product:', error);
        showMessage('Terjadi kesalahan saat menghapus produk', 'error');
    }
}

// Open stock modal
function openStockModal(productId, productName) {
    document.getElementById('stockProductId').value = productId;
    document.getElementById('stockProductName').textContent = productName;
    document.getElementById('stockModal').classList.remove('hidden');
}

// Close stock modal
function closeStockModal() {
    document.getElementById('stockModal').classList.add('hidden');
    document.getElementById('stockForm').reset();
}

// Upload stock
async function uploadStock() {
    const formData = new FormData();
    const productId = document.getElementById('stockProductId').value;
    const file = document.getElementById('stockFile').files[0];
    const notes = document.getElementById('stockNotes').value;
    
    if (!file) {
        showMessage('Pilih file untuk diupload', 'error');
        return;
    }
    
    formData.append('file', file);
    if (notes) {
        formData.append('notes', notes);
    }
    
    try {
        const response = await apiCall(`/products/${productId}/stock/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showMessage(data.message, 'success');
            closeStockModal();
            loadProducts();
        } else {
            showMessage(data.message || 'Gagal upload stock', 'error');
        }
    } catch (error) {
        console.error('Error uploading stock:', error);
        showMessage('Terjadi kesalahan saat upload stock', 'error');
    }
}

// Show loading state
function showLoading(show) {
    const loading = document.getElementById('loadingProducts');
    const table = document.getElementById('productsTable');
    
    if (show) {
        loading.classList.remove('hidden');
        table.classList.add('hidden');
    } else {
        loading.classList.add('hidden');
        table.classList.remove('hidden');
    }
}

// Show message
function showMessage(message, type = 'info') {
    const container = document.getElementById('messageContainer');
    const messageId = 'msg-' + Date.now();
    
    const bgColor = type === 'success' ? 'bg-green-500' : 
                   type === 'error' ? 'bg-red-500' : 'bg-blue-500';
    
    const icon = type === 'success' ? 'fa-check-circle' : 
                type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
    
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `${bgColor} text-white px-4 py-3 rounded-lg shadow-lg mb-2 flex items-center space-x-2 transform transition-all duration-300 translate-x-full`;
    messageDiv.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
        <button onclick="removeMessage('${messageId}')" class="ml-2 text-white hover:text-gray-200">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(messageDiv);
    
    // Animate in
    setTimeout(() => {
        messageDiv.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        removeMessage(messageId);
    }, 5000);
}

// Remove message
function removeMessage(messageId) {
    const messageDiv = document.getElementById(messageId);
    if (messageDiv) {
        messageDiv.classList.add('translate-x-full');
        setTimeout(() => {
            messageDiv.remove();
        }, 300);
    }
}

// Format number with thousand separators
function formatNumber(num) {
    return new Intl.NumberFormat('id-ID').format(num);
}
