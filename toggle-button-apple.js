document.addEventListener('DOMContentLoaded', function () {
    const readyBtn = document.getElementById("ready-btn");
    const customBtn = document.getElementById("custom-btn");
    const toggleBg = document.getElementById("toggle-bg");
    function doubleVibration() {
        if (Telegram?.WebApp?.HapticFeedback) {
            Telegram.WebApp.HapticFeedback.impactOccurred('light');
            setTimeout(() => {
                Telegram.WebApp.HapticFeedback.impactOccurred('light');
            }, 100); 
        }
    }
    readyBtn.addEventListener("click", () => {
        toggleBg.style.transform = "translateX(0)";
        document.querySelector('.Video').style.display = 'block';
        document.querySelector('.Live').style.display = 'none';
        doubleVibration();
    });
    customBtn.addEventListener("click", () => {
        toggleBg.style.transform = "translateX(100%) translateX(2px)";
        document.querySelector('.Video').style.display = 'none';
        document.querySelector('.Live').style.display = 'block';
        doubleVibration();
    });
});