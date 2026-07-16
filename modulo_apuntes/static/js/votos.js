function getCsrfToken(container) {
    const tokenInput = container.querySelector('input[name="csrfmiddlewaretoken"]');
    return tokenInput ? tokenInput.value : '';
}

function setActiveButton(container, votoUsuario) {
    container.querySelectorAll('[data-voto]').forEach((button) => {
        const activo = button.dataset.voto === votoUsuario;
        button.classList.toggle('is-activo', activo);
        button.setAttribute('aria-pressed', activo ? 'true' : 'false');
    });
}

function actualizarConteos(container, data) {
    const utilCount = container.querySelector('[data-voto-count="util"]');
    const noUtilCount = container.querySelector('[data-voto-count="no_util"]');
    const prestigio = container.querySelector('[data-voto-prestigio]');

    if (utilCount) utilCount.textContent = data.total_utiles;
    if (noUtilCount) noUtilCount.textContent = data.total_no_utiles;
    if (prestigio) prestigio.textContent = data.prestigio_apunte;

    setActiveButton(container, data.voto_usuario || '');
}

async function enviarVoto(container, tipo) {
    const url = container.dataset.votosUrl;
    const csrfToken = getCsrfToken(container);
    const formData = new FormData();
    formData.append('tipo', tipo);
    formData.append('csrfmiddlewaretoken', csrfToken);

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || 'No se pudo registrar el voto.');
    }

    actualizarConteos(container, data);
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-votos-container]').forEach((container) => {
        container.querySelectorAll('[data-voto]').forEach((button) => {
            button.addEventListener('click', async () => {
                button.disabled = true;
                try {
                    await enviarVoto(container, button.dataset.voto);
                } catch (error) {
                    alert(error.message);
                } finally {
                    button.disabled = false;
                }
            });
        });
    });
});
