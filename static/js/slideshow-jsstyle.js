// Updated slide data with actual image URLs
let slide_data = [
    {
        'src': "{{ url_for('static', filename='img/slideshow/home-bg1.png') }}",
        'title': 'Slide Title 1',
        'copy': 'Description for slide 1.'
    },
    {
        'src': "{{ url_for('static', filename='img/slideshow/home-bg2.png') }}", 
        'title': 'Slide Title 2',
        'copy': 'Description for slide 2.'
    },
    {
        'src': "{{ url_for('static', filename='img/slideshow/home-bg3.png') }}", 
        'title': 'Slide Title 3',
        'copy': 'Description for slide 3.'
    }
];

let currentSlide = 0;
let leftSlider = document.getElementById('left-slider');

// Function to build the slides and append them to the DOM
function buildSlides() {
    slide_data.forEach((slide, index) => {
        let slideElement = document.createElement('div');
        slideElement.classList.add('slide');
        slideElement.style.backgroundImage = `url(${slide.src})`;

        if (index == 0) {
            slideElement.classList.add('current');
        }

        leftSlider.appendChild(slideElement);
    });
}

// Function to move to the next slide
function nextSlide() {
    let slides = document.querySelectorAll('#left-slider .slide');
    
    slides[currentSlide].classList.remove('current'); // Remove current class from current slide
    
    // Increment the current slide index
    currentSlide = (currentSlide + 1) % slides.length;
    
    // Add current class to the new slide
    slides[currentSlide].classList.add('current');
}

// Set an interval for the slideshow to transition every 5 seconds
setInterval(nextSlide, 5000); // Auto slide every 5 seconds

// Build the slides when the DOM is loaded
document.addEventListener('DOMContentLoaded', buildSlides);
