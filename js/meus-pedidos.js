const estadoMeusPedidos = {
  pedidos: [],
  solicitacoes: [],
  statusAtivo: "to_separate",
  csrfToken: ""
};

const meusPedidosEls = {
  form: document.getElementById("pedidosForm"),
  email: document.getElementById("pedidosEmail"),
  telefone: document.getElementById("pedidosTelefone"),
  sair: document.getElementById("pedidosSair"),
  mensagem: document.getElementById("pedidosMensagem"),
  conteudo: document.getElementById("pedidosConteudo"),
  tabs: document.getElementById("pedidosTabs"),
  lista: document.getElementById("pedidosLista"),
  devolucaoForm: document.getElementById("devolucaoForm"),
  devolucaoPedido: document.getElementById("devolucaoPedido"),
  devolucaoMensagem: document.getElementById("devolucaoMensagem"),
  solicitacoesLista: document.getElementById("solicitacoesLista")
};

meusPedidosEls.form.addEventListener("submit", entrarMeusPedidos);
meusPedidosEls.sair.addEventListener("click", sairMeusPedidos);
meusPedidosEls.tabs.addEventListener("click", trocarAbaPedidos);
meusPedidosEls.devolucaoForm.addEventListener("submit", enviarSolicitacaoDevolucao);
iniciarMeusPedidos();

async function iniciarMeusPedidos() {
  try {
    const resposta = await fetch("/api/customer/session", { credentials: "same-origin" });
    const dados = await resposta.json();
    estadoMeusPedidos.csrfToken = dados.csrfToken || "";
    if (dados.authenticated) {
      meusPedidosEls.email.value = dados.email || "";
      meusPedidosEls.telefone.value = dados.phone || "";
      await carregarMeusPedidos();
    }
  } catch {
    mostrarMensagem("Nao foi possivel iniciar a consulta de pedidos.");
  }
}

async function entrarMeusPedidos(event) {
  event.preventDefault();
  const botao = meusPedidosEls.form.querySelector('button[type="submit"]');
  botao.disabled = true;
  mostrarMensagem("Entrando e buscando seus pedidos...");

  try {
    const resposta = await fetch("/api/customer/login", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": estadoMeusPedidos.csrfToken
      },
      body: JSON.stringify({
        email: meusPedidosEls.email.value.trim(),
        phone: meusPedidosEls.telefone.value.trim()
      })
    });
    const dados = await resposta.json().catch(() => ({}));
    if (!resposta.ok) throw new Error(dados.error || "Nao foi possivel entrar.");
    await carregarMeusPedidos();
  } catch (error) {
    mostrarMensagem(error.message || "Nao foi possivel entrar.");
  } finally {
    botao.disabled = false;
  }
}

async function carregarMeusPedidos() {
  const resposta = await fetch("/api/customer/orders", { credentials: "same-origin" });
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(dados.error || "Nao foi possivel buscar seus pedidos.");

  estadoMeusPedidos.pedidos = dados.orders || [];
  await carregarSolicitacoes();
  mostrarMensagem(`${estadoMeusPedidos.pedidos.length} pedido(s) encontrado(s).`);
  meusPedidosEls.conteudo.hidden = estadoMeusPedidos.pedidos.length === 0;
  meusPedidosEls.sair.hidden = false;
  renderizarMeusPedidos();
  meusPedidosEls.devolucaoPedido.innerHTML = estadoMeusPedidos.pedidos
    .map(pedido => `<option value="${escaparHtml(pedido.reference)}">${escaparHtml(pedido.reference)} · ${moedaPedido(Number(pedido.total) || 0)}</option>`)
    .join("");
}

async function carregarSolicitacoes() {
  const resposta = await fetch("/api/customer/requests", { credentials: "same-origin" });
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(dados.error || "Nao foi possivel buscar as solicitacoes.");
  estadoMeusPedidos.solicitacoes = dados.requests || [];
  renderizarSolicitacoes();
}

