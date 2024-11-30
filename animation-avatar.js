document.addEventListener('DOMContentLoaded', function () {
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  
  // Найдем контейнер, в котором будет размещен canvas
  const container = document.querySelector('._Content_container_not-button');

  function setCanvasSize() {
    const containerWidth = container.offsetWidth;  // Ширина контейнера
    const containerHeight = container.offsetHeight; // Высота контейнера
    // Уменьшаем размер canvas на 20%
    canvas.width = containerWidth * 0.8;
    canvas.height = containerHeight * 0.8;
  }

  // Устанавливаем размер canvas при загрузке страницы
  setCanvasSize();

  const avatarImg = new Image();
  avatarImg.src = 'avatarka-kovheg.jpg'; // Убедитесь, что файл доступен

  const starSVG =
    `<svg xmlns="http://www.w3.org/2000/svg" width="56px" height="56px" viewBox="0 0 512.736 512.736">
      <path style="fill:#FFD83B;" d="M238,512.736c0-76.8-128.544-205.344-205.344-205.344c76.8,0,205.344-128.544,205.344-205.344 c0,76.8,128.544,205.344,205.344,205.344C366.544,307.392,238,435.936,238,512.736z"/>
    </svg>`;
  const starImage = new Image();
  starImage.src = 'data:image/svg+xml;base64,' + btoa(starSVG);

  const stars = [];
  const starCount = 200;
  let scale = 1;
  let time = 0;

  class Star {
    constructor(x, y, size, speed, angle) {
      this.x = x;
      this.y = y;
      this.size = size;
      this.speed = speed;
      this.angle = angle;
      this.alpha = Math.random() * 0.8 + 0.2;
    }

    draw() {
      ctx.globalAlpha = this.alpha;
      ctx.drawImage(
        starImage,
        this.x,
        this.y,
        this.size,
        this.size
      );
    }

    update() {
      this.x += this.speed * Math.cos(this.angle);
      this.y += this.speed * Math.sin(this.angle);
      this.alpha -= 0.015;
      if (this.alpha <= 0) {
        this.reset();
      }
    }

    reset() {
      const avatarX = canvas.width / 2;
      const avatarY = canvas.height / 2 - 56;

      this.x = avatarX;
      this.y = avatarY;
      this.alpha = Math.random() * 0.8 + 0.2;
    }
  }

  function initStars() {
    const avatarX = canvas.width / 2;
    const avatarY = canvas.height / 2 - 56;

    for (let i = 0; i < starCount; i++) {
      const angle = Math.random() * 2 * Math.PI;
      const speed = Math.random() * 4 + 1.5;
      const size = Math.random() * 20 + 10;
      stars.push(new Star(avatarX, avatarY, size, speed, angle));
    }
  }

  function drawBlurEffect(avatarSize) {
    const blurSize = avatarSize * 1.2;
    const avatarX = canvas.width / 2 - blurSize / 2;
    const avatarY = canvas.height / 2 - 56 - blurSize / 2;

    ctx.save();
    ctx.globalAlpha = 0.8;
    ctx.fillStyle = '#000';
    ctx.filter = 'blur(12px)';
    ctx.beginPath();
    ctx.arc(
      canvas.width / 2,
      canvas.height / 2 - 56,
      blurSize / 2,
      0,
      Math.PI * 2
    );
    ctx.fill();
    ctx.restore();
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    stars.forEach((star) => {
      star.update();
      star.draw();
    });

    time += 0.05;
    scale = 1 + Math.sin(time) * 0.1;

    const avatarSize = 100 * scale;

    drawBlurEffect(avatarSize);

    const avatarX = canvas.width / 2 - avatarSize / 2;
    const avatarY = canvas.height / 2 - 56 - avatarSize / 2;

    ctx.save();
    ctx.beginPath();
    ctx.arc(
      canvas.width / 2,
      canvas.height / 2 - 56,
      avatarSize / 2,
      0,
      Math.PI * 2
    );
    ctx.closePath();
    ctx.clip();
    ctx.globalAlpha = 1;
    ctx.drawImage(avatarImg, avatarX, avatarY, avatarSize, avatarSize);
    ctx.restore();

    requestAnimationFrame(animate);
  }

  avatarImg.onload = () => {
    initStars();
    animate();
  };

  window.addEventListener('resize', setCanvasSize);
});
