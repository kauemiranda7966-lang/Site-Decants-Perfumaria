const estadoMeusPedidos = {
  pedidos: [],
  statusAtivo: "to_separate"
};

const meusPedidosEls = {
  form: document.getElementById("pedidosForm"),
  referencia: document.getElementById("pedidosReferencia"),
  contato: document.getElementById("pedidosContato"),
  mensagem: document.getElementById("pedidosMensagem"),
  conteudo: document.getElementById("pedidosConteudo"),
  tabs: document.getElementById("pedidosTabs"),
  lista: document.getElementById("pedidosLista")
};

meusPedidosEls.form.addEventListener("submit", buscarMeusPedidos);
meusPedidosEls.tabs.addEventListener("click", trocarAbaPedidos);

async function buscarMeusPedidos(event) {
  event.preventDefault();
  const referencia = meusPedidosEls.referencia.value.trim().toUpperCase();
  const contato = meusPedidosEls.contato.value.trim();
  const botao = meusPedidosEls.form.querySelector("button");

  if (!referencia || !contato) return;

  meusPedidosEls.mensagem.hidden = false;
  meusPedidosEls.mensagem.textContent = "Buscando seus pedidos...";
  meusPedidosEls.conteudo.hidden = true;
  botao.disabled = true;

  try {
    const params = new URLSearchParams({ reference: referencia, contact: contato });
    const resposta = await fetch(`/api/customer/orders?${params}`, {
      credentials: "same-origin"
    });
    const dados = await resposta.json().catch(() => ({}));
    if (!resposta.ok) throw new Error(dados.error || "Nao foi possivel buscar seus pedidos.");

    estadoMeusPedidos.pedidos = dados.orders || [];
    meusPedidosEls.mensagem.textContent = estadoMeusPedidos.pedidos.length
      ? `${estadoMeusPedidos.pedidos.length} pedido(s) encontrado(s).`
      : "Nenhum pedido encontrado para este contato.";
    meusPedidosEls.conteudo.hidden = estadoMeusPedidos.pedidos.length === 0;
    renderizarMeusPedidos();
  } catch (error) {
    meusPedidosEls.mensagem.textContent = error.message || "Nao foi possivel buscar seus pedidos.";
  } finally {
    botao.disabled = false;
  }
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
        <div>
          <span>Pedido</span>
          <strong>${escaparHtml(pedido.reference)}</strong>
        </div>
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
    approved: "to_separate",
    paid: "to_separate",
    creating_payment: "to_separate",
    pending: "to_separate",
    awaiting_payment: "to_separate",
    whatsapp_pending: "to_separate",
    preparing: "to_separate",
    to_separate: "to_separate",
    separated: "separated",
    shipped: "separated",
    delivered: "separated",
    completed: "separated",
    cancelled: "cancelled",
    refunded: "cancelled",
    charged_back: "cancelled",
    rejected: "cancelled",
    expired: "cancelled"
  };
  return mapa[status] || "to_separate";
}

function rotuloStatusCliente(status) {
  const mapa = {
    awaiting_payment: "Aguardando pagamento",
    creating_payment: "Criando pagamento",
    whatsapp_pending: "Aguardando WhatsApp",
    pending: "Pagamento pendente",
    approved: "Em separacao",
    paid: "Em separacao",
    to_separate: "Em separacao",
    preparing: "Em separacao",
    separated: "Separado",
    shipped: "Separado",
    delivered: "Entregue",
    completed: "Entregue",
    cancelled: "Cancelado",
    refunded: "Cancelado",
    charged_back: "Cancelado",
    rejected: "Recusado",
    expired: "Expirado"
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
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
