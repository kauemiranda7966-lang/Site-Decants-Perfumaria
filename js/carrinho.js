const estadoCarrinho = {
  itens: [],
  cupom: ""
};

const elementosCarrinho = {
  vazio: document.getElementById("carrinhoVazio"),
  conteudo: document.getElementById("carrinhoConteudo"),
  itens: document.getElementById("carrinhoItens"),
  selecionarTodos: document.getElementById("selecionarTodos"),
  selecionarTodosMobile: document.getElementById("selecionarTodosMobile"),
  excluirSelecionados: document.getElementById("excluirSelecionados"),
  subtotal: document.getElementById("carrinhoSubtotal"),
  desconto: document.getElementById("carrinhoDesconto"),
  frete: document.getElementById("carrinhoFrete"),
  total: document.getElementById("carrinhoTotal"),
  totalMobile: document.getElementById("carrinhoTotalMobile"),
  cupom: document.getElementById("carrinhoCupom"),
  mensagemCupom: document.getElementById("mensagemCupom"),
  mensagem: document.getElementById("carrinhoMensagem"),
  checkout: document.getElementById("carrinhoCheckout"),
  whatsapp: document.getElementById("finalizarWhatsApp"),
  finalizarMobile: document.getElementById("finalizarMobile"),
  barraMobile: document.getElementById("carrinhoBarraMobile")
};

document.addEventListener("DOMContentLoaded", iniciarCarrinho);

function iniciarCarrinho() {
  estadoCarrinho.itens = window.lerCarrinho ? window.lerCarrinho() : [];
  vincularEventosCarrinho();
  renderizarCarrinho();
}

function vincularEventosCarrinho() {
  elementosCarrinho.selecionarTodos.addEventListener("change", event => selecionarTodosItens(event.target.checked));
  elementosCarrinho.selecionarTodosMobile.addEventListener("change", event => selecionarTodosItens(event.target.checked));
  elementosCarrinho.excluirSelecionados.addEventListener("click", excluirItensSelecionados);
  document.getElementById("aplicarCupom").addEventListener("click", aplicarCupomCarrinho);
  elementosCarrinho.checkout.addEventListener("submit", event => finalizarCarrinho(event, false));
  elementosCarrinho.whatsapp.addEventListener("click", event => finalizarCarrinho(event, true));
  elementosCarrinho.finalizarMobile.addEventListener("click", () => {
    elementosCarrinho.checkout.scrollIntoView({ behavior: "smooth", block: "start" });
    document.getElementById("carrinhoNome").focus();
  });
  document.getElementById("carrinhoTelefone").addEventListener("input", mascararTelefoneCarrinho);
}

function renderizarCarrinho() {
  const vazio = estadoCarrinho.itens.length === 0;
  elementosCarrinho.vazio.hidden = !vazio;
  elementosCarrinho.conteudo.hidden = vazio;
  elementosCarrinho.barraMobile.hidden = vazio;

  if (vazio) {
    atualizarResumoCarrinho();
    return;
  }

  elementosCarrinho.itens.innerHTML = estadoCarrinho.itens.map(item => `
    <article class="carrinho-item" data-chave="${escaparHtml(item.chave)}">
      <input class="item-selecionado" type="checkbox" aria-label="Selecionar ${escaparHtml(item.nome)}" ${item.selecionado !== false ? "checked" : ""}>
      <div class="carrinho-item-imagem">
        <img src="${escaparHtml(item.imagem)}" alt="${escaparHtml(item.nome)}">
      </div>
      <div class="carrinho-item-info">
        <h3>${escaparHtml(item.nome)}</h3>
        <p>${item.categoria === "feminino" ? "Perfume feminino" : "Perfume masculino"} em decant</p>
        <span>Estoque disponível: ${Number(item.estoque) || 1}</span>
      </div>
      <select class="carrinho-volume" aria-label="Tamanho">
        <option value="5" ${Number(item.volume) === 5 ? "selected" : ""}>5 ml</option>
        <option value="10" ${Number(item.volume) === 10 ? "selected" : ""}>10 ml</option>
      </select>
      <strong class="carrinho-preco">${moeda(precoItem(item))}</strong>
      <div class="carrinho-quantidade" aria-label="Quantidade">
        <button class="diminuir-item" type="button" aria-label="Diminuir">−</button>
        <span>${Number(item.quantidade) || 1}</span>
        <button class="aumentar-item" type="button" aria-label="Aumentar">+</button>
      </div>
      <button class="carrinho-remover" type="button" aria-label="Remover ${escaparHtml(item.nome)}"><i class="fa-regular fa-trash-can"></i></button>
    </article>
  `).join("");

  elementosCarrinho.itens.querySelectorAll(".carrinho-item").forEach(elemento => {
    const chave = elemento.dataset.chave;
    elemento.querySelector(".item-selecionado").addEventListener("change", event => atualizarItem(chave, { selecionado: event.target.checked }));
    elemento.querySelector(".carrinho-volume").addEventListener("change", event => alterarVolumeItem(chave, Number(event.target.value)));
    elemento.querySelector(".diminuir-item").addEventListener("click", () => alterarQuantidadeItem(chave, -1));
    elemento.querySelector(".aumentar-item").addEventListener("click", () => alterarQuantidadeItem(chave, 1));
    elemento.querySelector(".carrinho-remover").addEventListener("click", () => removerItem(chave));
  });

  atualizarResumoCarrinho();
}

