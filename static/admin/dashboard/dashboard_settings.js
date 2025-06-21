// Dashboard settings functionality
let currentSettings = {};
let hasUnsavedChanges = false;

// Initialize settings dashboard
async function initSettingsDashboard() {
    const token = checkAuth();
    if (!token) return;

    showLoading(true);
    
    try {
        await loadAllSettings();
        initEventListeners();
        initTabNavigation();
        showToast('Dashboard settings berhasil dimuat', 'success', 3000);
    } catch (error) {
        console.error('Error loading settings dashboard:', error);
        showToast('Gagal memuat data settings', 'error');
    } finally {
        showLoading(false);
    }
}

// Load all settings
async function loadAllSettings() {
    try {
        const response = await apiRequest('/api/v1/admin/settings');
        
        if (response && response.ok) {
            const data = await response.json();
            currentSettings = data.data || {};
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
        
        populateSettingsForms();
    } catch (error) {
        console.error('Error loading settings:', error);
        currentSettings = {};
        populateSettingsForms();
    }
}

// Populate settings forms
function populateSettingsForms() {
    // General settings
    populateForm('siteInfoForm', currentSettings.general || {});
    populateForm('businessForm', currentSettings.general || {});
    
    // Payment settings
    populatePaymentSettings();
    
    // Notification settings
    populateForm('emailNotificationForm', currentSettings.notification || {});
    populateForm('discordNotificationForm', currentSettings.notification || {});
    
    // Security settings
    populateForm('securityConfigForm', currentSettings.security || {});
    
    // API settings
    populateApiSettings();
}

// Populate form with data
function populateForm(formId, data) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    Object.keys(data).forEach(key => {
        const element = form.querySelector(`[name="${key}"]`);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = data[key];
            } else {
                element.value = data[key] || '';
            }
        }
    });
}

// Populate payment settings
function populatePaymentSettings() {
    const paymentData = currentSettings.payment || {};
    
    // Payment gateways
    Object.keys(paymentData).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = paymentData[key];
            } else if (element.type === 'password' && paymentData[key]) {
                element.value = '***hidden***';
                element.dataset.originalValue = paymentData[key];
            } else {
                element.value = paymentData[key] || '';
            }
        }
    });
    
    // Payment configuration
    populateForm('paymentConfigForm', paymentData);
}

// Populate API settings
function populateApiSettings() {
    const apiData = currentSettings.api || {};
    
    const apiKeyElement = document.getElementById('apiKey');
    const webhookSecretElement = document.getElementById('webhookSecret');
    
    if (apiKeyElement && apiData.api_key) {
        apiKeyElement.value = apiData.api_key;
    }
    
    if (webhookSecretElement && apiData.webhook_secret) {
        webhookSecretElement.value = apiData.webhook_secret;
    }
}

// Initialize tab navigation
function initTabNavigation() {
    const tabs = document.querySelectorAll('.settings-tab');
    const contents = document.querySelectorAll('.settings-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.add('hidden'));
            
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Show corresponding content
            const tabId = tab.id.replace('Tab', 'Settings');
            const content = document.getElementById(tabId);
            if (content) {
                content.classList.remove('hidden');
            }
        });
    });
}

// Initialize event listeners
function initEventListeners() {
    // Form submissions
    const forms = [
        'siteInfoForm',
        'businessForm',
        'paymentConfigForm',
        'emailNotificationForm',
        'discordNotificationForm',
        'securityConfigForm',
        'changePasswordForm'
    ];
    
    forms.forEach(formId => {
        const form = document.getElementById(formId);
        if (form) {
            form.addEventListener('submit', (e) => handleFormSubmit(e, formId));
        }
    });
    
    // Special buttons
    const savePaymentBtn = document.getElementById('savePaymentBtn');
    if (savePaymentBtn) {
        savePaymentBtn.addEventListener('click', savePaymentSettings);
    }
    
    const saveAllBtn = document.getElementById('saveAllBtn');
    if (saveAllBtn) {
        saveAllBtn.addEventListener('click', saveAllSettings);
    }
    
    // API key generation
    const generateApiKeyBtn = document.getElementById('generateApiKey');
    if (generateApiKeyBtn) {
        generateApiKeyBtn.addEventListener('click', () => generateApiKey('api_key'));
    }
    
    const generateWebhookSecretBtn = document.getElementById('generateWebhookSecret');
    if (generateWebhookSecretBtn) {
        generateWebhookSecretBtn.addEventListener('click', () => generateApiKey('webhook_secret'));
    }
    
    // Track changes
    trackFormChanges();
    
    // Warn before leaving with unsaved changes
    window.addEventListener('beforeunload', (e) => {
        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
}

// Track form changes
function trackFormChanges() {
    const inputs = document.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        input.addEventListener('change', () => {
            hasUnsavedChanges = true;
            updateSaveButtonState();
        });
    });
}

