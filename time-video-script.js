document.addEventListener('DOMContentLoaded', function () {
    function adjustBottomLine() {
        const timeLeft = document.querySelector('.time-left');
        const timeRight = document.querySelector('.time-right');
        const bottomLine = document.querySelector('.bottom-line');

        const leftIndent = timeLeft.offsetWidth + 21;
        const rightIndent = timeRight.offsetWidth + 21;

        bottomLine.style.left = `${leftIndent}px`;
        bottomLine.style.right = `${rightIndent}px`;
    }

    window.onload = adjustBottomLine;
    window.onresize = adjustBottomLine;
});