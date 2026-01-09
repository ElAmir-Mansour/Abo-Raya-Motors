/**
 * GSAP Animations & Micro-interactions
 * Adds smooth animations to cards, buttons, and page elements
 */

document.addEventListener('DOMContentLoaded', function () {
    // Check if GSAP is loaded
    if (typeof gsap === 'undefined') {
        console.warn('GSAP not loaded');
        return;
    }

    // 1. Staggered card entrance animations (Fixed with Batch)
    const cards = gsap.utils.toArray(".listing-card");

    // Set initial hidden state immediately
    if (cards.length > 0) {
        gsap.set(cards, { opacity: 0, y: 30 });

        // Use ScrollTrigger.batch for reliable staggered animations on scroll
        ScrollTrigger.batch(cards, {
            onEnter: batch => gsap.to(batch, {
                opacity: 1,
                y: 0,
                stagger: 0.1,
                duration: 0.6,
                ease: "power2.out",
                overwrite: true,
                onComplete: () => {
                    // Clean up inline styles to prevent CSS conflicts
                    gsap.set(batch, { clearProps: "all" });
                }
            }),
            start: "top 95%",
            once: true // Animate only once per session
        });
    }

    // 2. Hero content fade-in
    gsap.from(".hero-content", {
        duration: 1,
        y: 30,
        opacity: 0,
        ease: "power3.out",
        delay: 0.3
    });

    //3. Animate glasscards on scroll
    gsap.utils.toArray('.glass-card').forEach((card, index) => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: "top 85%",
                toggleActions: "play none none none"
            },
            y: 40,
            opacity: 0,
            duration: 0.6,
            delay: index * 0.1,
            ease: "power2.out"
        });
    });

    // 4. Button hover animations (using GSAP)
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            gsap.to(button, {
                scale: 1.05,
                duration: 0.3,
                ease: "power2.out"
            });
        });

        button.addEventListener('mouseleave', () => {
            gsap.to(button, {
                scale: 1,
                duration: 0.3,
                ease: "power2.out"
            });
        });
    });

    // 5. Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.style.background = 'rgba(15, 23, 42, 0.95)';
                navbar.style.backdropFilter = 'blur(20px)';
            } else {
                navbar.style.background = 'rgba(15, 23, 42, 0.9)';
            }
        });
    }

    // 6. Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                gsap.to(window, {
                    duration: 1,
                    scrollTo: target,
                    ease: "power2.inOut"
                });
            }
        });
    });
});

/**
 * Phone Reveal Animation
 * Shows phone number with smooth reveal effect
 */
function revealPhone(listingId, btn) {
    const button = btn || event.currentTarget;
    const currentLang = document.documentElement.lang || 'ar';

    // Show loading state
    button.disabled = true;
    const originalContent = button.innerHTML;
    button.innerHTML = '<span class="loading"></span> Loading...';

    // Fetch phone number
    fetch(`/${currentLang}/ajax/reveal-phone/${listingId}/`)
        .then(response => response.json())
        .then(data => {
            // Animate the reveal
            gsap.to(button, {
                scale: 1.1,
                duration: 0.2,
                yoyo: true,
                repeat: 1,
                onComplete: () => {
                    button.innerHTML = `<i class="bi bi-telephone-fill"></i> ${data.phone_number}`;
                    button.classList.remove('btn-primary');
                    button.classList.add('btn-success');
                }
            });
        })
        .catch(error => {
            console.error('Error revealing phone:', error);
            button.innerHTML = 'Error loading phone';
            button.disabled = false;
            // Restore button after delay
            setTimeout(() => {
                button.innerHTML = originalContent;
            }, 3000);
        });
}

// Make function globally available
window.revealPhone = revealPhone;
