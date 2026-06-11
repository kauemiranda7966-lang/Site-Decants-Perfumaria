// #ABRIR_CHECKOUT
function abrirCheckout(nomeProduto) {
  const produto = produtos.find(item => item.nome === nomeProduto);
  if (produto && !produtoDisponivel(produto)) return;

  checkoutProdutoAtual = produto;
  checkoutFreteAtual = null;
  checkoutCotacaoId += 1;
  const modalExistente = document.querySelector(".modal-checkout");
  if (modalExistente) modalExistente.remove();

  if (!produto) {
    exibirAvisoCheckoutIndisponivel(nomeProduto);
    return;
  }

  document.body.insertAdjacentHTML("beforeend", `
    <div class="modal-checkout" onclick="fecharCheckout(event)">
      <form class="checkout-card" id="checkoutForm" onsubmit="enviarCheckout(event)">
        <button class="modal-fechar checkout-fechar" type="button" aria-label="Fechar" onclick="fecharCheckout()">&times;</button>

        <div class="checkout-topo">
          <span>Pedido seguro</span>
          <h2>${produto.nome}</h2>
          <p>Escolha o volume e finalize pelo Mercado Pago ou WhatsApp.</p>
        </div>

        <div class="checkout-produto">
          <img src="${obterImagemProduto(produto)}" alt="${produto.nome}" loading="lazy">
          <div>
            <strong>${extrairMarcaProduto(produto.nome)}</strong>
            <p>Estoque disponivel: ${produto.estoque}</p>
          </div>
        </div>

        <div class="checkout-opcoes" role="radiogroup" aria-label="Volume do decant">
          ${montarOpcaoCheckout(produto, 5, true)}
          ${montarOpcaoCheckout(produto, 10, false)}
        </div>

        <label class="checkout-label">
          Quantidade
          <input id="checkoutQuantidade" type="number" min="1" max="${Math.max(1, produto.estoque)}" value="1" oninput="atualizarTotalCheckout()">
        </label>

        <div class="checkout-grid">
          <label class="checkout-label">
            Nome completo
            <input id="checkoutNome" autocomplete="name" minlength="5" maxlength="80" required>
          </label>
          <label class="checkout-label">
            WhatsApp
            <input id="checkoutTelefone" autocomplete="tel" placeholder="(88) 99999-9999" required oninput="mascararTelefoneLoja(event)">
          </label>
          <label class="checkout-label">
            E-mail
            <input id="checkoutEmail" type="email" autocomplete="email" required>
          </label>
          <label class="checkout-label">
            CEP
            <input id="checkoutCep" autocomplete="postal-code" inputmode="numeric" maxlength="9" placeholder="00000-000" required oninput="mascararECalcularCepCheckout(event)">
          </label>
          <label class="checkout-label checkout-endereco">
            Endereco completo
            <input id="checkoutEndereco" autocomplete="street-address" minlength="10" maxlength="160" placeholder="Rua, numero, bairro e cidade" required>
          </label>
        </div>

        <div class="checkout-total">
          <span>Produtos <strong id="checkoutSubtotal">R$ ${obterPrecoProduto(produto, 5)}</strong></span>
          <span>Frete <strong id="checkoutFrete">Informe o CEP</strong></span>
          <span>Total</span>
          <strong id="checkoutTotal">R$ ${obterPrecoProduto(produto, 5)}</strong>
        </div>

        <p class="checkout-mensagem" id="checkoutMensagem" hidden></p>

        <div class="checkout-acoes">
          <button class="checkout-pagar" type="submit">
            <i class="fa-regular fa-credit-card"></i>
            Pagar online
          </button>
          <button class="checkout-whatsapp" type="button" onclick="enviarCheckout(event, true)">
            <i class="fa-brands fa-whatsapp"></i>
            Enviar no WhatsApp
          </button>
        </div>
      </form>
    </div>
  `);

  atualizarTotalCheckout();
}

// #MONTAR_OPCAO_CHECKOUT
function montarOpcaoCheckout(produto, volume, checked) {
  return `
    <label class="checkout-volume ${checked ? "ativo" : ""}">
      <input name="checkoutVolume" type="radio" value="${volume}" ${checked ? "checked" : ""} onchange="atualizarVolumeCheckout(event)">
      <span>${volume}ml</span>
      <strong>R$ ${obterPrecoProduto(produto, volume)}</strong>
    </label>
  `;
}

// #ATUALIZAR_VOLUME_CHECKOUT
function atualizarVolumeCheckout(event) {
  document.querySelectorAll(".checkout-volume").forEach(label => label.classList.remove("ativo"));
  event.currentTarget.closest(".checkout-volume").classList.add("ativo");
  atualizarTotalCheckout();
}

