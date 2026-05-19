const produtosPadrao = [
  { nome: "Dior Sauvage", categoria: "masculino", img: "img/produtos/masculinos/dior-sauvage.png", preco5: "59,99", preco10: "109,99" },
  { nome: "Dior Homme Sport", categoria: "masculino", img: "img/produtos/masculinos/dior_homme_sport.png", preco5: "66,99", preco10: "105,00" },
  { nome: "Bleu de Chanel", categoria: "masculino", img: "img/produtos/masculinos/bleu_de_chanel.png", preco5: "80,99", preco10: "139,99" },
  { nome: "Allure Homme Sport", categoria: "masculino", img: "img/produtos/masculinos/allure_homme_sport.png", preco5: "80,99", preco10: "139,99" },
  { nome: "Club de Nuit Intense", categoria: "masculino", img: "img/produtos/masculinos/club_de_nuit_intense.png", preco5: "44,99", preco10: "54,99" },
  { nome: "Asad Lattafa", categoria: "masculino", img: "img/produtos/masculinos/asad_lattafa.png", preco5: "44,99", preco10: "69,99" },
  { nome: "212 VIP Black", categoria: "masculino", img: "img/produtos/masculinos/212_vip_black.png", preco5: "46,99", preco10: "75,99" },
  { nome: "212 Men", categoria: "masculino", img: "img/produtos/masculinos/212_men.png", preco5: "44,99", preco10: "69,99" },
  { nome: "Encre Noire", categoria: "masculino", img: "img/produtos/masculinos/Encre_Noire.png", preco5: "54,99", preco10: "99,99" },
  { nome: "Ferrari Black", categoria: "masculino", img: "img/produtos/masculinos/Ferrari_Black.png", preco5: "34,99", preco10: "49,99" },
  { nome: "Le Male Elixir", categoria: "masculino", img: "img/produtos/masculinos/le_male_elixir.png", preco5: "54,99", preco10: "114,99" },
  { nome: "Le Male Le Parfum", categoria: "masculino", img: "img/produtos/masculinos/le_male_le_parfum.png", preco5: "44,99", preco10: "69,99" },
  { nome: "One Million", categoria: "masculino", img: "img/produtos/masculinos/one_million_paco_rabanne.png", preco5: "46,99", preco10: "74,99" },
  { nome: "Phantom", categoria: "masculino", img: "img/produtos/masculinos/Phantom_Paco_Rabanne.png", preco5: "49,99", preco10: "84,99" },
  { nome: "Invictus Victory", categoria: "masculino", img: "img/produtos/masculinos/Invictus_Victory.png", preco5: "54,99", preco10: "94,99" },
  { nome: "Invictus Victory Elixir", categoria: "masculino", img: "img/produtos/masculinos/Invictus_Victory_Elixir.png", preco5: "54,99", preco10: "94,99" },
  { nome: "Silver Scent", categoria: "masculino", img: "img/produtos/masculinos/Silver_Scence.png", preco5: "44,99", preco10: "69,99" },
  { nome: "Versace Eros", categoria: "masculino", img: "img/produtos/masculinos/versace_eros.png", preco5: "69,99", preco10: "99,99" },
  { nome: "L'eau d'Issey Miyake", categoria: "masculino", img: "img/produtos/masculinos/homme_Issey_miyake.png", preco5: "44,99", preco10: "69,99" },
  { nome: "Hugo Boss Night", categoria: "masculino", img: "img/produtos/masculinos/Hugo_Boss_Bottled_Night.png", preco5: "59,99", preco10: "69,99" },
  { nome: "Scandal Masculino EDT", categoria: "masculino", img: "img/produtos/masculinos/scandal_pour homme.png", preco5: "59,99", preco10: "109,99" },
  { nome: "Good Girl", categoria: "feminino", img: "img/produtos/femininos/Good_Girl.jpg", preco5: "54,99", preco10: "94,99" },
  { nome: "Scandal Feminino", categoria: "feminino", img: "img/produtos/femininos/scandal.jpg", preco5: "59,99", preco10: "109,99" },
  { nome: "Libre Yves Saint", categoria: "feminino", img: "img/produtos/femininos/libre_yves_saint_laurent.png", preco5: "69,99", preco10: "129,99" },
  { nome: "Yara Rosa", categoria: "feminino", img: "img/produtos/femininos/yara_rosa.png", preco5: "54,99", preco10: "69,99" },
  { nome: "La Vie Est Belle", categoria: "feminino", img: "img/produtos/femininos/la_vie_est_belle.png", preco5: "54,99", preco10: "89,99" },
  { nome: "212 VIP Rosé", categoria: "feminino", img: "img/produtos/femininos/212_vip_rose.png", preco5: "54,99", preco10: "89,99" },
  { nome: "Lady Million", categoria: "feminino", img: "img/produtos/femininos/lady_million.png", preco5: "59,99", preco10: "109,99" },
  { nome: "Issey Miyake Fem", categoria: "feminino", img: "img/produtos/femininos/issey_miyake_fem.png", preco5: "54,99", preco10: "99,99" },
  { nome: "Afeef Lattafa", categoria: "feminino", img: "img/produtos/femininos/afeef_lattafa.png", preco5: "44,99", preco10: "69,99" },
  { nome: "Royal Amber Rouge", categoria: "feminino", img: "img/produtos/femininos/royal_amber_rougue.png", preco5: "59,99", preco10: "109,99" },
  { nome: "My Way", categoria: "feminino", img: "img/produtos/femininos/my_way.png", preco5: "59,99", preco10: "109,99" },
  { nome: "Idôle", categoria: "feminino", img: "img/produtos/femininos/Idole.png", preco5: "59,99", preco10: "109,99" }
];

const produtosDestaquePadrao = ["Dior Sauvage", "La Vie Est Belle", "Versace Eros", "Yara Rosa"];
const produtos = produtosPadrao.map(normalizarProdutoLoja);
window.decantsProdutos = produtos;
window.decantsProdutosPadrao = produtosPadrao.map(normalizarProdutoLoja);
let checkoutProdutoAtual = null;

