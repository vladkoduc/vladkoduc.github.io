document.addEventListener("DOMContentLoaded", () => {
    document.querySelector('.episodes-btn').addEventListener('click', function() {
        const episodesBtnClick = document.querySelector('.episodes-btn-click');
        if (episodesBtnClick.classList.contains('show')) {
            episodesBtnClick.classList.remove('show'); 
        } else {
            episodesBtnClick.classList.add('show'); 
        }
    });
});