// Update save button state
function updateSaveButtonState() {
    const saveAllBtn = document.getElementById('saveAllBtn');
    if (saveAllBtn) {
        if (hasUnsavedChanges) {
            saveAllBtn.classList.add('bg-orange-600', 'hover:bg-orange-700');
            saveAllBtn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
            saveAllBtn.innerHTML = '<i class="fas fa-exclamation-triangle mr-2"></i>Ada Perubahan';
        } else {
            saveAllBtn.classList.remove('bg-orange-600', 'hover:bg-orange-700');
            saveAllBtn.classList.add('bg-blue-600', 'hover:bg-blue-700');
            saveAllBtn.innerHTML = '<i class="fas fa-save mr-2"></i>Simpan Semua';
        }
    }
}

// Handle form submission
async function handleFormSubmit(e, formId) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Convert checkboxes
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        data[checkbox.name] = checkbox.checked;
    });
    
    showLoading(true);
    
    try {
        let endpoint = '/settings/general';
        
        // Determine endpoint based on form
        switch (formId) {
            case 'siteInfoForm':
            case 'businessForm':
                endpoint = '/settings/general';
                break;
            case 'paymentConfigForm':
                endpoint = '/settings/payment';
                break;
            case 'emailNotificationForm':
            case 'discordNotificationForm':
                endpoint = '/settings/notification';
                break;
            case 'securityConfigForm':
                endpoint = '/settings/security';
                break;
            case 'changePasswordForm':
                endpoint = '/settings/change-password';
                break;
        }
        
        const response = await apiRequest(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
        
        if (response && response.ok) {
            showToast('Pengaturan berhasil disimpan', 'success');
            
            if (formId === 'changePasswordForm') {
                form.reset();
            } else {
                // Update current settings
                updateCurrentSettings(formId, data);
                hasUnsavedChanges = false;
                updateSaveButtonState();
            }
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal menyimpan pengaturan', 'error');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        showToast('Terjadi kesalahan saat menyimpan pengaturan', 'error');
    } finally {
        showLoading(false);
    }
}

// Update current settings
function updateCurrentSettings(formId, data) {
    switch (formId) {
        case 'siteInfoForm':
        case 'businessForm':
            currentSettings.general = { ...currentSettings.general, ...data };
            break;
        case 'paymentConfigForm':
            currentSettings.payment = { ...currentSettings.payment, ...data };
            break;
        case 'emailNotificationForm':
        case 'discordNotificationForm':
            currentSettings.notification = { ...currentSettings.notification, ...data };
            break;
        case 'securityConfigForm':
            currentSettings.security = { ...currentSettings.security, ...data };
            break;
    }
}

// Save payment settings
async function savePaymentSettings() {
    const paymentData = {};
    
    // Collect payment gateway settings
    const paymentFields = [
        'midtrans_enabled', 'midtrans_server_key', 'midtrans_client_key',
        'xendit_enabled', 'xendit_secret_key', 'xendit_webhook_token'
    ];
    
    paymentFields.forEach(field => {
        const element = document.getElementById(field);
        if (element) {
            if (element.type === 'checkbox') {
                paymentData[field] = element.checked;
            } else if (element.type === 'password' && element.value === '***hidden***') {
                // Keep original value if not changed
                paymentData[field] = element.dataset.originalValue || '';
            } else {
                paymentData[field] = element.value;
            }
        }
    });
    
    showLoading(true);
    
    try {
        const response = await apiRequest('/settings/payment-gateways', {
            method: 'PUT',
            body: JSON.stringify(paymentData)
        });
        
        if (response && response.ok) {
            showToast('Payment gateway settings berhasil disimpan', 'success');
            currentSettings.payment = { ...currentSettings.payment, ...paymentData };
            hasUnsavedChanges = false;
            updateSaveButtonState();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal menyimpan payment settings', 'error');
        }
    } catch (error) {
        console.error('Error saving payment settings:', error);
        showToast('Terjadi kesalahan saat menyimpan payment settings', 'error');
    } finally {
        showLoading(false);
    }
}

// Save all settings
async function saveAllSettings() {
    if (!hasUnsavedChanges) {
        showToast('Tidak ada perubahan untuk disimpan', 'info');
        return;
    }
    
    showLoading(true);
    
    try {
        const allData = {
            general: collectFormData(['siteInfoForm', 'businessForm']),
            payment: collectFormData(['paymentConfigForm']),
            notification: collectFormData(['emailNotificationForm', 'discordNotificationForm']),
            security: collectFormData(['securityConfigForm'])
        };
        
        const response = await apiRequest('/settings/bulk', {
            method: 'PUT',
            body: JSON.stringify(allData)
        });
        
        if (response && response.ok) {
            showToast('Semua pengaturan berhasil disimpan', 'success');
            currentSettings = { ...currentSettings, ...allData };
            hasUnsavedChanges = false;
            updateSaveButtonState();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal menyimpan pengaturan', 'error');
        }
    } catch (error) {
        console.error('Error saving all settings:', error);
        showToast('Terjadi kesalahan saat menyimpan pengaturan', 'error');
    } finally {
        showLoading(false);
    }
}

// Collect form data
function collectFormData(formIds) {
    const data = {};
    
    formIds.forEach(formId => {
        const form = document.getElementById(formId);
        if (form) {
            const formData = new FormData(form);
            const formObject = Object.fromEntries(formData.entries());
            
            // Handle checkboxes
            const checkboxes = form.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                formObject[checkbox.name] = checkbox.checked;
            });
            
            Object.assign(data, formObject);
        }
    });
    
    return data;
}

