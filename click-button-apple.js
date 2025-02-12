document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".apple .rectangle2, .apple .rectangle3, .apple .rectangle4, .apple .rectangle5, .apple .rectangle8, .apple .rectangle11, .apple .rectangle13, .apple .rectangle14");
    buttons.forEach((button) => {
        button.style.transition = "background-color 0.1s ease";
        button.addEventListener("touchstart", () => {
            const hintColor = getComputedStyle(document.documentElement)
                .getPropertyValue("--tg-theme-hint-color");
            button.style.backgroundColor = convertToRGBA(hintColor, 0.3);
        });
        button.addEventListener("touchend", () => {
            const sectionColor = getComputedStyle(document.documentElement)
                .getPropertyValue("--tg-theme-section-bg-color");
            button.style.backgroundColor = sectionColor;
        });
    });
    function convertToRGBA(hexColor, opacity) {
        const hex = hexColor.trim().replace("#", "");
        const bigint = parseInt(hex, 16);
        const r = (bigint >> 16) & 255;
        const g = (bigint >> 8) & 255;
        const b = bigint & 255;
        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }
});