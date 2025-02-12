document.addEventListener('DOMContentLoaded', () => {
  const rectangles = document.querySelectorAll('.apple .rectangle10');
  rectangles.forEach(rectangle => {
    rectangle.addEventListener('touchstart', () => {
      rectangle.classList.add('active');
    });
    rectangle.addEventListener('touchend', () => {
      rectangle.classList.remove('active');
    });
    rectangle.addEventListener('mousedown', () => {
      rectangle.classList.add('active');
    });
    rectangle.addEventListener('mouseup', () => {
      rectangle.classList.remove('active');
    });
    rectangle.addEventListener('mouseleave', () => {
      rectangle.classList.remove('active');
    });
  });
});