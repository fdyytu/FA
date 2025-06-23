// Discord Stats Data Loader
async function loadDiscordStats() {
    try {
        // Get all Discord data in parallel with error handling
        const [logsResponse, commandsResponse, botsResponse] = await Promise.all([
            apiRequest('/discord/logs?limit=10').catch(() => ({ data: { logs: [] } })),
            apiRequest('/discord/commands/recent?limit=5').catch(() => ({ data: { commands: [] } })),
            apiRequest('/discord/bots').catch(() => ({ data: { bots: [] } }))
        ]);
        
        // Update UI with available data
        if (logsResponse && logsResponse.data) {
            updateDiscordLogs(logsResponse.data.logs || []);
        }
        
        if (commandsResponse && commandsResponse.data) {
            updateDiscordCommands(commandsResponse.data.commands || []);
        }
        
        if (botsResponse && botsResponse.data) {
            updateDiscordBots(botsResponse.data.bots || []);
        }
        
        // Remove error states if any
        document.querySelectorAll('.discord-section').forEach(section => {
            section.classList.remove('error');
        });
        
    } catch (error) {
        console.error('Error loading Discord stats:', error);
        showToast('Beberapa data Discord tidak dapat dimuat', 'warning');
        
        // Add error state to sections
        document.querySelectorAll('.discord-section').forEach(section => {
            section.classList.add('error');
        });
    }
}

// Export function
window.loadDiscordStats = loadDiscordStats;
