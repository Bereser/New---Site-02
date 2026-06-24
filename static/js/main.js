// Script global para todas as páginas

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle (se necessário)
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
});
