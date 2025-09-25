(function(){
  class NavbarController {
    constructor() {
      this.navbar = document.getElementById('navbar');
      this.mobileMenu = document.getElementById('mobileMenu');
      this.mobileMenuBtn = document.getElementById('mobileMenuBtn');
      this.closeMobileMenuBtn = document.getElementById('closeMobileMenu');
      this.mobileMenuOpen = false;
      this.activeSection = '';
      this.isScrolled = false;
      
      this.init();
    }
    
    init() {
      this.bindEvents();
      this.checkActiveSection();
    }
    
    bindEvents() {
      // Mobile menu toggle
      this.mobileMenuBtn?.addEventListener('click', () => this.toggleMobileMenu());
      this.closeMobileMenuBtn?.addEventListener('click', () => this.toggleMobileMenu());
      
      // Close mobile menu when clicking on mobile links
      const mobileLinks = document.querySelectorAll('.mobile-nav-link');
      mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
          if (this.mobileMenuOpen) {
            this.toggleMobileMenu();
          }
        });
      });
      
      // Scroll events
      window.addEventListener('scroll', () => this.handleScroll());
      
      // Handle section navigation
      const sectionLinks = document.querySelectorAll('[data-section]');
      sectionLinks.forEach(link => {
        link.addEventListener('click', (e) => this.handleSectionClick(e));
      });
    }
    
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen;
      
      if (this.mobileMenuOpen) {
        this.mobileMenu.classList.add('open');
        document.body.classList.add('mobile-menu-open');
      } else {
        this.mobileMenu.classList.remove('open');
        document.body.classList.remove('mobile-menu-open');
      }
    }
    
    handleScroll() {
      this.checkScrolled();
      this.checkActiveSection();
    }
    
    checkScrolled() {
      const scrolled = window.scrollY > 50;
      if (scrolled !== this.isScrolled) {
        this.isScrolled = scrolled;
        this.navbar.classList.toggle('scrolled', scrolled);
      }
    }
    
    checkActiveSection() {
      const sections = ['nuestra-escuela', 'servicios', 'noticias', 'contacto'];
      
      // Only check sections if we're on the home page
      if (window.location.pathname === '/') {
        for (const sectionId of sections) {
          const element = document.getElementById(sectionId);
          if (element) {
            const rect = element.getBoundingClientRect();
            // If section is visible in viewport
            if (rect.top <= 150 && rect.bottom >= 150) {
              if (this.activeSection !== sectionId) {
                this.setActiveSection(sectionId);
              }
              return;
            }
          }
        }
        // If no section is active, clear active state
        if (this.activeSection) {
          this.setActiveSection('');
        }
      }
    }
    
    setActiveSection(sectionId) {
      this.activeSection = sectionId;
      
      // Remove active class from all section links
      const allSectionLinks = document.querySelectorAll('[data-section]');
      allSectionLinks.forEach(link => {
        link.classList.remove('active');
      });
      
      // Add active class to current section links
      if (sectionId) {
        const activeSectionLinks = document.querySelectorAll(`[data-section="${sectionId}"]`);
        activeSectionLinks.forEach(link => {
          link.classList.add('active');
        });
      }
    }
    
    handleSectionClick(e) {
      const section = e.target.getAttribute('data-section');
      if (section && window.location.pathname === '/') {
        e.preventDefault();
        
        const element = document.getElementById(section);
        if (element) {
          const navbarHeight = this.navbar.offsetHeight;
          const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
          const offsetPosition = elementPosition - navbarHeight - 20;
          
          window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
          });
        }
      }
    }
  }

  // Initialize navbar when DOM is loaded
  document.addEventListener('DOMContentLoaded', () => {
    new NavbarController();
  });
})();

