/**
 * Adiciona funcionalidade para fechar elementos de alerta quando um botão
 * de fechamento é clicado.
 */
const closeButtons = document.querySelectorAll('[data-dismiss="alert"]');

closeButtons.forEach((button) => {
    button.addEventListener('click', function() {
        button.parentElement.style.display = 'none';
    });
});