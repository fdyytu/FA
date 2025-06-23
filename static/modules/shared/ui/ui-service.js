// UI Service Module - Navigation & Mobile Menu
// Maksimal 50 baris per file

class UIService {
    static initMobileMenu() {
        const openBtn = document.getElementById('openSidebar');
        const closeBtn = document.getElementById('closeSidebar');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobileMenuOverlay');

        if (openBtn) {
            openBtn.addEventListener('click', () => {
                sidebar.classList.remove('sidebar-hidden');
                overlay.classList.remove('hidden');
            });
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', this.closeMobileMenu);
        }
        
        if (overlay) {
            overlay.addEventListener('click', this.closeMobileMenu);
        }
    }

    static closeMobileMenu() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobileMenuOverlay');
        sidebar.classList.add('sidebar-hidden');
        overlay.classList.add('hidden');
    }

    static initNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        const currentPage = window.location.pathname.split('/').pop();
        
        navItems.forEach(item => {
            const href = item.getAttribute('href');
            if (href && href === currentPage) {
                item.classList.add('active');
            }
            
            item.addEventListener('click', (e) => {
                if (item.tagName === 'A' && item.getAttribute('href')) {
                    return;
                }
                
                e.preventDefault();
                navItems.forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');
            });
        });
    }
}

window.UIService = UIService;