const notasPorProduto = {
  "Dior Sauvage": "bergamota, pimenta, lavanda, ambroxan e madeiras",
  "Dior Homme Sport": "limão, bergamota, gengibre, elemi e madeiras",
  "Bleu de Chanel": "cítricos, hortelã, gengibre, incenso, âmbar e sândalo",
  "Allure Homme Sport": "laranja, notas marinhas, pimenta, almíscar e fava tonka",
  "Club de Nuit Intense": "limão, abacaxi, bergamota, rosa, bétula, almíscar e âmbar",
  "Asad Lattafa": "pimenta preta, tabaco, baunilha, âmbar, patchouli e madeiras",
  "212 VIP Black": "absinto, lavanda, anis, baunilha e almíscar",
  "212 Men": "folhas verdes, especiarias, lavanda, sândalo e almíscar",
  "Encre Noire": "cipreste, vetiver, cashmere, almíscar e madeira",
  "Ferrari Black": "maçã, ameixa, bergamota, canela, baunilha e cedro",
  "Le Male Elixir": "lavanda, hortelã, baunilha, mel, tabaco e fava tonka",
  "Le Male Le Parfum": "cardamomo, lavanda, íris, baunilha e madeiras",
  "One Million": "toranja, canela, couro, âmbar, patchouli e especiarias",
  "Phantom": "lavanda, limão, maçã, patchouli, baunilha e vetiver",
  "Invictus Victory": "limão, pimenta rosa, lavanda, baunilha, fava tonka e âmbar",
  "Invictus Victory Elixir": "lavanda, cardamomo, pimenta, incenso, baunilha e fava tonka",
  "Silver Scent": "flor de laranjeira, limão, lavanda, cardamomo, fava tonka e âmbar",
  "Versace Eros": "hortelã, maçã verde, limão, fava tonka, baunilha e cedro",
  "L'eau d'Issey Miyake": "yuzu, bergamota, noz-moscada, lírio, tabaco e sândalo",
  "Hugo Boss Night": "lavanda, bétula, violeta, cardamomo e madeiras",
  "Scandal Masculino EDT": "sálvia, mandarina, caramelo, fava tonka, vetiver e cedro",
  "Good Girl": "amêndoa, café, jasmim, tuberosa, cacau, fava tonka e baunilha",
  "Scandal Feminino": "laranja sanguínea, mel, gardênia, patchouli e caramelo",
  "Libre Yves Saint": "lavanda, mandarina, flor de laranjeira, jasmim, baunilha e âmbar gris",
  "Yara Rosa": "orquídea, frutas tropicais, baunilha, almíscar e notas doces",
  "La Vie Est Belle": "íris, pera, cassis, jasmim, flor de laranjeira, patchouli e pralinê",
  "212 VIP Rosé": "champagne rosé, pêssego, flor de pêssego, almíscar e âmbar",
  "Lady Million": "framboesa, neroli, flor de laranjeira, jasmim, mel e patchouli",
  "Issey Miyake Fem": "lótus, frésia, rosa, lírio, peônia, madeiras e almíscar",
  "Afeef Lattafa": "bergamota, pimenta rosa, jasmim, tuberosa, baunilha e sândalo",
  "Royal Amber Rouge": "açafrão, jasmim, âmbar, madeiras, resinas e almíscar",
  "My Way": "bergamota, flor de laranjeira, tuberosa, jasmim, baunilha e cedro",
  "Idôle": "bergamota, pera, rosa, jasmim, almíscar branco e baunilha"
};

const marcasPorProduto = {
  "Dior Sauvage": "Dior",
  "Dior Homme Sport": "Dior",
  "Bleu de Chanel": "Chanel",
  "Allure Homme Sport": "Chanel",
  "Club de Nuit Intense": "Armaf",
  "Asad Lattafa": "Lattafa",
  "212 VIP Black": "Carolina Herrera",
  "212 Men": "Carolina Herrera",
  "Encre Noire": "Lalique",
  "Ferrari Black": "Ferrari",
  "Le Male Elixir": "Jean Paul Gaultier",
  "Le Male Le Parfum": "Jean Paul Gaultier",
  "One Million": "Paco Rabanne",
  "Phantom": "Paco Rabanne",
  "Invictus Victory": "Paco Rabanne",
  "Invictus Victory Elixir": "Paco Rabanne",
  "Silver Scent": "Jacques Bogart",
  "Versace Eros": "Versace",
  "L'eau d'Issey Miyake": "Issey Miyake",
  "Hugo Boss Night": "Hugo Boss",
  "Scandal Masculino EDT": "Jean Paul Gaultier",
  "Good Girl": "Carolina Herrera",
  "Scandal Feminino": "Jean Paul Gaultier",
  "Libre Yves Saint": "Yves Saint Laurent",
  "Yara Rosa": "Lattafa",
  "La Vie Est Belle": "Lancôme",
  "212 VIP Rosé": "Carolina Herrera",
  "Lady Million": "Paco Rabanne",
  "Issey Miyake Fem": "Issey Miyake",
  "Afeef Lattafa": "Lattafa",
  "Royal Amber Rouge": "Lattafa",
  "My Way": "Giorgio Armani",
  "Idôle": "Lancôme"
};

const logosPorMarca = {
  "Dior": "img/marcas/dior.png",
  "Chanel": "img/marcas/chanel.png",
  "Armaf": "img/marcas/armaf.png",
  "Lattafa": "img/marcas/lattafa.png",
  "Carolina Herrera": "img/marcas/carolina-herrera.png",
  "Lalique": "img/marcas/lalique.png",
  "Ferrari": "img/marcas/ferrari.png",
  "Jean Paul Gaultier": "img/marcas/jean-paul-gaultier.png",
  "Paco Rabanne": "img/marcas/paco-rabanne.png",
  "Jacques Bogart": "img/marcas/jacques-bogart.png",
  "Versace": "img/marcas/versace.png",
  "Issey Miyake": "img/marcas/issey-miyake.png",
  "Hugo Boss": "img/marcas/hugo-boss.png",
  "Yves Saint Laurent": "img/marcas/yves-saint-laurent.png",
  "Lancôme": "img/marcas/lancome.png",
  "Giorgio Armani": "img/marcas/giorgio-armani.png",
  "Decant's": "img/marcas/decants.png"
};

