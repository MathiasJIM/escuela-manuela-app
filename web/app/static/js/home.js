(function() {
  let currentImageIndex = 0;
  let carouselInterval = null;
  const images = document.querySelectorAll('.hero-image');
  const indicators = document.querySelectorAll('.indicator');
  
  // Function to show specific image
  function showImage(index) {
    // Hide all images
    images.forEach(img => img.classList.remove('active'));
    indicators.forEach(indicator => indicator.classList.remove('active'));
    
    // Show current image
    if (images[index]) {
      images[index].classList.add('active');
      indicators[index].classList.add('active');
    }
    
    currentImageIndex = index;
  }
  
  // Function to go to next image
  function nextImage() {
    const nextIndex = (currentImageIndex + 1) % images.length;
    showImage(nextIndex);
  }
  
  // Function to start carousel
  function startCarousel() {
    carouselInterval = setInterval(nextImage, 10000); // Change every 10 seconds
  }
  
  // Function to stop carousel
  function stopCarousel() {
    if (carouselInterval) {
      clearInterval(carouselInterval);
      carouselInterval = null;
    }
  }
  
  // Add click events to indicators
  indicators.forEach((indicator, index) => {
    indicator.addEventListener('click', () => {
      showImage(index);
      // Restart carousel timer
      stopCarousel();
      startCarousel();
    });
  });
  
  // Scroll to section function
  window.scrollToSection = function(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
      const navbar = document.getElementById('navbar');
      const navbarHeight = navbar ? navbar.offsetHeight : 80;
      const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
      const offsetPosition = elementPosition - navbarHeight - 20;
      
      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  };
  
  // Initialize carousel when DOM is loaded
  document.addEventListener('DOMContentLoaded', () => {
    if (images.length > 0) {
      showImage(0); // Show first image
      startCarousel(); // Start automatic carousel
      
      // Pause carousel on hover
      const heroContainer = document.querySelector('.hero-container');
      if (heroContainer) {
        heroContainer.addEventListener('mouseenter', stopCarousel);
        heroContainer.addEventListener('mouseleave', startCarousel);
      }
    }
  });
  
  // Clean up interval when page unloads
  window.addEventListener('beforeunload', stopCarousel);
})();
