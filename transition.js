document.addEventListener('DOMContentLoaded', function () {
    Telegram.WebApp.BackButton.show();
    Telegram.WebApp.BackButton.onClick(() => {
        window.history.back(); 
        Telegram.WebApp.BackButton.hide(); 
    });
    window.addEventListener("popstate", () => {
        Telegram.WebApp.BackButton.hide();
    });  
});