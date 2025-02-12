document.addEventListener('DOMContentLoaded', function () {
    const elements = document.querySelectorAll('.non-apple .rectangle2, .non-apple .rectangle3, .non-apple .rectangle4, .non-apple .rectangle5, .non-apple .rectangle8, .non-apple .rectangle11, .non-apple .rectangle13, .non-apple .rectangle14');
    elements.forEach(element => {
        element.addEventListener('mousedown', function (e) {
            const ripple = document.createElement('div');
            ripple.classList.add('ripple');
            const size = Math.max(this.clientWidth, this.clientHeight);
            const x = e.clientX - this.offsetLeft - size / 2;
            const y = e.clientY - this.offsetTop - size / 2;
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            this.appendChild(ripple);
            ripple.style.animation = 'ripple-animation 0.9s ease-out forwards';
        });
        element.addEventListener('mouseup', function () {
            const ripples = this.querySelectorAll('.ripple');
            ripples.forEach(ripple => {
                ripple.style.animation = 'ripple-animation 0.9s ease-out forwards';
                setTimeout(() => {
                    ripple.remove();
                }, 900);
            });
        });
    });
});