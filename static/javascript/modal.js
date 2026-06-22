// ============================================================
// MODAL GLOBAL REUTILIZABLE
// ============================================================

(function() {
    'use strict';

    // Elementos del DOM
    const modal = document.getElementById('modalGlobal');
    const overlay = modal.querySelector('.modal-overlay');
    const titulo = document.getElementById('modalTitulo');
    const mensaje = document.getElementById('modalMensaje');
    const footer = document.getElementById('modalFooter');
    const btnCerrar = document.getElementById('modalCerrar');
    const btnCancelar = document.getElementById('modalBtnCancelar');
    const btnConfirmar = document.getElementById('modalBtnConfirmar');

    // Estado interno
    let accionConfirmar = null;
    let accionCancelar = null;

    // ============================================================
    // FUNCIONES PÚBLICAS (Accesibles desde cualquier lugar)
    // ============================================================

    /**
     * Muestra un modal de confirmación (eliminar, etc.)
     */
    window.mostrarModalConfirmacion = function(opciones) {
        const defaults = {
            titulo: 'Confirmar acción',
            mensaje: '¿Estás seguro?',
            textoConfirmar: 'Confirmar',
            textoCancelar: 'Cancelar',
            tipo: 'peligro', // 'peligro' | 'primario' | 'info'
            onConfirm: null,
            onCancel: null
        };

        const config = { ...defaults, ...opciones };

        // Configurar el modal
        titulo.textContent = config.titulo;
        mensaje.textContent = config.mensaje;
        btnConfirmar.textContent = config.textoConfirmar;
        btnCancelar.textContent = config.textoCancelar;

        // Configurar tipo de modal (clase CSS)
        modal.className = 'modal-global';
        if (config.tipo) {
            modal.classList.add('modal-' + config.tipo);
        }

        // Guardar callbacks
        accionConfirmar = config.onConfirm || null;
        accionCancelar = config.onCancel || null;

        // Mostrar ambos botones
        btnCancelar.style.display = '';
        btnConfirmar.style.display = '';

        // Abrir modal
        abrirModal();
    };

    /**
     * Muestra un modal informativo (éxito, error, info)
     */
    window.mostrarModalInfo = function(opciones) {
        const defaults = {
            titulo: 'Información',
            mensaje: 'Mensaje informativo',
            textoBoton: 'Aceptar',
            tipo: 'info', // 'exito' | 'error' | 'info'
            onClose: null
        };

        const config = { ...defaults, ...opciones };

        titulo.textContent = config.titulo;
        mensaje.textContent = config.mensaje;
        btnConfirmar.textContent = config.textoBoton;

        // Configurar tipo
        modal.className = 'modal-global';
        if (config.tipo) {
            modal.classList.add('modal-' + config.tipo);
        }

        // Ocultar botón cancelar (solo mostrar confirmar)
        btnCancelar.style.display = 'none';
        btnConfirmar.style.display = '';

        // Guardar callback
        accionConfirmar = config.onClose || null;
        accionCancelar = null;

        abrirModal();
    };

    /**
     * Cierra el modal manualmente
     */
    window.cerrarModal = function() {
        cerrarModal();
    };

    // ============================================================
    // FUNCIONES PRIVADAS
    // ============================================================

    function abrirModal() {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    function cerrarModal() {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        accionConfirmar = null;
        accionCancelar = null;
    }

    // ============================================================
    // EVENTOS
    // ============================================================

    // Cerrar con botón X
    btnCerrar.addEventListener('click', function() {
        if (accionCancelar && typeof accionCancelar === 'function') {
            accionCancelar();
        }
        cerrarModal();
    });

    // Cerrar con overlay
    overlay.addEventListener('click', function() {
        if (accionCancelar && typeof accionCancelar === 'function') {
            accionCancelar();
        }
        cerrarModal();
    });

    // Cerrar con ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'flex') {
            if (accionCancelar && typeof accionCancelar === 'function') {
                accionCancelar();
            }
            cerrarModal();
        }
    });

    // Botón Cancelar
    btnCancelar.addEventListener('click', function() {
        if (accionCancelar && typeof accionCancelar === 'function') {
            accionCancelar();
        }
        cerrarModal();
    });

    // Botón Confirmar
    btnConfirmar.addEventListener('click', function() {
        if (accionConfirmar && typeof accionConfirmar === 'function') {
            accionConfirmar();
        }
        cerrarModal();
    });

})();