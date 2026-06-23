/**
 * Composant Cloche de Notifications
 * Affiche les notifications avec badge de compteur
 * Trie par urgence puis date d'arrivée
 */

class NotificationBell {
    constructor(options = {}) {
        this.bellContainer = document.getElementById('notification-bell-container');
        this.bellIcon = document.getElementById('notification-bell-icon');
        this.countBadge = document.getElementById('notification-count-badge');
        this.dropdownMenu = document.getElementById('notification-dropdown-menu');
        this.notificationsList = document.getElementById('notifications-list');
        this.markAllBtn = document.getElementById('mark-all-as-read-btn');
        
        this.apiUrl = options.apiUrl || '/api/notifications/';
        this.updateInterval = options.updateInterval || 30000; // 30 secondes
        this.notificationLimit = options.notificationLimit || 8;
        
        if (!this.bellContainer) return;
        
        this.init();
    }
    
    init() {
        // Event listeners
        if (this.bellIcon) {
            this.bellIcon.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown();
            });
        }
        
        if (this.markAllBtn) {
            this.markAllBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.markAllAsRead();
            });
        }
        
        // Fermer le dropdown en cliquant ailleurs
        document.addEventListener('click', (e) => {
            if (!this.bellContainer.contains(e.target)) {
                this.closeDropdown();
            }
        });
        
        // Charger les notifications au démarrage
        this.loadNotifications();
        
        // Actualiser les notifications toutes les 30 secondes
        setInterval(() => this.loadNotifications(), this.updateInterval);
    }
    
    toggleDropdown() {
        if (this.dropdownMenu.classList.contains('show')) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }
    
    openDropdown() {
        this.dropdownMenu.classList.add('show');
        this.bellIcon.classList.add('active');
        
        // Marquer comme lues après 2 secondes de consultation
        setTimeout(() => {
            const unreadNotifications = this.dropdownMenu.querySelectorAll('[data-notification-id]:not([data-read="true"])');
            unreadNotifications.forEach(notif => {
                const notifId = notif.getAttribute('data-notification-id');
                this.markAsRead(notifId, false); // false = ne pas recharger
            });
            // Recharger après tous les marquages
            if (unreadNotifications.length > 0) {
                setTimeout(() => this.loadNotifications(), 500);
            }
        }, 2000);
    }
    
    closeDropdown() {
        this.dropdownMenu.classList.remove('show');
        this.bellIcon.classList.remove('active');
    }
    
    loadNotifications() {
        const url = this.apiUrl.includes('/unread/') 
            ? this.apiUrl 
            : this.apiUrl.replace('notifications/', 'notifications/unread/') + `?limit=${this.notificationLimit}`;
        
        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken(),
            },
        })
        .then(response => response.json())
        .then(data => {
            this.updateBadge(data.count);
            this.renderNotifications(data.notifications || []);
        })
        .catch(error => console.error('Erreur chargement notifications:', error));
    }
    
    renderNotifications(notifications) {
        if (!this.notificationsList) return;
        
        if (notifications.length === 0) {
            this.notificationsList.innerHTML = `
                <div class="notification-empty text-center py-4 text-muted">
                    <i class="bi bi-check-circle" style="font-size: 2rem;"></i>
                    <p>Aucune notification</p>
                </div>
            `;
            return;
        }
        
        this.notificationsList.innerHTML = notifications.map(notif => this.renderNotificationItem(notif)).join('');
        
        // Ajouter event listeners aux boutons de notification
        this.notificationsList.querySelectorAll('.notification-item-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const notifId = btn.getAttribute('data-notification-id');
                const lien = btn.getAttribute('data-lien');
                this.markAsRead(notifId, true);
                if (lien) {
                    setTimeout(() => window.location.href = lien, 300);
                }
            });
        });
    }
    
    renderNotificationItem(notif) {
        const typeIcon = this.getTypeIcon(notif.type);
        const typeLabel = this.getTypeLabel(notif.type);
        const urgentClass = notif.is_urgent ? 'urgent' : '';
        const dateFormatted = this.formatDate(new Date(notif.cree_le));
        const courierInfo = notif.courrier_numero ? ` (${notif.courrier_numero})` : '';
        
        return `
            <button 
                class="notification-item-btn ${urgentClass}" 
                data-notification-id="${notif.id}" 
                data-lien="${notif.lien}"
                data-read="${notif.lue}"
                type="button">
                <div class="notification-icon ${typeIcon}">
                    <i class="bi ${this.getNotificationIcon(notif.type)}"></i>
                </div>
                <div class="notification-content">
                    <div class="notification-title">
                        ${notif.titre}
                        ${notif.is_urgent ? '<span class="urgent-badge">🔴 URGENT</span>' : ''}
                    </div>
                    <div class="notification-message">${notif.message}${courierInfo}</div>
                    <div class="notification-time">${dateFormatted}</div>
                </div>
                <div class="notification-close">
                    <i class="bi bi-x"></i>
                </div>
            </button>
        `;
    }
    
    getTypeIcon(type) {
        const icons = {
            'COURRIER_ASSIGNE': 'icon-primary',
            'COURRIER_ECHU': 'icon-danger',
            'COURRIER_RETOURNE': 'icon-warning',
            'RAPPEL': 'icon-info',
        };
        return icons[type] || 'icon-secondary';
    }
    
    getTypeLabel(type) {
        const labels = {
            'COURRIER_ASSIGNE': 'Courrier assigné',
            'COURRIER_ECHU': 'Courrier échu',
            'COURRIER_RETOURNE': 'Courrier retourné',
            'RAPPEL': 'Rappel',
        };
        return labels[type] || 'Notification';
    }
    
    getNotificationIcon(type) {
        const icons = {
            'COURRIER_ASSIGNE': 'bi-envelope-check',
            'COURRIER_ECHU': 'bi-exclamation-triangle-fill',
            'COURRIER_RETOURNE': 'bi-arrow-counterclockwise',
            'RAPPEL': 'bi-bell-fill',
        };
        return icons[type] || 'bi-bell';
    }
    
    formatDate(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'À l\'instant';
        if (diffMins < 60) return `Il y a ${diffMins}m`;
        if (diffHours < 24) return `Il y a ${diffHours}h`;
        if (diffDays < 7) return `Il y a ${diffDays}j`;
        
        return date.toLocaleDateString('fr-FR', { 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    markAsRead(notificationId, reload = true) {
        const url = this.apiUrl.replace('notifications/', `notifications/${notificationId}/read/`);
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken(),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (reload) {
                this.loadNotifications();
            }
        })
        .catch(error => console.error('Erreur marquage notification:', error));
    }
    
    markAllAsRead() {
        const url = this.apiUrl.replace('notifications/', 'notifications/read-all/');
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken(),
            },
        })
        .then(response => response.json())
        .then(data => {
            this.loadNotifications();
        })
        .catch(error => console.error('Erreur marquage toutes notifications:', error));
    }
    
    updateBadge(count) {
        if (!this.countBadge) return;
        
        if (count > 0) {
            this.countBadge.textContent = count > 99 ? '99+' : count;
            this.countBadge.style.display = 'flex';
            this.bellIcon.classList.add('has-notifications');
        } else {
            this.countBadge.style.display = 'none';
            this.bellIcon.classList.remove('has-notifications');
        }
    }
    
    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialiser la cloche au chargement du DOM
document.addEventListener('DOMContentLoaded', () => {
    new NotificationBell({
        apiUrl: '/api/notifications/unread/',
        updateInterval: 30000, // 30 secondes
        notificationLimit: 8,
    });
});
