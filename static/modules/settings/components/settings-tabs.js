// Settings Tab Navigation Component
// Maksimal 50 baris per file

class SettingsTabs {
    constructor() {
        this.activeTab = 'general';
    }

    // Initialize tab navigation
    initTabNavigation() {
        const tabs = document.querySelectorAll('.settings-tab');
        const contents = document.querySelectorAll('.settings-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchTab(tab, tabs, contents);
            });
        });
    }

    // Switch to specific tab
    switchTab(clickedTab, allTabs, allContents) {
        // Remove active class from all tabs
        allTabs.forEach(t => t.classList.remove('active'));
        allContents.forEach(c => c.classList.add('hidden'));
        
        // Add active class to clicked tab
        clickedTab.classList.add('active');
        
        // Show corresponding content
        const tabId = clickedTab.id.replace('Tab', 'Settings');
        const content = document.getElementById(tabId);
        if (content) {
            content.classList.remove('hidden');
        }
        
        // Update active tab
        this.activeTab = tabId.replace('Settings', '').toLowerCase();
    }

    // Get current active tab
    getActiveTab() {
        return this.activeTab;
    }

    // Switch to tab programmatically
    switchToTab(tabName) {
        const tab = document.getElementById(`${tabName}Tab`);
        if (tab) {
            tab.click();
        }
    }

    // Check if tab has unsaved changes
    hasUnsavedChanges(tabName) {
        const forms = this.getTabForms(tabName);
        return forms.some(form => this.formHasChanges(form));
    }

    // Get forms for specific tab
    getTabForms(tabName) {
        const tabContent = document.getElementById(`${tabName}Settings`);
        return tabContent ? Array.from(tabContent.querySelectorAll('form')) : [];
    }
}

// Export instance
window.settingsTabs = new SettingsTabs();