function alterarVolumeItem(chave, volume) {
  const item = encontrarItem(chave);
  if (!item || item.volume === volume) return;

  const produto = obterProduto(item.nome);
  const novaChave = `${item.nome}-${volume}`;
  const duplicado = estadoCarrinho.itens.find(outro => outro.chave === novaChave);

  if (duplicado) {
    duplicado.quantidade = Math.min(duplicado.estoque, duplicado.quantidade + item.quantidade);
    duplicado.selecionado = true;
    estadoCarrinho.itens = estadoCarrinho.itens.filter(outro => outro.chave !== chave);
  } else {
    item.volume = volume;
    item.chave = novaChave;
    item.preco = produto ? precoProduto(produto, volume) : item.preco;
  }

  persistirERenderizar();
}

function alterarQuantidadeItem(chave, delta) {
  const item = encontrarItem(chave);
  if (!item) return;
  item.quantidade = Math.max(1, Math.min(Number(item.estoque) || 1, Number(item.quantidade) + delta));
  persistirERenderizar();
}

function atualizarItem(chave, alteracoes) {
  const item = encontrarItem(chave);
  if (!item) return;
  Object.assign(item, alteracoes);
  persistirERenderizar();
}

function removerItem(chave) {
  estadoCarrinho.itens = estadoCarrinho.itens.filter(item => item.chave !== chave);
  persistirERenderizar();
}

function selecionarTodosItens(selecionado) {
  estadoCarrinho.itens.forEach(item => item.selecionado = selecionado);
  persistirERenderizar();
}

function excluirItensSelecionados() {
  estadoCarrinho.itens = estadoCarrinho.itens.filter(item => item.selecionado === false);
  persistirERenderizar();
}

function persistirERenderizar() {
  window.salvarCarrinho?.(estadoCarrinho.itens);
  renderizarCarrinho();
}

function atualizarResumoCarrinho() {
  const selecionados = itensSelecionados();
  const subtotal = selecionados.reduce((soma, item) => soma + precoItem(item) * Number(item.quantidade || 1), 0);
  const desconto = calcularDesconto(subtotal);
  const total = Math.max(0, subtotal - desconto);
  const todosMarcados = estadoCarrinho.itens.length > 0 && estadoCarrinho.itens.every(item => item.selecionado !== false);

  elementosCarrinho.selecionarTodos.checked = todosMarcados;
  elementosCarrinho.selecionarTodosMobile.checked = todosMarcados;
  elementosCarrinho.subtotal.textContent = moeda(subtotal);
  elementosCarrinho.desconto.textContent = desconto ? `-${moeda(desconto)}` : moeda(0);
  elementosCarrinho.frete.textContent = subtotal >= 199 ? "Grátis" : "Calculado depois";
  elementosCarrinho.total.textContent = moeda(total);
  elementosCarrinho.totalMobile.textContent = moeda(total);
}

function aplicarCupomCarrinho() {
  const codigo = elementosCarrinho.cupom.value.trim().toUpperCase();
  estadoCarrinho.cupom = "";

  if (!codigo) {
    elementosCarrinho.mensagemCupom.textContent = "Digite um código de cupom.";
  } else if (codigo === "DECANTS5") {
    estadoCarrinho.cupom = codigo;
    elementosCarrinho.mensagemCupom.textContent = "Cupom aplicado: 5% de desconto.";
  } else {
    elementosCarrinho.mensagemCupom.textContent = "Cupom inválido ou expirado.";
  }

  atualizarResumoCarrinho();
}

