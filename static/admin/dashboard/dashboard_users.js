// Dashboard users functionality
let currentPage = 1;
let itemsPerPage = 10;
let totalItems = 0;
let users = [];
let filteredUsers = [];

// Initialize users dashboard
async function initUsersDashboard() {
    const token = checkAuth();
    if (!token) return;

    showLoading(true);
    
    try {
        await Promise.all([
            loadUserStats(),
            loadUsers()
        ]);
        
        initEventListeners();
        showToast('Dashboard users berhasil dimuat', 'success', 3000);
    } catch (error) {
        console.error('Error loading users dashboard:', error);
        showToast('Gagal memuat data users', 'error');
    } finally {
        showLoading(false);
    }
}

// Load user statistics
async function loadUserStats() {
    try {
        const response = await apiRequest('/api/v1/admin/dashboard/stats/users');
        
        if (response && response.ok) {
            const data = await response.json();
            updateUserStats(data.data || data);
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
    } catch (error) {
        console.error('Error loading user stats:', error);
        showError('Gagal memuat statistik users');
        updateUserStats({
            total_users: 0,
            active_users: 0,
            premium_users: 0,
            new_users_today: 0
        });
    }
}

// Update user statistics cards
function updateUserStats(stats) {
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

// Load users
async function loadUsers() {
    const loadingElement = document.getElementById('loadingUsers');
    const tableContainer = document.getElementById('usersTableContainer');
    
    if (loadingElement) loadingElement.classList.remove('hidden');
    if (tableContainer) tableContainer.classList.add('hidden');
    
    try {
        const response = await apiRequest('/api/v1/users');
        
        if (response && response.ok) {
            const data = await response.json();
            users = data.data || [];
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
        
        filteredUsers = [...users];
        totalItems = filteredUsers.length;
        renderUsersTable();
        updatePagination();
        
    } catch (error) {
        console.error('Error loading users:', error);
        users = [];
        filteredUsers = [];
        totalItems = 0;
        renderUsersTable();
        updatePagination();
    } finally {
        if (loadingElement) loadingElement.classList.add('hidden');
        if (tableContainer) tableContainer.classList.remove('hidden');
    }
}

// Render users table
function renderUsersTable() {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageUsers = filteredUsers.slice(startIndex, endIndex);
    
    tbody.innerHTML = pageUsers.map(user => `
        <tr class="table-row">
            <td class="px-6 py-4 whitespace-nowrap">
                <input type="checkbox" class="user-checkbox rounded border-gray-300" value="${user.id}">
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                        <div class="h-10 w-10 rounded-full bg-gradient-to-r ${getRoleGradient(user.role)} flex items-center justify-center">
                            <span class="text-white text-sm font-medium">${user.username.charAt(0).toUpperCase()}</span>
                        </div>
                    </div>
                    <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">${user.username}</div>
                        <div class="text-sm text-gray-500">${user.email}</div>
                        ${user.phone ? `<div class="text-xs text-gray-400">${user.phone}</div>` : ''}
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeClass(user.role)}">
                    ${getRoleIcon(user.role)} ${user.role.toUpperCase()}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">${formatCurrency(user.balance)}</div>
                <button onclick="manageBalance(${user.id})" class="text-xs text-blue-600 hover:text-blue-800">
                    Kelola Balance
                </button>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">${formatNumber(user.transaction_count || 0)}</div>
                <div class="text-xs text-gray-500">transaksi</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${getStatusBadge(user.status)}
                ${user.is_verified ? '<div class="text-xs text-green-600 mt-1"><i class="fas fa-check-circle mr-1"></i>Verified</div>' : '<div class="text-xs text-gray-400 mt-1"><i class="fas fa-times-circle mr-1"></i>Unverified</div>'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                    <button onclick="editUser(${user.id})" class="text-blue-600 hover:text-blue-900" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="viewUserDetails(${user.id})" class="text-green-600 hover:text-green-900" title="Detail">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="toggleUserStatus(${user.id})" class="text-orange-600 hover:text-orange-900" title="${user.status === 'active' ? 'Nonaktifkan' : 'Aktifkan'}">
                        <i class="fas ${user.status === 'active' ? 'fa-user-slash' : 'fa-user-check'}"></i>
                    </button>
                    <button onclick="deleteUser(${user.id})" class="text-red-600 hover:text-red-900" title="Hapus">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    updateTableInfo();
}

// Get role gradient class
function getRoleGradient(role) {
    switch (role) {
        case 'admin': return 'from-red-500 to-pink-600';
        case 'vip': return 'from-purple-500 to-indigo-600';
        case 'premium': return 'from-yellow-500 to-orange-600';
        default: return 'from-blue-500 to-cyan-600';
    }
}

// Get role badge class
function getRoleBadgeClass(role) {
    switch (role) {
        case 'admin': return 'bg-red-100 text-red-800';
        case 'vip': return 'bg-purple-100 text-purple-800';
        case 'premium': return 'bg-yellow-100 text-yellow-800';
        default: return 'bg-blue-100 text-blue-800';
    }
}

// Get role icon
function getRoleIcon(role) {
    switch (role) {
        case 'admin': return '<i class="fas fa-crown mr-1"></i>';
        case 'vip': return '<i class="fas fa-gem mr-1"></i>';
        case 'premium': return '<i class="fas fa-star mr-1"></i>';
        default: return '<i class="fas fa-user mr-1"></i>';
    }
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
                renderUsersTable();
                updatePagination();
            }
        };
    }
    
    if (nextBtn) {
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.onclick = () => {
            if (currentPage < totalPages) {
                currentPage++;
                renderUsersTable();
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
    renderUsersTable();
    updatePagination();
}

// Filter users
function filterUsers() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const roleFilter = document.getElementById('roleFilter')?.value || '';
    const statusFilter = document.getElementById('statusFilter')?.value || '';
    
    filteredUsers = users.filter(user => {
        const matchesSearch = !searchTerm || 
            user.username.toLowerCase().includes(searchTerm) ||
            user.email.toLowerCase().includes(searchTerm) ||
            (user.phone && user.phone.includes(searchTerm));
            
        const matchesRole = !roleFilter || user.role === roleFilter;
        const matchesStatus = !statusFilter || user.status === statusFilter;
        
        return matchesSearch && matchesRole && matchesStatus;
    });
    
    totalItems = filteredUsers.length;
    currentPage = 1;
    renderUsersTable();
    updatePagination();
}

// Initialize event listeners
function initEventListeners() {
    // Search and filters
    const searchInput = document.getElementById('searchInput');
    const roleFilter = document.getElementById('roleFilter');
    const statusFilter = document.getElementById('statusFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterUsers, 300));
    }
    
    if (roleFilter) {
        roleFilter.addEventListener('change', filterUsers);
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', filterUsers);
    }
    
    // Buttons
    const addUserBtn = document.getElementById('addUserBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    const exportBtn = document.getElementById('exportBtn');
    const bulkActionBtn = document.getElementById('bulkActionBtn');
    
    if (addUserBtn) {
        addUserBtn.addEventListener('click', () => openUserModal());
    }
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshUsers);
    }
    
    if (exportBtn) {
        exportBtn.addEventListener('click', exportUsers);
    }
    
    if (bulkActionBtn) {
        bulkActionBtn.addEventListener('click', showBulkActionMenu);
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
    // User modal
    const userForm = document.getElementById('userForm');
    const cancelUserBtn = document.getElementById('cancelUserBtn');
    
    if (userForm) {
        userForm.addEventListener('submit', handleUserSubmit);
    }
    
    if (cancelUserBtn) {
        cancelUserBtn.addEventListener('click', () => closeModal('userModal'));
    }
    
    // Balance modal
    const balanceForm = document.getElementById('balanceForm');
    const cancelBalanceBtn = document.getElementById('cancelBalanceBtn');
    
    if (balanceForm) {
        balanceForm.addEventListener('submit', handleBalanceSubmit);
    }
    
    if (cancelBalanceBtn) {
        cancelBalanceBtn.addEventListener('click', () => closeModal('balanceModal'));
    }
}

// Open user modal
function openUserModal(userId = null) {
    const modal = document.getElementById('userModal');
    const modalTitle = document.getElementById('modalTitle');
    const form = document.getElementById('userForm');
    
    if (!modal || !form) return;
    
    // Reset form
    form.reset();
    
    if (userId) {
        // Edit mode
        const user = users.find(u => u.id === userId);
        if (user) {
            modalTitle.textContent = 'Edit User';
            populateUserForm(user);
        }
    } else {
        // Add mode
        modalTitle.textContent = 'Tambah User';
    }
    
    openModal('userModal');
}

// Populate user form
function populateUserForm(user) {
    const fields = {
        userId: user.id,
        userName: user.username,
        userEmail: user.email,
        userPhone: user.phone,
        userRole: user.role,
        userBalance: user.balance,
        userActive: user.is_active,
        userVerified: user.is_verified
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

// Handle user form submission
async function handleUserSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const userData = Object.fromEntries(formData.entries());
    
    // Convert checkboxes
    userData.is_active = formData.has('is_active');
    userData.is_verified = formData.has('is_verified');
    
    // Convert numbers
    userData.balance = parseFloat(userData.balance) || 0;
    
    // Remove password if empty
    if (!userData.password) {
        delete userData.password;
    }
    
    showLoading(true);
    
    try {
        const isEdit = userData.id;
        const endpoint = isEdit ? `/users/${userData.id}` : '/users';
        const method = isEdit ? 'PUT' : 'POST';
        
        const response = await apiRequest(endpoint, {
            method: method,
            body: JSON.stringify(userData)
        });
        
        if (response && response.ok) {
            showToast(`User berhasil ${isEdit ? 'diperbarui' : 'ditambahkan'}`, 'success');
            closeModal('userModal');
            await loadUsers();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal menyimpan user', 'error');
        }
    } catch (error) {
        console.error('Error saving user:', error);
        showToast('Terjadi kesalahan saat menyimpan user', 'error');
    } finally {
        showLoading(false);
    }
}

// Edit user
function editUser(userId) {
    openUserModal(userId);
}

// View user details
function viewUserDetails(userId) {
    const user = users.find(u => u.id === userId);
    if (!user) return;
    
    const details = `
        <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">Username</label>
                    <p class="text-sm text-gray-900">${user.username}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Email</label>
                    <p class="text-sm text-gray-900">${user.email}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Phone</label>
                    <p class="text-sm text-gray-900">${user.phone || '-'}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Role</label>
                    <p class="text-sm text-gray-900">${user.role}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Balance</label>
                    <p class="text-sm text-gray-900">${formatCurrency(user.balance)}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Transaksi</label>
                    <p class="text-sm text-gray-900">${user.transaction_count || 0}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Status</label>
                    <p class="text-sm text-gray-900">${user.status}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Last Login</label>
                    <p class="text-sm text-gray-900">${formatDateTime(user.last_login)}</p>
                </div>
            </div>
        </div>
    `;
    
    showAlert('Detail User', details, 'info');
}

// Toggle user status
async function toggleUserStatus(userId) {
    const user = users.find(u => u.id === userId);
    if (!user) return;
    
    const newStatus = user.status === 'active' ? 'inactive' : 'active';
    
    if (!confirm(`Apakah Anda yakin ingin ${newStatus === 'active' ? 'mengaktifkan' : 'menonaktifkan'} user ini?`)) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await apiRequest(`/users/${userId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status: newStatus })
        });
        
        if (response && response.ok) {
            showToast(`User berhasil ${newStatus === 'active' ? 'diaktifkan' : 'dinonaktifkan'}`, 'success');
            await loadUsers();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal mengubah status user', 'error');
        }
    } catch (error) {
        console.error('Error toggling user status:', error);
        showToast('Terjadi kesalahan saat mengubah status user', 'error');
    } finally {
        showLoading(false);
    }
}

