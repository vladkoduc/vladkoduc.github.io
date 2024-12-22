document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.tab-item');
    const indicator = document.querySelector('.indicator');
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    const tabItems = document.querySelectorAll('.tab-item');
    function updateIndicator(activeTab) {
      const textNode = activeTab.childNodes[0]; 
      const text = textNode.nodeValue.trim(); 
      const tempElement = document.createElement('span');
      tempElement.style.visibility = 'hidden';
      tempElement.style.position = 'absolute';
      tempElement.style.whiteSpace = 'nowrap';
      tempElement.style.fontSize = window.getComputedStyle(activeTab).fontSize;
      tempElement.style.fontFamily = window.getComputedStyle(activeTab).fontFamily;
      tempElement.textContent = text;
      document.body.appendChild(tempElement);
      const textWidth = tempElement.offsetWidth;
      document.body.removeChild(tempElement);
      const tabRect = activeTab.getBoundingClientRect(); 
      const parentRect = activeTab.parentElement.getBoundingClientRect();
      const tabOffset = tabRect.left - parentRect.left; 
      const centeredLeft = tabOffset + (tabRect.width - textWidth) / 2; 
      indicator.style.width = `${textWidth}px`;
      indicator.style.left = `${centeredLeft}px`;
    }
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        updateIndicator(tab);
        if (Telegram?.WebApp?.HapticFeedback) {
          Telegram.WebApp.HapticFeedback.impactOccurred('light');
          setTimeout(() => {
              Telegram.WebApp.HapticFeedback.impactOccurred('light');
          }, 100); 
        }
      });
    });
    window.addEventListener('resize', () => {
      const activeTab = document.querySelector('.tab-item.active');
      if (activeTab) {
        updateIndicator(activeTab);
      }
    });
    updateIndicator(document.querySelector('.tab-item.active'));


    toggleBtns.forEach(btn => {
      btn.addEventListener('click', () => {
          toggleBtns.forEach(b => b.classList.remove('active')); // Убираем активный класс у всех кнопок
          btn.classList.add('active'); // Добавляем активный класс выбранной кнопке

          if (btn.id === 'ready-btn') {
              // Показать Video, скрыть Live
              document.querySelector('.Video').style.display = 'block';
              document.querySelector('.Live').style.display = 'none';
          } else if (btn.id === 'custom-btn') {
              // Показать Live, скрыть Video
              document.querySelector('.Video').style.display = 'none';
              document.querySelector('.Live').style.display = 'block';
          }
      });
  });

  // Слушаем клики на tab-item
  tabItems.forEach(item => {
      item.addEventListener('click', () => {
          tabItems.forEach(tab => tab.classList.remove('active')); // Убираем активный класс у всех табов
          item.classList.add('active'); // Добавляем активный класс выбранному табу

          if (item.dataset.index == 0) {
              // Показать Video
              document.querySelector('.Video').style.display = 'block';
              document.querySelector('.Live').style.display = 'none';
          } else {
              // Показать Live
              document.querySelector('.Video').style.display = 'none';
              document.querySelector('.Live').style.display = 'block';
          }
      });
  });
});