document.addEventListener('DOMContentLoaded', function () {
    Telegram.WebApp.BackButton.show();
    Telegram.WebApp.BackButton.onClick(() => {
        window.location.href = "index2.html";
        Telegram.WebApp.BackButton.hide(); 
    });
});