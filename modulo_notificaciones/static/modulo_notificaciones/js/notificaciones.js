/**
 * Notificaciones Dropdown
 * ========================
 * Controla la apertura/cierre del dropdown de notificaciones
 * con toggle y cierre al hacer clic fuera.
 */

document.addEventListener('DOMContentLoaded', function() {
    const bellBtn = document.getElementById('notiBellBtn');
    const dropdown = document.getElementById('notiDropdown');

    if (bellBtn && dropdown) {
        // Abrir y cerrar el menú con clic en la campana
        bellBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdown.classList.toggle('active');
        });

        // Cerrar el menú si se hace clic fuera de él
        document.addEventListener('click', function(e) {
            if (!dropdown.contains(e.target) && e.target !== bellBtn) {
                dropdown.classList.remove('active');
            }
        });
    }
});

