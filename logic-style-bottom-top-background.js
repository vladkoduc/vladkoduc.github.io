function isMobile(){const userAgent = navigator.userAgent || navigator.vendor || window.opera;return /Mobi|Android|iPhone|iPad|iPod|BlackBerry|Windows Phone|Opera Mini|IEMobile|WPDesktop|Samsung|Nokia|Xiaomi|OnePlus|Huawei|Sony|Motorola|Oppo|Vivo|LG|HTC|Realme|Google|Pixel/i.test(userAgent);}if (isMobile()) {const headerColor = getComputedStyle(document.documentElement).getPropertyValue('--tg-theme-secondary-bg-color');Telegram.WebApp.setHeaderColor(headerColor);Telegram.WebApp.setBackgroundColor(headerColor);}