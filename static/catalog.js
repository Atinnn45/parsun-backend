// Catalog JavaScript - Modern, performant, accessible

class CatalogApp {
    constructor() {
        this.initSearch();
        this.initPreview();
        this.initScrollAnimations();
        this.initLoading();
    }

    initSearch() {
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const cards = document.querySelectorAll('.catalog-card');
            
            cards.forEach(card => {
                const name = card.dataset.name.toLowerCase();
                card.classList.toggle('hidden', !name.includes(query));
            });
        });
    }

    initPreview() {
        this.modal = document.getElementById('previewModal');
        this.previewImage = document.getElementById('previewImage');
        
        if (!this.modal) return;



        // Close modal events
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) closePreview();
        });

        // Keyboard support
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.style.display === 'block') {
                closePreview();
            }
        });

        // Image click handlers - open in new tab
        document.addEventListener('click', (e) => {
            if (e.target.closest('.catalog-image img')) {
                const img = e.target.closest('img');
                window.open(img.src, '_blank');
            }
        });
    }

    initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.catalog-card, .brand-card').forEach(card => {
            observer.observe(card);
        });
    }

    initLoading() {
        const loading = document.getElementById('loadingSpinner');
        if (loading) {
            // Hide loading after short delay or when content loads
            setTimeout(() => {
                loading.style.opacity = '0';
                setTimeout(() => loading.style.display = 'none', 300);
            }, 800);
        }

        // Lazy load images with observer
        if ('IntersectionObserver' in window) {
            const imgObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src || img.src;
                        img.classList.remove('lazy');
                        imgObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[loading="lazy"]').forEach(img => {
                imgObserver.observe(img);
            });
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new CatalogApp();
});

// Utility function for PDF check
window.isPDF = (filename) => filename.toLowerCase().endsWith('.pdf');

// Smooth page transitions
window.addEventListener('pageshow', () => {
    document.body.classList.add('page-loaded');
});

// Preload critical fonts
if ('fonts' in document) {
    document.fonts.load('400 16px Inter').then(() => {
        document.documentElement.classList.add('fonts-loaded');
    });
}

