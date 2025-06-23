// Discord Module Loader
// Maksimal 50 baris per modul

class DiscordModuleLoader {
    constructor() {
        this.modules = [
            '/static/modules/admin/discord/api/discord-api-service.js',
            '/static/modules/admin/discord/api/discord-monitoring-api.js',
            '/static/modules/admin/discord/ui/discord-stats-ui.js',
            '/static/modules/admin/discord/components/discord-bots-list.js',
            '/static/modules/admin/discord/components/discord-bots-fallback.js',
            '/static/modules/admin/discord/utils/discord-ui-utils.js',
            '/static/modules/admin/discord/utils/discord-bot-utils.js',
            '/static/modules/admin/discord/handlers/discord-data-loader.js',
            '/static/modules/admin/discord/discord-main-controller.js'
        ];
        this.loadedModules = new Set();
    }

    // Load all modules
    async loadAll() {
        try {
            for (const module of this.modules) {
                await this.loadModule(module);
            }
            console.log('All Discord modules loaded successfully');
            return true;
        } catch (error) {
            console.error('Error loading Discord modules:', error);
            return false;
        }
    }

    // Load single module
    async loadModule(src) {
        return new Promise((resolve, reject) => {
            if (this.loadedModules.has(src)) {
                resolve();
                return;
            }
            const script = document.createElement('script');
            script.src = src;
            script.onload = () => {
                this.loadedModules.add(src);
                resolve();
            };
            script.onerror = () => reject(new Error(`Failed to load ${src}`));
            document.head.appendChild(script);
        });
    }
}

// Export instance
const discordModuleLoader = new DiscordModuleLoader();
