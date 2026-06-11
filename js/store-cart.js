// #COMPRAR
function comprar(nomeProduto) {
  const produto = produtos.find(item => item.nome === nomeProduto);
  if (!produto || !produtoDisponivel(produto)) return;

  const volumeSelecionado = Number(document.querySelector(".modal-volume-card.ativo")?.dataset.volume || 5);
  const quantidadeSelecionada = Math.max(1, Number(document.getElementById("modalQuantidade")?.textContent || 1));
  adicionarAoCarrinho(produto, volumeSelecionado, quantidadeSelecionada);
  mostrarConfirmacaoCarrinho(produto.nome, volumeSelecionado, quantidadeSelecionada);
}

// #MOSTRAR_CONFIRMACAO_CARRINHO
function mostrarConfirmacaoCarrinho(nomeProduto, volume, quantidade) {
  document.querySelector(".carrinho-confirmacao")?.remove();

  const confirmacao = document.createElement("aside");
  confirmacao.className = "carrinho-confirmacao";
  confirmacao.setAttribute("role", "status");
  confirmacao.setAttribute("aria-live", "polite");
  confirmacao.innerHTML = `
    <span class="carrinho-confirmacao-icone" aria-hidden="true">
      <i class="fa-solid fa-check"></i>
    </span>
    <div>
      <strong>Adicionado ao carrinho</strong>
      <p></p>
    </div>
    <a href="carrinho.html">Ver carrinho</a>
    <button type="button" aria-label="Fechar aviso">
      <i class="fa-solid fa-xmark" aria-hidden="true"></i>
    </button>
  `;

  confirmacao.querySelector("p").textContent = `${quantidade}x ${nomeProduto} - ${volume}ml`;
  confirmacao.querySelector("button").addEventListener("click", () => confirmacao.remove());
  document.body.appendChild(confirmacao);

  window.requestAnimationFrame(() => confirmacao.classList.add("visivel"));
  window.setTimeout(() => {
    confirmacao.classList.remove("visivel");
    window.setTimeout(() => confirmacao.remove(), 240);
  }, 4200);
}

// #LER_CARRINHO
function lerCarrinho() {
  try {
    const itens = JSON.parse(localStorage.getItem(CHAVE_CARRINHO) || "[]");
    return Array.isArray(itens) ? itens : [];
  } catch (error) {
    return [];
  }
}

// #SALVAR_CARRINHO
function salvarCarrinho(itens) {
  localStorage.setItem(CHAVE_CARRINHO, JSON.stringify(itens));
  atualizarContadoresCarrinho();
}

// #ADICIONAR_AO_CARRINHO
function adicionarAoCarrinho(produto, volume = 5, quantidade = 1) {
  const itens = lerCarrinho();
  const chave = `${produto.nome}-${volume}`;
  const existente = itens.find(item => item.chave === chave);
  const estoque = Math.max(1, Number(produto.estoque) || 1);

  if (existente) {
    existente.quantidade = Math.min(estoque, existente.quantidade + quantidade);
    existente.selecionado = true;
  } else {
    itens.push({
      chave,
      produtoId: produto.id || 0,
      nome: produto.nome,
      categoria: produto.categoria,
      imagem: obterImagemProduto(produto),
      volume,
      preco: obterPrecoProduto(produto, volume),
      quantidade: Math.min(estoque, quantidade),
      estoque,
      selecionado: true
    });
  }

  salvarCarrinho(itens);
}

// #ATUALIZAR_CONTADORES_CARRINHO
function atualizarContadoresCarrinho() {
  const total = lerCarrinho().reduce((soma, item) => soma + Number(item.quantidade || 0), 0);
  document.querySelectorAll("[data-carrinho-contador]").forEach(contador => {
    contador.textContent = total > 99 ? "99+" : String(total);
    contador.hidden = total === 0;
  });
}

// #SCROLL_TO_CLUBE_OFERTAS
function scrollToClubeOfertas() {
  document.getElementById("clube-ofertas")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

// #CADASTRAR_CLUBE_OFERTAS
async function cadastrarClubeOfertas(event) {
  event.preventDefault();

  const form = event.currentTarget;
  const mensagem = document.getElementById("clubeOfertasMensagem");
  const botao = form.querySelector("button[type='submit']");
  const payload = {
    nome: document.getElementById("clubeNome").value.trim(),
    email: document.getElementById("clubeEmail").value.trim(),
    telefone: document.getElementById("clubeTelefone").value.trim()
  };

  mensagem.hidden = false;
  mensagem.classList.remove("erro", "sucesso");

  if (!validarLeadClube(payload)) {
    mensagem.classList.add("erro");
    mensagem.textContent = "Informe um e-mail valido e um WhatsApp com DDD.";
    return;
  }

  botao.disabled = true;
  mensagem.textContent = "Salvando seu cadastro...";

  try {
    if (!window.location.protocol.startsWith("http")) {
      salvarLeadLocalClube(payload);
    } else {
      await apiLoja("/api/leads", {
        method: "POST",
        body: JSON.stringify(payload)
      });
    }

    form.reset();
    mensagem.classList.add("sucesso");
    mensagem.textContent = "Cadastro realizado com sucesso. Voce entrou para o Clube de Ofertas.";
  } catch (error) {
    mensagem.classList.add("erro");
    mensagem.textContent = error.message || "Nao foi possivel salvar seu cadastro agora.";
  } finally {
    botao.disabled = false;
  }
}

// #VALIDAR_LEAD_CLUBE
function validarLeadClube(payload) {
  const emailValido = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(payload.email);
  const telefoneValido = payload.telefone.replace(/\D/g, "").length >= 10;
  return emailValido && telefoneValido;
}

// #SALVAR_LEAD_LOCAL_CLUBE
function salvarLeadLocalClube(payload) {
  const chave = "decantsClubeOfertas";
  const leads = JSON.parse(localStorage.getItem(chave) || "[]");
  leads.push({ ...payload, telefone: payload.telefone.replace(/\D/g, ""), createdAt: new Date().toISOString() });
  localStorage.setItem(chave, JSON.stringify(leads));
}
