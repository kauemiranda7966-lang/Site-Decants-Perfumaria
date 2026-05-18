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
  { nome: "212 VIP RosÃ©", categoria: "feminino", img: "img/produtos/femininos/212_vip_rose.png", preco5: "54,99", preco10: "89,99" },
  { nome: "Lady Million", categoria: "feminino", img: "img/produtos/femininos/lady_million.png", preco5: "59,99", preco10: "109,99" },
  { nome: "Issey Miyake Fem", categoria: "feminino", img: "img/produtos/femininos/issey_miyake_fem.png", preco5: "54,99", preco10: "99,99" },
  { nome: "Afeef Lattafa", categoria: "feminino", img: "img/produtos/femininos/afeef_lattafa.png", preco5: "44,99", preco10: "69,99" },
  { nome: "Royal Amber Rouge", categoria: "feminino", img: "img/produtos/femininos/royal_amber_rougue.png", preco5: "59,99", preco10: "109,99" },
  { nome: "My Way", categoria: "feminino", img: "img/produtos/femininos/my_way.png", preco5: "59,99", preco10: "109,99" },
  { nome: "IdÃ´le", categoria: "feminino", img: "img/produtos/femininos/Idole.png", preco5: "59,99", preco10: "109,99" }
];

const produtosDestaquePadrao = ["Dior Sauvage", "La Vie Est Belle", "Versace Eros", "Yara Rosa"];
const produtos = produtosPadrao.map(normalizarProdutoLoja);
window.decantsProdutos = produtos;
window.decantsProdutosPadrao = produtosPadrao.map(normalizarProdutoLoja);
let checkoutProdutoAtual = null;

