/**
* Template Name: Logis
* Template URL: https://bootstrapmade.com/logis-bootstrap-logistics-website-template/
* Updated: Aug 07 2024 with Bootstrap v5.3.3
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/

(function() {
  "use strict";

  // Função para verificar se um elemento existe antes de manipulá-lo
  function safeQuerySelector(selector) {
    const element = document.querySelector(selector);
    return element || null;
  }

  // Função para verificar se um elemento existe antes de adicionar event listener
  function safeAddEventListener(element, event, callback) {
    if (element) {
      element.addEventListener(event, callback);
    }
  }

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = safeQuerySelector('body');
    const selectHeader = safeQuerySelector('#header');
    
    if (!selectHeader || !selectBody) return;
    
    if (!selectHeader.classList.contains('scroll-up-sticky') && 
        !selectHeader.classList.contains('sticky-top') && 
        !selectHeader.classList.contains('fixed-top')) return;
    
    window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
  }

  // Só adiciona os event listeners se estiver na página principal
  const header = safeQuerySelector('#header');
  if (header) {
    safeAddEventListener(document, 'scroll', toggleScrolled);
    safeAddEventListener(window, 'load', toggleScrolled);
  }

  /**
   * Mobile nav toggle
   */
  const mobileNavToggleBtn = safeQuerySelector('.mobile-nav-toggle');
  if (mobileNavToggleBtn) {
    function mobileNavToogle() {
      const body = safeQuerySelector('body');
      if (body) {
        body.classList.toggle('mobile-nav-active');
        mobileNavToggleBtn.classList.toggle('bi-list');
        mobileNavToggleBtn.classList.toggle('bi-x');
      }
    }
    safeAddEventListener(mobileNavToggleBtn, 'click', mobileNavToogle);
  }

  /**
   * Hide mobile nav on same-page/hash links
   */
  const navmenuLinks = document.querySelectorAll('#navmenu a');
  if (navmenuLinks.length > 0) {
    navmenuLinks.forEach(navmenu => {
      safeAddEventListener(navmenu, 'click', () => {
        const mobileNav = safeQuerySelector('.mobile-nav-active');
        if (mobileNav) {
          mobileNavToogle();
        }
      });
    });
  }

  /**
   * Toggle mobile nav dropdowns
   */
  const dropdownToggles = document.querySelectorAll('.navmenu .toggle-dropdown');
  if (dropdownToggles.length > 0) {
    dropdownToggles.forEach(navmenu => {
      safeAddEventListener(navmenu, 'click', function(e) {
        e.preventDefault();
        const parent = this.parentNode;
        const nextSibling = parent.nextElementSibling;
        if (parent && nextSibling) {
          parent.classList.toggle('active');
          nextSibling.classList.toggle('dropdown-active');
        }
        e.stopImmediatePropagation();
      });
    });
  }

  /**
   * Preloader
   */
  const preloader = safeQuerySelector('#preloader');
  if (preloader) {
    safeAddEventListener(window, 'load', () => {
      preloader.remove();
    });
  }

  /**
   * Scroll top button
   */
  const scrollTop = safeQuerySelector('.scroll-top');
  if (scrollTop) {
    function toggleScrollTop() {
      window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
    }
    safeAddEventListener(scrollTop, 'click', (e) => {
      e.preventDefault();
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
    safeAddEventListener(window, 'load', toggleScrollTop);
    safeAddEventListener(document, 'scroll', toggleScrollTop);
  }

  /**
   * Animation on scroll function and init
   */
  function aosInit() {
    if (typeof AOS !== 'undefined') {
      AOS.init({
        duration: 600,
        easing: 'ease-in-out',
        once: true,
        mirror: false
      });
    }
  }
  safeAddEventListener(window, 'load', aosInit);

  /**
   * Initiate Pure Counter
   */
  if (typeof PureCounter !== 'undefined') {
    new PureCounter();
  }

  /**
   * Initiate glightbox
   */
  if (typeof GLightbox !== 'undefined') {
    const glightbox = GLightbox({
      selector: '.glightbox'
    });
  }

  /**
   * Init swiper sliders
   */
  function initSwiper() {
    const swiperElements = document.querySelectorAll(".init-swiper");
    if (swiperElements.length > 0) {
      swiperElements.forEach(function(swiperElement) {
        const configElement = swiperElement.querySelector(".swiper-config");
        if (configElement) {
          try {
            let config = JSON.parse(configElement.innerHTML.trim());
            if (swiperElement.classList.contains("swiper-tab")) {
              initSwiperWithCustomPagination(swiperElement, config);
            } else {
              new Swiper(swiperElement, config);
            }
          } catch (e) {
            console.error('Erro ao inicializar swiper:', e);
          }
        }
      });
    }
  }
  safeAddEventListener(window, "load", initSwiper);

  /**
   * Frequently Asked Questions Toggle
   */
  const faqItems = document.querySelectorAll('.faq-item h3, .faq-item .faq-toggle');
  if (faqItems.length > 0) {
    faqItems.forEach((faqItem) => {
      safeAddEventListener(faqItem, 'click', () => {
        const parent = faqItem.parentNode;
        if (parent) {
          parent.classList.toggle('faq-active');
        }
      });
    });
  }

})();