const produtos = produtosPadrao.map(normalizarProdutoLoja);
window.decantsProdutos = produtos;
window.decantsProdutosPadrao = produtosPadrao.map(normalizarProdutoLoja);
let checkoutProdutoAtual = null;
let checkoutFreteAtual = null;
let checkoutCotacaoId = 0;
const CHAVE_CARRINHO = "decantsCarrinho";


// #CARREGAR_PRODUTOS_LOJA
async function carregarProdutosLoja() {
  if (!window.location.protocol.startsWith("http")) return;

  try {
    const resposta = await fetch("/api/products", { cache: "no-store" });
    if (!resposta.ok) throw new Error("API indisponivel");

    const produtosApi = await resposta.json();
    produtos.splice(0, produtos.length, ...produtosApi.map(normalizarProdutoLoja));
    window.decantsProdutos = produtos;
    atualizarVitrine();
  } catch (error) {
    console.warn("Nao foi possivel carregar os produtos do servidor.", error);
  }
}

// #NORMALIZAR_PRODUTO_LOJA
function normalizarProdutoLoja(produto) {
  const produtoCompleto = {
    ...produto,
    nome: repararTextoCatalogo(produto.nome || ""),
    chamada: repararTextoCatalogo(produto.chamada || ""),
    estoque: Number.isFinite(Number(produto.estoque)) ? Number(produto.estoque) : 10,
    promocao: Boolean(produto.promocao),
    precoPromocional5: produto.precoPromocional5 || "",
    precoPromocional10: produto.precoPromocional10 || "",
    destaque: Boolean(produto.destaque),
    selo: produto.selo || "",
    img: normalizarCaminhoImagem(produto.img || "")
  };

  if (!("destaque" in produto)) {
    produtoCompleto.destaque = produtosDestaquePadrao.includes(produtoCompleto.nome);
  }

  return produtoCompleto;
}

// #NORMALIZAR_CAMINHO_IMAGEM
function normalizarCaminhoImagem(caminho) {
  return String(caminho || "").trim().replace(/^\/+/, "");
}

function escaparHtmlLoja(valor) {
  return String(valor ?? "").replace(/[&<>"']/g, caractere => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[caractere]);
}

function escaparAtributoLoja(valor) {
  return escaparHtmlLoja(valor).replace(/`/g, "&#96;");
}

// #REPARAR_TEXTO_CATALOGO
function repararTextoCatalogo(texto) {
  const valor = String(texto || "");
  if (!/[\u00c3\u00c2\ufffd]/.test(valor)) return valor;

  try {
    const bytes = Array.from(valor, caractere => `%${caractere.charCodeAt(0).toString(16).padStart(2, "0")}`).join("");
    return decodeURIComponent(bytes);
  } catch (error) {
    return valor;
  }
}

// #OBTER_PRECO_PRODUTO
function obterPrecoProduto(produto, volume) {
  const precoBase = volume === 10 ? produto.preco10 : produto.preco5;
  const precoPromocional = volume === 10 ? produto.precoPromocional10 : produto.precoPromocional5;

  return produto.promocao && precoPromocional ? precoPromocional : precoBase;
}

// #RENDERIZAR_PRECO_CARD
function renderizarPrecoCard(produto, volume) {
  const precoBase = volume === 10 ? produto.preco10 : produto.preco5;
  const precoFinal = obterPrecoProduto(produto, volume);
  const label = `${volume}ml`;
  const precoBaseSeguro = escaparHtmlLoja(precoBase);
  const precoFinalSeguro = escaparHtmlLoja(precoFinal);

  if (produto.promocao && precoFinal !== precoBase) {
    return `<p class="preco-promocional"><span>${label} <s>R$ ${precoBaseSeguro}</s></span><strong>R$ ${precoFinalSeguro}</strong></p>`;
  }

  return `<p>${label} R$ ${precoBaseSeguro}</p>`;
}

// #PRODUTO_DISPONIVEL
function produtoDisponivel(produto) {
  return Number(produto.estoque) > 0;
}
