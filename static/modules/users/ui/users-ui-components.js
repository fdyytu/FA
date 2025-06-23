// Users UI Components
// Menangani semua komponen UI untuk users

class UsersUIComponents {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.totalItems = 0;
        this.users = [];
        this.filteredUsers = [];
    }

    // Update user statistics cards
    updateUserStats(stats) {
        const elements = {
            totalUsers: document.getElementById('totalUsers'),
            activeUsers: document.getElementById('activeUsers'),
            premiumUsers: document.getElementById('premiumUsers'),
            newUsersToday: document.getElementById('newUsersToday')
        };
        
        if (elements.totalUsers) {
            elements.totalUsers.textContent = formatNumber(stats.total_users || 0);
        }
        
        if (elements.activeUsers) {
            elements.activeUsers.textContent = formatNumber(stats.active_users || 0);
        }
        
        if (elements.premiumUsers) {
            elements.premiumUsers.textContent = formatNumber(stats.premium_users || 0);
        }
        
        if (elements.newUsersToday) {
            elements.newUsersToday.textContent = formatNumber(stats.new_users_today || 0);
        }
    }

    // Set users data
    setUsersData(usersData) {
        this.users = usersData;
        this.filteredUsers = [...usersData];
        this.totalItems = this.filteredUsers.length;
    }

    // Render users table
    renderUsersTable() {
        const tableBody = document.getElementById('usersTableBody');
        const loadingElement = document.getElementById('loadingUsers');
        const tableContainer = document.getElementById('usersTableContainer');
        
        if (loadingElement) loadingElement.classList.add('hidden');
        if (tableContainer) tableContainer.classList.remove('hidden');
        
        if (!tableBody) return;
        
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const paginatedUsers = this.filteredUsers.slice(startIndex, endIndex);
        
        tableBody.innerHTML = paginatedUsers.map(user => `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10">
                            <div class="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                                <span class="text-white text-sm font-medium">${this.getInitials(user.username || user.email)}</span>
                            </div>
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">${user.username || 'N/A'}</div>
                            <div class="text-sm text-gray-500">${user.email || 'N/A'}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${this.getStatusClass(user.status)}">
                        ${user.status || 'unknown'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${user.role || 'user'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${formatDate(user.created_at) || 'N/A'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${formatDate(user.last_login) || 'Never'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button onclick="usersUIComponents.viewUser('${user.id}')" 
                            class="text-indigo-600 hover:text-indigo-900 mr-3">
                        View
                    </button>
                    <button onclick="usersUIComponents.editUser('${user.id}')" 
                            class="text-blue-600 hover:text-blue-900 mr-3">
                        Edit
                    </button>
                    <button onclick="usersUIComponents.deleteUser('${user.id}')" 
                            class="text-red-600 hover:text-red-900">
                        Delete
                    </button>
                </td>
            </tr>
        `).join('');
        
        this.updatePagination();
    }

    // Get user initials
    getInitials(name) {
        if (!name) return '?';
        return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    }

    // Get status class
    getStatusClass(status) {
        switch (status?.toLowerCase()) {
            case 'active':
                return 'bg-green-100 text-green-800';
            case 'inactive':
                return 'bg-red-100 text-red-800';
            case 'pending':
                return 'bg-yellow-100 text-yellow-800';
            case 'suspended':
                return 'bg-gray-100 text-gray-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    }

    // Update pagination
    updatePagination() {
        const totalPages = Math.ceil(this.totalItems / this.itemsPerPage);
        const paginationContainer = document.getElementById('usersPagination');
        
        if (!paginationContainer) return;
        
        let paginationHTML = '';
        
        // Previous button
        paginationHTML += `
            <button onclick="usersUIComponents.goToPage(${this.currentPage - 1})" 
                    ${this.currentPage === 1 ? 'disabled' : ''} 
                    class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-l-md hover:bg-gray-50 ${this.currentPage === 1 ? 'cursor-not-allowed opacity-50' : ''}">
                Previous
            </button>
        `;
        
        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === this.currentPage) {
                paginationHTML += `
                    <button class="px-3 py-2 text-sm font-medium text-white bg-indigo-600 border border-indigo-600">
                        ${i}
                    </button>
                `;
            } else {
                paginationHTML += `
                    <button onclick="usersUIComponents.goToPage(${i})" 
                            class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50">
                        ${i}
                    </button>
                `;
            }
        }
        
        // Next button
        paginationHTML += `
            <button onclick="usersUIComponents.goToPage(${this.currentPage + 1})" 
                    ${this.currentPage === totalPages ? 'disabled' : ''} 
                    class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-r-md hover:bg-gray-50 ${this.currentPage === totalPages ? 'cursor-not-allowed opacity-50' : ''}">
                Next
            </button>
        `;
        
        paginationContainer.innerHTML = paginationHTML;
        
        // Update info
        const infoElement = document.getElementById('usersInfo');
        if (infoElement) {
            const startItem = (this.currentPage - 1) * this.itemsPerPage + 1;
            const endItem = Math.min(this.currentPage * this.itemsPerPage, this.totalItems);
            infoElement.textContent = `Showing ${startItem} to ${endItem} of ${this.totalItems} users`;
        }
    }

    // Go to page
    goToPage(page) {
        const totalPages = Math.ceil(this.totalItems / this.itemsPerPage);
        if (page < 1 || page > totalPages) return;
        
        this.currentPage = page;
        this.renderUsersTable();
    }

    // Filter users
    filterUsers(searchTerm) {
        if (!searchTerm) {
            this.filteredUsers = [...this.users];
        } else {
            this.filteredUsers = this.users.filter(user => 
                (user.username && user.username.toLowerCase().includes(searchTerm.toLowerCase())) ||
                (user.email && user.email.toLowerCase().includes(searchTerm.toLowerCase())) ||
                (user.role && user.role.toLowerCase().includes(searchTerm.toLowerCase()))
            );
        }
        
        this.totalItems = this.filteredUsers.length;
        this.currentPage = 1;
        this.renderUsersTable();
    }

    // View user
    viewUser(userId) {
        // Implementation for viewing user details
        console.log('View user:', userId);
        // This would typically open a modal or navigate to user details page
    }

    // Edit user
    editUser(userId) {
        // Implementation for editing user
        console.log('Edit user:', userId);
        // This would typically open an edit modal
    }

    // Delete user
    async deleteUser(userId) {
        if (!confirm('Are you sure you want to delete this user?')) {
            return;
        }
        
        try {
            await usersApiService.deleteUser(userId);
            showToast('User deleted successfully', 'success');
            // Reload users list
            const users = await usersApiService.loadUsers();
            this.setUsersData(users);
            this.renderUsersTable();
        } catch (error) {
            showToast('Failed to delete user', 'error');
        }
    }
}

// Export instance
window.usersUIComponents = new UsersUIComponents();
