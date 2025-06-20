// Discord Bot Manager
class DiscordBotManager {
    constructor(dataService, uiController) {
        this.dataService = dataService;
        this.uiController = uiController;
    }

    async toggleBot(botId) {
        UIUtils.showLoading(true);
        
        try {
            const response = await apiClient.post(`/admin/discord/bots/${botId}/toggle`);
            
            if (response && response.ok) {
                UIUtils.showToast('Status bot berhasil diubah', 'success');
                await this.loadAndRenderBots();
            } else {
                const errorData = await response.json();
                UIUtils.showToast(errorData.message || 'Gagal mengubah status bot', 'error');
            }
        } catch (error) {
            console.error('Error toggling bot:', error);
            UIUtils.showToast('Terjadi kesalahan saat mengubah status bot', 'error');
        } finally {
            UIUtils.showLoading(false);
        }
    }

    async deleteBot(botId) {
        if (!confirm('Apakah Anda yakin ingin menghapus bot ini?')) {
            return;
        }
        
        UIUtils.showLoading(true);
        
        try {
            const response = await apiClient.delete(`/admin/discord/bots/${botId}`);
            
            if (response && response.ok) {
                UIUtils.showToast('Bot berhasil dihapus', 'success');
                await this.loadAndRenderBots();
            } else {
                const errorData = await response.json();
                UIUtils.showToast(errorData.message || 'Gagal menghapus bot', 'error');
            }
        } catch (error) {
            console.error('Error deleting bot:', error);
            UIUtils.showToast('Terjadi kesalahan saat menghapus bot', 'error');
        } finally {
            UIUtils.showLoading(false);
        }
    }

    async loadAndRenderBots() {
        const bots = await this.dataService.loadBots();
        this.uiController.renderBotsList(bots);
    }
}
