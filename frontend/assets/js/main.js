// Main JavaScript untuk GameStore
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadProducts();
    setupEventListeners();
});

// Initialize aplikasi
function initializeApp() {
    // Check if user is logged in
    if (gameStoreAPI.isLoggedIn()) {
        updateUIForLoggedInUser();
    }
    
    // Setup smooth scrolling
    setupSmoothScrolling();
    
    // Setup category filters
    setupCategoryFilters();
}

// Update UI untuk user yang sudah login
async function updateUIForLoggedInUser() {
    try {
        const userResult = await gameStoreAPI.getCurrentUser();
        if (userResult.success) {
            const user = userResult.data;
            updateNavigation(user);
        }
    } catch (error) {
        console.error('Error getting user data:', error);
    }
}

// Update navigation untuk user yang login
function updateNavigation(user) {
    const navButtons = document.querySelector('.flex.items-center.space-x-4');
    navButtons.innerHTML = `
        <div class="flex items-center space-x-4">
            <span class="text-gray-700">Saldo: ${gameStoreAPI.formatCurrency(user.balance || 0)}</span>
            <div class="relative">
                <button onclick="toggleUserMenu()" class="flex items-center space-x-2 text-gray-700 hover:text-blue-600">
                    <i class="fas fa-user-circle text-xl"></i>
                    <span>${user.username}</span>
                    <i class="fas fa-chevron-down text-sm"></i>
                </button>
                <div id="userMenu" class="hidden absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 z-50">
                    <a href="pages/dashboard.html" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">
                        <i class="fas fa-tachometer-alt mr-2"></i>Dashboard
                    </a>
                    <a href="pages/wallet.html" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">
                        <i class="fas fa-wallet mr-2"></i>Wallet
                    </a>
                    <a href="#" onclick="gameStoreAPI.logout()" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">
                        <i class="fas fa-sign-out-alt mr-2"></i>Logout
                    </a>
                </div>
            </div>
        </div>
    `;
}

// Toggle user menu
function toggleUserMenu() {
    const menu = document.getElementById('userMenu');
    menu.classList.toggle('hidden');
}

// Setup smooth scrolling
function setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Setup category filters
function setupCategoryFilters() {
    const categoryButtons = document.querySelectorAll('.category-btn');
    categoryButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            categoryButtons.forEach(b => {
                b.classList.remove('active', 'bg-blue-600', 'text-white');
                b.classList.add('bg-white', 'text-gray-700');
            });
            
            // Add active class to clicked button
            this.classList.add('active', 'bg-blue-600', 'text-white');
            this.classList.remove('bg-white', 'text-gray-700');
            
            // Filter products
            const category = this.dataset.category;
            filterProducts(category);
        });
    });
}

// Setup event listeners
function setupEventListeners() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Register form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // Close modals when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('fixed') && e.target.classList.contains('inset-0')) {
            hideLogin();
            hideRegister();
        }
    });
}

// Load products dari API
async function loadProducts() {
    try {
        showLoading();
        const result = await gameStoreAPI.getPopularProducts(24);
        
        if (result.success) {
            displayProducts(result.data);
        } else {
            // Fallback ke dummy data jika API belum ready
            displayDummyProducts();
        }
    } catch (error) {
        console.error('Error loading products:', error);
        displayDummyProducts();
    } finally {
        hideLoading();
    }
}

// Display products
function displayProducts(products) {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;
    
    grid.innerHTML = products.map(product => `
        <div class="product-card bg-white rounded-lg shadow-md overflow-hidden card-hover cursor-pointer" 
             onclick="selectProduct('${product.code}', '${product.name}', ${product.price})"
             data-category="${product.category}">
            <div class="aspect-square bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <i class="fas fa-gamepad text-white text-3xl"></i>
            </div>
            <div class="p-4">
                <h3 class="font-semibold text-sm mb-1 truncate">${product.name}</h3>
                <p class="text-blue-600 font-bold text-sm">${gameStoreAPI.formatCurrency(product.price)}</p>
                <div class="mt-2">
                    <span class="inline-block bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded">
                        ${product.category}
                    </span>
                </div>
            </div>
        </div>
    `).join('');
}