// #ATUALIZAR_TOTAL_CHECKOUT
function atualizarTotalCheckout() {
  if (!checkoutProdutoAtual) return;

  const volume = Number(document.querySelector("input[name='checkoutVolume']:checked")?.value || 5);
  const quantidade = Math.max(1, Number(document.getElementById("checkoutQuantidade")?.value || 1));
  const subtotal = precoTextoParaNumero(obterPrecoProduto(checkoutProdutoAtual, volume)) * quantidade;
  const total = subtotal + (checkoutFreteAtual || 0);
  const subtotalElemento = document.getElementById("checkoutSubtotal");
  const totalElemento = document.getElementById("checkoutTotal");
  if (subtotalElemento) subtotalElemento.textContent = `R$ ${formatarMoedaLoja(subtotal)}`;
  if (totalElemento) totalElemento.textContent = `R$ ${formatarMoedaLoja(total)}`;
  if (document.getElementById("checkoutCep")?.value.replace(/\D/g, "").length === 8) {
    calcularFreteCheckout();
  }
}

function mascararECalcularCepCheckout(event) {
  const digitos = event.target.value.replace(/\D/g, "").slice(0, 8);
  event.target.value = digitos.replace(/^(\d{5})(\d)/, "$1-$2");
  checkoutFreteAtual = null;
  const freteElemento = document.getElementById("checkoutFrete");
  if (freteElemento) freteElemento.textContent = digitos.length === 8 ? "Calculando..." : "Informe o CEP";
  atualizarTotalCheckout();
}

async function calcularFreteCheckout() {
  if (!checkoutProdutoAtual) return;
  const cep = document.getElementById("checkoutCep")?.value.replace(/\D/g, "") || "";
  if (cep.length !== 8 || new Set(cep).size === 1) return;

  const volume = Number(document.querySelector("input[name='checkoutVolume']:checked")?.value || 5);
  const quantidade = Math.max(1, Number(document.getElementById("checkoutQuantidade")?.value || 1));
  const subtotal = precoTextoParaNumero(obterPrecoProduto(checkoutProdutoAtual, volume)) * quantidade;
  const cotacaoId = ++checkoutCotacaoId;
  const freteElemento = document.getElementById("checkoutFrete");
  if (freteElemento) freteElemento.textContent = "Calculando...";

  try {
    const params = new URLSearchParams({
      postalCode: cep,
      productAmount: subtotal.toFixed(2)
    });
    const dados = await apiLoja(`/api/shipping/quote?${params}`, { headers: {} });
    if (cotacaoId !== checkoutCotacaoId) return;
    checkoutFreteAtual = Number(dados.shippingAmount) || 0;
    if (freteElemento) {
      freteElemento.textContent = checkoutFreteAtual === 0
        ? "Gratis"
        : `R$ ${formatarMoedaLoja(checkoutFreteAtual)}`;
    }
    const totalElemento = document.getElementById("checkoutTotal");
    if (totalElemento) totalElemento.textContent = `R$ ${formatarMoedaLoja(subtotal + checkoutFreteAtual)}`;
  } catch (error) {
    if (cotacaoId !== checkoutCotacaoId) return;
    checkoutFreteAtual = null;
    if (freteElemento) freteElemento.textContent = "Nao calculado";
    const mensagem = document.getElementById("checkoutMensagem");
    if (mensagem) {
      mensagem.hidden = false;
      mensagem.classList.add("erro");
      mensagem.textContent = error.message;
    }
  }
}

// #ENVIAR_CHECKOUT
async function enviarCheckout(event, preferirWhatsApp = false) {
  event.preventDefault();
  if (!checkoutProdutoAtual) return;
  const form = document.getElementById("checkoutForm");
  if (!form.reportValidity()) return;

  const mensagem = document.getElementById("checkoutMensagem");
  const botoes = document.querySelectorAll(".checkout-acoes button");
  mensagem.hidden = false;
  mensagem.classList.remove("erro", "sucesso");
  mensagem.textContent = "Criando pedido...";
  botoes.forEach(botao => botao.disabled = true);

  let volume = Number(document.querySelector("input[name='checkoutVolume']:checked")?.value || 5);
  let quantidade = Math.max(1, Number(document.getElementById("checkoutQuantidade").value || 1));
  const postalCode = document.getElementById("checkoutCep").value.trim();
  if (checkoutFreteAtual === null) {
    mensagem.classList.add("erro");
    mensagem.textContent = "Aguarde o calculo do frete pelo CEP.";
    botoes.forEach(botao => botao.disabled = false);
    return;
  }

  try {
    const resposta = await apiLoja("/api/checkout", {
      method: "POST",
      body: JSON.stringify({
        customer: {
          name: document.getElementById("checkoutNome").value,
          phone: document.getElementById("checkoutTelefone").value,
          email: document.getElementById("checkoutEmail").value,
          postalCode,
          address: document.getElementById("checkoutEndereco").value
        },
        items: [{
          productId: checkoutProdutoAtual.id || 0,
          productName: checkoutProdutoAtual.nome,
          volume,
          quantity: quantidade
        }],
        paymentMethod: preferirWhatsApp ? "whatsapp" : "mercado_pago"
      })
    });

    mensagem.classList.add("sucesso");
    mensagem.textContent = `Pedido ${resposta.reference} criado.`;

    if (preferirWhatsApp) {
      window.open(resposta.whatsappUrl, "_blank", "noopener");
      mensagem.textContent = `Pedido ${resposta.reference} pronto para enviar no WhatsApp.`;
      return;
    }

    if (!resposta.paymentUrl) {
      mensagem.classList.remove("sucesso");
      mensagem.classList.add("erro");
      mensagem.textContent = "Nao foi possivel gerar o link de pagamento. Confira os dados e tente novamente.";
      return;
    }

    window.location.href = resposta.paymentUrl;
  } catch (error) {
    mensagem.classList.add("erro");
    mensagem.textContent = error.message || "Nao foi possivel criar o pedido.";
  } finally {
    botoes.forEach(botao => botao.disabled = false);
  }
}