async function enviarSolicitacaoDevolucao(event) {
  event.preventDefault();
  const formElement = event.currentTarget;
  const botao = formElement.querySelector("button[type='submit']");
  botao.disabled = true;
  meusPedidosEls.devolucaoMensagem.hidden = false;
  meusPedidosEls.devolucaoMensagem.textContent = "Registrando solicitacao...";
  try {
    const resposta = await fetch("/api/customer/requests", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": estadoMeusPedidos.csrfToken },
      body: JSON.stringify({
        requestType: "return",
        orderReference: meusPedidosEls.devolucaoPedido.value,
        category: document.getElementById("devolucaoCategoria").value,
        reason: document.getElementById("devolucaoMotivo").value,
        details: document.getElementById("devolucaoDetalhes").value,
        acceptedPolicy: document.getElementById("devolucaoAceite").checked
      })
    });
    const dados = await resposta.json().catch(() => ({}));
    if (!resposta.ok) throw new Error(dados.error || "Nao foi possivel registrar.");

    const fotos = [...document.getElementById("devolucaoFotos").files].slice(0, 5);
    for (const foto of fotos) {
      const form = new FormData();
      form.append("image", foto);
      const upload = await fetch(`/api/customer/requests/${dados.id}/attachments`, {
        method: "POST",
        credentials: "same-origin",
        headers: { "X-CSRF-Token": estadoMeusPedidos.csrfToken },
        body: form
      });
      const uploadData = await upload.json().catch(() => ({}));
      if (!upload.ok) throw new Error(uploadData.error || "Solicitacao criada, mas uma foto falhou.");
    }
    formElement.reset();
    meusPedidosEls.devolucaoMensagem.textContent = `Solicitacao registrada. Protocolo ${dados.protocol}.`;
    await carregarSolicitacoes();
  } catch (error) {
    meusPedidosEls.devolucaoMensagem.textContent = error.message;
  } finally {
    botao.disabled = false;
  }
}

function renderizarSolicitacoes() {
  meusPedidosEls.solicitacoesLista.innerHTML = estadoMeusPedidos.solicitacoes.map(item => {
    const anexos = (item.attachments || []).map(anexo =>
      `<a target="_blank" rel="noopener" href="/api/customer/requests/${item.id}/attachments/${anexo.id}">${escaparHtml(anexo.original_name)}</a>`
    ).join("");
    const etiqueta = item.reverse_code
      ? `<a class="pedido-acao secundario" href="/api/customer/requests/${item.id}/reverse-label.pdf" download>Baixar etiqueta reversa</a>`
      : "";
    return `
      <article class="solicitacao-card">
        <div><strong>${escaparHtml(item.protocol)}</strong><span>${rotuloSolicitacao(item.status)}</span></div>
        <p>${escaparHtml(item.order_reference || "LGPD")} · ${escaparHtml(rotuloCategoriaSolicitacao(item.category))}${item.reason ? " · " + escaparHtml(item.reason) : ""}</p>
        ${item.resolution ? `<p><b>Resposta:</b> ${escaparHtml(item.resolution)}</p>` : ""}
        ${anexos ? `<div class="solicitacao-anexos">${anexos}</div>` : ""}
        ${etiqueta}
      </article>
    `;
  }).join("") || `<p>Nenhuma solicitacao registrada.</p>`;
}

function rotuloCategoriaSolicitacao(category) {
  const labels = {
    cancelamento_antes_separacao: "Cancelamento antes da separacao",
    arrependimento: "Direito de arrependimento",
    produto_incorreto: "Produto incorreto",
    avaria: "Produto avariado",
    vazamento: "Vazamento",
    defeito: "Problema de qualidade",
    outro: "Outro"
  };
  return labels[category] || category;
}

function rotuloSolicitacao(status) {
  const labels = {
    pending: "Pendente", in_review: "Em analise", awaiting_customer: "Aguardando voce",
    awaiting_return: "Aguardando devolucao", approved: "Aprovada", rejected: "Recusada",
    refunded: "Reembolsada", completed: "Concluida"
  };
  return labels[status] || status;
}

async function sairMeusPedidos() {
  await fetch("/api/customer/logout", {
    method: "POST",
    credentials: "same-origin",
    headers: { "X-CSRF-Token": estadoMeusPedidos.csrfToken }
  });
  estadoMeusPedidos.pedidos = [];
  estadoMeusPedidos.solicitacoes = [];
  meusPedidosEls.form.reset();
  meusPedidosEls.sair.hidden = true;
  meusPedidosEls.conteudo.hidden = true;
  mostrarMensagem("Voce saiu da area de pedidos.");
}

function mostrarMensagem(texto) {
  meusPedidosEls.mensagem.hidden = false;
  meusPedidosEls.mensagem.textContent = texto;
}