// Display dummy products untuk demo
function displayDummyProducts() {
    const dummyProducts = [
        { code: 'ML_86', name: 'Mobile Legends 86 Diamond', price: 20000, category: 'game' },
        { code: 'FF_70', name: 'Free Fire 70 Diamond', price: 10000, category: 'game' },
        { code: 'PUBG_60', name: 'PUBG Mobile 60 UC', price: 15000, category: 'game' },
        { code: 'GI_60', name: 'Genshin Impact 60 Genesis', price: 15000, category: 'game' },
        { code: 'TSEL_10', name: 'Telkomsel 10K', price: 11000, category: 'pulsa' },
        { code: 'XL_10', name: 'XL 10K', price: 11000, category: 'pulsa' },
        { code: 'ISAT_10', name: 'Indosat 10K', price: 11000, category: 'pulsa' },
        { code: 'AXIS_10', name: 'Axis 10K', price: 11000, category: 'pulsa' },
        { code: 'PLN_20', name: 'PLN 20K', price: 21000, category: 'ppob' },
        { code: 'BPJS_50', name: 'BPJS 50K', price: 51000, category: 'ppob' },
        { code: 'PDAM_30', name: 'PDAM 30K', price: 31000, category: 'ppob' },
        { code: 'WIFI_100', name: 'WiFi 100K', price: 101000, category: 'ppob' }
    ];
    
    displayProducts(dummyProducts);
}

// Filter products berdasarkan kategori
function filterProducts(category) {
    const products = document.querySelectorAll('.product-card');
    
    products.forEach(product => {
        if (category === 'all' || product.dataset.category === category) {
            product.style.display = 'block';
        } else {
            product.style.display = 'none';
        }
    });
}

// Select product untuk pembelian
function selectProduct(code, name, price) {
    if (!gameStoreAPI.isLoggedIn()) {
        showLogin();
        return;
    }
    
    // Redirect ke halaman pembelian atau buka modal
    window.location.href = `pages/purchase.html?product=${code}&name=${encodeURIComponent(name)}&price=${price}`;
}

// Modal functions
function showLogin() {
    document.getElementById('loginModal').classList.remove('hidden');
}

function hideLogin() {
    document.getElementById('loginModal').classList.add('hidden');
}

function showRegister() {
    document.getElementById('registerModal').classList.remove('hidden');
}

function hideRegister() {
    document.getElementById('registerModal').classList.add('hidden');
}

// Handle login
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    if (!username || !password) {
        showNotification('Mohon isi username dan password', 'error');
        return;
    }
    
    try {
        showButtonLoading(e.target.querySelector('button[type="submit"]'));
        
        const result = await gameStoreAPI.login(username, password);
        
        if (result.success) {
            showNotification('Login berhasil!', 'success');
            hideLogin();
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        showNotification('Terjadi kesalahan saat login', 'error');
    } finally {
        hideButtonLoading(e.target.querySelector('button[type="submit"]'), 'Masuk');
    }
}

// Handle register
async function handleRegister(e) {
    e.preventDefault();
    
    const userData = {
        username: document.getElementById('regUsername').value,
        email: document.getElementById('regEmail').value,
        full_name: document.getElementById('regFullName').value,
        phone_number: document.getElementById('regPhone').value,
        password: document.getElementById('regPassword').value
    };
    
    // Validasi
    if (!userData.username || !userData.email || !userData.password) {
        showNotification('Mohon isi semua field yang wajib', 'error');
        return;
    }
    
    try {
        showButtonLoading(e.target.querySelector('button[type="submit"]'));
        
        const result = await gameStoreAPI.register(userData);
        
        if (result.success) {
            showNotification('Registrasi berhasil! Silakan login.', 'success');
            hideRegister();
            setTimeout(() => {
                showLogin();
            }, 1000);
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        showNotification('Terjadi kesalahan saat registrasi', 'error');
    } finally {
        hideButtonLoading(e.target.querySelector('button[type="submit"]'), 'Daftar');
    }
}

// Utility functions
function scrollToProducts() {
    document.getElementById('products').scrollIntoView({
        behavior: 'smooth'
    });
}

function showLoading() {
    const grid = document.getElementById('productsGrid');
    if (grid) {
        grid.innerHTML = `
            <div class="col-span-full flex justify-center items-center py-12">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <span class="ml-3 text-gray-600">Memuat produk...</span>
            </div>
        `;
    }
}

function hideLoading() {
    // Loading akan hilang saat products di-render
}

function showButtonLoading(button) {
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...';
}

function hideButtonLoading(button, originalText) {
    button.disabled = false;
    button.innerHTML = originalText;
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${
                type === 'success' ? 'fa-check-circle' :
                type === 'error' ? 'fa-exclamation-circle' :
                'fa-info-circle'
            } mr-2"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Close user menu when clicking outside
document.addEventListener('click', function(e) {
    const userMenu = document.getElementById('userMenu');
    if (userMenu && !e.target.closest('.relative')) {
        userMenu.classList.add('hidden');
    }
});