function calcularDesconto(subtotal) {
  return estadoCarrinho.cupom === "DECANTS5" ? subtotal * .05 : 0;
}

async function finalizarCarrinho(event, preferirWhatsApp) {
  event.preventDefault();
  const selecionados = itensSelecionados();
  const mensagem = elementosCarrinho.mensagem;

  mensagem.hidden = false;
  mensagem.textContent = "";

  if (!selecionados.length) {
    mensagem.textContent = "Selecione pelo menos um produto para finalizar.";
    return;
  }

  if (!elementosCarrinho.checkout.reportValidity()) return;

  const botoes = elementosCarrinho.checkout.querySelectorAll("button");
  botoes.forEach(botao => botao.disabled = true);
  mensagem.textContent = "Criando seu pedido...";

  const payload = {
    customer: {
      name: document.getElementById("carrinhoNome").value.trim(),
      phone: document.getElementById("carrinhoTelefone").value.trim(),
      email: document.getElementById("carrinhoEmail").value.trim(),
      address: document.getElementById("carrinhoEndereco").value.trim()
    },
    items: selecionados.map(item => ({
      productId: Number(item.produtoId) || 0,
      productName: item.nome,
      volume: Number(item.volume),
      quantity: Number(item.quantidade)
    })),
    coupon: estadoCarrinho.cupom,
    paymentMethod: preferirWhatsApp ? "whatsapp" : "mercado_pago"
  };

  try {
    const resposta = await enviarPedidoCarrinho(payload);
    mensagem.textContent = `Pedido ${resposta.reference} criado com sucesso.`;

    if (preferirWhatsApp) {
      removerItensFinalizados(selecionados);
      window.open(resposta.whatsappUrl, "_blank", "noopener");
      return;
    }

    if (!resposta.paymentUrl) {
      mensagem.textContent = "Nao foi possivel gerar o link de pagamento. Confira os dados e tente novamente.";
      return;
    }

    removerItensFinalizados(selecionados);
    window.location.href = resposta.paymentUrl;
  } catch (error) {
    mensagem.textContent = error.message || "Não foi possível criar o pedido.";
  } finally {
    botoes.forEach(botao => botao.disabled = false);
  }
}

async function enviarPedidoCarrinho(payload) {
  const resposta = await fetch("/api/checkout", {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(dados.error || "Não foi possível criar o pedido.");
  return dados;
}

function removerItensFinalizados(finalizados) {
  const chaves = new Set(finalizados.map(item => item.chave));
  estadoCarrinho.itens = estadoCarrinho.itens.filter(item => !chaves.has(item.chave));
  window.salvarCarrinho?.(estadoCarrinho.itens);
}

function itensSelecionados() {
  return estadoCarrinho.itens.filter(item => item.selecionado !== false);
}

function encontrarItem(chave) {
  return estadoCarrinho.itens.find(item => item.chave === chave);
}

function obterProduto(nome) {
  return (window.decantsProdutos || []).find(produto => produto.nome === nome);
}

function precoProduto(produto, volume) {
  const promocional = volume === 10 ? produto.precoPromocional10 : produto.precoPromocional5;
  const base = volume === 10 ? produto.preco10 : produto.preco5;
  return produto.promocao && promocional ? promocional : base;
}

function precoItem(item) {
  const produto = obterProduto(item.nome);
  const texto = produto ? precoProduto(produto, Number(item.volume)) : item.preco;
  return Number(String(texto || "0").replace(/\./g, "").replace(",", ".")) || 0;
}

function moeda(valor) {
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function mascararTelefoneCarrinho(event) {
  const digitos = event.target.value.replace(/\D/g, "").slice(0, 11);
  event.target.value = digitos.length <= 10
    ? digitos.replace(/^(\d{0,2})(\d{0,4})(\d{0,4}).*/, (_, ddd, parte1, parte2) => `${ddd ? `(${ddd}` : ""}${ddd.length === 2 ? ") " : ""}${parte1}${parte2 ? `-${parte2}` : ""}`)
    : digitos.replace(/^(\d{2})(\d{5})(\d{4})$/, "($1) $2-$3");
}

function escaparHtml(valor) {
  return String(valor || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
