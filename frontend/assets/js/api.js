// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Token management
class TokenManager {
    static getToken() {
        return localStorage.getItem('access_token');
    }

    static setToken(token) {
        localStorage.setItem('access_token', token);
    }

    static removeToken() {
        localStorage.removeItem('access_token');
    }

    static isAuthenticated() {
        return !!this.getToken();
    }
}

// API Client
class APIClient {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const token = TokenManager.getToken();

        const defaultHeaders = {
            'Content-Type': 'application/json',
        };

        if (token) {
            defaultHeaders['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            headers: defaultHeaders,
            ...options,
        };

        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                if (response.status === 401) {
                    TokenManager.removeToken();
                    window.location.href = 'login.html';
                    return;
                }
                throw new Error(data.message || data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // Auth endpoints
    static async login(credentials) {
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);

        return this.request('/auth/login', {
            method: 'POST',
            headers: {},
            body: formData,
        });
    }

    static async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: userData,
        });
    }

    static async getCurrentUser() {
        return this.request('/auth/me');
    }

    static async updateProfile(profileData) {
        return this.request('/auth/profile', {
            method: 'PUT',
            body: profileData,
        });
    }

    static async changePassword(passwordData) {
        return this.request('/auth/change-password', {
            method: 'POST',
            body: passwordData,
        });
    }

    // Wallet endpoints
    static async getWalletBalance() {
        return this.request('/wallet/balance');
    }

    static async getWalletTransactions(page = 1, perPage = 20) {
        return this.request(`/wallet/transactions?page=${page}&per_page=${perPage}`);
    }

    static async transferMoney(transferData) {
        return this.request('/wallet/transfer', {
            method: 'POST',
            body: transferData,
        });
    }

    static async createManualTopup(topupData) {
        return this.request('/wallet/topup/manual', {
            method: 'POST',
            body: topupData,
        });
    }

    static async createMidtransTopup(topupData) {
        return this.request('/wallet/topup/midtrans', {
            method: 'POST',
            body: topupData,
        });
    }

    // PPOB endpoints
    static async getPPOBCategories() {
        return this.request('/ppob/categories');
    }

    static async getPPOBProducts(category) {
        return this.request(`/ppob/products?category=${category}`);
    }

    static async inquiryPPOB(inquiryData) {
        return this.request('/ppob/inquiry', {
            method: 'POST',
            body: inquiryData,
        });
    }

    static async paymentPPOB(paymentData) {
        return this.request('/ppob/payment', {
            method: 'POST',
            body: paymentData,
        });
    }

    static async getPPOBTransactions(page = 1, perPage = 20, filters = {}) {
        const params = new URLSearchParams({
            page: page.toString(),
            per_page: perPage.toString(),
            ...filters,
        });
        return this.request(`/ppob/transactions?${params}`);
    }

    static async getPPOBTransactionDetail(transactionId) {
        return this.request(`/ppob/transactions/${transactionId}`);
    }

    static async getPopularProducts() {
        return this.request('/ppob/popular-products');
    }

    static async getPPOBStatistics() {
        return this.request('/ppob/statistics');
    }
}

