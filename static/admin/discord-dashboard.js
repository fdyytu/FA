// Enhanced Discord Bot Admin Dashboard JavaScript
class DiscordDashboard {
    constructor() {
        this.apiBase = '/api/v1/discord';
        this.currentTab = 'bots';
        this.data = {
            bots: [],
            products: [],
            worlds: [],
            users: [],
            stats: {}
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadInitialData();
    }
    
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadInitialData();
        });
        
        // Modal controls
        this.setupModalControls();
        
        // Form submissions
        this.setupFormSubmissions();
        
        // User filter
        document.getElementById('userFilter').addEventListener('change', (e) => {
            this.filterUsers(e.target.value);
        });
    }
    
    setupModalControls() {
        // Add Bot Modal
        document.getElementById('addBotBtn').addEventListener('click', () => {
            this.showModal('addBotModal');
        });
        document.getElementById('cancelAddBot').addEventListener('click', () => {
            this.hideModal('addBotModal');
        });
        
        // Add Product Modal
        document.getElementById('addProductBtn').addEventListener('click', () => {
            this.populateBotSelect();
            this.showModal('addProductModal');
        });
        document.getElementById('cancelAddProduct').addEventListener('click', () => {
            this.hideModal('addProductModal');
        });
        
        // Add World Modal
        document.getElementById('addWorldBtn').addEventListener('click', () => {
            this.showModal('addWorldModal');
        });
        document.getElementById('cancelAddWorld').addEventListener('click', () => {
            this.hideModal('addWorldModal');
        });
    }
    
    setupFormSubmissions() {
        // Add Bot Form
        document.getElementById('addBotForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.submitBotForm(e.target);
        });
        
        // Add Product Form
        document.getElementById('addProductForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.submitProductForm(e.target);
        });
        
        // Add World Form
        document.getElementById('addWorldForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.submitWorldForm(e.target);
        });
    }
    
    async loadInitialData() {
        this.showLoading();
        try {
            await Promise.all([
                this.loadStats(),
                this.loadBots(),
                this.loadProducts(),
                this.loadWorlds(),
                this.loadUsers()
            ]);
            this.renderCurrentTab();
        } catch (error) {
            this.showError('Failed to load data: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    async loadStats() {
        try {
            const response = await fetch(`${this.apiBase}/stats`);
            const result = await response.json();
            if (result.success) {
                this.data.stats = result.data;
                this.renderStats();
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    async loadBots() {
        try {
            const response = await fetch(`${this.apiBase}/bots`);
            const result = await response.json();
            if (result.success) {
                this.data.bots = result.data.bots;
            }
        } catch (error) {
            console.error('Error loading bots:', error);
        }
    }
    
    async loadProducts() {
        try {
            const response = await fetch(`${this.apiBase}/live-stocks`);
            const result = await response.json();
            if (result.success) {
                this.data.products = result.data.stocks;
            }
        } catch (error) {
            console.error('Error loading products:', error);
        }
    }
    
    async loadWorlds() {
        try {
            const response = await fetch(`${this.apiBase}/world-configs`);
            const result = await response.json();
            if (result.success) {
                this.data.worlds = result.data.worlds;
            }
        } catch (error) {
            console.error('Error loading worlds:', error);
        }
    }
    
    async loadUsers() {
        try {
            const response = await fetch(`${this.apiBase}/discord-users`);
            const result = await response.json();
            if (result.success) {
                this.data.users = result.data.users;
            }
        } catch (error) {
            console.error('Error loading users:', error);
        }
    }
    
    renderStats() {
        const stats = this.data.stats;
        document.getElementById('totalBots').textContent = stats.bots?.total || 0;
        document.getElementById('totalUsers').textContent = stats.users?.total || 0;
        document.getElementById('totalProducts').textContent = stats.products?.total || 0;
        document.getElementById('totalWorlds').textContent = stats.worlds?.total || 0;
    }
    
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active', 'border-blue-500', 'text-blue-600');
            btn.classList.add('border-transparent', 'text-gray-500');
        });
        
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active', 'border-blue-500', 'text-blue-600');
        document.querySelector(`[data-tab="${tabName}"]`).classList.remove('border-transparent', 'text-gray-500');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });
        
        document.getElementById(`${tabName}-tab`).classList.remove('hidden');
        
        this.currentTab = tabName;
        this.renderCurrentTab();
    }
    
    renderCurrentTab() {
        switch (this.currentTab) {
            case 'bots':
                this.renderBots();
                break;
            case 'products':
                this.renderProducts();
                break;
            case 'worlds':
                this.renderWorlds();
                break;
            case 'users':
                this.renderUsers();
                break;
        }
    }
    
    renderBots() {
        const tbody = document.getElementById('botsTableBody');
        tbody.innerHTML = '';
        
        this.data.bots.forEach(bot => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">${bot.bot_name}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-500">${bot.guild_id}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full status-${bot.status}">
                        ${bot.status.charAt(0).toUpperCase() + bot.status.slice(1)}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-500">${bot.live_stock_channel_id || 'Not set'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button onclick="dashboard.startBot(${bot.id})" class="text-green-600 hover:text-green-900 mr-3" ${bot.status === 'active' ? 'disabled' : ''}>
                        <i class="fas fa-play"></i>
                    </button>
                    <button onclick="dashboard.stopBot(${bot.id})" class="text-red-600 hover:text-red-900 mr-3" ${bot.status === 'inactive' ? 'disabled' : ''}>
                        <i class="fas fa-stop"></i>
                    </button>
                    <button onclick="dashboard.editBot(${bot.id})" class="text-blue-600 hover:text-blue-900 mr-3">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="dashboard.deleteBot(${bot.id})" class="text-red-600 hover:text-red-900">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
    
    renderProducts() {
        const tbody = document.getElementById('productsTableBody');
        tbody.innerHTML = '';
        
        this.data.products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        ${product.is_featured ? '<i class="fas fa-star text-yellow-400 mr-2"></i>' : ''}
                        <div class="text-sm font-medium text-gray-900">${product.product_name}</div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-500">${product.product_code}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${product.price_wl} WL</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${product.stock_quantity}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${product.is_active ? 'status-active' : 'status-inactive'}">
                        ${product.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button onclick="dashboard.editProduct(${product.id})" class="text-blue-600 hover:text-blue-900 mr-3">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="dashboard.deleteProduct(${product.id})" class="text-red-600 hover:text-red-900">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
    
    renderWorlds() {
        const grid = document.getElementById('worldsGrid');
        grid.innerHTML = '';
        
        this.data.worlds.forEach(world => {
            const card = document.createElement('div');
            card.className = 'bg-white rounded-lg shadow-md p-6 card-hover';
            card.innerHTML = `
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold text-gray-900">${world.world_name}</h3>
                    <span class="px-2 py-1 text-xs font-semibold rounded-full ${world.is_active ? 'status-active' : 'status-inactive'}">
                        ${world.is_active ? 'Active' : 'Inactive'}
                    </span>
                </div>
                <p class="text-gray-600 mb-4">${world.world_description || 'No description'}</p>
                <div class="flex items-center justify-between">
                    <span class="text-sm text-gray-500">Access: ${world.access_level}</span>
                    <div class="flex space-x-2">
                        <button onclick="dashboard.editWorld(${world.id})" class="text-blue-600 hover:text-blue-900">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button onclick="dashboard.deleteWorld(${world.id})" class="text-red-600 hover:text-red-900">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
            grid.appendChild(card);
        });
    }
    
    renderUsers() {
        const tbody = document.getElementById('usersTableBody');
        tbody.innerHTML = '';
        
        this.data.users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="text-sm font-medium text-gray-900">${user.discord_username}</div>
                        <div class="text-xs text-gray-500 ml-2">#${user.discord_id}</div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${user.grow_id || 'Not set'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">
                        ${user.wallet ? `
                            WL: ${user.wallet.wl_balance}<br>
                            DL: ${user.wallet.dl_balance}<br>
                            BGL: ${user.wallet.bgl_balance}
                        ` : 'No wallet'}
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex flex-col space-y-1">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${user.is_verified ? 'status-active' : 'status-inactive'}">
                            ${user.is_verified ? 'Verified' : 'Unverified'}
                        </span>
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${user.is_active ? 'status-active' : 'status-inactive'}">
                            ${user.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-500">${new Date(user.created_at).toLocaleDateString()}</div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
    
    async submitBotForm(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        try {
            this.showLoading();
            const response = await fetch(`${this.apiBase}/bots`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                this.showSuccess('Bot created successfully!');
                this.hideModal('addBotModal');
                form.reset();
                await this.loadBots();
                this.renderBots();
            } else {
                this.showError(result.message || 'Failed to create bot');
            }
        } catch (error) {
            this.showError('Error creating bot: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    async submitProductForm(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        data.bot_id = parseInt(data.bot_id);
        data.price_wl = parseFloat(data.price_wl);
        data.stock_quantity = parseInt(data.stock_quantity);
        data.is_featured = formData.has('is_featured');
        
        try {
            this.showLoading();
            const response = await fetch(`${this.apiBase}/live-stocks`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                this.showSuccess('Product created successfully!');
                this.hideModal('addProductModal');
                form.reset();
                await this.loadProducts();
                this.renderProducts();
            } else {
                this.showError(result.message || 'Failed to create product');
            }
        } catch (error) {
            this.showError('Error creating product: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    async submitWorldForm(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        try {
            this.showLoading();
            const response = await fetch(`${this.apiBase}/world-configs`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                this.showSuccess('World configuration created successfully!');
                this.hideModal('addWorldModal');
                form.reset();
                await this.loadWorlds();
                this.renderWorlds();
            } else {
                this.showError(result.message || 'Failed to create world configuration');
            }
        } catch (error) {
            this.showError('Error creating world configuration: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    async startBot(botId) {
        try {
            this.showLoading();
            const response = await fetch(`${this.apiBase}/bots/${botId}/start`, {
                method: 'POST'
            });
            
            const result = await response.json();
            if (result.success) {
                this.showSuccess('Bot started successfully!');
                await this.loadBots();
                this.renderBots();
            } else {
                this.showError(result.message || 'Failed to start bot');
            }
        } catch (error) {
            this.showError('Error starting bot: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    async stopBot(botId) {
        try {
            this.showLoading();
            const response = await fetch(`${this.apiBase}/bots/${botId}/stop`, {
                method: 'POST'
            });
            
            const result = await response.json();
            if (result.success) {
                this.showSuccess('Bot stopped successfully!');
                await this.loadBots();
                this.renderBots();
            } else {
                this.showError(result.message || 'Failed to stop bot');
            }
        } catch (error) {
            this.showError('Error stopping bot: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    populateBotSelect() {
        const select = document.getElementById('productBotSelect');
        select.innerHTML = '<option value="">Select Bot</option>';
        
        this.data.bots.forEach(bot => {
            const option = document.createElement('option');
            option.value = bot.id;
            option.textContent = bot.bot_name;
            select.appendChild(option);
        });
    }
    
    filterUsers(filter) {
        // Implementation for filtering users
        this.renderUsers();
    }
    
    showModal(modalId) {
        document.getElementById(modalId).classList.remove('hidden');
        document.getElementById(modalId).classList.add('flex');
    }
    
    hideModal(modalId) {
        document.getElementById(modalId).classList.add('hidden');
        document.getElementById(modalId).classList.remove('flex');
    }
    
    showLoading() {
        document.getElementById('loadingOverlay').classList.remove('hidden');
        document.getElementById('loadingOverlay').classList.add('flex');
    }
    
    hideLoading() {
        document.getElementById('loadingOverlay').classList.add('hidden');
        document.getElementById('loadingOverlay').classList.remove('flex');
    }
    
    showSuccess(message) {
        // Simple alert for now - can be enhanced with toast notifications
        alert('Success: ' + message);
    }
    
    showError(message) {
        // Simple alert for now - can be enhanced with toast notifications
        alert('Error: ' + message);
    }
    
    // Placeholder methods for edit/delete operations
    editBot(botId) {
        console.log('Edit bot:', botId);
        // Implementation for editing bot
    }
    
    deleteBot(botId) {
        if (confirm('Are you sure you want to delete this bot?')) {
            console.log('Delete bot:', botId);
            // Implementation for deleting bot
        }
    }
    
    editProduct(productId) {
        console.log('Edit product:', productId);
        // Implementation for editing product
    }
    
    deleteProduct(productId) {
        if (confirm('Are you sure you want to delete this product?')) {
            console.log('Delete product:', productId);
            // Implementation for deleting product
        }
    }
    
    editWorld(worldId) {
        console.log('Edit world:', worldId);
        // Implementation for editing world
    }
    
    deleteWorld(worldId) {
        if (confirm('Are you sure you want to delete this world configuration?')) {
            console.log('Delete world:', worldId);
            // Implementation for deleting world
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DiscordDashboard();
});
