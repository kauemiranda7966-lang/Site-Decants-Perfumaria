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

// #INICIAR_NAVEGACAO_CATALOGO
function iniciarNavegacaoCatalogo() {
  document.querySelectorAll(".catalogo-seta").forEach(botao => {
    const container = document.getElementById(botao.dataset.catalogo);
    if (!container) return;

    botao.addEventListener("click", () => {
      const direcao = Number(botao.dataset.direcao || 1);
      container.scrollBy({
        left: direcao * Math.max(260, container.clientWidth * 0.82),
        behavior: "smooth"
      });
    });

    container.addEventListener("scroll", () => atualizarSetasCatalogo(container), { passive: true });
  });

  window.addEventListener("resize", atualizarTodasSetasCatalogo);
  window.requestAnimationFrame(atualizarTodasSetasCatalogo);
}

// #ATUALIZAR_TODAS_SETAS_CATALOGO
function atualizarTodasSetasCatalogo() {
  document.querySelectorAll(".produtos-scroll").forEach(atualizarSetasCatalogo);
}

// #ATUALIZAR_SETAS_CATALOGO
function atualizarSetasCatalogo(container) {
  const trilho = container.closest(".catalogo-trilho");
  if (!trilho) return;

  const anterior = trilho.querySelector(".catalogo-seta-anterior");
  const proxima = trilho.querySelector(".catalogo-seta-proxima");
  const limite = Math.max(0, container.scrollWidth - container.clientWidth);

  if (anterior) anterior.disabled = container.scrollLeft <= 2;
  if (proxima) proxima.disabled = container.scrollLeft >= limite - 2;
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
    const nome = escaparHtmlLoja(produto.nome);
    const nomeAtributo = escaparAtributoLoja(produto.nome);
    const imagem = escaparAtributoLoja(obterImagemProduto(produto));
    const fallback = escaparAtributoLoja(produto.img);

    container.innerHTML += `
      <div class="card ${semEstoque ? "produto-esgotado" : ""}" style="--card-index: ${index};">
        <span class="card-brilho" aria-hidden="true"></span>
        <img src="${imagem}" alt="${nomeAtributo}" data-fallback-image="${fallback}" loading="lazy" onerror="marcarImagemProdutoIndisponivel(this, this.dataset.fallbackImage)">
        ${produto.promocao ? '<span class="tag-promocao">PromoÃ§Ã£o</span>' : ""}
        <h3>${nome}</h3>
        ${renderizarPrecoCard(produto, 5)}
        ${renderizarPrecoCard(produto, 10)}
        <p class="estoque-card">${semEstoque ? "Produto esgotado" : `Estoque: ${produto.estoque}`}</p>

        <div class="acoes-card">
          <button class="btn-comprar" data-produto="${nomeAtributo}" onclick="comprar(this.dataset.produto)" ${semEstoque ? "disabled" : ""}>${semEstoque ? "ESGOTADO" : "COMPRAR"}</button>
          <button class="btn-ver-mais" data-produto="${nomeAtributo}" onclick="verMaisProduto(this.dataset.produto)">VER MAIS</button>
        </div>
      </div>
    `;
  });

  window.requestAnimationFrame(() => atualizarSetasCatalogo(container));
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

  catalogoPagina.innerHTML = produtosCategoria.map((produto, index) => {
    const nome = escaparHtmlLoja(produto.nome);
    const nomeAtributo = escaparAtributoLoja(produto.nome);
    const imagem = escaparAtributoLoja(obterImagemProduto(produto));
    const fallback = escaparAtributoLoja(produto.img);

    return `
      <article class="catalogo-card ${produtoDisponivel(produto) ? "" : "produto-esgotado"}" style="--card-index: ${index};">
        <div class="catalogo-card-imagem">
          <img src="${imagem}" alt="${nomeAtributo}" data-fallback-image="${fallback}" loading="lazy" onerror="marcarImagemProdutoIndisponivel(this, this.dataset.fallbackImage)">
        </div>
        ${produto.promocao ? '<span class="tag-promocao">PromoÃ§Ã£o</span>' : ""}
        <h3>${nome}</h3>
        <div class="catalogo-precos">
          <span>5ml: R$ ${escaparHtmlLoja(obterPrecoProduto(produto, 5))}</span>
          <span>10ml: R$ ${escaparHtmlLoja(obterPrecoProduto(produto, 10))}</span>
        </div>
        <p class="estoque-card">${produtoDisponivel(produto) ? `Estoque: ${produto.estoque}` : "Produto esgotado"}</p>
        <div class="catalogo-acoes">
          <button class="btn-comprar" data-produto="${nomeAtributo}" onclick="comprar(this.dataset.produto)" ${produtoDisponivel(produto) ? "" : "disabled"}>${produtoDisponivel(produto) ? "COMPRAR" : "ESGOTADO"}</button>
          <button class="btn-ver-mais" data-produto="${nomeAtributo}" onclick="verMaisProduto(this.dataset.produto)">VER MAIS</button>
        </div>
      </article>
    `;
  }).join("");
}

// #INICIAR_CAROUSEL_DESTAQUES
function iniciarCarouselDestaques() {
  const destaques = produtos.filter(produto => produto.destaque).slice(0, 8);

  if (destaques.length) {
    carouselPremium.querySelectorAll(".carousel-slide").forEach(slide => slide.remove());

    const controles = carouselPremium.querySelector(".carousel-anterior");
    destaques.forEach((produto, index) => {
      const imagem = obterImagemDestaqueProduto(produto) || produto.img;
      const nome = escaparHtmlLoja(produto.nome);
      const nomeAtributo = escaparAtributoLoja(produto.nome);
      const slide = document.createElement("div");
      slide.className = `carousel-slide ${index === 0 ? "ativo" : ""}`;
      slide.dataset.produto = produto.nome;
      slide.innerHTML = `
        <img src="${escaparAtributoLoja(imagem)}" alt="${nomeAtributo}" loading="lazy">
        <div class="carousel-conteudo">
          <span class="selo-destaque">${escaparHtmlLoja(produto.selo || (produto.promocao ? "Oferta" : "Destaque"))}</span>
          ${produto.promocao ? '<strong class="selo-desconto">PromoÃ§Ã£o</strong>' : ""}
          <p class="carousel-kicker">${escaparHtmlLoja(produto.chamada || (produto.categoria === "masculino" ? "Masculino selecionado" : "Feminino selecionado"))}</p>
          <h2>${nome.toUpperCase()}</h2>
          <p class="carousel-preco">R$ ${escaparHtmlLoja(obterPrecoProduto(produto, 5))}</p>
          <div class="acoes-destaque">
            <button class="btn-comprar" data-produto="${nomeAtributo}" onclick="comprar(this.dataset.produto)" ${produtoDisponivel(produto) ? "" : "disabled"}>${produtoDisponivel(produto) ? "COMPRAR" : "ESGOTADO"}</button>
            <button class="btn-ver-mais" data-produto="${nomeAtributo}" onclick="verMaisProduto(this.dataset.produto)">VER MAIS</button>
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
