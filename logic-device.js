document.addEventListener('DOMContentLoaded', function () {
    const isAppleDevice = /iPhone|iPad|iPod|Macintosh/.test(navigator.userAgent);
  
  
    if (isAppleDevice) {
        document.body.classList.add('apple');
    } else {
        document.body.classList.add('non-apple');
    }
  });