document.addEventListener('DOMContentLoaded', function () {
    (function() {
        var userAgent = navigator.userAgent;
        if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
            document.body.classList.add('apple');
        } else if (/Macintosh/.test(userAgent)) {
            document.body.classList.add('appleMac');
        } else if (/Android/.test(userAgent)) {
            document.body.classList.add('android');
        } else {
            document.body.classList.add('non-apple');
        }
    })();
});