const estadoMeusPedidos = {
  pedidos: [],
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
  lista: document.getElementById("pedidosLista")
};

meusPedidosEls.form.addEventListener("submit", entrarMeusPedidos);
meusPedidosEls.sair.addEventListener("click", sairMeusPedidos);
meusPedidosEls.tabs.addEventListener("click", trocarAbaPedidos);
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
  mostrarMensagem(`${estadoMeusPedidos.pedidos.length} pedido(s) encontrado(s).`);
  meusPedidosEls.conteudo.hidden = estadoMeusPedidos.pedidos.length === 0;
  meusPedidosEls.sair.hidden = false;
  renderizarMeusPedidos();
}

async function sairMeusPedidos() {
  await fetch("/api/customer/logout", {
    method: "POST",
    credentials: "same-origin",
    headers: { "X-CSRF-Token": estadoMeusPedidos.csrfToken }
  });
  estadoMeusPedidos.pedidos = [];
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
    delivered: "Entregue", completed: "Entregue", cancelled: "Cancelado",
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
