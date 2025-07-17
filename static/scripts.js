document.addEventListener('DOMContentLoaded', () => {
    console.log('Online Auction System loaded');
    
    // Initialize carousel
    initializeCarousel();
    
    // Initialize mobile navigation
    initializeMobileNav();
});

// Mobile Navigation Toggle
function initializeMobileNav() {
    const mobileToggle = document.getElementById('mobileToggle');
    const navbarMenu = document.getElementById('navbarMenu');
    
    if (mobileToggle && navbarMenu) {
        mobileToggle.addEventListener('click', () => {
            mobileToggle.classList.toggle('active');
            navbarMenu.classList.toggle('active');
        });
        
        // Close mobile menu when clicking on a link
        navbarMenu.addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-link')) {
                mobileToggle.classList.remove('active');
                navbarMenu.classList.remove('active');
            }
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!mobileToggle.contains(e.target) && !navbarMenu.contains(e.target)) {
                mobileToggle.classList.remove('active');
                navbarMenu.classList.remove('active');
            }
        });
    }
}

// Custom Carousel Functionality
let currentSlide = 0;
const slides = document.querySelectorAll('.carousel-slide');
const totalSlides = slides.length;

function initializeCarousel() {
    if (totalSlides > 0) {
        // Auto-rotate carousel every 5 seconds
        setInterval(nextSlide, 5000);
    }
}

function showSlide(index) {
    // Hide all slides
    slides.forEach(slide => {
        slide.classList.remove('active');
    });
    
    // Show current slide
    if (slides[index]) {
        slides[index].classList.add('active');
    }
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % totalSlides;
    showSlide(currentSlide);
}

function previousSlide() {
    currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
    showSlide(currentSlide);
}

// Auction countdown timer functionality
function updateCountdownTimers() {
    const timers = document.querySelectorAll('.countdown-timer');
    timers.forEach(timer => {
        // This would update countdown timers in real-time
        // Implementation would depend on actual auction end times from backend
    });
}

// Bid form validation
function validateBidForm(form) {
    const bidAmount = form.querySelector('input[type="number"]');
    const currentBid = parseFloat(bidAmount.getAttribute('min'));
    const newBid = parseFloat(bidAmount.value);
    
    if (newBid <= currentBid) {
        alert('Your bid must be higher than the current bid.');
        return false;
    }
    
    return true;
}

// Add event listeners for bid forms
document.addEventListener('submit', (e) => {
    if (e.target.classList.contains('bid-form')) {
        if (!validateBidForm(e.target)) {
            e.preventDefault();
        }
    }
});

// Smooth scroll for anchor links
document.addEventListener('click', (e) => {
    if (e.target.matches('a[href^="#"]')) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});
