/**
 * Gerencia o clique no botão "expandir" dos cards de resíduos.
 * Alterna a visibilidade dos detalhes do card (mostra/esconde).
 */
document.addEventListener("click", (e) => {
  if (e.target.matches(".btn-expand")) {
    e.preventDefault();
    e.stopPropagation();

    const targetId = e.target.getAttribute("data-target");
    const details = document.getElementById(targetId);

    if (!details) return;

    details.classList.toggle("hidden");
    e.target.innerText = details.classList.contains("hidden")
      ? "Ver detalhes"
      : "Ocultar detalhes";
  }
});

/**
 * Função global para alternar visibilidade de detalhes de resíduos.
 * Usada por handlers inline no HTML.
 * @param {string} elementId - ID do elemento a ser mostrado/escondido
 */
if (!window.toggleDetails) {
  window.toggleDetails = function (elementId) {
    const element = document.getElementById(elementId);
    if (element) {
      element.classList.toggle("hidden");
    }
  };
}

/**
 * Função global para abrir localização no Google Maps.
 * Abre nova aba com coordenadas do ponto de coleta.
 * @param {string} _nome - Nome do local (não usado)
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @param {string} _endereco - Endereço (não usado)
 */
if (!window.abrirNoMapa) {
  window.abrirNoMapa = function (_nome, lat, lon, _endereco) {
    const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${lat},${lon}`;
    window.open(googleMapsUrl, "_blank");
  };
}
const toggleSenha = document.getElementById("toggle-senha");
if (toggleSenha) {
  toggleSenha.addEventListener("click", function (e) {
    e.preventDefault();
    const senhaInput = document.getElementById("senha");
    const tipo = senhaInput.type === "password" ? "text" : "password";
    senhaInput.type = tipo;
    this.innerHTML =
      tipo === "password"
        ? '<i class="fas fa-eye"></i>'
        : '<i class="fas fa-eye-slash"></i>';
  });
}

const toggleConfirmar = document.getElementById("toggle-confirmar");
if (toggleConfirmar) {
  toggleConfirmar.addEventListener("click", function (e) {
    e.preventDefault();
    const confirmarInput = document.getElementById("confirmar_senha");
    const tipo = confirmarInput.type === "password" ? "text" : "password";
    confirmarInput.type = tipo;
    this.innerHTML =
      tipo === "password"
        ? '<i class="fas fa-eye"></i>'
        : '<i class="fas fa-eye-slash"></i>';
  });
}

// ===== Validação de requisitos de senha em tempo real =====
const senha = document.getElementById("senha");
if (senha) {
  senha.addEventListener("input", () => {
    const valor = senha.value;

    // Verifica cada requisito e atualiza a classe CSS
    const reqMin = document.getElementById("req-min");
    if (reqMin) reqMin.classList.toggle("ok", valor.length >= 8);

    const reqMai = document.getElementById("req-mai");
    if (reqMai) reqMai.classList.toggle("ok", /[A-Z]/.test(valor));

    const reqMinu = document.getElementById("req-minu");
    if (reqMinu) reqMinu.classList.toggle("ok", /[a-z]/.test(valor));

    const reqNum = document.getElementById("req-num");
    if (reqNum) reqNum.classList.toggle("ok", /\d/.test(valor));

    const reqEsp = document.getElementById("req-esp");
    if (reqEsp) reqEsp.classList.toggle("ok", /[@$!%*?&#]/.test(valor));
  });
}

/* Máscara de Telefone */
document.addEventListener('DOMContentLoaded', function() {
    const telefoneInput = document.getElementById('telefone');
    if (telefoneInput) {
        telefoneInput.addEventListener('input', function (e) {
            let v = e.target.value.replace(/\D/g, "");
            v = v.substring(0, 11);
            
            if (v.length > 10) {
                // (XX) XXXXX-XXXX
                v = v.replace(/^(\d\d)(\d{5})(\d{4}).*/, "($1) $2-$3");
            } else if (v.length > 5) {
                // (XX) XXXX-XXXX
                v = v.replace(/^(\d\d)(\d{4})(\d{0,4}).*/, "($1) $2-$3");
            } else if (v.length > 2) {
                // (XX) ...
                v = v.replace(/^(\d\d)(\d{0,5}).*/, "($1) $2");
            } else {
                v = v.replace(/^(\d*)/, "($1");
            }
            
            e.target.value = v;
        });
    }
});