const notasPorProduto = {
  "Dior Sauvage": "bergamota, pimenta, lavanda, ambroxan e madeiras",
  "Dior Homme Sport": "limÃ£o, bergamota, gengibre, elemi e madeiras",
  "Bleu de Chanel": "cÃ­tricos, hortelÃ£, gengibre, incenso, Ã¢mbar e sÃ¢ndalo",
  "Allure Homme Sport": "laranja, notas marinhas, pimenta, almÃ­scar e fava tonka",
  "Club de Nuit Intense": "limÃ£o, abacaxi, bergamota, rosa, bÃ©tula, almÃ­scar e Ã¢mbar",
  "Asad Lattafa": "pimenta preta, tabaco, baunilha, Ã¢mbar, patchouli e madeiras",
  "212 VIP Black": "absinto, lavanda, anis, baunilha e almÃ­scar",
  "212 Men": "folhas verdes, especiarias, lavanda, sÃ¢ndalo e almÃ­scar",
  "Encre Noire": "cipreste, vetiver, cashmere, almÃ­scar e madeira",
  "Ferrari Black": "maÃ§Ã£, ameixa, bergamota, canela, baunilha e cedro",
  "Le Male Elixir": "lavanda, hortelÃ£, baunilha, mel, tabaco e fava tonka",
  "Le Male Le Parfum": "cardamomo, lavanda, Ã­ris, baunilha e madeiras",
  "One Million": "toranja, canela, couro, Ã¢mbar, patchouli e especiarias",
  "Phantom": "lavanda, limÃ£o, maÃ§Ã£, patchouli, baunilha e vetiver",
  "Invictus Victory": "limÃ£o, pimenta rosa, lavanda, baunilha, fava tonka e Ã¢mbar",
  "Invictus Victory Elixir": "lavanda, cardamomo, pimenta, incenso, baunilha e fava tonka",
  "Silver Scent": "flor de laranjeira, limÃ£o, lavanda, cardamomo, fava tonka e Ã¢mbar",
  "Versace Eros": "hortelÃ£, maÃ§Ã£ verde, limÃ£o, fava tonka, baunilha e cedro",
  "L'eau d'Issey Miyake": "yuzu, bergamota, noz-moscada, lÃ­rio, tabaco e sÃ¢ndalo",
  "Hugo Boss Night": "lavanda, bÃ©tula, violeta, cardamomo e madeiras",
  "Scandal Masculino EDT": "sÃ¡lvia, mandarina, caramelo, fava tonka, vetiver e cedro",
  "Good Girl": "amÃªndoa, cafÃ©, jasmim, tuberosa, cacau, fava tonka e baunilha",
  "Scandal Feminino": "laranja sanguÃ­nea, mel, gardÃªnia, patchouli e caramelo",
  "Libre Yves Saint": "lavanda, mandarina, flor de laranjeira, jasmim, baunilha e Ã¢mbar gris",
  "Yara Rosa": "orquÃ­dea, frutas tropicais, baunilha, almÃ­scar e notas doces",
  "La Vie Est Belle": "Ã­ris, pera, cassis, jasmim, flor de laranjeira, patchouli e pralinÃª",
  "212 VIP RosÃ©": "champagne rosÃ©, pÃªssego, flor de pÃªssego, almÃ­scar e Ã¢mbar",
  "Lady Million": "framboesa, neroli, flor de laranjeira, jasmim, mel e patchouli",
  "Issey Miyake Fem": "lÃ³tus, frÃ©sia, rosa, lÃ­rio, peÃ´nia, madeiras e almÃ­scar",
  "Afeef Lattafa": "bergamota, pimenta rosa, jasmim, tuberosa, baunilha e sÃ¢ndalo",
  "Royal Amber Rouge": "aÃ§afrÃ£o, jasmim, Ã¢mbar, madeiras, resinas e almÃ­scar",
  "My Way": "bergamota, flor de laranjeira, tuberosa, jasmim, baunilha e cedro",
  "IdÃ´le": "bergamota, pera, rosa, jasmim, almÃ­scar branco e baunilha"
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
  "La Vie Est Belle": "LancÃ´me",
  "212 VIP RosÃ©": "Carolina Herrera",
  "Lady Million": "Paco Rabanne",
  "Issey Miyake Fem": "Issey Miyake",
  "Afeef Lattafa": "Lattafa",
  "Royal Amber Rouge": "Lattafa",
  "My Way": "Giorgio Armani",
  "IdÃ´le": "LancÃ´me"
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
  "LancÃ´me": "img/marcas/lancome.png",
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

// Funcao: carregarProdutosLoja
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

// Funcao: normalizarProdutoLoja
function normalizarProdutoLoja(produto) {
  const produtoCompleto = {
    ...produto,
    estoque: Number.isFinite(Number(produto.estoque)) ? Number(produto.estoque) : 10,
    promocao: Boolean(produto.promocao),
    precoPromocional5: produto.precoPromocional5 || "",
    precoPromocional10: produto.precoPromocional10 || "",
    destaque: Boolean(produto.destaque),
    selo: produto.selo || "",
    chamada: produto.chamada || ""
  };

  if (!("destaque" in produto)) {
    produtoCompleto.destaque = produtosDestaquePadrao.includes(produto.nome);
  }

  return produtoCompleto;
}

// Funcao: obterPrecoProduto
function obterPrecoProduto(produto, volume) {
  const precoBase = volume === 10 ? produto.preco10 : produto.preco5;
  const precoPromocional = volume === 10 ? produto.precoPromocional10 : produto.precoPromocional5;

  return produto.promocao && precoPromocional ? precoPromocional : precoBase;
}

// Funcao: renderizarPrecoCard
function renderizarPrecoCard(produto, volume) {
  const precoBase = volume === 10 ? produto.preco10 : produto.preco5;
  const precoFinal = obterPrecoProduto(produto, volume);
  const label = `${volume}ml`;

  if (produto.promocao && precoFinal !== precoBase) {
    return `<p class="preco-promocional"><span>${label} <s>R$ ${precoBase}</s></span><strong>R$ ${precoFinal}</strong></p>`;
  }

  return `<p>${label} R$ ${precoBase}</p>`;
}

// Funcao: produtoDisponivel
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

// Funcao: preencherFiltrosAvancados
function preencherFiltrosAvancados() {
  preencherSelect(familiaFiltro, obterOpcoesDetalhes("familia"));
  preencherSelect(intensidadeFiltro, obterOpcoesDetalhes("intensidade"));
}

// Funcao: preencherSelect
function preencherSelect(select, opcoes) {
  if (!select) return;

  opcoes.forEach(opcao => {
    const option = document.createElement("option");
    option.value = normalizarTexto(opcao);
    option.textContent = opcao;
    select.appendChild(option);
  });
}

// Funcao: obterOpcoesDetalhes
function obterOpcoesDetalhes(campo) {
  return [...new Set(produtos.map(produto => montarDetalhesProduto(produto)[campo]))].sort((a, b) =>
    a.localeCompare(b, "pt-BR")
  );
}

// Funcao: mostrarTodos
function mostrarTodos() {
  renderProdutos(produtos.filter(produto => produto.categoria === "masculino"), masculinosContainer);
  renderProdutos(produtos.filter(produto => produto.categoria === "feminino"), femininosContainer);
}

// Funcao: atualizarVitrine
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

// Funcao: preencherSelectComOpcoes
function preencherSelectComOpcoes(select, opcoes) {
  const valorAtual = select.value;
  const primeiraOpcao = select.options[0]?.cloneNode(true);
  select.innerHTML = "";
  if (primeiraOpcao) select.appendChild(primeiraOpcao);
  preencherSelect(select, opcoes);
  select.value = [...select.options].some(option => option.value === valorAtual) ? valorAtual : "";
}

// Funcao: mostrarCategoria
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

// Funcao: abrirCatalogo
function abrirCatalogo(tipo) {
  window.location.href = `produtos.html?categoria=${tipo}`;
}

// Funcao: renderProdutos
function renderProdutos(lista, container) {
  if (!container) return;

  container.innerHTML = "";

  if (lista.length === 0) {
    container.innerHTML = `<p class="sem-resultados">Nenhum perfume encontrado.</p>`;
    return;
  }

  lista.forEach(produto => {
    const semEstoque = !produtoDisponivel(produto);

    container.innerHTML += `
      <div class="card ${semEstoque ? "produto-esgotado" : ""}">
        <img src="${produto.img}" alt="${produto.nome}">
        ${produto.promocao ? '<span class="tag-promocao">PromoÃ§Ã£o</span>' : ""}
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

// Funcao: renderizarPaginaCatalogo
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

  catalogoPagina.innerHTML = produtosCategoria.map(produto => `
    <article class="catalogo-card ${produtoDisponivel(produto) ? "" : "produto-esgotado"}">
      <div class="catalogo-card-imagem">
        <img src="${produto.img}" alt="${produto.nome}">
      </div>
      ${produto.promocao ? '<span class="tag-promocao">PromoÃ§Ã£o</span>' : ""}
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

// Funcao: iniciarCarouselDestaques
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
          ${produto.promocao ? '<strong class="selo-desconto">PromoÃ§Ã£o</strong>' : ""}
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

// Funcao: verMaisProduto
function verMaisProduto(nomeProduto) {
  const produto = produtos.find(item => item.nome === nomeProduto);
  if (!produto) return;

  const detalhes = montarDetalhesProduto(produto);
  const acordes = montarAcordesProduto(detalhes.notas, detalhes.familia);
  const imagemDestaque = obterImagemDestaqueProduto(produto);
  const temImagemDestaque = Boolean(imagemDestaque);
  const imagemModal = imagemDestaque || produto.img;
  const marcaProduto = extrairMarcaProduto(produto.nome);
  const logoMarca = obterLogoMarca(marcaProduto);
  const modalExistente = document.querySelector(".modal-produto");
  const semEstoque = !produtoDisponivel(produto);

  if (modalExistente) modalExistente.remove();

  document.body.insertAdjacentHTML("beforeend", `
    <div class="modal-produto" onclick="fecharDetalhesProduto(event)">
      <div class="modal-conteudo ${temImagemDestaque ? "modal-conteudo-destaque" : ""}" ${temImagemDestaque ? `style="--imagem-destaque: url('${imagemDestaque}');"` : ""}>
        <button class="modal-fechar" aria-label="Fechar" onclick="fecharDetalhesProduto()">&times;</button>
        <div class="${temImagemDestaque ? "modal-hero-conteudo" : "modal-produto-grid"}">
          <div class="modal-topo">
            <span>${produto.categoria === "masculino" ? "Masculino" : "Feminino"}</span>
            <h2>${produto.nome}</h2>
          </div>

          <div class="modal-imagem-destaque">
            <img src="${imagemModal}" alt="${produto.nome}">
          </div>

          <div class="modal-info">
            <div class="modal-marca">
              <img src="${logoMarca}" alt="Logo ${marcaProduto}" loading="lazy" onerror="this.hidden=true; this.nextElementSibling.hidden=false;">
              <strong hidden>${marcaProduto}</strong>
            </div>

            <div class="modal-editorial">
              <span>Decant selecionado</span>
              <p>Uma leitura elegante da fragrancia, pensada para quem quer experimentar antes de escolher o frasco ideal.</p>
            </div>

            <div class="modal-opcoes-volume">
              <div>
                <span>5 ml</span>
                <strong>R$ ${obterPrecoProduto(produto, 5)}</strong>
              </div>
              <div>
                <span>10 ml</span>
                <strong>R$ ${obterPrecoProduto(produto, 10)}</strong>
              </div>
            </div>

            <div class="acordes">
              <h3>Principais Acordes</h3>
              ${acordes.map(acorde => `
                <div class="acorde-barra" style="--largura: ${acorde.valor}%; --cor: ${acorde.cor};">
                  <span>${acorde.nome}</span>
                </div>
              `).join("")}
            </div>

            <div class="modal-detalhes">
              <p class="modal-preco">${semEstoque ? "Produto esgotado" : `A partir de R$ ${obterPrecoProduto(produto, 5)}`}</p>
              <ul>
                <li><strong>FamÃ­lia olfativa:</strong> ${detalhes.familia}</li>
                <li><strong>Notas:</strong> ${detalhes.notas}</li>
                <li><strong>Intensidade:</strong> ${detalhes.intensidade}</li>
                <li><strong>OcasiÃ£o:</strong> ${detalhes.ocasiao}</li>
              </ul>
              <button class="btn-comprar" data-produto="${produto.nome}" onclick="comprar(this.dataset.produto)" ${semEstoque ? "disabled" : ""}>${semEstoque ? "ESGOTADO" : "COMPRAR"}</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `);

  ajustarFormatoImagemModal();
}

// Funcao: obterImagemDestaqueProduto
function obterImagemDestaqueProduto(produto) {
  return imagensDestaquePorProduto[normalizarTexto(produto.nome)] || "";
}

// Funcao: obterLogoMarca
function obterLogoMarca(marca) {
  return logosPorMarca[marca] || logosPorMarca["Decant's"];
}

// Funcao: ajustarFormatoImagemModal
function ajustarFormatoImagemModal() {
  const modal = document.querySelector(".modal-conteudo");
  const imagem = modal ? modal.querySelector(".modal-imagem-destaque img") : null;

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

// Funcao: montarDetalhesProduto
function montarDetalhesProduto(produto) {
  const masculino = produto.categoria === "masculino";
  const nome = normalizarTexto(produto.nome);

  let familia = masculino ? "Amadeirado aromÃ¡tico" : "Floral elegante";
  let intensidade = "MÃ©dia";
  let ocasiao = masculino ? "Dia a dia, encontros e ocasiÃµes especiais" : "Dia a dia, encontros e eventos";

  if (nome.includes("elixir") || nome.includes("victory") || nome.includes("million") || nome.includes("good girl") || nome.includes("scandal")) {
    intensidade = "Alta";
    ocasiao = "Noite, eventos e momentos marcantes";
  }

  if (nome.includes("sport") || nome.includes("issey") || nome.includes("my way")) {
    familia = masculino ? "CÃ­trico aromÃ¡tico" : "Floral fresco";
    intensidade = "MÃ©dia";
    ocasiao = "Dia, trabalho e clima quente";
  }

  if (nome.includes("lattafa") || nome.includes("amber") || nome.includes("yara")) {
    familia = "Oriental adocicado";
  }

  return {
    familia,
    notas: notasPorProduto[produto.nome] || "notas cÃ­tricas, florais, amadeiradas e almiscaradas",
    intensidade,
    ocasiao
  };
}

// Funcao: montarAcordesProduto
function montarAcordesProduto(notas, familia) {
  const texto = normalizarTexto(`${notas} ${familia}`);
  const regras = [
    { nome: "cÃ­trico", cor: "#f5ef3b", termos: ["bergamota", "limao", "laranja", "toranja", "mandarina", "yuzu", "citricos"] },
    { nome: "aromÃ¡tico", cor: "#3a8c7e", termos: ["lavanda", "hortela", "anis", "absinto", "alecrim", "aromatico"] },
    { nome: "amadeirado", cor: "#7a4920", termos: ["madeira", "madeiras", "cedro", "sandal", "vetiver", "cashmere", "betula", "cipreste"] },
    { nome: "floral", cor: "#d783a8", termos: ["rosa", "jasmim", "tuberosa", "lirio", "peonia", "gardenia", "flor", "floral", "orquidea", "fresia", "lotus"] },
    { nome: "Ã¢mbarado", cor: "#8e4519", termos: ["ambar", "amber", "resinas"] },
    { nome: "doce", cor: "#c27a45", termos: ["baunilha", "mel", "caramelo", "praline", "chocolate", "cacau", "doce"] },
    { nome: "especiado", cor: "#78a436", termos: ["pimenta", "cardamomo", "canela", "noz", "acafrao", "especiarias"] },
    { nome: "fresco", cor: "#6d9ea6", termos: ["marinhas", "fresco", "verde", "folhas", "champagne"] },
    { nome: "frutado", cor: "#d15265", termos: ["maca", "pera", "pessego", "framboesa", "ameixa", "abacaxi", "cassis", "frutas"] },
    { nome: "almiscarado", cor: "#9a9a90", termos: ["almiscar", "almiscarado"] },
    { nome: "couro", cor: "#5b351f", termos: ["couro", "tabaco", "cafe"] },
    { nome: "balsÃ¢mico", cor: "#73583e", termos: ["incenso", "tonka", "fava tonka", "balsamico"] }
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
    { nome: "aromÃ¡tico", cor: "#3a8c7e", valor: 96 },
    { nome: "amadeirado", cor: "#7a4920", valor: 82 },
    { nome: "fresco", cor: "#6d9ea6", valor: 70 },
    { nome: "almiscarado", cor: "#9a9a90", valor: 62 }
  ];

  return base.map((acorde, index) => ({
    ...acorde,
    valor: Math.max(44, Math.min(100, acorde.valor - index * 2))
  }));
}

// Funcao: extrairMarcaProduto
function extrairMarcaProduto(nomeProduto) {
  if (marcasPorProduto[nomeProduto]) return marcasPorProduto[nomeProduto];

  const nome = normalizarTexto(nomeProduto);
  const marcas = ["Dior", "Chanel", "Lattafa", "Paco Rabanne", "Carolina Herrera", "Yves Saint Laurent", "LancÃ´me", "Issey Miyake", "Ferrari", "Versace", "Hugo Boss", "Jean Paul Gaultier", "Armaf", "Lalique", "Jacques Bogart", "Giorgio Armani"];
  const marca = marcas.find(item => nome.includes(normalizarTexto(item)));

  if (marca) return marca;
  if (nome.includes("one million") || nome.includes("phantom") || nome.includes("invictus")) return "Paco Rabanne";
  if (nome.includes("good girl")) return "Carolina Herrera";
  if (nome.includes("libre")) return "Yves Saint Laurent";
  if (nome.includes("idole") || nome.includes("la vie est belle")) return "LancÃ´me";

  return "Decant's";
}

// Funcao: fecharDetalhesProduto
function fecharDetalhesProduto(event) {
  if (event && !event.target.classList.contains("modal-produto")) return;

  const modal = document.querySelector(".modal-produto");
  if (modal) modal.remove();
}

// Funcao: comprar
function comprar(nomeProduto) {
  abrirCheckout(nomeProduto);
}

// Funcao: abrirCheckout
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

// Funcao: montarOpcaoCheckout
function montarOpcaoCheckout(produto, volume, checked) {
  return `
    <label class="checkout-volume ${checked ? "ativo" : ""}">
      <input name="checkoutVolume" type="radio" value="${volume}" ${checked ? "checked" : ""} onchange="atualizarVolumeCheckout(event)">
      <span>${volume}ml</span>
      <strong>R$ ${obterPrecoProduto(produto, volume)}</strong>
    </label>
  `;
}

// Funcao: atualizarVolumeCheckout
function atualizarVolumeCheckout(event) {
  document.querySelectorAll(".checkout-volume").forEach(label => label.classList.remove("ativo"));
  event.currentTarget.closest(".checkout-volume").classList.add("ativo");
  atualizarTotalCheckout();
}

// Funcao: atualizarTotalCheckout
function atualizarTotalCheckout() {
  if (!checkoutProdutoAtual) return;

  const volume = Number(document.querySelector("input[name='checkoutVolume']:checked")?.value || 5);
  const quantidade = Math.max(1, Number(document.getElementById("checkoutQuantidade")?.value || 1));
  const total = precoTextoParaNumero(obterPrecoProduto(checkoutProdutoAtual, volume)) * quantidade;
  const totalElemento = document.getElementById("checkoutTotal");
  if (totalElemento) totalElemento.textContent = `R$ ${formatarMoedaLoja(total)}`;
}

// Funcao: enviarCheckout
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

// Funcao: fecharCheckout
function fecharCheckout(event) {
  if (event && !event.target.classList.contains("modal-checkout")) return;

  const modal = document.querySelector(".modal-checkout");
  if (modal) modal.remove();
}

// Funcao: montarWhatsAppLocalCheckout
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

// Funcao: exibirAvisoCheckoutIndisponivel
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

// Funcao: precoTextoParaNumero
function precoTextoParaNumero(valor) {
  return Number(String(valor || "0").replace(/\./g, "").replace(",", "."));
}

// Funcao: formatarMoedaLoja
function formatarMoedaLoja(valor) {
  return Number(valor || 0).toFixed(2).replace(".", ",");
}

// Funcao: mascararTelefoneLoja
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

// Funcao: apiLoja
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

// Funcao: exibirRetornoPagamento
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

// Funcao: pesquisarProdutos
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

// Funcao: produtoCombinaComFiltro
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

// Funcao: normalizarTexto
function normalizarTexto(texto) {
  return texto
    .toString()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

// Funcao: scrollToProdutos
function scrollToProdutos() {
  const catalogo = document.querySelector(".catalogo");

  if (catalogo) {
    catalogo.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}