const imagensDestaquePorProduto = {
  "dior sauvage": "img/highlights/masculine/dior_sauvage.png",
  "dior homme sport": "img/highlights/masculine/dior_homme_sport.png",
  "bleu de chanel": "img/highlights/masculine/bleu_de_chanel.png",
  "allure homme sport": "img/highlights/masculine/allure_homme_sport.png",
  "club de nuit intense": "img/highlights/masculine/club_de_nuit_intense.png",
  "asad lattafa": "img/highlights/masculine/asad_lattafa.png",
  "212 vip black": "img/highlights/masculine/212_vip_black.png",
  "212 men": "img/highlights/masculine/212_men.png",
  "encre noire": "img/highlights/masculine/Encre_Noire.png",
  "ferrari black": "img/highlights/masculine/ferrari_black.png",
  "le male elixir": "img/highlights/masculine/le_male_elixir.png",
  "le male le parfum": "img/highlights/masculine/le_male_le_parfum.png",
  "one million": "img/highlights/masculine/one_million.png",
  "phantom": "img/highlights/masculine/Phantom_Paco_Rabanne.png",
  "invictus victory": "img/highlights/masculine/Invictus_Victory.png",
  "invictus victory elixir": "img/highlights/masculine/Invictus_Victory_Elixir.png",
  "silver scent": "img/highlights/masculine/Silver_Scence.png",
  "versace eros": "img/highlights/masculine/versace_eros.png",
  "l'eau d'issey miyake": "img/highlights/masculine/issey_miyake.png",
  "hugo boss night": "img/highlights/masculine/Hugo_Boss_Bottled_Night.png",
  "scandal masculino edt": "img/highlights/masculine/scandal_pour homme.png",
  "good girl": "img/highlights/feminine/Good_Girl.png",
  "scandal feminino": "img/highlights/feminine/scandal.png",
  "libre yves saint": "img/highlights/feminine/libre_yves_saint.png",
  "yara rosa": "img/highlights/feminine/yara_rosa.png",
  "la vie est belle": "img/highlights/feminine/la_vie_est_belle.png",
  "212 vip rose": "img/highlights/feminine/212_vip_rose.png",
  "lady million": "img/highlights/feminine/lady_million.png",
  "issey miyake fem": "img/highlights/feminine/issey_miyake_fem.png",
  "afeef lattafa": "img/highlights/feminine/afeef_lattafa.png",
  "royal amber rouge": "img/highlights/feminine/royal_amber_rougue.png",
  "my way": "img/highlights/feminine/my_way.png",
  "idole": "img/highlights/feminine/idole.png"
};

const imagensModalPorProduto = {
  "dior sauvage": [
    "img/modal/masculinos/dior_sauvage1.png",
    "img/modal/masculinos/dior_sauvage2.png",
    "img/modal/masculinos/dior_sauvage3.png",
    "img/modal/masculinos/dior_sauvage4.png"
  ]
};

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
    img: produto.img || ""
  };

  if (!("destaque" in produto)) {
    produtoCompleto.destaque = produtosDestaquePadrao.includes(produtoCompleto.nome);
  }

  return produtoCompleto;
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

  if (produto.promocao && precoFinal !== precoBase) {
    return `<p class="preco-promocional"><span>${label} <s>R$ ${precoBase}</s></span><strong>R$ ${precoFinal}</strong></p>`;
  }

  return `<p>${label} R$ ${precoBase}</p>`;
}

// #PRODUTO_DISPONIVEL
function produtoDisponivel(produto) {
  return Number(produto.estoque) > 0;
}



const masculinosContainer = document.getElementById("masculinosContainer");
const femininosContainer = document.getElementById("femininosContainer");
const searchInput = document.getElementById("searchInput");
const categoriaFiltro = document.getElementById("categoriaFiltro");
const generoFiltro = document.getElementById("generoFiltro");
const familiaFiltro = document.getElementById("familiaFiltro");
const intensidadeFiltro = document.getElementById("intensidadeFiltro");
const catalogoPagina = document.getElementById("catalogoPagina");
const catalogoTituloCategoria = document.getElementById("catalogoTituloCategoria");
const tabMasculino = document.getElementById("tabMasculino");
const tabFeminino = document.getElementById("tabFeminino");
const carouselPremium = document.querySelector(".carousel-premium");

if (masculinosContainer && femininosContainer) {
  preencherFiltrosAvancados();
  mostrarTodos();
}

if (catalogoPagina) {
  renderizarPaginaCatalogo();
}

if (carouselPremium) {
  iniciarCarouselDestaques();
}

carregarProdutosLoja();
exibirRetornoPagamento();

if (searchInput) {
  searchInput.addEventListener("input", () => pesquisarProdutos(false));
  searchInput.addEventListener("keydown", event => {
    if (event.key === "Enter") {
      event.preventDefault();
      pesquisarProdutos();
    }
  });
}

[categoriaFiltro, generoFiltro, familiaFiltro, intensidadeFiltro].forEach(filtro => {
  if (filtro) filtro.addEventListener("change", () => pesquisarProdutos(false));
});

document.addEventListener("keydown", event => {
  if (!event.target.classList?.contains("modal-volume-card")) return;
  if (!["Enter", " "].includes(event.key)) return;

  event.preventDefault();
  selecionarVolumeModal(event.target);
});

document.addEventListener("keydown", event => {
  if (event.key === "Escape") fecharDetalhesProduto();
});

// #PREENCHER_FILTROS_AVANCADOS
function preencherFiltrosAvancados() {
  preencherSelect(familiaFiltro, obterOpcoesDetalhes("familia"));
  preencherSelect(intensidadeFiltro, obterOpcoesDetalhes("intensidade"));
}

// #PREENCHER_SELECT
function preencherSelect(select, opcoes) {
  if (!select) return;

  opcoes.forEach(opcao => {
    const option = document.createElement("option");
    option.value = normalizarTexto(opcao);
    option.textContent = opcao;
    select.appendChild(option);
  });
}

// #OBTER_OPCOES_DETALHES
function obterOpcoesDetalhes(campo) {
  return [...new Set(produtos.map(produto => montarDetalhesProduto(produto)[campo]))].sort((a, b) =>
    a.localeCompare(b, "pt-BR")
  );
}

// #MOSTRAR_TODOS
function mostrarTodos() {
  renderProdutos(produtos.filter(produto => produto.categoria === "masculino"), masculinosContainer);
  renderProdutos(produtos.filter(produto => produto.categoria === "feminino"), femininosContainer);
}

// #ATUALIZAR_VITRINE
function atualizarVitrine() {
  if (familiaFiltro) {
    preencherSelectComOpcoes(familiaFiltro, obterOpcoesDetalhes("familia"));
  }

  if (intensidadeFiltro) {
    preencherSelectComOpcoes(intensidadeFiltro, obterOpcoesDetalhes("intensidade"));
  }

  if (masculinosContainer && femininosContainer) {
    pesquisarProdutos(false);
  }

  if (catalogoPagina) {
    renderizarPaginaCatalogo();
  }

  if (carouselPremium) {
    iniciarCarouselDestaques();
  }
}

