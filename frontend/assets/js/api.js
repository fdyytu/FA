// API Configuration
const API_BASE_URL = window.location.origin + '/api/v1';

class GameStoreAPI {
    constructor() {
        this.token = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }

    // Helper method untuk request dengan authentication
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (response.status === 401 && this.refreshToken) {
                // Token expired, try to refresh
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    headers['Authorization'] = `Bearer ${this.token}`;
                    return await fetch(url, { ...options, headers });
                }
            }

            return response;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    // Authentication Methods
    async login(username, password) {
        try {
            const response = await this.request('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            
            if (response.ok && data.success) {
                this.token = data.data.access_token;
                this.refreshToken = data.data.refresh_token;
                localStorage.setItem('access_token', this.token);
                localStorage.setItem('refresh_token', this.refreshToken);
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message || 'Login gagal' };
            }
        } catch (error) {
            return { success: false, message: 'Terjadi kesalahan saat login' };
        }
    }

    async register(userData) {
        try {
            const response = await this.request('/auth/', {
                method: 'POST',
                body: JSON.stringify(userData)
            });

            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message || 'Registrasi gagal' };
            }
        } catch (error) {
            return { success: false, message: 'Terjadi kesalahan saat registrasi' };
        }
    }

    async refreshAccessToken() {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: this.refreshToken })
            });

            const data = await response.json();
            
            if (response.ok && data.success) {
                this.token = data.data.access_token;
                localStorage.setItem('access_token', this.token);
                return true;
            } else {
                this.logout();
                return false;
            }
        } catch (error) {
            this.logout();
            return false;
        }
    }

    async getCurrentUser() {
        try {
            const response = await this.request('/auth/me');
            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            return { success: false, message: 'Gagal mengambil data user' };
        }
    }

    logout() {
        this.token = null;
        this.refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.reload();
    }

    // PPOB Methods
    async getCategories() {
        try {
            const response = await this.request('/ppob/categories');
            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            return { success: false, message: 'Gagal mengambil kategori' };
        }
    }

    async getProductsByCategory(category) {
        try {
            const response = await this.request(`/ppob/products/${category}`);
            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            return { success: false, message: 'Gagal mengambil produk' };
        }
    }

    async getPopularProducts(limit = 12) {
        try {
            const response = await this.request(`/ppob/popular-products?limit=${limit}`);
            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            return { success: false, message: 'Gagal mengambil produk populer' };
        }
    }

    async inquiry(productCode, customerNumber) {
        try {
            const response = await this.request('/ppob/inquiry', {
                method: 'POST',
                body: JSON.stringify({
                    product_code: productCode,
                    customer_number: customerNumber
                })
            });

            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            return { success: false, message: 'Gagal melakukan inquiry' };
        }
    }

    async payment(inquiryData) {
        try {
            const response = await this.request('/ppob/payment', {
                method: 'POST',
                body: JSON.stringify(inquiryData)
            });

            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            return { success: false, message: 'Gagal melakukan pembayaran' };
        }
    }

    // Wallet Methods
    async getWalletBalance() {
        try {
            const response = await this.request('/wallet/balance');
            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            return { success: false, message: 'Gagal mengambil saldo' };
        }
    }

    async getTransactionHistory(page = 1, limit = 10) {
        try {
            const response = await this.request(`/ppob/transactions?page=${page}&limit=${limit}`);
            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, data: data.data };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            return { success: false, message: 'Gagal mengambil riwayat transaksi' };
        }
    }

    // Utility Methods
    isLoggedIn() {
        return !!this.token;
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(amount);
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('id-ID', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Global API instance
window.gameStoreAPI = new GameStoreAPI();
