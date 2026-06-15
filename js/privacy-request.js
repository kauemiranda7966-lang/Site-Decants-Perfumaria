const lgpdForm = document.getElementById("lgpdForm");
let lgpdCsrfToken = "";

async function iniciarFormularioLgpd() {
  if (!lgpdForm) return;
  const response = await fetch("/api/customer/session", { credentials: "same-origin" });
  const data = await response.json();
  lgpdCsrfToken = data.csrfToken || "";
  if (data.authenticated) {
    document.getElementById("lgpdEmail").value = data.email || "";
    document.getElementById("lgpdTelefone").value = data.phone || "";
  }
}

lgpdForm?.addEventListener("submit", async event => {
  event.preventDefault();
  const button = lgpdForm.querySelector("button[type='submit']");
  const message = document.getElementById("lgpdMensagem");
  button.disabled = true;
  message.hidden = false;
  message.textContent = "Enviando solicitacao...";
  try {
    const response = await fetch("/api/customer/requests", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": lgpdCsrfToken },
      body: JSON.stringify({
        requestType: "privacy",
        name: document.getElementById("lgpdNome").value,
        email: document.getElementById("lgpdEmail").value,
        phone: document.getElementById("lgpdTelefone").value,
        category: document.getElementById("lgpdCategoria").value,
        details: document.getElementById("lgpdDetalhes").value
      })
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "Nao foi possivel enviar.");
    lgpdForm.reset();
    message.textContent = `Solicitacao registrada. Protocolo ${data.protocol}.`;
  } catch (error) {
    message.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

iniciarFormularioLgpd().catch(() => {});
