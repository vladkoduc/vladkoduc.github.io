function navigateToPage(url) {
    window.location.href = url; 
}
document.addEventListener('DOMContentLoaded', function() {
function handleFullscreenMode() {
    const currentUrl = window.location.pathname;
    if (currentUrl.includes("videoplayer.html")) {
        Telegram.WebApp.requestFullscreen();
    } else {
        Telegram.WebApp.exitFullscreen();
    }
}
window.addEventListener("load", handleFullscreenMode);
window.addEventListener("popstate", handleFullscreenMode);
});