// Delete user
async function deleteUser(userId) {
    if (!confirm('Apakah Anda yakin ingin menghapus user ini?')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await apiRequest(`/users/${userId}`, {
            method: 'DELETE'
        });
        
        if (response && response.ok) {
            showToast('User berhasil dihapus', 'success');
            await loadUsers();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal menghapus user', 'error');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        showToast('Terjadi kesalahan saat menghapus user', 'error');
    } finally {
        showLoading(false);
    }
}

// Manage balance
function manageBalance(userId) {
    const user = users.find(u => u.id === userId);
    if (!user) return;
    
    document.getElementById('balanceUserId').value = userId;
    document.getElementById('balanceUserName').textContent = user.username;
    document.getElementById('currentBalance').textContent = formatCurrency(user.balance);
    
    openModal('balanceModal');
}

// Handle balance form submission
async function handleBalanceSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const balanceData = Object.fromEntries(formData.entries());
    
    balanceData.amount = parseFloat(balanceData.amount);
    
    showLoading(true);
    
    try {
        const response = await apiRequest(`/users/${balanceData.userId}/balance`, {
            method: 'PUT',
            body: JSON.stringify(balanceData)
        });
        
        if (response && response.ok) {
            showToast('Balance berhasil diperbarui', 'success');
            closeModal('balanceModal');
            await loadUsers();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal memperbarui balance', 'error');
        }
    } catch (error) {
        console.error('Error updating balance:', error);
        showToast('Terjadi kesalahan saat memperbarui balance', 'error');
    } finally {
        showLoading(false);
    }
}

