document.addEventListener('DOMContentLoaded', function () {
    if (window.Telegram && window.Telegram.WebApp) {
        Telegram.WebApp.ready();
        Telegram.WebApp.expand();
        Telegram.WebApp.disableVerticalSwipes();
        const headerColor = 'var(--tg-theme-bg-color)';
        const backgroundColor = 'var(--tg-theme-secondary-bg-color)';
        const isAppleDevice = /iPhone|iPad|iPod|Macintosh/i.test(navigator.userAgent);
        if (isAppleDevice) {
            Telegram.WebApp.setBackgroundColor(headerColor);
            Telegram.WebApp.setHeaderColor(headerColor);
            Telegram.WebApp.setBottomBarColor(headerColor);
        } else {
            Telegram.WebApp.setBackgroundColor(backgroundColor);
            Telegram.WebApp.setHeaderColor(backgroundColor);
            Telegram.WebApp.setBottomBarColor(backgroundColor);
        }   
    }   
});