// #FECHAR_CHECKOUT
function fecharCheckout(event) {
  if (event && !event.target.classList.contains("modal-checkout")) return;

  const modal = document.querySelector(".modal-checkout");
  if (modal) modal.remove();
}

// #EXIBIR_AVISO_CHECKOUT_INDISPONIVEL
function exibirAvisoCheckoutIndisponivel(nomeProduto) {
  document.body.insertAdjacentHTML("beforeend", `
    <div class="modal-checkout" onclick="fecharCheckout(event)">
      <div class="checkout-card checkout-aviso">
        <button class="modal-fechar checkout-fechar" type="button" aria-label="Fechar" onclick="fecharCheckout()">&times;</button>
        <div class="checkout-topo">
          <span>Checkout indisponivel</span>
          <h2>${nomeProduto}</h2>
          <p>Nao consegui localizar este produto no catalogo carregado. Recarregue a pagina e tente novamente.</p>
        </div>
      </div>
    </div>
  `);
}

// #PRECO_TEXTO_PARA_NUMERO
function precoTextoParaNumero(valor) {
  return Number(String(valor || "0").replace(/\./g, "").replace(",", "."));
}

// #FORMATAR_MOEDA_LOJA
function formatarMoedaLoja(valor) {
  return Number(valor || 0).toFixed(2).replace(".", ",");
}

// #MASCARAR_TELEFONE_LOJA
function mascararTelefoneLoja(event) {
  if (/[a-zA-Z]/.test(event.target.value)) return;

  const numeros = event.target.value.replace(/\D/g, "").slice(0, 11);
  const ddd = numeros.slice(0, 2);
  const inicio = numeros.length > 10 ? numeros.slice(2, 7) : numeros.slice(2, 6);
  const fim = numeros.length > 10 ? numeros.slice(7) : numeros.slice(6);

  if (numeros.length <= 2) {
    event.target.value = ddd ? `(${ddd}` : "";
    return;
  }

  event.target.value = `(${ddd}) ${inicio}${fim ? `-${fim}` : ""}`;
}

// #API_LOJA
async function apiLoja(url, options = {}) {
  if (!window.location.protocol.startsWith("http")) {
    throw new Error("Abra a loja pelo servidor: http://localhost:8000/index.html");
  }

  let resposta;
  try {
    resposta = await fetch(url, {
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options
    });
  } catch (error) {
    throw new Error("Nao foi possivel conectar ao servidor. Verifique se ele esta rodando em http://localhost:8000.");
  }

  const texto = await resposta.text();
  let dados = {};
  try {
    dados = texto ? JSON.parse(texto) : {};
  } catch (error) {
    throw new Error("O servidor respondeu em um formato invalido. Recarregue a pagina e tente novamente.");
  }

  if (!resposta.ok) {
    throw new Error(dados.error || "Erro ao comunicar com o servidor.");
  }

  return dados;
}

// #EXIBIR_RETORNO_PAGAMENTO
function exibirRetornoPagamento() {
  const parametros = new URLSearchParams(window.location.search);
  const pedido = parametros.get("pedido");
  const pagamento = parametros.get("pagamento");
  if (!pedido || !pagamento) return;

  const mensagens = {
    aprovado: "Pagamento aprovado. Obrigado pela compra!",
    recusado: "Pagamento nao aprovado. Voce pode tentar novamente ou chamar no WhatsApp.",
    pendente: "Pagamento pendente. Assim que confirmar, seguimos com o pedido."
  };

  document.body.insertAdjacentHTML("afterbegin", `
    <div class="pagamento-retorno">
      <strong>Pedido ${pedido}</strong>
      <span>${mensagens[pagamento] || "Status do pagamento atualizado."}</span>
      <button type="button" onclick="this.parentElement.remove()">OK</button>
    </div>
  `);
}
