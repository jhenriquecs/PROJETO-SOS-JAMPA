// ===== Toggle de visibilidade de senha =====
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
