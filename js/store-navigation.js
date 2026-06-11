// #PESQUISAR_PRODUTOS
function pesquisarProdutos(rolarAteCatalogo = true) {
  const busca = normalizarTexto(searchInput ? searchInput.value : "");
  const categoria = categoriaFiltro ? categoriaFiltro.value : "";
  const genero = generoFiltro ? generoFiltro.value : "";
  const familia = familiaFiltro ? familiaFiltro.value : "";
  const intensidade = intensidadeFiltro ? intensidadeFiltro.value : "";
  const categoriaSelecionada = genero || categoria;

  const filtradosMasculinos = produtos.filter(produto =>
    produto.categoria === "masculino" &&
    produtoCombinaComFiltro(produto, busca, categoriaSelecionada, familia, intensidade)
  );

  const filtradosFemininos = produtos.filter(produto =>
    produto.categoria === "feminino" &&
    produtoCombinaComFiltro(produto, busca, categoriaSelecionada, familia, intensidade)
  );

  renderProdutos(filtradosMasculinos, masculinosContainer);
  renderProdutos(filtradosFemininos, femininosContainer);

  if (rolarAteCatalogo) scrollToProdutos();
}

// #PRODUTO_COMBINA_COM_FILTRO
function produtoCombinaComFiltro(produto, busca, categoriaSelecionada, familiaSelecionada, intensidadeSelecionada) {
  const detalhes = montarDetalhesProduto(produto);
  const camposBusca = [
    produto.nome,
    produto.categoria,
    extrairMarcaProduto(produto.nome),
    detalhes.familia,
    detalhes.notas,
    detalhes.intensidade,
    detalhes.ocasiao
  ].map(normalizarTexto);

  const combinaBusca = !busca || camposBusca.some(campo => campo.includes(busca));
  const combinaCategoria = !categoriaSelecionada || produto.categoria === categoriaSelecionada;
  const combinaFamilia = !familiaSelecionada || normalizarTexto(detalhes.familia) === familiaSelecionada;
  const combinaIntensidade = !intensidadeSelecionada || normalizarTexto(detalhes.intensidade) === intensidadeSelecionada;

  return combinaBusca && combinaCategoria && combinaFamilia && combinaIntensidade;
}

// #NORMALIZAR_TEXTO
function normalizarTexto(texto) {
  return texto
    .toString()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

// #SCROLL_TO_PRODUTOS
function scrollToProdutos() {
  const catalogo = document.querySelector(".catalogo");

  if (catalogo) {
    catalogo.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

// #ALTERNAR_MENU_MOBILE
function alternarMenuMobile(botao) {
  const menu = document.getElementById("menuPrincipal");
  if (!menu) return;

  const aberto = menu.classList.toggle("menu-aberto");
  botao.setAttribute("aria-expanded", String(aberto));
  botao.setAttribute("aria-label", aberto ? "Fechar menu" : "Abrir menu");

  const icone = botao.querySelector("i");
  if (icone) {
    icone.classList.toggle("fa-bars", !aberto);
    icone.classList.toggle("fa-xmark", aberto);
  }
}

if (typeof window !== "undefined") {
  Object.assign(window, {
    mostrarCategoria,
    abrirCatalogo,
    pesquisarProdutos,
    scrollToProdutos,
    scrollToClubeOfertas,
    comprar,
    verMaisProduto,
    fecharDetalhesProduto,
    selecionarImagemModal,
    navegarImagemModal,
    selecionarVolumeModal,
    alterarQuantidadeModal,
    comprarViaWhatsAppProduto,
    finalizarCarregamentoImagemModal,
    marcarImagemModalIndisponivel,
    marcarImagemProdutoIndisponivel,
    abrirCheckout,
    fecharCheckout,
    enviarCheckout,
    atualizarVolumeCheckout,
    atualizarTotalCheckout,
    mascararTelefoneLoja,
    alternarMenuMobile,
    lerCarrinho,
    salvarCarrinho,
    adicionarAoCarrinho,
    atualizarContadoresCarrinho
  });
}