function trocarAbaPedidos(event) {
  const aba = event.target.closest("button[data-status]");
  if (!aba) return;
  estadoMeusPedidos.statusAtivo = aba.dataset.status;
  renderizarMeusPedidos();
}

function renderizarMeusPedidos() {
  const totais = estadoMeusPedidos.pedidos.reduce((acc, pedido) => {
    const status = statusOperacionalCliente(pedido.status);
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, {});

  meusPedidosEls.tabs.querySelectorAll("button[data-status]").forEach(botao => {
    botao.classList.toggle("active", botao.dataset.status === estadoMeusPedidos.statusAtivo);
    botao.querySelector("span").textContent = totais[botao.dataset.status] || 0;
  });

  const pedidos = estadoMeusPedidos.pedidos.filter(
    pedido => statusOperacionalCliente(pedido.status) === estadoMeusPedidos.statusAtivo
  );

  meusPedidosEls.lista.innerHTML = pedidos.map(renderizarPedido).join("") || `
    <div class="pedidos-vazio">
      <i class="fa-regular fa-clipboard"></i>
      <strong>Nenhum pedido nesta aba</strong>
      <span>Quando um pedido chegar aqui, ele aparece automaticamente na lista.</span>
    </div>
  `;
}

function renderizarPedido(pedido) {
  const itens = (pedido.items || []).map(item => `
    <li>
      <span>${Number(item.quantity) || 1}x ${escaparHtml(item.product_name)} ${Number(item.volume) || ""}ml</span>
      <strong>${moedaPedido(Number(item.subtotal) || 0)}</strong>
    </li>
  `).join("");

  return `
    <article class="pedido-card">
      <div class="pedido-card-topo">
        <div><span>Pedido</span><strong>${escaparHtml(pedido.reference)}</strong></div>
        <mark class="${statusOperacionalCliente(pedido.status)}">${rotuloStatusCliente(pedido.status)}</mark>
      </div>
      <ul>${itens}</ul>
      <div class="pedido-card-rodape">
        <span>${formatarDataPedido(pedido.created_at)}</span>
        <strong>${moedaPedido(Number(pedido.total) || 0)}</strong>
      </div>
      ${renderizarAcaoPedido(pedido)}
    </article>
  `;
}

function renderizarAcaoPedido(pedido) {
  if (pedido.paymentUrl && ["awaiting_payment", "pending"].includes(pedido.status)) {
    return `<a class="pedido-acao" href="${escaparHtml(pedido.paymentUrl)}">Pagar pedido</a>`;
  }
  if (pedido.whatsappUrl && statusOperacionalCliente(pedido.status) !== "cancelled") {
    return `<a class="pedido-acao secundario" href="${escaparHtml(pedido.whatsappUrl)}" target="_blank" rel="noopener">Chamar no WhatsApp</a>`;
  }
  return "";
}

function statusOperacionalCliente(status) {
  const mapa = {
    approved: "to_separate", paid: "to_separate", creating_payment: "to_separate",
    pending: "to_separate", awaiting_payment: "to_separate", whatsapp_pending: "to_separate",
    preparing: "to_separate", to_separate: "to_separate", separated: "separated",
    shipped: "separated", delivered: "separated", completed: "separated",
    risk_review: "to_separate",
    cancelled: "cancelled", refunded: "cancelled", charged_back: "cancelled",
    rejected: "cancelled", expired: "cancelled", payment_error: "cancelled"
  };
  return mapa[status] || "to_separate";
}

function rotuloStatusCliente(status) {
  const mapa = {
    awaiting_payment: "Aguardando pagamento", creating_payment: "Criando pagamento",
    whatsapp_pending: "Aguardando WhatsApp", pending: "Pagamento pendente",
    approved: "Em separacao", paid: "Em separacao", to_separate: "Em separacao",
    preparing: "Em separacao", separated: "Separado", shipped: "Separado",
    delivered: "Entregue", completed: "Entregue", risk_review: "Pagamento em analise",
    cancelled: "Cancelado",
    refunded: "Cancelado", charged_back: "Cancelado", rejected: "Recusado",
    expired: "Expirado", payment_error: "Erro no pagamento"
  };
  return mapa[status] || "Em separacao";
}

function formatarDataPedido(valor) {
  const data = new Date(String(valor || "").replace(" ", "T"));
  if (Number.isNaN(data.getTime())) return "";
  return data.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" });
}

function moedaPedido(valor) {
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function escaparHtml(valor) {
  return String(valor || "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
