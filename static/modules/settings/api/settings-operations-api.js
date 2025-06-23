// Settings Operations API Service
// Maksimal 50 baris per file

class SettingsOperationsApi {
    constructor() {
        this.baseUrl = '/api/v1';
    }

    // Save payment gateway settings
    async savePaymentGateways(paymentData) {
        const response = await apiRequest('/settings/payment-gateways', {
            method: 'PUT',
            body: JSON.stringify(paymentData)
        });
        return response;
    }

    // Generate API key
    async generateApiKey(type) {
        const response = await apiRequest(`/settings/generate-${type.replace('_', '-')}`, {
            method: 'POST'
        });
        return response;
    }

    // Test email configuration
    async testEmailConfig(emailConfig) {
        const response = await apiRequest('/settings/test-email', {
            method: 'POST',
            body: JSON.stringify(emailConfig)
        });
        return response;
    }

    // Test Discord webhook
    async testDiscordWebhook(webhookUrl) {
        const response = await apiRequest('/settings/test-discord', {
            method: 'POST',
            body: JSON.stringify({ webhook_url: webhookUrl })
        });
        return response;
    }

    // Import settings
    async importSettings(settingsData) {
        const response = await apiRequest('/settings/import', {
            method: 'POST',
            body: JSON.stringify(settingsData)
        });
        return response;
    }

    // Reset settings to default
    async resetToDefault() {
        const response = await apiRequest('/settings/reset', {
            method: 'POST'
        });
        return response;
    }
}

// Export instance
window.settingsOperationsApi = new SettingsOperationsApi();
