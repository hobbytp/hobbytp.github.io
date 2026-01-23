document.addEventListener('DOMContentLoaded', function () {
    // initial check for lightbox
    initLightbox();
});

function initLightbox() {
    // 1. Create Modal if it doesn't exist
    if (!document.getElementById('lightbox-modal')) {
        const modal = document.createElement('div');
        modal.id = 'lightbox-modal';
        modal.innerHTML = `
            <span class="lightbox-close">&times;</span>
            <img id="lightbox-img" alt="Lightbox Image">
        `;
        document.body.appendChild(modal);

        // Event Listeners for Modal
        const closeBtn = modal.querySelector('.lightbox-close');

        // Close on click close button
        closeBtn.onclick = function () {
            closeLightbox(modal);
        };

        // Close on click outside image
        modal.onclick = function (e) {
            if (e.target === modal) {
                closeLightbox(modal);
            }
        };

        // Close on Esc key
        document.addEventListener('keydown', function (e) {
            if (e.key === "Escape" && modal.classList.contains('show')) {
                closeLightbox(modal);
            }
        });
    }

    // 2. Attach click events to all images with class 'lightbox-image'
    const images = document.querySelectorAll('.lightbox-image');
    images.forEach(img => {
        img.addEventListener('click', function (e) {
            e.preventDefault(); // Prevent default link behavior if wrapped in a link
            openLightbox(this);
        });
    });
}

function openLightbox(imgElement) {
    const modal = document.getElementById('lightbox-modal');
    const modalImg = document.getElementById('lightbox-img');

    // Get full resolution source from data attribute, fallback to src
    const fullSrc = imgElement.getAttribute('data-full-src') || imgElement.src;

    modalImg.src = fullSrc;
    modalImg.alt = imgElement.alt;

    modal.classList.add('show');
    document.body.style.overflow = 'hidden'; // Disable background scrolling
}

function closeLightbox(modal) {
    modal.classList.remove('show');
    setTimeout(() => {
        // Clear src to stop video/loading/memory usage (optional, mostly good for cleanup)
        const modalImg = document.getElementById('lightbox-img');
        if (modalImg) modalImg.src = '';
    }, 300); // Wait for transition
    document.body.style.overflow = ''; // Re-enable background scrolling
}
