function openEditProfilePicModal() {
  const modal = document.getElementById("editProfilePicModal");
  if (modal) modal.classList.add("active");
}

function closeEditProfilePicModal() {
  const modal = document.getElementById("editProfilePicModal");
  if (modal) modal.classList.remove("active");
}

function openEditProfileModal() {
  const modal = document.getElementById("editProfileModal");
  if (modal) modal.classList.add("active");
}

function closeEditProfileModal() {
  const modal = document.getElementById("editProfileModal");
  if (modal) modal.classList.remove("active");
}

// Encapsula inicialização para garantir que DOM e Cropper estejam disponíveis
function initProfileCropper() {
  // Fallback loader for CropperJS if CDN falhar
  let cropperLoadingPromise = null;
  function ensureCropperLoaded() {
    if (typeof Cropper !== "undefined") return Promise.resolve();
    if (cropperLoadingPromise) return cropperLoadingPromise;
    cropperLoadingPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.js";
      script.onload = () => resolve();
      script.onerror = (err) => reject(err);
      document.head.appendChild(script);
    });
    return cropperLoadingPromise;
  }

  const modal = document.getElementById("editProfilePicModal");
  if (modal) {
    modal.addEventListener("click", function (e) {
      if (e.target === this) {
        closeEditProfilePicModal();
      }
    });
  }

  let cropper;
  const imageInput = document.getElementById("profileImageInput");
  const imageToCrop = document.getElementById("imageToCrop");
  const cropperArea = document.getElementById("cropperArea");
  const imageUploadArea = document.getElementById("imageUploadArea");
  const form = document.getElementById("editProfilePicForm");


  // Se algum elemento não existir, aborta silenciosamente (ex: página errada)
  if (!imageInput || !imageToCrop || !cropperArea || !imageUploadArea || !form) {
    return;
  }

  // Abre diálogo de arquivo ao clicar no botão
  const btnSelectImage = document.getElementById("btnSelectImage");
  
  if (btnSelectImage) {
    btnSelectImage.addEventListener("click", function (e) {
      e.preventDefault();
      imageInput.click();
    });
  }

  imageInput.addEventListener("change", function (e) {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      const reader = new FileReader();
      reader.onload = function (ev) {
        imageToCrop.src = ev.target.result;
        imageUploadArea.style.display = "none";
        cropperArea.style.display = "flex";

        if (cropper) {
          cropper.destroy();
        }

        ensureCropperLoaded()
          .then(() => {
            if (typeof Cropper !== "undefined") {
              // Detecta se é mobile e ajusta config
              const isMobile = window.innerWidth <= 768;
              const minWidth = isMobile ? 200 : 400;
              const minHeight = isMobile ? 200 : 300;
              
              cropper = new Cropper(imageToCrop, {
                aspectRatio: 1,
                viewMode: 1,
                autoCropArea: 1,
                responsive: true,
                guides: true,
                highlight: true,
                cropBoxMovable: true,
                cropBoxResizable: true,
                toggleDragModeOnDblclick: true,
                minContainerWidth: minWidth,
                minContainerHeight: minHeight,
              });
            }
          });
      };
      reader.readAsDataURL(file);
    }
  });

  form.addEventListener("submit", function (e) {
    if (cropper) {
      e.preventDefault();
      cropper
        .getCroppedCanvas({
          width: 300,
          height: 300,
        })
        .toBlob((blob) => {
          const formData = new FormData(form);
          // Replace the file in FormData with the cropped blob
          formData.set("profile_image", blob, "profile.jpg");

          // Send via fetch
          fetch(form.action || window.location.href, {
            method: "POST",
            body: formData,
          })
            .then((response) => {
              if (response.ok) {
                window.location.reload();
              } else {
                alert("Erro ao atualizar perfil");
              }
            })
            .catch((err) => {
              console.error(err);
              alert("Erro ao atualizar perfil");
            });
        }, "image/jpeg");
    }
    // If no cropper (user didn't change image), let the form submit normally
  });
}

// ===== CROPPER PARA FOTO DE CAPA =====
function initCoverCropper() {
  let cropperLoadingPromise = null;
  function ensureCropperLoaded() {
    if (typeof Cropper !== "undefined") return Promise.resolve();
    if (cropperLoadingPromise) return cropperLoadingPromise;
    cropperLoadingPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.js";
      script.onload = () => resolve();
      script.onerror = (err) => reject(err);
      document.head.appendChild(script);
    });
    return cropperLoadingPromise;
  }

  let cropper;
  const coverImageInput = document.getElementById("coverImageInput");
  const imageToCropCover = document.getElementById("imageToCropCover");
  const coverCropperArea = document.getElementById("coverCropperArea");
  const coverUploadArea = document.getElementById("coverUploadArea");
  const btnSelectCover = document.getElementById("btnSelectCover");
  const form = document.getElementById("editProfileForm");

  // Se algum elemento não existir, aborta silenciosamente
  if (!coverImageInput || !imageToCropCover || !coverCropperArea || !coverUploadArea || !btnSelectCover || !form) {
    return;
  }

  // Abre diálogo de arquivo ao clicar no botão
  btnSelectCover.addEventListener("click", function (e) {
    e.preventDefault();
    coverImageInput.click();
  });

  coverImageInput.addEventListener("change", function (e) {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      const reader = new FileReader();
      reader.onload = function (ev) {
        imageToCropCover.src = ev.target.result;
        coverUploadArea.style.display = "none";
        coverCropperArea.style.display = "flex";

        if (cropper) {
          cropper.destroy();
        }

        ensureCropperLoaded()
          .then(() => {
            if (typeof Cropper !== "undefined") {
              const isMobile = window.innerWidth <= 768;
              const minWidth = isMobile ? 200 : 400;
              const minHeight = isMobile ? 100 : 200;
              
              cropper = new Cropper(imageToCropCover, {
                aspectRatio: 940 / 350, // Proporção da capa
                viewMode: 1,
                autoCropArea: 1,
                responsive: true,
                guides: true,
                highlight: true,
                cropBoxMovable: true,
                cropBoxResizable: true,
                toggleDragModeOnDblclick: true,
                minContainerWidth: minWidth,
                minContainerHeight: minHeight,
              });
            }
          });
      };
      reader.readAsDataURL(file);
    }
  });

  // Intercepta submit do formulário de edição de perfil
  form.addEventListener("submit", function (e) {
    if (cropper && coverImageInput.files.length > 0) {
      e.preventDefault();
      cropper
        .getCroppedCanvas({
          width: 940,
          height: 350,
        })
        .toBlob((blob) => {
          const formData = new FormData(form);
          formData.set("cover_image", blob, "cover.jpg");

          fetch(form.action || window.location.href, {
            method: "POST",
            body: formData,
          })
            .then((response) => {
              if (response.ok) {
                window.location.reload();
              } else {
                alert("Erro ao atualizar perfil");
              }
            })
            .catch((err) => {
              console.error(err);
              alert("Erro ao atualizar perfil");
            });
        }, "image/jpeg");
    }
  });
}

// Garante execução mesmo se DOMContentLoaded já tiver disparado
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initCoverCropper);
} else {
  initCoverCropper();
}

// Garante execução mesmo se DOMContentLoaded já tiver disparado
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initProfileCropper);
} else {
  initProfileCropper();
}
