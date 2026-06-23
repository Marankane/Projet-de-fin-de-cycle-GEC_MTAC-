document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const toggleBtn = document.getElementById('sidebar-toggle-btn');

    if (!sidebar || !mainContent || !toggleBtn) {
        console.warn("Sidebar, main content, or toggle button not found. Sidebar toggle functionality disabled.");
        return;
    }

    // Load saved state from localStorage
    const savedState = localStorage.getItem('sidebarState');
    if (savedState) {
        if (savedState === 'collapsed') {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('sidebar-collapsed');
        } else if (savedState === 'hidden') {
            sidebar.classList.add('hidden');
            mainContent.classList.add('sidebar-hidden');
        }
    }

    toggleBtn.addEventListener('click', function() {
        const isMobile = window.innerWidth <= 768;

        if (isMobile) {
            // Sur mobile, on bascule simplement la visibilité sans passer par l'état "réduit"
            sidebar.classList.toggle('show-mobile');
            return;
        }

        if (sidebar.classList.contains('hidden')) {
            sidebar.classList.remove('hidden');
            mainContent.classList.remove('sidebar-hidden');
            localStorage.setItem('sidebarState', 'full');
        } else if (sidebar.classList.contains('collapsed')) {
            sidebar.classList.remove('collapsed');
            mainContent.classList.remove('sidebar-collapsed');
            sidebar.classList.add('hidden');
            mainContent.classList.add('sidebar-hidden');
            localStorage.setItem('sidebarState', 'hidden');
        } else {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('sidebar-collapsed');
            localStorage.setItem('sidebarState', 'collapsed');
        }
    });
});