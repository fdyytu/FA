// Settings Export/Import Utils
// Maksimal 50 baris per file

class SettingsExportUtils {
    // Export settings to JSON file
    exportSettings(currentSettings) {
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
        
        return true;
    }

    // Create file input for import
    createFileInput(onFileSelect) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = onFileSelect;
        return input;
    }

    // Parse imported file
    parseImportFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                try {
                    const importData = JSON.parse(e.target.result);
                    
                    if (!importData.settings) {
                        reject(new Error('Format file tidak valid'));
                        return;
                    }
                    
                    resolve(importData.settings);
                } catch (error) {
                    reject(new Error('File tidak valid atau terjadi kesalahan'));
                }
            };
            
            reader.onerror = () => {
                reject(new Error('Gagal membaca file'));
            };
            
            reader.readAsText(file);
        });
    }
}

// Export instance
window.settingsExportUtils = new SettingsExportUtils();
