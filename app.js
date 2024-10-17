window.Telegram.WebApp.ready();

// Функция для настройки темы
function applyTheme() {
    const themeParams = window.Telegram.WebApp.themeParams;

    // Если тема светлая, делаем её темнее
    if (themeParams.bg_color === '#ffffff') {
        document.documentElement.style.setProperty('--tg-theme-bg-color', 'var(--tg-light-bg-color)');
        document.documentElement.style.setProperty('--tg-theme-text-color', 'var(--tg-light-text-color)');
    } else {
        // Иначе используем тёмную тему
        document.documentElement.style.setProperty('--tg-theme-bg-color', 'var(--tg-dark-bg-color)');
        document.documentElement.style.setProperty('--tg-theme-text-color', 'var(--tg-dark-text-color)');
    }

    // Применение переменных
    document.body.style.backgroundColor = window.getComputedStyle(document.documentElement).getPropertyValue('--tg-theme-bg-color');
    document.body.style.color = window.getComputedStyle(document.documentElement).getPropertyValue('--tg-theme-text-color');
}

// Вызываем функцию при загрузке приложения
applyTheme();