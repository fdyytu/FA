// Settings Form UI Components
// Maksimal 50 baris per file

class SettingsFormUI {
    // Populate form with data
    populateForm(formId, data) {
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
    populatePaymentSettings(paymentData) {
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
    }

    // Populate API settings
    populateApiSettings(apiData) {
        const apiKeyElement = document.getElementById('apiKey');
        const webhookSecretElement = document.getElementById('webhookSecret');
        
        if (apiKeyElement && apiData.api_key) {
            apiKeyElement.value = apiData.api_key;
        }
        
        if (webhookSecretElement && apiData.webhook_secret) {
            webhookSecretElement.value = apiData.webhook_secret;
        }
    }

    // Collect form data
    collectFormData(formIds) {
        const data = {};
        
        formIds.forEach(formId => {
            const form = document.getElementById(formId);
            if (form) {
                const formData = new FormData(form);
                const formObject = Object.fromEntries(formData.entries());
                Object.assign(data, formObject);
            }
        });
        
        return data;
    }
}

// Export instance
window.settingsFormUI = new SettingsFormUI();
