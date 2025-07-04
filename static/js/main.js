// Main application JavaScript - Fixed recursion issues
class OnlineLearningApp {
    constructor() {
        this.isInitialized = false;
        this.cartCount = 0;
        this.init();
    }

    init() {
        if (this.isInitialized) return;
        
        console.log('Initializing Online Learning App...');
        
        // Initialize all components
        this.setupEventListeners();
        this.setupLazyLoading();
        this.updateCartCount();
        this.setupAnimations();
        this.setupFormValidation();
        
        this.isInitialized = true;
        console.log('App initialized successfully');
    }

    setupEventListeners() {
        // Navigation toggle for mobile
        const navToggle = document.querySelector('.nav-toggle');
        const navMenu = document.querySelector('.nav-menu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
            });
        }

        // Cart functionality
        const addToCartBtns = document.querySelectorAll('.add-to-cart');
        addToCartBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const courseId = btn.dataset.courseId;
                this.addToCart(courseId);
            });
        });

        // Rating system
        const ratingStars = document.querySelectorAll('.rating-stars .star');
        ratingStars.forEach(star => {
            star.addEventListener('click', (e) => {
                const rating = parseInt(star.dataset.rating);
                this.setRating(rating);
            });
            
            star.addEventListener('mouseenter', (e) => {
                const rating = parseInt(star.dataset.rating);
                this.highlightStars(rating);
            });
        });

        // Search functionality
        const searchForm = document.querySelector('.search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                const searchInput = searchForm.querySelector('input[name="q"]');
                if (!searchInput.value.trim()) {
                    e.preventDefault();
                    this.showNotification('Qidiruv uchun kalit so\'z kiriting', 'warning');
                }
            });
        }

        // Lesson creation in course form
        const addLessonBtn = document.querySelector('#add-lesson-btn');
        if (addLessonBtn) {
            addLessonBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.addLessonField();
            });
        }

        // Video preview functionality
        const videoInputs = document.querySelectorAll('input[type="file"][accept="video/*"]');
        videoInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.previewVideo(e.target);
            });
        });

        // Modal functionality
        const modalTriggers = document.querySelectorAll('[data-modal]');
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.dataset.modal;
                this.openModal(modalId);
            });
        });

        // Close modal functionality
        const modalCloseBtns = document.querySelectorAll('.modal-close');
        modalCloseBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeModal(btn.closest('.modal'));
            });
        });
    }

    setupLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for older browsers
            images.forEach(img => {
                img.src = img.dataset.src;
                img.classList.remove('lazy');
            });
        }
    }

    updateCartCount() {
        // Prevent multiple calls
        if (this.updatingCart) return;
        this.updatingCart = true;

        const cartCountElement = document.querySelector('.cart-count');
        if (!cartCountElement) {
            this.updatingCart = false;
            return;
        }

        // Get cart count from server
        fetch('/api/cart/count')
            .then(response => response.json())
            .then(data => {
                this.cartCount = data.count;
                cartCountElement.textContent = this.cartCount;
                
                // Show/hide cart count badge
                if (this.cartCount > 0) {
                    cartCountElement.classList.add('show');
                } else {
                    cartCountElement.classList.remove('show');
                }
            })
            .catch(error => {
                console.error('Error fetching cart count:', error);
            })
            .finally(() => {
                this.updatingCart = false;
            });
    }

    addToCart(courseId) {
        // Add visual feedback
        const btn = document.querySelector(`[data-course-id="${courseId}"]`);
        if (btn) {
            btn.classList.add('loading');
            btn.disabled = true;
        }

        // Simulate adding to cart (in real app this would be an API call)
        setTimeout(() => {
            if (btn) {
                btn.classList.remove('loading');
                btn.disabled = false;
            }
            
            this.showNotification('Kurs savatga qo\'shildi!', 'success');
            this.updateCartCount();
        }, 1000);
    }

    setRating(rating) {
        const ratingForm = document.querySelector('.rating-form');
        if (ratingForm) {
            const ratingInput = ratingForm.querySelector('input[name="rating"]');
            if (ratingInput) {
                ratingInput.value = rating;
            }
        }
        
        this.highlightStars(rating);
        this.showNotification(`${rating} yulduzli baho qo'yildi`, 'success');
    }

    highlightStars(rating) {
        const stars = document.querySelectorAll('.rating-stars .star');
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }

    addLessonField() {
        const lessonsContainer = document.querySelector('#lessons-container');
        if (!lessonsContainer) return;

        const lessonCount = lessonsContainer.children.length;
        const lessonHTML = `
            <div class="lesson-item bg-white p-6 rounded-lg shadow-md mb-4">
                <h3 class="text-lg font-semibold mb-4">Dars ${lessonCount + 1}</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Dars nomi</label>
                        <input type="text" name="lesson_title_${lessonCount}" 
                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
                               required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Dars videosi</label>
                        <input type="file" name="lesson_video_${lessonCount}" 
                               accept="video/*" 
                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <div class="video-preview mt-2" id="video-preview-${lessonCount}"></div>
                    </div>
                </div>
                <div class="mt-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Dars matni</label>
                    <textarea name="lesson_content_${lessonCount}" rows="4"
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              required></textarea>
                </div>
                <button type="button" class="mt-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 remove-lesson-btn">
                    <i class="fas fa-trash"></i> Darsni o'chirish
                </button>
            </div>
        `;

        lessonsContainer.insertAdjacentHTML('beforeend', lessonHTML);

        // Update lesson count input
        const lessonCountInput = document.querySelector('input[name="lesson_count"]');
        if (lessonCountInput) {
            lessonCountInput.value = lessonCount + 1;
        }

        // Add event listeners for new elements
        const newLessonItem = lessonsContainer.lastElementChild;
        const removeBtn = newLessonItem.querySelector('.remove-lesson-btn');
        const videoInput = newLessonItem.querySelector('input[type="file"]');

        if (removeBtn) {
            removeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.removeLessonField(newLessonItem);
            });
        }

        if (videoInput) {
            videoInput.addEventListener('change', (e) => {
                this.previewVideo(e.target);
            });
        }
    }

    removeLessonField(lessonItem) {
        lessonItem.remove();
        
        // Update lesson count
        const lessonsContainer = document.querySelector('#lessons-container');
        const lessonCountInput = document.querySelector('input[name="lesson_count"]');
        if (lessonCountInput && lessonsContainer) {
            lessonCountInput.value = lessonsContainer.children.length;
        }

        // Renumber remaining lessons
        const remainingLessons = lessonsContainer.querySelectorAll('.lesson-item');
        remainingLessons.forEach((lesson, index) => {
            const title = lesson.querySelector('h3');
            if (title) {
                title.textContent = `Dars ${index + 1}`;
            }
        });
    }

    previewVideo(input) {
        const file = input.files[0];
        if (!file) return;

        const previewContainer = input.nextElementSibling;
        if (!previewContainer || !previewContainer.classList.contains('video-preview')) return;

        // Check file type
        if (!file.type.startsWith('video/')) {
            this.showNotification('Faqat video fayllar qabul qilinadi', 'error');
            input.value = '';
            return;
        }

        // Check file size (max 100MB)
        if (file.size > 100 * 1024 * 1024) {
            this.showNotification('Video fayl hajmi 100MB dan oshmasligi kerak', 'error');
            input.value = '';
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            previewContainer.innerHTML = `
                <video controls class="w-full max-w-md rounded-lg shadow-md">
                    <source src="${e.target.result}" type="${file.type}">
                    Brauzeringiz video playbackni qo'llab-quvvatlamaydi.
                </video>
                <p class="text-sm text-gray-600 mt-2">
                    <strong>Fayl:</strong> ${file.name}<br>
                    <strong>Hajmi:</strong> ${this.formatFileSize(file.size)}
                </p>
            `;
        };
        reader.readAsDataURL(file);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    setupAnimations() {
        // Smooth scrolling for anchor links
        const anchorLinks = document.querySelectorAll('a[href^="#"]');
        anchorLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Fade in animation on scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                }
            });
        }, observerOptions);

        const animateElements = document.querySelectorAll('.animate-on-scroll');
        animateElements.forEach(el => observer.observe(el));
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'Bu maydon to\'ldirilishi shart');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });

        // Email validation
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value && !this.isValidEmail(field.value)) {
                this.showFieldError(field, 'Email manzil noto\'g\'ri');
                isValid = false;
            }
        });

        // Password confirmation
        const passwordField = form.querySelector('input[name="password"]');
        const confirmPasswordField = form.querySelector('input[name="confirm_password"]');
        
        if (passwordField && confirmPasswordField) {
            if (passwordField.value !== confirmPasswordField.value) {
                this.showFieldError(confirmPasswordField, 'Parollar mos kelmaydi');
                isValid = false;
            }
        }

        return isValid;
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error text-red-500 text-sm mt-1';
        errorElement.textContent = message;
        
        field.parentNode.appendChild(errorElement);
        field.classList.add('border-red-500');
    }

    clearFieldError(field) {
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        field.classList.remove('border-red-500');
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            document.body.classList.add('modal-open');
        }
    }

    closeModal(modal) {
        if (modal) {
            modal.classList.add('hidden');
            document.body.classList.remove('modal-open');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type} fixed top-4 right-4 z-50 bg-white border-l-4 p-4 rounded-lg shadow-lg max-w-md`;
        
        const colors = {
            success: 'border-green-500 bg-green-50',
            error: 'border-red-500 bg-red-50',
            warning: 'border-yellow-500 bg-yellow-50',
            info: 'border-blue-500 bg-blue-50'
        };

        notification.className += ` ${colors[type]}`;
        notification.innerHTML = `
            <div class="flex items-center">
                <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">${message}</p>
                </div>
                <button class="ml-4 text-gray-400 hover:text-gray-600" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new OnlineLearningApp();
});

// Prevent multiple initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.app) {
            window.app = new OnlineLearningApp();
        }
    });
} else {
    // DOM is already ready
    if (!window.app) {
        window.app = new OnlineLearningApp();
    }
}
