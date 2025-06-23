// Users Main Controller
// Controller utama untuk users dashboard

class UsersMainController {
    constructor() {
        this.isInitialized = false;
    }

    // Initialize users dashboard
    async initUsersDashboard() {
        const token = checkAuth();
        if (!token) return;

        showLoading(true);
        
        try {
            await Promise.all([
                this.loadUserStats(),
                this.loadUsers()
            ]);
            
            this.initEventListeners();
            this.isInitialized = true;
            showToast('Dashboard users berhasil dimuat', 'success', 3000);
        } catch (error) {
            console.error('Error loading users dashboard:', error);
            showToast('Gagal memuat data users', 'error');
        } finally {
            showLoading(false);
        }
    }

    // Load user statistics
    async loadUserStats() {
        try {
            const stats = await usersApiService.loadUserStats();
            usersUIComponents.updateUserStats(stats);
        } catch (error) {
            console.error('Error in loadUserStats:', error);
            showError('Gagal memuat statistik users');
        }
    }

    // Load users
    async loadUsers() {
        try {
            const users = await usersApiService.loadUsers();
            usersUIComponents.setUsersData(users);
            usersUIComponents.renderUsersTable();
        } catch (error) {
            console.error('Error in loadUsers:', error);
            showError('Gagal memuat data users');
        }
    }

    // Initialize event listeners
    initEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('userSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                usersUIComponents.filterUsers(e.target.value);
            });
        }

        // Items per page selector
        const itemsPerPageSelect = document.getElementById('itemsPerPage');
        if (itemsPerPageSelect) {
            itemsPerPageSelect.addEventListener('change', (e) => {
                usersUIComponents.itemsPerPage = parseInt(e.target.value);
                usersUIComponents.currentPage = 1;
                usersUIComponents.renderUsersTable();
            });
        }

        // Refresh button
        const refreshButton = document.getElementById('refreshUsers');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.refreshUsers();
            });
        }

        // Add user button
        const addUserButton = document.getElementById('addUser');
        if (addUserButton) {
            addUserButton.addEventListener('click', () => {
                this.showAddUserModal();
            });
        }

        // Export users button
        const exportButton = document.getElementById('exportUsers');
        if (exportButton) {
            exportButton.addEventListener('click', () => {
                this.exportUsers();
            });
        }

        // Status filter
        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.filterByStatus(e.target.value);
            });
        }

        // Role filter
        const roleFilter = document.getElementById('roleFilter');
        if (roleFilter) {
            roleFilter.addEventListener('change', (e) => {
                this.filterByRole(e.target.value);
            });
        }
    }

    // Refresh users
    async refreshUsers() {
        const refreshButton = document.getElementById('refreshUsers');
        if (refreshButton) {
            refreshButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>Refreshing...';
        }

        try {
            await this.loadUsers();
            showToast('Data users berhasil diperbarui', 'success', 2000);
        } catch (error) {
            showToast('Gagal memperbarui data users', 'error');
        } finally {
            if (refreshButton) {
                refreshButton.innerHTML = '<i class="fas fa-sync-alt mr-1"></i>Refresh';
            }
        }
    }

    // Filter by status
    filterByStatus(status) {
        if (!status || status === 'all') {
            usersUIComponents.filteredUsers = [...usersUIComponents.users];
        } else {
            usersUIComponents.filteredUsers = usersUIComponents.users.filter(user => 
                user.status?.toLowerCase() === status.toLowerCase()
            );
        }
        
        usersUIComponents.totalItems = usersUIComponents.filteredUsers.length;
        usersUIComponents.currentPage = 1;
        usersUIComponents.renderUsersTable();
    }

    // Filter by role
    filterByRole(role) {
        if (!role || role === 'all') {
            usersUIComponents.filteredUsers = [...usersUIComponents.users];
        } else {
            usersUIComponents.filteredUsers = usersUIComponents.users.filter(user => 
                user.role?.toLowerCase() === role.toLowerCase()
            );
        }
        
        usersUIComponents.totalItems = usersUIComponents.filteredUsers.length;
        usersUIComponents.currentPage = 1;
        usersUIComponents.renderUsersTable();
    }

    // Show add user modal
    showAddUserModal() {
        // Implementation for showing add user modal
        console.log('Show add user modal');
        // This would typically show a modal for adding new user
    }

    // Export users
    exportUsers() {
        const exportData = {
            users: usersUIComponents.filteredUsers,
            total_count: usersUIComponents.totalItems,
            exported_at: new Date().toISOString(),
            filters_applied: {
                search: document.getElementById('userSearch')?.value || '',
                status: document.getElementById('statusFilter')?.value || 'all',
                role: document.getElementById('roleFilter')?.value || 'all'
            }
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `users-export-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        showToast('Data users berhasil diekspor', 'success');
    }

    // Update user status
    async updateUserStatus(userId, newStatus) {
        try {
            await usersApiService.updateUserStatus(userId, newStatus);
            showToast('Status user berhasil diperbarui', 'success');
            await this.loadUsers(); // Reload users list
        } catch (error) {
            showToast('Gagal memperbarui status user', 'error');
        }
    }

    // Bulk actions
    async bulkDeleteUsers(userIds) {
        if (!confirm(`Are you sure you want to delete ${userIds.length} users?`)) {
            return;
        }

        try {
            const promises = userIds.map(id => usersApiService.deleteUser(id));
            await Promise.all(promises);
            showToast(`${userIds.length} users deleted successfully`, 'success');
            await this.loadUsers(); // Reload users list
        } catch (error) {
            showToast('Failed to delete some users', 'error');
        }
    }

    // Search users
    async searchUsers(query) {
        if (!query.trim()) {
            await this.loadUsers();
            return;
        }

        try {
            const searchResults = await usersApiService.searchUsers(query);
            usersUIComponents.setUsersData(searchResults);
            usersUIComponents.renderUsersTable();
        } catch (error) {
            showToast('Gagal mencari users', 'error');
        }
    }
}

// Export instance
window.usersMainController = new UsersMainController();
