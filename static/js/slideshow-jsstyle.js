const slides = document.querySelectorAll('.slideshow-container .slide');

const slideImages = [
    "{{ url_for('static', filename='img/slideshow/home-bg1.png') }}",
    "{{ url_for('static', filename='img/slideshow/home-bg2.png') }}",
    "{{ url_for('static', filename='img/slideshow/home-bg3.png') }}"
];

slides.forEach((slide, index) => {
    slide.style.backgroundImage = `url(${slideImages[index]})`;
});

let currentSlideIndex = 0;

function showNextSlide() {
    slides[currentSlideIndex].classList.remove('current');
    currentSlideIndex = (currentSlideIndex + 1) % slides.length;
    slides[currentSlideIndex].classList.add('current');
}

slides[currentSlideIndex].classList.add('current');
setInterval(showNextSlide, 5000); // Adjust the timing as needed
