document.addEventListener("DOMContentLoaded", () => {
    const boostButton = document.querySelector(".boost-button");
    const spans = boostButton.querySelectorAll("span");
    let currentIndex = 0; 
    boostButton.addEventListener("click", () => {
        const currentSpan = spans[currentIndex];
        const nextIndex = (currentIndex + 1) % spans.length;
        const nextSpan = spans[nextIndex];
        currentSpan.classList.remove("active");
        currentSpan.classList.add("hidden");
        nextSpan.classList.remove("hidden");
        nextSpan.classList.add("active");
        currentIndex = nextIndex;
    });
});