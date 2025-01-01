document.addEventListener('DOMContentLoaded', function () {
    const readyBtn2 = document.getElementById("ready-btn-video");
    const customBtn2 = document.getElementById("custom-btn-video");
    const toggleBg2 = document.getElementById("toggle-bg-video");
    function doubleVibration() {
        if (Telegram?.WebApp?.HapticFeedback) {
            Telegram.WebApp.HapticFeedback.impactOccurred('light');
            setTimeout(() => {
                Telegram.WebApp.HapticFeedback.impactOccurred('light');
            }, 100); 
        }
    }
    readyBtn2.addEventListener("click", () => {
        toggleBg2.style.transform = "translateX(0)";
        document.querySelector('.Video-description').style.display = 'block';
        document.querySelector('.Video-episode').style.display = 'none';
        doubleVibration();
    });
    customBtn2.addEventListener("click", () => {
        toggleBg2.style.transform = "translateX(100%) translateX(2px)";
        document.querySelector('.Video-description').style.display = 'none';
        document.querySelector('.Video-episode').style.display = 'block';
        doubleVibration();
    });
});