document.addEventListener("DOMContentLoaded", () => {
    const tg = window.Telegram.WebApp;
    const user = tg.initDataUnsafe?.user;
    if (user && user.id === 1781692500) {
        document.getElementById("specialButton").style.display = "flex";
    }
});
