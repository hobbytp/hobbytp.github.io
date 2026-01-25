document.addEventListener('DOMContentLoaded', function () {
    // initial check for lightbox
    initLightbox();
});

function lockBodyScroll() {
    const body = document.body;
    const current = Number(body.dataset.scrollLockCount || '0');
    if (current === 0) {
        body.dataset.scrollLockOverflow = body.style.overflow || '';
        body.style.overflow = 'hidden';
    }
    body.dataset.scrollLockCount = String(current + 1);
}

function unlockBodyScroll() {
    const body = document.body;
    const current = Number(body.dataset.scrollLockCount || '0');
    const next = Math.max(0, current - 1);
    if (next === 0) {
        body.style.overflow = body.dataset.scrollLockOverflow || '';
        delete body.dataset.scrollLockOverflow;
        delete body.dataset.scrollLockCount;
    } else {
        body.dataset.scrollLockCount = String(next);
    }
}

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

        // Close on click image itself (more intuitive than only clicking the backdrop)
        const modalImg = modal.querySelector('#lightbox-img');
        if (modalImg) {
            modalImg.onclick = function () {
                closeLightbox(modal);
            };
        }

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

        // Safety: when navigating away, always unlock scroll
        window.addEventListener('pagehide', function () {
            if (modal.classList.contains('show')) {
                closeLightbox(modal);
            }
        });
    }

    // 2. Attach click events to all images with class 'lightbox-image'
    const images = document.querySelectorAll('.lightbox-image');
    // console.log("Lightbox initialized. Found images:", images.length);
    images.forEach(img => {
        img.addEventListener('click', function (e) {
            e.preventDefault(); // Prevent default link behavior if wrapped in a link
            // console.log("Lightbox clicked:", this.src);
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
    lockBodyScroll(); // Disable background scrolling (supports multiple overlays)
}

function closeLightbox(modal) {
    modal.classList.remove('show');
    setTimeout(() => {
        // Clear src to stop video/loading/memory usage (optional, mostly good for cleanup)
        const modalImg = document.getElementById('lightbox-img');
        if (modalImg) modalImg.src = '';
    }, 300); // Wait for transition
    unlockBodyScroll(); // Re-enable background scrolling
}

