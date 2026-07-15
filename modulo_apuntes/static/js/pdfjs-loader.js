export const PDFJS_VERSION = '4.10.38';
export const PDFJS_MODULE_URL = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${PDFJS_VERSION}/pdf.min.mjs`;

export async function loadPdfJs() {
    return import(PDFJS_MODULE_URL);
}
