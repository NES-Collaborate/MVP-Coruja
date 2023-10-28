// Inicialização
const htmlElement = document.documentElement;
const themeToggle = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");

// Carregar o tema salvo, se houver
const savedTheme = localStorage.getItem("theme");
if (savedTheme) {
    htmlElement.setAttribute("data-bs-theme", savedTheme);
    setThemeIcon(savedTheme);
}

if (themeToggle && themeIcon) {
    themeToggle.addEventListener("click", () => {
        const themeAttr = htmlElement.attributes.getNamedItem("data-bs-theme");
        if (themeAttr) {
            // Alternar o tema
            const newTheme = themeAttr.value === "dark" ? "light" : "dark";
            themeAttr.value = newTheme;

            // Salvar o tema no localStorage
            localStorage.setItem("theme", newTheme);

            // Definir o ícone do tema
            setThemeIcon(newTheme);
        }
    });
} else {
    console.error("Botão ou ícone para alternar o tema não encontrado");
}

// Função para definir o ícone do tema
function setThemeIcon(theme) {
    if (theme === "dark") {
        themeIcon.className = "bi bi-moon";
        // Altera tema da navbar
        $('#app_navbar').addClass("bg-dark")
        $('#app_navbar').removeClass("bg-light")
    } else {
        themeIcon.className = "bi bi-sun";
        // Altera tema da navbar
        $('#app_navbar').removeClass("bg-dark")
        $('#app_navbar').addClass("bg-light")
    }
    // Adicionar animação
    themeIcon.classList.add("animate__animated", "animate__flip");

    // Remover animação após completar para poder animar novamente
    themeIcon.addEventListener("animationend", () => {
        themeIcon.classList.remove("animate__animated", "animate__flip");
    });
}


var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})