// #PREENCHER_SELECT_COM_OPCOES
function preencherSelectComOpcoes(select, opcoes) {
  const valorAtual = select.value;
  const primeiraOpcao = select.options[0]?.cloneNode(true);
  select.innerHTML = "";
  if (primeiraOpcao) select.appendChild(primeiraOpcao);
  preencherSelect(select, opcoes);
  select.value = [...select.options].some(option => option.value === valorAtual) ? valorAtual : "";
}

// #MOSTRAR_CATEGORIA
function mostrarCategoria(tipo) {
  const filtrados = produtos.filter(produto => produto.categoria === tipo);

  if (tipo === "masculino") {
    renderProdutos(filtrados, masculinosContainer);
    masculinosContainer.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  if (tipo === "feminino") {
    renderProdutos(filtrados, femininosContainer);
    femininosContainer.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

// #ABRIR_CATALOGO
function abrirCatalogo(tipo) {
  window.location.href = `produtos.html?categoria=${tipo}`;
}

// #RENDER_PRODUTOS
function renderProdutos(lista, container) {
  if (!container) return;

  container.innerHTML = "";

  if (lista.length === 0) {
    container.innerHTML = `<p class="sem-resultados">Nenhum perfume encontrado.</p>`;
    return;
  }

  lista.forEach((produto, index) => {
    const semEstoque = !produtoDisponivel(produto);

    container.innerHTML += `
      <div class="card ${semEstoque ? "produto-esgotado" : ""}" style="--card-index: ${index};">
        <span class="card-brilho" aria-hidden="true"></span>
        <img src="${produto.img}" alt="${produto.nome}" loading="lazy">
        ${produto.promocao ? '<span class="tag-promocao">Promoção</span>' : ""}
        <h3>${produto.nome}</h3>
        ${renderizarPrecoCard(produto, 5)}
        ${renderizarPrecoCard(produto, 10)}
        <p class="estoque-card">${semEstoque ? "Produto esgotado" : `Estoque: ${produto.estoque}`}</p>

        <div class="acoes-card">
          <button class="btn-comprar" data-produto="${produto.nome}" onclick="comprar(this.dataset.produto)" ${semEstoque ? "disabled" : ""}>${semEstoque ? "ESGOTADO" : "COMPRAR"}</button>
          <button class="btn-ver-mais" data-produto="${produto.nome}" onclick="verMaisProduto(this.dataset.produto)">VER MAIS</button>
        </div>
      </div>
    `;
  });
}

// #RENDERIZAR_PAGINA_CATALOGO
function renderizarPaginaCatalogo() {
  const parametros = new URLSearchParams(window.location.search);
  const categoria = parametros.get("categoria") === "feminino" ? "feminino" : "masculino";
  const produtosCategoria = produtos.filter(produto => produto.categoria === categoria);

  document.title = `${categoria === "masculino" ? "Perfumes Masculinos" : "Perfumes Femininos"} | Decant's Perfumaria`;

  if (catalogoTituloCategoria) {
    catalogoTituloCategoria.textContent = categoria === "masculino" ? "MASCULINOS" : "FEMININOS";
  }

  if (tabMasculino) tabMasculino.classList.toggle("ativo", categoria === "masculino");
  if (tabFeminino) tabFeminino.classList.toggle("ativo", categoria === "feminino");

  catalogoPagina.innerHTML = produtosCategoria.map((produto, index) => `
    <article class="catalogo-card ${produtoDisponivel(produto) ? "" : "produto-esgotado"}" style="--card-index: ${index};">
      <div class="catalogo-card-imagem">
        <img src="${produto.img}" alt="${produto.nome}" loading="lazy">
      </div>
      ${produto.promocao ? '<span class="tag-promocao">Promoção</span>' : ""}
      <h3>${produto.nome}</h3>
      <div class="catalogo-precos">
        <span>5ml: R$ ${obterPrecoProduto(produto, 5)}</span>
        <span>10ml: R$ ${obterPrecoProduto(produto, 10)}</span>
      </div>
      <p class="estoque-card">${produtoDisponivel(produto) ? `Estoque: ${produto.estoque}` : "Produto esgotado"}</p>
      <div class="catalogo-acoes">
        <button class="btn-comprar" data-produto="${produto.nome}" onclick="comprar(this.dataset.produto)" ${produtoDisponivel(produto) ? "" : "disabled"}>${produtoDisponivel(produto) ? "COMPRAR" : "ESGOTADO"}</button>
        <button class="btn-ver-mais" data-produto="${produto.nome}" onclick="verMaisProduto(this.dataset.produto)">VER MAIS</button>
      </div>
    </article>
  `).join("");
}

// #INICIAR_CAROUSEL_DESTAQUES
function iniciarCarouselDestaques() {
  const destaques = produtos.filter(produto => produto.destaque).slice(0, 8);

  if (destaques.length) {
    carouselPremium.querySelectorAll(".carousel-slide").forEach(slide => slide.remove());

    const controles = carouselPremium.querySelector(".carousel-anterior");
    destaques.forEach((produto, index) => {
      const imagem = obterImagemDestaqueProduto(produto) || produto.img;
      const slide = document.createElement("div");
      slide.className = `carousel-slide ${index === 0 ? "ativo" : ""}`;
      slide.dataset.produto = produto.nome;
      slide.innerHTML = `
        <img src="${imagem}" alt="${produto.nome}">
        <div class="carousel-conteudo">
          <span class="selo-destaque">${produto.selo || (produto.promocao ? "Oferta" : "Destaque")}</span>
          ${produto.promocao ? '<strong class="selo-desconto">Promoção</strong>' : ""}
          <p class="carousel-kicker">${produto.chamada || (produto.categoria === "masculino" ? "Masculino selecionado" : "Feminino selecionado")}</p>
          <h2>${produto.nome.toUpperCase()}</h2>
          <p class="carousel-preco">R$ ${obterPrecoProduto(produto, 5)}</p>
          <div class="acoes-destaque">
            <button class="btn-comprar" data-produto="${produto.nome}" onclick="comprar(this.dataset.produto)" ${produtoDisponivel(produto) ? "" : "disabled"}>${produtoDisponivel(produto) ? "COMPRAR" : "ESGOTADO"}</button>
            <button class="btn-ver-mais" data-produto="${produto.nome}" onclick="verMaisProduto(this.dataset.produto)">VER MAIS</button>
          </div>
        </div>
      `;
      carouselPremium.insertBefore(slide, controles);
    });
  }

  const slides = [...carouselPremium.querySelectorAll(".carousel-slide")];
  const anterior = carouselPremium.querySelector(".carousel-anterior");
  const proximo = carouselPremium.querySelector(".carousel-proximo");
  const indicadores = carouselPremium.querySelector(".carousel-indicadores");
  let slideAtual = Math.max(0, slides.findIndex(slide => slide.classList.contains("ativo")));
  let autoplayId;

  if (!slides.length || !indicadores) return;

  indicadores.innerHTML = slides.map((slide, index) => `
    <button type="button" aria-label="Ir para destaque ${index + 1}" ${index === slideAtual ? 'class="ativo"' : ""}></button>
  `).join("");

  const botoesIndicadores = [...indicadores.querySelectorAll("button")];

  const mostrarSlide = novoIndice => {
    slideAtual = (novoIndice + slides.length) % slides.length;

    slides.forEach((slide, index) => {
      slide.classList.toggle("ativo", index === slideAtual);
    });

    botoesIndicadores.forEach((botao, index) => {
      botao.classList.toggle("ativo", index === slideAtual);
    });
  };

  const reiniciarAutoplay = () => {
    window.clearInterval(autoplayId);
    autoplayId = window.setInterval(() => mostrarSlide(slideAtual + 1), 5200);
  };

  anterior?.addEventListener("click", () => {
    mostrarSlide(slideAtual - 1);
    reiniciarAutoplay();
  });

  proximo?.addEventListener("click", () => {
    mostrarSlide(slideAtual + 1);
    reiniciarAutoplay();
  });

  botoesIndicadores.forEach((botao, index) => {
    botao.addEventListener("click", () => {
      mostrarSlide(index);
      reiniciarAutoplay();
    });
  });

  carouselPremium.addEventListener("mouseenter", () => window.clearInterval(autoplayId));
  carouselPremium.addEventListener("mouseleave", reiniciarAutoplay);

  mostrarSlide(slideAtual);
  reiniciarAutoplay();
}

// #VER_MAIS_PRODUTO
function verMaisProduto(nomeProduto) {
  const produto = produtos.find(item => item.nome === nomeProduto);
  if (!produto) return;

  const detalhes = montarDetalhesProduto(produto);
  const acordes = montarAcordesProduto(detalhes.notas, detalhes.familia);
  const imagemDestaque = obterImagemDestaqueProduto(produto);
  const imagensGaleria = montarGaleriaModalProduto(produto, imagemDestaque);
  const marcaProduto = extrairMarcaProduto(produto.nome);
  const logoMarca = obterLogoMarca(marcaProduto);
  const modalExistente = document.querySelector(".modal-produto");
  const semEstoque = !produtoDisponivel(produto);
  const preco5 = obterPrecoProduto(produto, 5);
  const preco10 = obterPrecoProduto(produto, 10);

  if (modalExistente) modalExistente.remove();
  document.body.classList.add("modal-aberto");

  document.body.insertAdjacentHTML("beforeend", `
    <div class="modal-produto modal-produto-premium" role="dialog" aria-modal="true" aria-labelledby="modalProdutoTitulo" onclick="fecharDetalhesProduto(event)">
      <div class="modal-conteudo modal-conteudo-premium">
        <button class="modal-fechar modal-fechar-premium" type="button" aria-label="Fechar" onclick="fecharDetalhesProduto()">
          <span aria-hidden="true">&times;</span>
        </button>

        <div class="modal-layout-premium">
          ${renderizarGaleriaModal(produto, imagensGaleria)}
          ${renderizarInfoModal(produto, detalhes, acordes, marcaProduto, logoMarca, preco5, preco10)}
        </div>

        <div class="modal-compra-premium">
          <div class="modal-preco-final">
            <span>A partir de</span>
            <strong id="modalPrecoSelecionado">R$ ${preco5}</strong>
          </div>

          <div class="modal-quantidade" aria-label="Quantidade">
            <button type="button" aria-label="Diminuir quantidade" onclick="alterarQuantidadeModal(-1)">-</button>
            <strong id="modalQuantidade">1</strong>
            <button type="button" aria-label="Aumentar quantidade" onclick="alterarQuantidadeModal(1)">+</button>
          </div>

          <button class="modal-btn-whatsapp" type="button" data-produto="${produto.nome}" onclick="comprar(this.dataset.produto)" ${semEstoque ? "disabled" : ""}>
            <i class="fa-brands fa-whatsapp" aria-hidden="true"></i>
            Comprar via WhatsApp
          </button>

          <button class="modal-btn-principal" type="button" data-produto="${produto.nome}" onclick="comprar(this.dataset.produto)" ${semEstoque ? "disabled" : ""}>
            <i class="fa-solid fa-bag-shopping" aria-hidden="true"></i>
            ${semEstoque ? "Produto esgotado" : "Adicionar ao carrinho"}
          </button>
        </div>

        <div class="modal-beneficios-premium" aria-label="Benefícios da compra">
          <span><i class="fa-solid fa-lock" aria-hidden="true"></i> Compra segura</span>
          <span><i class="fa-solid fa-truck-fast" aria-hidden="true"></i> Envio rápido</span>
          <span><i class="fa-regular fa-circle-check" aria-hidden="true"></i> Satisfação garantida</span>
        </div>
      </div>
    </div>
  `);

  ajustarFormatoImagemModal();
  atualizarResumoModal();
  const imagem = document.querySelector(".modal-galeria-imagem img");
  if (imagem && imagem.complete && imagem.naturalWidth) finalizarCarregamentoImagemModal(imagem);
}

// #MONTAR_GALERIA_MODAL_PRODUTO
function montarGaleriaModalProduto(produto, imagemDestaque) {
  const imagensModal = imagensModalPorProduto[normalizarTexto(produto.nome)] || [];

  if (imagensModal.length) {
    return [
      ...imagensModal
    ].filter((imagem, index, lista) => imagem && lista.indexOf(imagem) === index);
  }

  return [
    imagemDestaque || produto.img,
    produto.img
  ].filter((imagem, index, lista) => imagem && lista.indexOf(imagem) === index);
}

// #RENDERIZAR_GALERIA_MODAL
function renderizarGaleriaModal(produto, imagens) {
  const categoria = produto.categoria === "masculino" ? "Masculino" : "Feminino";
  const imagemPrincipal = imagens[0] || produto.img;
  const temImagemCinematica = imagemPrincipal.includes("img/modal/");

  return `
    <section class="modal-galeria-premium ${temImagemCinematica ? "modal-galeria-cinematica" : ""}" aria-label="Galeria do produto">
      <div class="modal-galeria-imagem modal-imagem-carregando">
        <span class="modal-skeleton" aria-hidden="true"></span>
        <span class="modal-selo-categoria">${categoria}</span>
        <button class="modal-favorito" type="button" aria-label="Favoritar perfume">
          <i class="fa-regular fa-heart" aria-hidden="true"></i>
        </button>
        <img src="${imagemPrincipal}" alt="${produto.nome}" onload="finalizarCarregamentoImagemModal(this)" onerror="marcarImagemModalIndisponivel(this)">
      </div>

      <div class="modal-thumbs" aria-label="Miniaturas">
        ${imagens.map((imagem, index) => `
          <button class="modal-thumb ${index === 0 ? "ativo" : ""} ${imagem.includes("img/modal/") ? "modal-thumb-cinematica" : ""}" type="button" aria-label="Ver imagem ${index + 1}" onclick="selecionarImagemModal(this)" data-src="${imagem}">
            <img src="${imagem}" alt="${produto.nome} miniatura ${index + 1}" loading="lazy">
          </button>
        `).join("")}
      </div>
    </section>
  `;
}

// #RENDERIZAR_INFO_MODAL
function renderizarInfoModal(produto, detalhes, acordes, marcaProduto, logoMarca, preco5, preco10) {
  const semEstoque = !produtoDisponivel(produto);

  return `
    <section class="modal-info-premium">
      <div class="modal-marca-linha">
        <span>${marcaProduto}</span>
        <div class="modal-logo-mini">
          <img src="${logoMarca}" alt="Logo ${marcaProduto}" loading="lazy" onerror="this.hidden=true; this.nextElementSibling.hidden=false;">
          <strong hidden>${marcaProduto}</strong>
        </div>
      </div>

      <h2 id="modalProdutoTitulo">${produto.nome}</h2>

      <div class="modal-rating" aria-label="Avaliação">
        <span aria-hidden="true">★★★★★</span>
        <small>Seleção premium</small>
      </div>

      <p class="modal-descricao">Uma leitura elegante da fragrancia, pensada para quem quer experimentar antes de escolher o frasco ideal.</p>

      <div class="modal-divisor"></div>

      <div class="modal-secao">
        <h3>Escolha o tamanho</h3>
        <div class="modal-opcoes-volume" role="radiogroup" aria-label="Tamanhos disponíveis">
          ${renderizarVolumeModal(5, preco5, true, semEstoque)}
          ${renderizarVolumeModal(10, preco10, false, semEstoque)}
        </div>
      </div>

      <div class="modal-secao">
        <h3>Principais acordes</h3>
        <div class="modal-acordes-premium">
          ${acordes.map(acorde => `<span style="--cor-chip: ${acorde.cor};">${acorde.nome}</span>`).join("")}
        </div>
      </div>

      <div class="modal-atributos-premium">
        <article>
          <i class="fa-regular fa-clock" aria-hidden="true"></i>
          <span>Fixação</span>
          <strong>${detalhes.intensidade}</strong>
        </article>
        <article>
          <i class="fa-regular fa-sun" aria-hidden="true"></i>
          <span>Ocasião</span>
          <strong>${detalhes.ocasiao.split(",")[0]}</strong>
        </article>
        <article>
          <i class="fa-solid fa-wand-magic-sparkles" aria-hidden="true"></i>
          <span>Familia</span>
          <strong>${detalhes.familia}</strong>
        </article>
      </div>

      <p class="modal-notas"><strong>Notas:</strong> ${detalhes.notas}</p>
    </section>
  `;
}

// #RENDERIZAR_VOLUME_MODAL
function renderizarVolumeModal(volume, preco, ativo, semEstoque) {
  const valorMl = precoTextoParaNumero(preco) / volume;

  return `
    <button class="modal-volume-card ${ativo ? "ativo" : ""}" type="button" role="radio" aria-checked="${ativo}" data-volume="${volume}" data-preco="${preco}" onclick="selecionarVolumeModal(this)" ${semEstoque ? "disabled" : ""}>
      <span>${volume} ml</span>
      <strong>R$ ${preco}</strong>
      <small>R$ ${formatarMoedaLoja(valorMl)} / ml</small>
    </button>
  `;
}

// #FINALIZAR_CARREGAMENTO_IMAGEM_MODAL
function finalizarCarregamentoImagemModal(imagem) {
  const wrapper = imagem.closest(".modal-imagem-destaque, .modal-galeria-imagem");
  if (!wrapper) return;

  wrapper.classList.remove("modal-imagem-carregando", "modal-imagem-falhou");
}

// #MARCAR_IMAGEM_MODAL_INDISPONIVEL
function marcarImagemModalIndisponivel(imagem) {
  const wrapper = imagem.closest(".modal-imagem-destaque, .modal-galeria-imagem");
  if (!wrapper) return;

  wrapper.classList.remove("modal-imagem-carregando");
  wrapper.classList.add("modal-imagem-falhou");
}

// #SELECIONAR_VOLUME_MODAL
function selecionarVolumeModal(elemento) {
  const grupo = elemento.closest(".modal-opcoes-volume");
  if (!grupo) return;

  grupo.querySelectorAll(".modal-volume-card").forEach(card => {
    card.classList.remove("ativo");
    card.setAttribute("aria-checked", "false");
  });
  elemento.classList.add("ativo");
  elemento.setAttribute("aria-checked", "true");
  atualizarResumoModal();
}

// #SELECIONAR_IMAGEM_MODAL
function selecionarImagemModal(botao) {
  const modal = botao.closest(".modal-conteudo-premium");
  const galeria = botao.closest(".modal-galeria-premium");
  const imagemPrincipal = modal?.querySelector(".modal-galeria-imagem img");
  const imagemArea = modal?.querySelector(".modal-galeria-imagem");
  const novaImagem = botao.dataset.src;

  if (!imagemPrincipal || !imagemArea || !novaImagem || imagemPrincipal.getAttribute("src") === novaImagem) return;

  modal.querySelectorAll(".modal-thumb").forEach(thumb => thumb.classList.remove("ativo"));
  botao.classList.add("ativo");
  galeria?.classList.toggle("modal-galeria-cinematica", novaImagem.includes("img/modal/"));
  imagemArea.classList.add("modal-imagem-carregando");
  imagemPrincipal.setAttribute("src", novaImagem);
}

// #ALTERAR_QUANTIDADE_MODAL
function alterarQuantidadeModal(delta) {
  const quantidadeElemento = document.getElementById("modalQuantidade");
  if (!quantidadeElemento) return;

  const atual = Number(quantidadeElemento.textContent || 1);
  quantidadeElemento.textContent = Math.max(1, Math.min(20, atual + delta));
  atualizarResumoModal();
}

// #ATUALIZAR_RESUMO_MODAL
function atualizarResumoModal() {
  const ativo = document.querySelector(".modal-volume-card.ativo");
  const precoElemento = document.getElementById("modalPrecoSelecionado");
  if (!ativo || !precoElemento) return;

  precoElemento.textContent = `R$ ${ativo.dataset.preco}`;
}
// #OBTER_IMAGEM_DESTAQUE_PRODUTO
function obterImagemDestaqueProduto(produto) {
  return imagensDestaquePorProduto[normalizarTexto(produto.nome)] || "";
}

// #OBTER_LOGO_MARCA
function obterLogoMarca(marca) {
  return logosPorMarca[marca] || logosPorMarca["Decant's"];
}

// #AJUSTAR_FORMATO_IMAGEM_MODAL
function ajustarFormatoImagemModal() {
  const modal = document.querySelector(".modal-conteudo");
  const imagem = modal ? modal.querySelector(".modal-galeria-imagem img, .modal-imagem-destaque img") : null;

  if (!modal || !imagem) return;

  const aplicarFormato = () => {
    const proporcao = imagem.naturalWidth / imagem.naturalHeight;
    const formato = proporcao > 1.18 ? "paisagem" : proporcao < 0.86 ? "retrato" : "quadrada";

    modal.classList.remove("modal-imagem-paisagem", "modal-imagem-retrato", "modal-imagem-quadrada");
    modal.classList.add(`modal-imagem-${formato}`);
    modal.style.setProperty("--imagem-proporcao", proporcao.toFixed(3));
  };

  if (imagem.complete && imagem.naturalWidth) {
    aplicarFormato();
  } else {
    imagem.addEventListener("load", aplicarFormato, { once: true });
  }
}

// #MONTAR_DETALHES_PRODUTO
function montarDetalhesProduto(produto) {
  const masculino = produto.categoria === "masculino";
  const nome = normalizarTexto(produto.nome);

  let familia = masculino ? "Amadeirado aromático" : "Floral elegante";
  let intensidade = "Média";
  let ocasiao = masculino ? "Dia a dia, encontros e ocasiões especiais" : "Dia a dia, encontros e eventos";

  if (nome.includes("elixir") || nome.includes("victory") || nome.includes("million") || nome.includes("good girl") || nome.includes("scandal")) {
    intensidade = "Alta";
    ocasiao = "Noite, eventos e momentos marcantes";
  }

  if (nome.includes("sport") || nome.includes("issey") || nome.includes("my way")) {
    familia = masculino ? "Cítrico aromático" : "Floral fresco";
    intensidade = "Média";
    ocasiao = "Dia, trabalho e clima quente";
  }

  if (nome.includes("lattafa") || nome.includes("amber") || nome.includes("yara")) {
    familia = "Oriental adocicado";
  }

  return {
    familia,
    notas: notasPorProduto[produto.nome] || "notas cítricas, florais, amadeiradas e almiscaradas",
    intensidade,
    ocasiao
  };
}

// #MONTAR_ACORDES_PRODUTO
function montarAcordesProduto(notas, familia) {
  const texto = normalizarTexto(`${notas} ${familia}`);
  const regras = [
    { nome: "cítrico", cor: "#f5ef3b", termos: ["bergamota", "limao", "laranja", "toranja", "mandarina", "yuzu", "citricos"] },
    { nome: "aromático", cor: "#3a8c7e", termos: ["lavanda", "hortela", "anis", "absinto", "alecrim", "aromatico"] },
    { nome: "amadeirado", cor: "#7a4920", termos: ["madeira", "madeiras", "cedro", "sandal", "vetiver", "cashmere", "betula", "cipreste"] },
    { nome: "floral", cor: "#d783a8", termos: ["rosa", "jasmim", "tuberosa", "lirio", "peonia", "gardenia", "flor", "floral", "orquidea", "fresia", "lotus"] },
    { nome: "âmbarado", cor: "#8e4519", termos: ["ambar", "amber", "resinas"] },
    { nome: "doce", cor: "#c27a45", termos: ["baunilha", "mel", "caramelo", "praline", "chocolate", "cacau", "doce"] },
    { nome: "especiado", cor: "#78a436", termos: ["pimenta", "cardamomo", "canela", "noz", "acafrao", "especiarias"] },
    { nome: "fresco", cor: "#6d9ea6", termos: ["marinhas", "fresco", "verde", "folhas", "champagne"] },
    { nome: "frutado", cor: "#d15265", termos: ["maca", "pera", "pessego", "framboesa", "ameixa", "abacaxi", "cassis", "frutas"] },
    { nome: "almiscarado", cor: "#9a9a90", termos: ["almiscar", "almiscarado"] },
    { nome: "couro", cor: "#5b351f", termos: ["couro", "tabaco", "cafe"] },
    { nome: "balsâmico", cor: "#73583e", termos: ["incenso", "tonka", "fava tonka", "balsamico"] }
  ];

  const encontrados = regras
    .map((regra, index) => {
      const ocorrencias = regra.termos.filter(termo => texto.includes(termo)).length;
      return {
        nome: regra.nome,
        cor: regra.cor,
        valor: Math.max(46, 100 - index * 7 + ocorrencias * 10),
        ocorrencias
      };
    })
    .filter(acorde => acorde.ocorrencias > 0)
    .sort((a, b) => b.valor - a.valor)
    .slice(0, 6);

  const base = encontrados.length ? encontrados : [
    { nome: "aromático", cor: "#3a8c7e", valor: 96 },
    { nome: "amadeirado", cor: "#7a4920", valor: 82 },
    { nome: "fresco", cor: "#6d9ea6", valor: 70 },
    { nome: "almiscarado", cor: "#9a9a90", valor: 62 }
  ];

  return base.map((acorde, index) => ({
    ...acorde,
    valor: Math.max(44, Math.min(100, acorde.valor - index * 2))
  }));
}

// #EXTRAIR_MARCA_PRODUTO
function extrairMarcaProduto(nomeProduto) {
  if (marcasPorProduto[nomeProduto]) return marcasPorProduto[nomeProduto];

  const nome = normalizarTexto(nomeProduto);
  const marcas = ["Dior", "Chanel", "Lattafa", "Paco Rabanne", "Carolina Herrera", "Yves Saint Laurent", "Lancôme", "Issey Miyake", "Ferrari", "Versace", "Hugo Boss", "Jean Paul Gaultier", "Armaf", "Lalique", "Jacques Bogart", "Giorgio Armani"];
  const marca = marcas.find(item => nome.includes(normalizarTexto(item)));

  if (marca) return marca;
  if (nome.includes("one million") || nome.includes("phantom") || nome.includes("invictus")) return "Paco Rabanne";
  if (nome.includes("good girl")) return "Carolina Herrera";
  if (nome.includes("libre")) return "Yves Saint Laurent";
  if (nome.includes("idole") || nome.includes("la vie est belle")) return "Lancôme";

  return "Decant's";
}

// #FECHAR_DETALHES_PRODUTO
function fecharDetalhesProduto(event) {
  if (event && !event.target.classList.contains("modal-produto")) return;

  const modal = document.querySelector(".modal-produto");
  if (!modal || modal.classList.contains("modal-saindo")) return;

  modal.classList.add("modal-saindo");
  document.body.classList.remove("modal-aberto");
  window.setTimeout(() => modal.remove(), 220);
}

// #COMPRAR
function comprar(nomeProduto) {
  abrirCheckout(nomeProduto);
}

// #ABRIR_CHECKOUT
function abrirCheckout(nomeProduto) {
  const produto = produtos.find(item => item.nome === nomeProduto);
  if (produto && !produtoDisponivel(produto)) return;

  checkoutProdutoAtual = produto;
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
          <img src="${produto.img}" alt="${produto.nome}">
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
            <input id="checkoutNome" autocomplete="name" required>
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
            Endereco de entrega
            <input id="checkoutEndereco" autocomplete="street-address" placeholder="Rua, numero, bairro, cidade">
          </label>
        </div>

        <div class="checkout-total">
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
  const total = precoTextoParaNumero(obterPrecoProduto(checkoutProdutoAtual, volume)) * quantidade;
  const totalElemento = document.getElementById("checkoutTotal");
  if (totalElemento) totalElemento.textContent = `R$ ${formatarMoedaLoja(total)}`;
}

// #ENVIAR_CHECKOUT
async function enviarCheckout(event, preferirWhatsApp = false) {
  event.preventDefault();
  if (!checkoutProdutoAtual) return;

  const mensagem = document.getElementById("checkoutMensagem");
  const botoes = document.querySelectorAll(".checkout-acoes button");
  mensagem.hidden = false;
  mensagem.classList.remove("erro", "sucesso");
  mensagem.textContent = "Criando pedido...";
  botoes.forEach(botao => botao.disabled = true);

  let volume = Number(document.querySelector("input[name='checkoutVolume']:checked")?.value || 5);
  let quantidade = Math.max(1, Number(document.getElementById("checkoutQuantidade").value || 1));

  try {
    const resposta = await apiLoja("/api/checkout", {
      method: "POST",
      body: JSON.stringify({
        customer: {
          name: document.getElementById("checkoutNome").value,
          phone: document.getElementById("checkoutTelefone").value,
          email: document.getElementById("checkoutEmail").value,
          address: document.getElementById("checkoutEndereco").value
        },
        items: [{
          productId: checkoutProdutoAtual.id || 0,
          productName: checkoutProdutoAtual.nome,
          volume,
          quantity: quantidade
        }]
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
      mensagem.textContent = resposta.paymentError
        ? `${resposta.paymentError}. Use o botao Enviar no WhatsApp para finalizar.`
        : "Mercado Pago ainda nao configurado. Use o botao Enviar no WhatsApp ou configure o token de pagamento.";
      return;
    }

    window.location.href = resposta.paymentUrl;
  } catch (error) {
    if (preferirWhatsApp) {
      window.open(montarWhatsAppLocalCheckout(volume, quantidade), "_blank", "noopener");
      mensagem.classList.add("sucesso");
      mensagem.textContent = "Nao consegui registrar no servidor, mas abri a mensagem do pedido no WhatsApp.";
      return;
    }

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

// #MONTAR_WHATS_APP_LOCAL_CHECKOUT
function montarWhatsAppLocalCheckout(volume, quantidade) {
  const numeroLoja = "558899641605";
  const preco = precoTextoParaNumero(obterPrecoProduto(checkoutProdutoAtual, volume));
  const total = formatarMoedaLoja(preco * quantidade);
  const linhas = [
    "Ola! Quero finalizar este pedido na Decant's Perfumaria.",
    `Cliente: ${document.getElementById("checkoutNome").value}`,
    `WhatsApp: ${document.getElementById("checkoutTelefone").value}`,
    `Item: ${quantidade}x ${checkoutProdutoAtual.nome} ${volume}ml`,
    `Total: R$ ${total}`,
    `Endereco: ${document.getElementById("checkoutEndereco").value || "A combinar"}`
  ];

  return `https://wa.me/${numeroLoja}?text=${encodeURIComponent(linhas.join("\n"))}`;
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

if (typeof window !== "undefined") {
  Object.assign(window, {
    mostrarCategoria,
    abrirCatalogo,
    pesquisarProdutos,
    scrollToProdutos,
    comprar,
    verMaisProduto,
    fecharDetalhesProduto,
    selecionarImagemModal,
    selecionarVolumeModal,
    alterarQuantidadeModal,
    finalizarCarregamentoImagemModal,
    marcarImagemModalIndisponivel,
    abrirCheckout,
    fecharCheckout,
    enviarCheckout,
    atualizarVolumeCheckout,
    atualizarTotalCheckout,
    mascararTelefoneLoja
  });
}