// Toggle select all
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const userCheckboxes = document.querySelectorAll('.user-checkbox');
    
    userCheckboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
}

// Refresh users
async function refreshUsers() {
    showLoading(true);
    try {
        await Promise.all([
            loadUserStats(),
            loadUsers()
        ]);
        showToast('Data users berhasil diperbarui', 'success', 3000);
    } catch (error) {
        showToast('Gagal memperbarui data users', 'error');
    } finally {
        showLoading(false);
    }
}

// Export users
function exportUsers() {
    const selectedUsers = getSelectedUsers();
    const dataToExport = selectedUsers.length > 0 ? selectedUsers : filteredUsers;
    
    const csv = convertUsersToCSV(dataToExport);
    downloadCSV(csv, 'users.csv');
    
    showToast(`${dataToExport.length} user berhasil diekspor`, 'success');
}

// Convert users to CSV
function convertUsersToCSV(data) {
    if (data.length === 0) return '';
    
    const headers = ['ID', 'Username', 'Email', 'Phone', 'Role', 'Balance', 'Transaksi', 'Status', 'Aktif', 'Verified', 'Last Login', 'Created At'];
    const rows = data.map(user => [
        user.id,
        user.username,
        user.email,
        user.phone || '',
        user.role,
        user.balance,
        user.transaction_count || 0,
        user.status,
        user.is_active ? 'Ya' : 'Tidak',
        user.is_verified ? 'Ya' : 'Tidak',
        formatDateTime(user.last_login),
        formatDateTime(user.created_at)
    ]);
    
    const csvContent = [headers, ...rows]
        .map(row => row.map(field => `"${field}"`).join(','))
        .join('\n');
    
    return csvContent;
}

// Get selected users
function getSelectedUsers() {
    const selectedIds = Array.from(document.querySelectorAll('.user-checkbox:checked'))
        .map(checkbox => parseInt(checkbox.value));
    
    return users.filter(user => selectedIds.includes(user.id));
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', () => {
    initUsersDashboard();
});