// Utility functions
class Utils {
    static formatCurrency(amount) {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0,
        }).format(amount);
    }

    static formatDate(dateString) {
        return new Intl.DateTimeFormat('id-ID', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        }).format(new Date(dateString));
    }

    static formatDateOnly(dateString) {
        return new Intl.DateTimeFormat('id-ID', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        }).format(new Date(dateString));
    }

    static getStatusBadge(status) {
        const statusMap = {
            success: { class: 'bg-green-100 text-green-800', icon: 'fas fa-check-circle', text: 'Berhasil' },
            pending: { class: 'bg-yellow-100 text-yellow-800', icon: 'fas fa-clock', text: 'Pending' },
            failed: { class: 'bg-red-100 text-red-800', icon: 'fas fa-times-circle', text: 'Gagal' },
            cancelled: { class: 'bg-gray-100 text-gray-800', icon: 'fas fa-ban', text: 'Dibatalkan' },
            processing: { class: 'bg-blue-100 text-blue-800', icon: 'fas fa-spinner', text: 'Diproses' },
        };

        const statusInfo = statusMap[status] || statusMap.pending;
        return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusInfo.class}">
            <i class="${statusInfo.icon} mr-1"></i>${statusInfo.text}
        </span>`;
    }

    static getTransactionTypeIcon(type) {
        const typeMap = {
            pulsa: 'fas fa-mobile-alt text-blue-600',
            listrik: 'fas fa-lightbulb text-yellow-600',
            pdam: 'fas fa-tint text-cyan-600',
            internet: 'fas fa-wifi text-purple-600',
            bpjs: 'fas fa-heartbeat text-green-600',
            multifinance: 'fas fa-car text-red-600',
            topup: 'fas fa-plus text-green-600',
            transfer: 'fas fa-exchange-alt text-blue-600',
            payment: 'fas fa-credit-card text-indigo-600',
        };

        return typeMap[type] || 'fas fa-receipt text-gray-600';
    }

    static showAlert(title, message, type = 'info') {
        const modal = document.getElementById('alertModal');
        const icon = document.getElementById('alertIcon');
        const iconClass = document.getElementById('alertIconClass');
        const titleEl = document.getElementById('alertTitle');
        const messageEl = document.getElementById('alertMessage');

        // Set icon and colors based on type
        const typeMap = {
            success: { icon: 'fas fa-check-circle', bgClass: 'bg-green-100', iconClass: 'text-green-600' },
            error: { icon: 'fas fa-times-circle', bgClass: 'bg-red-100', iconClass: 'text-red-600' },
            warning: { icon: 'fas fa-exclamation-triangle', bgClass: 'bg-yellow-100', iconClass: 'text-yellow-600' },
            info: { icon: 'fas fa-info-circle', bgClass: 'bg-blue-100', iconClass: 'text-blue-600' },
        };

        const typeInfo = typeMap[type] || typeMap.info;

        icon.className = `mx-auto flex items-center justify-center h-12 w-12 rounded-full mb-4 ${typeInfo.bgClass}`;
        iconClass.className = `text-2xl ${typeInfo.iconClass} ${typeInfo.icon}`;
        titleEl.textContent = title;
        messageEl.textContent = message;

        modal.classList.remove('hidden');

        // Close modal when OK button is clicked
        document.getElementById('alertOkButton').onclick = () => {
            modal.classList.add('hidden');
        };
    }

    static showLoading(element, show = true) {
        const spinner = element.querySelector('.fa-spinner');
        const text = element.querySelector('span');

        if (show) {
            element.disabled = true;
            if (spinner) spinner.classList.remove('hidden');
            if (text) text.textContent = 'Loading...';
        } else {
            element.disabled = false;
            if (spinner) spinner.classList.add('hidden');
        }
    }

    static validateForm(formData, rules) {
        const errors = {};

        for (const [field, rule] of Object.entries(rules)) {
            const value = formData[field];

            if (rule.required && (!value || value.trim() === '')) {
                errors[field] = `${rule.label} wajib diisi`;
                continue;
            }

            if (value && rule.minLength && value.length < rule.minLength) {
                errors[field] = `${rule.label} minimal ${rule.minLength} karakter`;
                continue;
            }

            if (value && rule.pattern && !rule.pattern.test(value)) {
                errors[field] = rule.message || `Format ${rule.label} tidak valid`;
                continue;
            }

            if (value && rule.match && value !== formData[rule.match]) {
                errors[field] = `${rule.label} tidak cocok`;
                continue;
            }
        }

        return errors;
    }

    static displayFormErrors(errors) {
        // Clear previous errors
        document.querySelectorAll('.error-message').forEach(el => el.remove());
        document.querySelectorAll('.border-red-500').forEach(el => {
            el.classList.remove('border-red-500');
            el.classList.add('border-gray-300');
        });

        // Display new errors
        for (const [field, message] of Object.entries(errors)) {
            const input = document.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.remove('border-gray-300');
                input.classList.add('border-red-500');

                const errorEl = document.createElement('p');
                errorEl.className = 'error-message text-red-500 text-sm mt-1';
                errorEl.textContent = message;
                input.parentNode.appendChild(errorEl);
            }
        }
    }
}

// Check authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    const publicPages = ['index.html', 'login.html', ''];
    const currentPage = window.location.pathname.split('/').pop();

    if (!publicPages.includes(currentPage) && !TokenManager.isAuthenticated()) {
        window.location.href = 'login.html';
    }
});
