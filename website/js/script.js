document.addEventListener('DOMContentLoaded', () => {
    
    // --- 3D Mouse Parallax Effect ---
    const visualArea = document.querySelector('.hero-visual');
    const cards = document.querySelectorAll('.interactive-card');
    
    if (visualArea && cards.length > 0) {
        visualArea.addEventListener('mousemove', (e) => {
            const rect = visualArea.getBoundingClientRect();
            
            // Calculate mouse coordinates relative to center of visual area (-0.5 to 0.5)
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            
            // Tilting amounts (max degrees)
            const maxTilt = 15;
            const rotateX = -y * maxTilt;
            const rotateY = x * maxTilt;
            
            // Apply slight perspective translation/rotation to each card based on depth
            cards.forEach(card => {
                let multiplier = 1;
                
                // Front card moves more, back card moves less
                if (card.classList.contains('card-front')) multiplier = 1.5;
                if (card.classList.contains('card-mid-back')) multiplier = 0.7;
                if (card.classList.contains('card-back')) multiplier = 0.5;
                if (card.classList.contains('card-main')) multiplier = 0.9;
                
                // Calculate rotation and translation shifts
                const rotX = rotateX * multiplier;
                const rotY = rotateY * multiplier;
                const transX = x * 20 * multiplier;
                const transY = y * 20 * multiplier;
                
                // Retain float animation classes but add dynamic styles for tilt
                card.style.transform = `perspective(1000px) rotateX(${rotX}deg) rotateY(${rotY}deg) translate3d(${transX}px, ${transY}px, 0)`;
                card.style.transition = 'transform 0.1s ease-out'; // Fast tracking during move
            });
        });
        
        // Reset card positions when mouse leaves visual area
        visualArea.addEventListener('mouseleave', () => {
            cards.forEach(card => {
                // Reset to default styles (animation styles will kick back in)
                card.style.transform = '';
                card.style.transition = 'transform 0.8s cubic-bezier(0.25, 1, 0.5, 1)';
            });
        });
    }

    // --- Scroll Reveal Effect ---
    const revealElements = document.querySelectorAll('.scroll-reveal');
    
    if ('IntersectionObserver' in window) {
        const observerOptions = {
            root: null, // Viewport
            threshold: 0.1, // Trigger when 10% is visible
            rootMargin: '0px 0px -50px 0px' // Slightly offset bottom threshold
        };
        
        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                    observer.unobserve(entry.target); // Reveal once only
                }
            });
        }, observerOptions);
        
        revealElements.forEach(el => observer.observe(el));
    } else {
        // Fallback for older browsers
        revealElements.forEach(el => el.classList.add('active'));
    }
    
    // --- Smooth Scroll Anchors ---
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const targetId = link.getAttribute('href');
            
            if (targetId !== '#') {
                e.preventDefault();
                const targetEl = document.querySelector(targetId);
                
                if (targetEl) {
                    window.scrollTo({
                        top: targetEl.offsetTop - 80, // Offset for fixed navbar
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    // --- Headless Form Submission using Web3Forms ---
    const feedbackForm = document.getElementById('feedbackForm');
    const formStatus = document.getElementById('formStatus');
    
    if (feedbackForm && formStatus) {
        feedbackForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // Check if Access Key is still default placeholder
            const accessKeyInput = feedbackForm.querySelector('input[name="access_key"]');
            if (accessKeyInput && accessKeyInput.value === 'YOUR_ACCESS_KEY_HERE') {
                formStatus.textContent = "Please set up your Web3Forms Access Key in index.html first.";
                formStatus.className = "form-status error";
                return;
            }
            
            formStatus.textContent = "Sending feedback...";
            formStatus.className = "form-status";
            
            const formData = new FormData(feedbackForm);
            
            fetch(feedbackForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(async (response) => {
                const json = await response.json();
                if (response.status === 200) {
                    formStatus.textContent = "Thank you! Your feedback has been sent successfully.";
                    formStatus.className = "form-status success";
                    feedbackForm.reset();
                } else {
                    formStatus.textContent = json.message || "Failed to send feedback. Please try again.";
                    formStatus.className = "form-status error";
                }
            })
            .catch((error) => {
                formStatus.textContent = "An error occurred. Check your connection and try again.";
                formStatus.className = "form-status error";
            });
        });
    }
});
