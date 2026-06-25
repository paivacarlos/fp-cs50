// Fade out and remove flash messages automatically after a few seconds
document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('.flash-messages .flash-message');
    flashMessages.forEach((msg) => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                msg.remove();
            }, 500);
        }, 4000); // Exibe por 4 segundos
    });
});
