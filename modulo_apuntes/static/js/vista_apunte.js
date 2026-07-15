import { PDFJS_VERSION, loadPdfJs } from './pdfjs-loader.js';

function setStatus(viewer, message) {
    const status = viewer.querySelector('[data-role="status"]');
    if (status) {
        status.textContent = message;
    }
}

function setError(viewer, message) {
    const error = viewer.querySelector('[data-role="error"]');
    if (error) {
        error.hidden = !message;
        error.textContent = message || '';
    }
}

function getElements(viewer) {
    return {
        canvas: viewer.querySelector('[data-role="canvas"]'),
        canvasWrap: viewer.querySelector('[data-role="canvas-wrap"]'),
        status: viewer.querySelector('[data-role="status"]'),
        error: viewer.querySelector('[data-role="error"]'),
        prevBtn: viewer.querySelector('[data-action="prev"]'),
        nextBtn: viewer.querySelector('[data-action="next"]'),
        zoomOutBtn: viewer.querySelector('[data-action="zoom-out"]'),
        zoomInBtn: viewer.querySelector('[data-action="zoom-in"]'),
    };
}

function updateButtons(elements, state) {
    if (elements.prevBtn) elements.prevBtn.disabled = state.pageNumber <= 1;
    if (elements.nextBtn) elements.nextBtn.disabled = state.pageNumber >= state.pdf.numPages;
}

async function renderPage(state, elements) {
    const renderId = ++state.renderId;
    const page = await state.pdf.getPage(state.pageNumber);
    const viewport = page.getViewport({ scale: state.scale });
    const context = elements.canvas.getContext('2d');

    const outputScale = window.devicePixelRatio || 1;
    elements.canvas.width = Math.floor(viewport.width * outputScale);
    elements.canvas.height = Math.floor(viewport.height * outputScale);
    elements.canvas.style.width = `${Math.floor(viewport.width)}px`;
    elements.canvas.style.height = `${Math.floor(viewport.height)}px`;

    context.setTransform(outputScale, 0, 0, outputScale, 0, 0);
    context.clearRect(0, 0, elements.canvas.width, elements.canvas.height);

    const renderTask = page.render({
        canvasContext: context,
        viewport,
    });

    await renderTask.promise;

    if (renderId !== state.renderId) return;

    setStatus(state.viewer, `Página ${state.pageNumber} de ${state.pdf.numPages}`);
    setError(state.viewer, '');
    updateButtons(elements, state);
}

function createState(viewer, pdf) {
    return {
        viewer,
        pdf,
        pageNumber: 1,
        scale: 1,
        renderId: 0,
    };
}

async function initViewer(viewer) {
    const pdfUrl = viewer.dataset.pdfUrl;
    const elements = getElements(viewer);

    try {
        setStatus(viewer, 'Cargando PDF...');
        const pdfjs = await loadPdfJs();
        pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${PDFJS_VERSION}/pdf.worker.min.mjs`;

        const pdf = await pdfjs.getDocument(pdfUrl).promise;
        const state = createState(viewer, pdf);

        const renderCurrentPage = () => renderPage(state, elements).catch((error) => {
            console.error(error);
            setError(viewer, 'No se pudo renderizar la página del PDF. Usa el enlace para abrirlo en una nueva pestaña.');
            setStatus(viewer, 'Error al renderizar el PDF');
        });

        if (elements.prevBtn) {
            elements.prevBtn.addEventListener('click', () => {
                if (state.pageNumber <= 1) return;
                state.pageNumber -= 1;
                renderCurrentPage();
            });
        }

        if (elements.nextBtn) {
            elements.nextBtn.addEventListener('click', () => {
                if (state.pageNumber >= state.pdf.numPages) return;
                state.pageNumber += 1;
                renderCurrentPage();
            });
        }

        if (elements.zoomOutBtn) {
            elements.zoomOutBtn.addEventListener('click', () => {
                state.scale = Math.max(0.5, state.scale - 0.1);
                renderCurrentPage();
            });
        }

        if (elements.zoomInBtn) {
            elements.zoomInBtn.addEventListener('click', () => {
                state.scale = Math.min(3, state.scale + 0.1);
                renderCurrentPage();
            });
        }

        await renderCurrentPage();
    } catch (error) {
        console.error(error);
        setStatus(viewer, 'No se pudo cargar el visor PDF.js');
        setError(viewer, 'Chrome no pudo cargar el visor PDF.js. Puedes abrir el archivo directamente con el enlace.');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.pdfjs-viewer').forEach((viewer) => {
        initViewer(viewer);
    });
});
