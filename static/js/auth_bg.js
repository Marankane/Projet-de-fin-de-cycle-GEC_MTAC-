/**
 * Script de rotation du fond d'écran pour la page de connexion
 */
document.addEventListener('DOMContentLoaded', function() {
    const authWrapper = document.querySelector('.auth-wrapper');
    
    // Liste des images présentes dans static/img/
    // Adaptez ces noms aux fichiers réels de votre projet
    const images = [
        '/static/img/rout6em.jpg',
        '/static/img/aereport2.jpg',
        '/static/img/aereport3.webp',
    ];

    if (authWrapper && images.length > 0) {
        let currentIndex = 0;
        
        // Appliquer la première image immédiatement au chargement de la page
        authWrapper.style.backgroundImage = `url('${images[currentIndex]}')`;

        setInterval(() => {
            currentIndex = (currentIndex + 1) % images.length;
            authWrapper.style.backgroundImage = `url('${images[currentIndex]}')`;
        }, 5000); // 5000ms = 5 secondes
    }
});
