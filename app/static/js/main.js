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

/**
 * Toggle de visibilidade para campo de senha no formulário de registro.
 * Alterna entre mostrar texto ou asteriscos.
 */
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

/**
 * Toggle de visibilidade para campo de confirmação de senha no registro.
 */
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

/**
 * Toggle de visibilidade para campo de senha no formulário de login.
 */
const toggleLogin = document.getElementById("toggle-password-login");
if (toggleLogin) {
  toggleLogin.addEventListener("click", function (e) {
    e.preventDefault();
    const passwordInput = document.getElementById("password");
    const tipo = passwordInput.type === "password" ? "text" : "password";
    passwordInput.type = tipo;
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

/* ===== Lógica do Widget de Criar Post ===== */

/**
 * Alterna a visibilidade dos campos de input (endereço, tags) no widget.
 * @param {string} id - O ID do elemento a ser alternado.
 */
/**
 * Alterna a visibilidade de campos adicionais no formulário de criação de post.
 * @param {string} id - ID do elemento a ser mostrado/escondido
 */
function toggleCpInput(id) {
  const el = document.getElementById(id);
  if (el.classList.contains("hidden-input")) {
    el.classList.remove("hidden-input");
    el.focus();
  } else {
    el.classList.add("hidden-input");
  }
}

/**
 * Inicializa o comportamento do widget de postagem.
 * Expande o widget quando o campo de descrição recebe foco.
 */
document.addEventListener("DOMContentLoaded", function () {
  const cpDesc = document.getElementById("cp-desc");
  const cpExtras = document.getElementById("cp-extras");
  const cpActions = document.getElementById("cp-actions");

  if (cpDesc) {
    cpDesc.addEventListener("focus", () => {
      cpExtras.classList.remove("hidden-initially");
      cpActions.classList.remove("hidden-initially");
    });
  }
});

/**
 * Envia uma requisição para curtir/descurtir um post.
 * Atualiza a interface com o novo número de curtidas e o estado do botão.
 * @param {string} postId - O ID do post.
 */
function toggleLike(postId) {
  fetch(`/posts/like/${postId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (response.status === 401) {
        return response.json().then((data) => {
          if (data.redirect) window.location.href = data.redirect;
        });
      }
      return response.json();
    })
    .then((data) => {
      if (!data) return;

      if (data && data.error) {
        console.error(data.error);
        return;
      }

      if (data) {
        // Atualiza o contador (ID corrigido para bater com o HTML)
        const countSpan = document.getElementById(`likes-val-${postId}`);
        if (countSpan) {
          countSpan.textContent = data.likes_count;
        }

        // Atualiza o estilo do botão
        const btn = document.getElementById(`like-btn-${postId}`);
        if (btn) {
          if (data.liked) {
            btn.classList.add("liked");
            btn.style.color = "#2e7d32";
          } else {
            btn.classList.remove("liked");
            btn.style.color = ""; // Remove cor inline para voltar ao CSS padrão
          }
        }
      }
    })
    .catch((err) => console.error("Erro ao curtir:", err));
}

/**
 * Compartilha o post usando a Web Share API ou copia o link.
 * @param {string} url - A URL do post para compartilhar.
 */
function sharePost(url) {
  // Garante URL absoluta
  const fullUrl = url.startsWith("http") ? url : window.location.origin + url;

  if (navigator.share) {
    navigator
      .share({
        title: "Confira este post no EcoPonto",
        url: fullUrl,
      })
      .catch(console.error);
  } else {
    // Fallback: Copiar para a área de transferência
    navigator.clipboard
      .writeText(fullUrl)
      .then(() => alert("Link copiado para a área de transferência!"))
      .catch((err) => console.error("Erro ao copiar:", err));
  }
}

/**
 * Alterna a visibilidade da seção de comentários de um post.
 * Carrega os comentários via AJAX se ainda não foram carregados.
 * @param {string} postId - ID do post
 */
function toggleComments(postId) {
  const section = document.getElementById(`comments-section-${postId}`);
  if (!section) return;

  if (section.classList.contains("hidden")) {
    section.classList.remove("hidden");
    loadComments(postId);
    // Foca no input
    setTimeout(() => {
      const input = document.getElementById(`comment-input-${postId}`);
      if (input) input.focus();
    }, 100);
  } else {
    section.classList.add("hidden");
  }
}

/**
 * Busca e renderiza os comentários de um post via API.
 * Evita recarregar se já foi carregado anteriormente.
 * @param {string} postId - ID do post
 */
function loadComments(postId) {
  const list = document.getElementById(`comments-list-${postId}`);
  if (!list) return;

  // Evita recarregar se já carregou (opcional)
  if (list.dataset.loaded === "true") return;

  list.innerHTML = '<div class="loading-comments">Carregando...</div>';

  fetch(`/posts/${postId}/comments`)
    .then((res) => res.json())
    .then((data) => {
      list.innerHTML = "";
      if (data.length === 0) {
        list.innerHTML =
          '<p class="no-comments">Seja o primeiro a comentar!</p>';
      } else {
        data.forEach((c) => {
          list.appendChild(createCommentElement(c));
        });
      }
      list.dataset.loaded = "true";
    })
    .catch((err) => {
      console.error(err);
      list.innerHTML = '<p class="error">Erro ao carregar comentários.</p>';
    });
}

/**
 * Cria o elemento DOM de um comentário com dados do autor e opções de exclusão.
 * @param {Object} c - Dados do comentário (id, text, author_nick, author_image, etc)
 * @returns {HTMLElement} Elemento div do comentário
 */
function createCommentElement(c) {
  const div = document.createElement("div");
  div.className = "comment-item";
  div.id = `comment-${c.id}`;
  
  // URL da imagem - usar direto se for URL completa, senão adicionar /static/
  const imgSrc = c.author_image && c.author_image.trim() !== ""
    ? c.author_image
    : `https://ui-avatars.com/api/?name=${encodeURIComponent(c.author_nick)}&background=random`;
  
  // Criar elemento de imagem com onerror fallback
  const imgElement = document.createElement('img');
  imgElement.src = imgSrc;
  imgElement.className = 'comment-avatar';
  imgElement.alt = 'Avatar';
  imgElement.onerror = function() {
    this.onerror = null;
    this.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(c.author_nick)}&background=random`;
  };

  let deleteBtn = "";
  // c.can_delete vem do backend
  if (c.can_delete) {
    deleteBtn = `<button class="delete-comment-btn" onclick="deleteComment('${c.id}', '${c.post_id || ""}')" title="Excluir">&times;</button>`;
  }

  // Construir HTML sem a tag img (vamos adicionar o elemento criado depois)
  div.innerHTML = `
        <div class="comment-bubble-wrapper">
            <div class="comment-bubble">
                <div class="comment-author">${c.author_nick}</div>
                <div class="comment-text">${c.text}</div>
            </div>
            ${deleteBtn}
        </div>
    `;
  
  // Inserir o elemento de imagem no início do div
  div.insertBefore(imgElement, div.firstChild);
  
  return div;
}

/**
 * Exclui um comentário via API DELETE.
 * Remove o elemento do DOM e atualiza contador de comentários.
 * @param {string} commentId - ID do comentário
 * @param {string} postId - ID do post (para atualizar contador)
 */
function deleteComment(commentId, postId) {
  fetch(`/posts/comment/${commentId}/delete`, {
    method: "DELETE",
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        const el = document.getElementById(`comment-${commentId}`);
        if (el) el.remove();

        // Atualiza contador visualmente (decrementa)
        // Se postId não veio, tentamos achar pelo contexto do DOM se necessário, mas ideal é vir.
        if (postId) {
          const countSpan = document.getElementById(`comments-val-${postId}`);
          if (countSpan) {
            let current = parseInt(countSpan.textContent) || 0;
            countSpan.textContent = Math.max(0, current - 1);
          }
        }
      } else {
        alert(data.error || "Erro ao excluir");
      }
    })
    .catch((err) => console.error(err));
}

/**
 * Envia um novo comentário via API POST.
 * Adiciona o comentário ao DOM e atualiza contador.
 * @param {string} postId - ID do post onde comentar
 */
function submitComment(postId) {
  const input = document.getElementById(`comment-input-${postId}`);
  const text = input.value.trim();
  if (!text) return;

  // Desabilita input enquanto envia
  input.disabled = true;

  fetch(`/posts/${postId}/comment`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: text }),
  })
    .then((res) => {
      if (res.status === 401) {
        return res.json().then((data) => {
          if (data.redirect) window.location.href = data.redirect;
        });
      }
      return res.json();
    })
    .then((data) => {
      input.disabled = false;
      if (!data) return;

      if (data.error) {
        alert(data.error);
        return;
      }

      const list = document.getElementById(`comments-list-${postId}`);
      const noComments = list.querySelector(".no-comments");
      if (noComments) noComments.remove();

      list.appendChild(createCommentElement(data));
      input.value = "";
      input.focus();

      // Atualiza contador
      const countSpan = document.getElementById(`comments-val-${postId}`);
      if (countSpan) countSpan.textContent = data.comments_count;
    })
    .catch((err) => {
      console.error(err);
      input.disabled = false;
      alert("Erro ao enviar comentário.");
    });
}

/**
 * Permite enviar comentário pressionando Enter (Ctrl+Enter para quebra de linha).
 * @param {KeyboardEvent} event - Evento do teclado
 * @param {string} postId - ID do post
 */
function checkEnter(event, postId) {
  if (event.key === "Enter") {
    submitComment(postId);
  }
}

/**
 * Formatação automática do telefone no cadastro
 */
document.addEventListener("DOMContentLoaded", function () {
  const phoneInput = document.getElementById("telefone");
  if (phoneInput) {
    phoneInput.addEventListener("input", function (e) {
      let value = e.target.value.replace(/\D/g, "");
      if (value.length > 11) value = value.slice(0, 11);

      let formattedValue = "";
      if (value.length > 0) {
        formattedValue = "(" + value.substring(0, 2);
      }
      if (value.length > 2) {
        formattedValue += ") " + value.substring(2, 7);
      }
      if (value.length > 7) {
        formattedValue += "-" + value.substring(7, 11);
      }

      e.target.value = formattedValue;
    });
  }
});