// Generate API key
async function generateApiKey(type) {
    if (!confirm(`Apakah Anda yakin ingin generate ${type === 'api_key' ? 'API Key' : 'Webhook Secret'} baru?`)) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await apiRequest(`/settings/generate-${type.replace('_', '-')}`, {
            method: 'POST'
        });
        
        if (response && response.ok) {
            const data = await response.json();
            const newKey = data.data[type];
            
            const element = document.getElementById(type === 'api_key' ? 'apiKey' : 'webhookSecret');
            if (element) {
                element.value = newKey;
            }
            
            showToast(`${type === 'api_key' ? 'API Key' : 'Webhook Secret'} baru berhasil digenerate`, 'success');
            
            // Update current settings
            currentSettings.api = currentSettings.api || {};
            currentSettings.api[type] = newKey;
        } else {
            const errorData = await response.json();
            showToast(errorData.message || `Gagal generate ${type}`, 'error');
        }
    } catch (error) {
        console.error(`Error generating ${type}:`, error);
        showToast(`Terjadi kesalahan saat generate ${type}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Test email configuration
async function testEmailConfig() {
    const emailForm = document.getElementById('emailNotificationForm');
    if (!emailForm) return;
    
    const formData = new FormData(emailForm);
    const emailConfig = Object.fromEntries(formData.entries());
    
    showLoading(true);
    
    try {
        const response = await apiRequest('/settings/test-email', {
            method: 'POST',
            body: JSON.stringify(emailConfig)
        });
        
        if (response && response.ok) {
            showToast('Test email berhasil dikirim', 'success');
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal mengirim test email', 'error');
        }
    } catch (error) {
        console.error('Error testing email config:', error);
        showToast('Terjadi kesalahan saat test email', 'error');
    } finally {
        showLoading(false);
    }
}

// Test Discord webhook
async function testDiscordWebhook() {
    const webhookUrl = document.getElementById('discordWebhook')?.value;
    
    if (!webhookUrl) {
        showToast('Masukkan Discord Webhook URL terlebih dahulu', 'warning');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await apiRequest('/settings/test-discord', {
            method: 'POST',
            body: JSON.stringify({ webhook_url: webhookUrl })
        });
        
        if (response && response.ok) {
            showToast('Test Discord webhook berhasil dikirim', 'success');
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal mengirim test Discord webhook', 'error');
        }
    } catch (error) {
        console.error('Error testing Discord webhook:', error);
        showToast('Terjadi kesalahan saat test Discord webhook', 'error');
    } finally {
        showLoading(false);
    }
}

// Export settings
function exportSettings() {
    const exportData = {
        settings: currentSettings,
        exported_at: new Date().toISOString(),
        version: '1.0'
    };
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `fa-settings-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    showToast('Settings berhasil diekspor', 'success');
}

// Import settings
function importSettings(file) {
    const reader = new FileReader();
    
    reader.onload = async (e) => {
        try {
            const importData = JSON.parse(e.target.result);
            
            if (!importData.settings) {
                showToast('Format file tidak valid', 'error');
                return;
            }
            
            if (!confirm('Apakah Anda yakin ingin mengimpor pengaturan ini? Pengaturan saat ini akan ditimpa.')) {
                return;
            }
            
            showLoading(true);
            
            const response = await apiRequest('/settings/import', {
                method: 'POST',
                body: JSON.stringify(importData.settings)
            });
            
            if (response && response.ok) {
                showToast('Settings berhasil diimpor', 'success');
                await loadAllSettings();
            } else {
                const errorData = await response.json();
                showToast(errorData.message || 'Gagal mengimpor settings', 'error');
            }
        } catch (error) {
            console.error('Error importing settings:', error);
            showToast('File tidak valid atau terjadi kesalahan', 'error');
        } finally {
            showLoading(false);
        }
    };
    
    reader.readAsText(file);
}

// Reset settings to default
async function resetToDefault() {
    if (!confirm('Apakah Anda yakin ingin mereset semua pengaturan ke default? Tindakan ini tidak dapat dibatalkan.')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await apiRequest('/settings/reset', {
            method: 'POST'
        });
        
        if (response && response.ok) {
            showToast('Settings berhasil direset ke default', 'success');
            await loadAllSettings();
            hasUnsavedChanges = false;
            updateSaveButtonState();
        } else {
            const errorData = await response.json();
            showToast(errorData.message || 'Gagal reset settings', 'error');
        }
    } catch (error) {
        console.error('Error resetting settings:', error);
        showToast('Terjadi kesalahan saat reset settings', 'error');
    } finally {
        showLoading(false);
    }
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', () => {
    initSettingsDashboard();
});
