/**
 * PDF Slide Viewer Logic
 * Uses Mozilla's PDF.js to render PDF pages on a canvas in a full-screen modal.
 */

(function () {
    const PDFJS_VERSION = '3.11.174';

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

    function ensurePdfJsReady() {
        if (!window.pdfjsLib) return false;
        // Configure PDF.js worker only once.
        if (!window.pdfjsLib.GlobalWorkerOptions.workerSrc) {
            window.pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${PDFJS_VERSION}/pdf.worker.min.js`;
        }
        return true;
    }

    class PdfSlideViewer {
    constructor(elementId, pdfUrl, title) {
        this.elementId = elementId;
        this.pdfUrl = pdfUrl;
        this.title = title;

        // State
        this.pdfDoc = null;
        this.pageNum = 1;
        this.pageRendering = false;
        this.pageNumPending = null;
        this.scale = 1.5; // Initial scale, will be responsive
        this.canvas = null;
        this.ctx = null;

        // DOM Elements
        this.card = document.getElementById(`pdf-card-${elementId}`);
        this.modal = document.getElementById(`pdf-modal-${elementId}`);
        this.canvas = this.modal.querySelector('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.pageNumDom = this.modal.querySelector('.current-page');
        this.pageCountDom = this.modal.querySelector('.total-pages');
        this.prevBtn = this.modal.querySelector('.pdf-prev-btn');
        this.nextBtn = this.modal.querySelector('.pdf-next-btn');
        this.closeBtn = this.modal.querySelector('.pdf-modal-close');
        this.fullscreenBtn = this.modal.querySelector('.pdf-modal-fullscreen');
        this.spinner = this.modal.querySelector('.pdf-loading-spinner');

        // Move modal to body to ensure position:fixed works correctly (avoids transform contexts)
        if (this.modal && this.modal.parentElement !== document.body) {
            document.body.appendChild(this.modal);
        }

        this.init();
    }

    init() {
        // Trigger preview rendering
        this.renderPreview();

        // Event Listeners
        this.card.addEventListener('click', () => this.openModal());
        this.closeBtn.addEventListener('click', () => this.closeModal());

        // Click backdrop to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.closeModal();
        });

        if (this.fullscreenBtn) {
            this.fullscreenBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleFullscreen();
            });
        }

        // Navigation
        this.prevBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.onPrevPage();
        });

        this.nextBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.onNextPage();
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (!this.modal.classList.contains('active')) return;

            if (e.key === 'ArrowLeft') this.onPrevPage();
            if (e.key === 'ArrowRight' || e.key === ' ') {
                e.preventDefault(); // Prevent scrolling on space
                this.onNextPage();
            }
            if (e.key === 'Escape') this.closeModal();
        });

        // Click outside to close (optional, maybe distracting)
        // this.modal.addEventListener('click', (e) => {
        //    if (e.target === this.modal) this.closeModal();
        // });

        // Window resize
        window.addEventListener('resize', () => {
            if (this.modal.classList.contains('active')) {
                this.queueRenderPage(this.pageNum);
            }
        });
    }

    /**
     * Renders the first page of the PDF as a preview thumbnail in the card.
     * Only runs if the preview container doesn't already have a background image (checked via a data attribute or class).
     */
    async renderPreview() {
        const previewContainer = this.card.querySelector('.pdf-slide-preview');
        // Check if custom cover is already set via inline style (background-image)
        if (previewContainer.style.backgroundImage && previewContainer.style.backgroundImage !== 'none') {
            return;
        }

        try {
            // We use a separate loading task for the preview so we don't interfere with the main modal loading
            // and we don't necessarily want to load the whole doc into memory if we can avoid it (though pdf.js handles this well)
            // But since we want to keep it simple, we can just load the doc.
            // Note: If renderPreview is called, we might want to store pdfDoc for later use in openModal?
            // optimizing: let's reuse this task if user opens modal quickly.

            if (!this.loadingTask) {
                this.loadingTask = window.pdfjsLib.getDocument(this.pdfUrl);
            }

            const pdf = await this.loadingTask.promise;

            // If we are here, we might as well save it to this.pdfDoc to save a request later
            // BUT, openModal does its own thing. Let's make openModal smart enough to check if loadingTask exists.
            // For now, let's just let openModal do its own load fallback or we assign it here carefully.
            this.pdfDoc = pdf;

            const page = await pdf.getPage(1);

            const canvas = document.createElement('canvas');
            canvas.className = 'pdf-preview-canvas';

            // Get viewport to calculate aspect ratio
            const viewport = page.getViewport({ scale: 1 });

            // We want high quality thumbnail matching the container width
            // Container width might not be fully determined if hidden or responsive, but let's grab clientWidth
            let targetWidth = previewContainer.clientWidth || 600; // heuristic fallback

            const scale = targetWidth / viewport.width;
            const scaledViewport = page.getViewport({ scale: scale * 1.5 }); // 1.5x density for sharpness

            canvas.height = scaledViewport.height;
            canvas.width = scaledViewport.width;

            // Add canvas to container - insert before the overlay
            const overlay = previewContainer.querySelector('.pdf-slide-overlay');
            previewContainer.insertBefore(canvas, overlay);

            const ctx = canvas.getContext('2d');
            const renderContext = {
                canvasContext: ctx,
                viewport: scaledViewport
            };

            await page.render(renderContext).promise;

        } catch (error) {
            console.error('Error generating preview:', error);
        }
    }

    openModal() {
        this.modal.classList.add('active');
        lockBodyScroll(); // Prevent scrolling background (supports multiple overlays)

        if (!this.pdfDoc) {
            // Check if we already started loading in renderPreview
            if (this.loadingTask) {
                this.showSpinner();
                this.loadingTask.promise.then(
                    (pdf) => {
                        this.pdfDoc = pdf;
                        this.pageCountDom.textContent = this.pdfDoc.numPages;
                        this.renderPage(this.pageNum);
                        this.hideSpinner();
                    },
                    (error) => {
                        console.error('Error loading PDF:', error);
                        alert('Failed to load PDF. Please check your connection.');
                        this.closeModal();
                        this.hideSpinner();
                    }
                );
            } else {
                this.loadPdf();
            }
        } else {
            // PDF already loaded (e.g. by renderPreview), but we need to ensure UI is synced
            this.pageCountDom.textContent = this.pdfDoc.numPages;
            this.queueRenderPage(this.pageNum);
            this.hideSpinner();
        }
    }

    closeModal() {
        this.modal.classList.remove('active');
        unlockBodyScroll();

        // If we entered browser fullscreen, exit when closing.
        if (document.fullscreenElement) {
            document.exitFullscreen().catch(() => {});
        }
    }

    toggleFullscreen() {
        const target = this.modal;
        if (!document.fullscreenElement) {
            if (target.requestFullscreen) {
                target.requestFullscreen({ navigationUI: 'hide' }).catch(() => {});
            }
        } else {
            document.exitFullscreen().catch(() => {});
        }
    }

    showSpinner() {
        this.spinner.classList.add('active');
    }

    hideSpinner() {
        this.spinner.classList.remove('active');
    }

    /**
     * Asynchronously downloads PDF.
     */
    async loadPdf() {
        this.showSpinner();
        try {
            const loadingTask = window.pdfjsLib.getDocument(this.pdfUrl);
            this.pdfDoc = await loadingTask.promise;

            this.pageCountDom.textContent = this.pdfDoc.numPages;
            this.renderPage(this.pageNum);
        } catch (error) {
            console.error('Error loading PDF:', error);
            alert('Failed to load PDF. Please check your connection.');
            this.closeModal();
        } finally {
            this.hideSpinner();
        }
    }

    /**
     * Get page info from document, resize canvas accordingly, and render page.
     * @param num Page number.
     */
    /**
     * Get page info from document, resize canvas accordingly, and render page.
     * @param num Page number.
     */
    async renderPage(num) {
        if (this.pageRendering) {
            this.pageNumPending = num;
            return;
        }

        this.pageRendering = true;

        try {
            const page = await this.pdfDoc.getPage(num);

            // Calculate scale to fit in the container (mostly height-bound)
            // Available height approx window height - toolbar (60px) - margin
            const containerWidth = window.innerWidth * 0.9;
            const containerHeight = (window.innerHeight - 80) * 0.9;

            const viewportUnscaled = page.getViewport({ scale: 1 });

            // Determine scale to 'contain' the page
            const scaleX = containerWidth / viewportUnscaled.width;
            const scaleY = containerHeight / viewportUnscaled.height;
            const scale = Math.min(scaleX, scaleY);

            const viewport = page.getViewport({ scale: scale });

            this.canvas.height = viewport.height;
            this.canvas.width = viewport.width;

            // Render PDF page into canvas context
            const renderContext = {
                canvasContext: this.ctx,
                viewport: viewport
            };

            const renderTask = page.render(renderContext);

            // Wait for render to finish
            await renderTask.promise;

            this.pageRendering = false;

            // Fade in effect
            this.canvas.classList.remove('fade-in');
            void this.canvas.offsetWidth; // Trigger reflow
            this.canvas.classList.add('fade-in');

            if (this.pageNumPending !== null) {
                // New page rendering is pending
                this.renderPage(this.pageNumPending);
                this.pageNumPending = null;
            }

            // Update page counters
            this.pageNumDom.textContent = num;

            // Button states
            this.prevBtn.disabled = num <= 1;
            this.nextBtn.disabled = num >= this.pdfDoc.numPages;

        } catch (err) {
            console.error('Page render error:', err);
            this.pageRendering = false;
        }
    }

    /**
     * If another page rendering in progress, waits until the rendering is
     * finised. Otherwise, executes rendering immediately.
     */
    queueRenderPage(num) {
        if (this.pageRendering) {
            this.pageNumPending = num;
        } else {
            this.renderPage(num);
        }
    }

    /**
     * Displays previous page.
     */
    onPrevPage() {
        if (this.pageNum <= 1) return;
        this.pageNum--;
        this.queueRenderPage(this.pageNum);
    }

    /**
     * Displays next page.
     */
    onNextPage() {
        if (!this.pdfDoc || this.pageNum >= this.pdfDoc.numPages) return;
        this.pageNum++;
        this.queueRenderPage(this.pageNum);
    }
}

// Global initialization function
window.initPdfSlide = function (elementId, pdfUrl, title) {
    const init = () => {
        if (!ensurePdfJsReady()) {
            // PDF.js 被阻断/加载失败时：降级为新标签打开 PDF，避免“点击没反应”且不锁滚动
            const card = document.getElementById(`pdf-card-${elementId}`);
            if (card) {
                card.addEventListener('click', () => window.open(pdfUrl, '_blank', 'noopener,noreferrer'));
            }
            return;
        }
        new PdfSlideViewer(elementId, pdfUrl, title);
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
};

})();
