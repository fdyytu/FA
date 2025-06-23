// Dashboard Discord Modular - Replacement untuk dashboard_discord.js
// Menggunakan modul-modul kecil maksimal 50 baris

// Global variables untuk kompatibilitas
let bots = [];
let worlds = [];
let recentCommands = [];
let botLogs = [];

// Initialize Discord dashboard - fungsi utama
async function initDiscordDashboard() {
    try {
        await discordModuleLoader.loadAll();
        if (typeof discordMainController !== 'undefined') {
            await discordMainController.init();
        } else {
            console.error('Discord main controller not loaded');
        }
    } catch (error) {
        console.error('Error initializing Discord dashboard:', error);
        if (typeof showToast === 'function') {
            showToast('Gagal memuat dashboard Discord', 'error');
        }
    }
}

// Fungsi kompatibilitas untuk file lama
async function loadDiscordStats() {
    if (typeof discordMainController !== 'undefined') {
        await discordMainController.loadStats();
    }
}

async function loadBots() {
    if (typeof DiscordDataLoader !== 'undefined') {
        bots = await DiscordDataLoader.loadBots();
    }
}

async function loadWorlds() {
    if (typeof DiscordDataLoader !== 'undefined') {
        worlds = await DiscordDataLoader.loadWorlds();
    }
}

async function loadRecentCommands() {
    if (typeof DiscordDataLoader !== 'undefined') {
        recentCommands = await DiscordDataLoader.loadRecentCommands();
    }
}

// Auto-initialize jika DOM sudah ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDiscordDashboard);
} else {
    initDiscordDashboard();
}
