document.addEventListener('DOMContentLoaded', () => {
    const faqToggles = document.querySelectorAll('.faq-toggle');

    faqToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const faqContent = toggle.nextElementSibling;
            
            toggle.classList.toggle('active');
            if (faqContent.style.maxHeight) {
                faqContent.style.maxHeight = null;
            } else {
                faqContent.style.maxHeight = faqContent.scrollHeight + 'px';
            }
        });
    });
});
