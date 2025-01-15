document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.main-button');
    const slider = document.querySelector('.slider-main-button');
    function updateSlider(button) {
        const buttonRect = button.getBoundingClientRect();
        const containerRect = button.parentElement.getBoundingClientRect();
        slider.style.width = `${buttonRect.width + 16}px`; 
        slider.style.transform = `translateX(${buttonRect.left - containerRect.left - 8}px)`;
    }
    function updateActiveSlider() {
        const activeButton = document.querySelector('.main-button.active');
        if (activeButton) {
            updateSlider(activeButton);
        }
    }
    buttons.forEach((button) => {
        button.addEventListener('click', () => {
            if (Telegram && Telegram.WebApp && Telegram.WebApp.HapticFeedback) {
                Telegram.WebApp.HapticFeedback.impactOccurred('medium');
            }
            buttons.forEach(btn => btn.classList.remove('active')); 
            button.classList.add('active'); 
            updateSlider(button); 
        });
    });
    window.addEventListener('resize', updateActiveSlider);
    updateActiveSlider();
});
