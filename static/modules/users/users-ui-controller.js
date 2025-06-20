// Users UI Controller
class UsersUIController {
    constructor() {
        this.elements = {};
        this.initElements();
    }

    initElements() {
        this.elements = {
            totalUsers: document.getElementById('totalUsers'),
            activeUsers: document.getElementById('activeUsers'),
            premiumUsers: document.getElementById('premiumUsers'),
            newUsersToday: document.getElementById('newUsersToday'),
            usersList: document.getElementById('usersList'),
            pagination: document.getElementById('usersPagination'),
            searchInput: document.getElementById('usersSearch')
        };
    }

    updateUserStats(stats) {
        if (this.elements.totalUsers) {
            this.elements.totalUsers.textContent = Formatters.formatNumber(stats.total_users || 0);
        }
        
        if (this.elements.activeUsers) {
            this.elements.activeUsers.textContent = Formatters.formatNumber(stats.active_users || 0);
        }
        
        if (this.elements.premiumUsers) {
            this.elements.premiumUsers.textContent = Formatters.formatNumber(stats.premium_users || 0);
        }
        
        if (this.elements.newUsersToday) {
            this.elements.newUsersToday.textContent = Formatters.formatNumber(stats.new_users_today || 0);
        }
    }

    renderUsersList(users) {
        if (!this.elements.usersList) return;
        
        this.elements.usersList.innerHTML = users.map(user => `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10">
                            <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                                <i class="fas fa-user text-gray-600"></i>
                            </div>
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">${user.username}</div>
                            <div class="text-sm text-gray-500">${user.email}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${user.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                        ${user.status}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${Formatters.formatDate(user.created_at)}
                </td>
            </tr>
        `).join('');
    }
}

const usersUIController = new UsersUIController();
