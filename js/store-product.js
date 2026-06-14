// #VER_MAIS_PRODUTO
function verMaisProduto(nomeProduto) {
  const produto = produtos.find(item => item.nome === nomeProduto);
  if (!produto) return;

  const detalhes = montarDetalhesProduto(produto);
  const acordes = montarAcordesProduto(detalhes.notas, detalhes.familia);
  const imagensGaleria = montarGaleriaModalProduto(produto);
  const marcaProduto = extrairMarcaProduto(produto.nome);
  const logoMarca = obterLogoMarca(marcaProduto);
  const modalExistente = document.querySelector(".modal-produto");
  const semEstoque = !produtoDisponivel(produto);
  const preco5 = obterPrecoProduto(produto, 5);
  const preco10 = obterPrecoProduto(produto, 10);
  const temaProduto = obterTemaVisualProduto(produto.nome);

  if (modalExistente) modalExistente.remove();
  document.body.classList.add("modal-aberto");

  document.body.insertAdjacentHTML("beforeend", `
    <div class="modal-produto modal-produto-premium" role="dialog" aria-modal="true" aria-labelledby="modalProdutoTitulo" onclick="fecharDetalhesProduto(event)">
      <div class="modal-conteudo modal-conteudo-premium" style="--produto-cor:${temaProduto.cor};--produto-cor-suave:${temaProduto.suave};">
        <button class="modal-fechar modal-fechar-premium" type="button" aria-label="Fechar" onclick="fecharDetalhesProduto()">
          <span aria-hidden="true">&times;</span>
        </button>

        ${renderizarHeaderProdutoMobile(produto)}

        <div class="modal-layout-premium">
          ${renderizarGaleriaModal(produto, imagensGaleria)}
          <div class="modal-detalhes-compra">
            ${renderizarInfoModal(produto, detalhes, acordes, marcaProduto, logoMarca, preco5, preco10)}
            ${renderizarCompraModal(produto, semEstoque, preco5)}
          </div>
        </div>

        ${renderizarNavegacaoProdutoMobile(produto.categoria)}
      </div>
    </div>
  `);

  ajustarFormatoImagemModal();
  atualizarResumoModal();
  const imagem = document.querySelector(".modal-galeria-imagem img");
  if (imagem && imagem.complete && imagem.naturalWidth) finalizarCarregamentoImagemModal(imagem);
}

// #OBTER_TEMA_VISUAL_PRODUTO
function obterTemaVisualProduto(nomeProduto) {
  const nome = normalizarTexto(nomeProduto);
  const temas = [
    { termos: ["bleu de chanel", "dior sauvage", "hugo boss night"], cor: "#173654", suave: "#e8eef3" },
    { termos: ["scandal masculino", "asad lattafa", "one million", "lady million"], cor: "#b7761f", suave: "#f5e8d2" },
    { termos: ["idole", "la vie est belle", "yara rosa", "212 vip rose"], cor: "#c98591", suave: "#f7e7e9" },
    { termos: ["ferrari black"], cor: "#711f25", suave: "#f0e5e5" },
    { termos: ["versace eros"], cor: "#176a5b", suave: "#e3f0ec" },
    { termos: ["good girl", "212 vip black", "encre noire"], cor: "#252830", suave: "#e8e8e9" }
  ];
  return temas.find(tema => tema.termos.some(termo => nome.includes(termo))) || {
    cor: "#b8862b",
    suave: "#f4ecdc"
  };
}

// #RENDERIZAR_HEADER_PRODUTO_MOBILE
function renderizarHeaderProdutoMobile(produto) {
  const nomeAtributo = escaparAtributoLoja(produto.nome);
  return `
    <header class="modal-mobile-header">
      <button class="modal-mobile-voltar" type="button" aria-label="Voltar ao catalogo" onclick="fecharDetalhesProduto()">
        <i class="fa-solid fa-xmark" aria-hidden="true"></i>
      </button>
      <a class="modal-mobile-logo" href="index.html" aria-label="Ir para o in&iacute;cio">
        <span class="modal-mobile-logo-simbolo"><img src="img/logo/logo.png" alt=""></span>
        <span class="modal-mobile-logo-texto"><strong>DECANT'S</strong><small>PERFUMARIA</small></span>
      </a>
      <div class="modal-mobile-acoes">
        <button type="button" aria-label="Buscar perfumes" onclick="abrirBuscaProdutoMobile()">
          <i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>
        </button>
        <button type="button" aria-label="Abrir compra de ${nomeAtributo}" data-produto="${nomeAtributo}" onclick="comprar(this.dataset.produto)">
          <i class="fa-solid fa-bag-shopping" aria-hidden="true"></i>
        </button>
      </div>
    </header>
  `;
}

// #RENDERIZAR_NAVEGACAO_PRODUTO_MOBILE
function renderizarNavegacaoProdutoMobile(categoria) {
  return `
    <nav class="modal-mobile-nav" aria-label="Navega&ccedil;&atilde;o principal">
      <a href="index.html"><i class="fa-solid fa-house" aria-hidden="true"></i><span>In&iacute;cio</span></a>
      <a class="${categoria === "masculino" ? "ativo" : ""}" href="produtos.html?categoria=masculino"><i class="fa-solid fa-bottle-droplet" aria-hidden="true"></i><span>Masculinos</span></a>
      <a class="${categoria === "feminino" ? "ativo" : ""}" href="produtos.html?categoria=feminino"><i class="fa-solid fa-bottle-droplet" aria-hidden="true"></i><span>Femininos</span></a>
      <a href="index.html#clube-ofertas"><i class="fa-solid fa-tag" aria-hidden="true"></i><span>Clube</span></a>
      <a href="contatos.html"><i class="fa-regular fa-user" aria-hidden="true"></i><span>Conta</span></a>
    </nav>
  `;
}

// #ABRIR_BUSCA_PRODUTO_MOBILE
function abrirBuscaProdutoMobile() {
  fecharDetalhesProduto();
  window.setTimeout(() => {
    const campo = document.querySelector(".campo-busca input");
    campo?.scrollIntoView({ behavior: "smooth", block: "center" });
    campo?.focus();
  }, 240);
}

// #MONTAR_GALERIA_MODAL_PRODUTO
function montarGaleriaModalProduto(produto) {
  const imagensContainer = imagensContainerPorProduto[normalizarTexto(produto.nome)] || [];
  const imagensValidas = imagensContainer.filter((imagem, index, lista) =>
    imagem && imagem.includes("img/container/") && lista.indexOf(imagem) === index
  );

  if (imagensValidas.length) return imagensValidas;

  const imagemFallback = obterImagemDestaqueProduto(produto) || produto.img;
  return imagemFallback ? [normalizarCaminhoImagem(imagemFallback)] : [];
}

// #OBTER_IMAGEM_PRODUTO
function obterImagemProduto(produto) {
  const imagensContainer = imagensContainerPorProduto[normalizarTexto(produto.nome)] || [];
  return produto.img || imagensContainer[0] || "";
}

// #MARCAR_IMAGEM_PRODUTO_INDISPONIVEL
function marcarImagemProdutoIndisponivel(imagem, fallback) {
  const caminhoFallback = normalizarCaminhoImagem(fallback);
  if (caminhoFallback && imagem.getAttribute("src") !== caminhoFallback) {
    imagem.src = caminhoFallback;
    return;
  }

  imagem.alt = `${imagem.alt} - imagem indisponivel`;
  imagem.classList.add("imagem-indisponivel");
}

// #RENDERIZAR_GALERIA_MODAL
function renderizarGaleriaModal(produto, imagens) {
  const categoria = produto.categoria === "masculino" ? "Masculino" : "Feminino";
  const imagemPrincipal = imagens[0] || "";
  const nomeAtributo = escaparAtributoLoja(produto.nome);

  return `
    <section class="modal-galeria-premium modal-galeria-cinematica" aria-label="Galeria do produto">
      <div class="modal-galeria-imagem modal-imagem-carregando">
        <span class="modal-skeleton" aria-hidden="true"></span>
        <span class="modal-selo-categoria">${categoria}</span>
        <button class="modal-favorito" type="button" aria-label="Favoritar perfume">
          <i class="fa-regular fa-heart" aria-hidden="true"></i>
        </button>
        ${imagens.length > 1 ? `
          <button class="modal-galeria-seta modal-galeria-anterior" type="button" aria-label="Imagem anterior" onclick="navegarImagemModal(-1)">
            <i class="fa-solid fa-chevron-left" aria-hidden="true"></i>
          </button>
          <button class="modal-galeria-seta modal-galeria-proxima" type="button" aria-label="PrÃ³xima imagem" onclick="navegarImagemModal(1)">
            <i class="fa-solid fa-chevron-right" aria-hidden="true"></i>
          </button>
        ` : ""}
        ${imagemPrincipal
          ? `<img src="${escaparAtributoLoja(imagemPrincipal)}" alt="${nomeAtributo}" onload="finalizarCarregamentoImagemModal(this)" onerror="marcarImagemModalIndisponivel(this)">`
          : `<div class="modal-sem-imagem">Imagem indisponivel</div>`}
      </div>

      ${imagens.length > 1 ? `<div class="modal-galeria-pontos" aria-label="Selecionar imagem">
        ${imagens.map((imagem, index) => `
          <button class="${index === 0 ? "ativo" : ""}" type="button" aria-label="Ver imagem ${index + 1}" onclick="selecionarImagemModal(this)" data-modal-imagem data-src="${escaparAtributoLoja(imagem)}"></button>
        `).join("")}
      </div>` : ""}

      ${imagens.length ? `<div class="modal-thumbs" aria-label="Miniaturas">
        ${imagens.map((imagem, index) => `
          <button class="modal-thumb ${index === 0 ? "ativo" : ""} modal-thumb-cinematica" type="button" aria-label="Ver imagem ${index + 1}" onclick="selecionarImagemModal(this)" data-modal-imagem data-src="${escaparAtributoLoja(imagem)}">
            <img src="${escaparAtributoLoja(imagem)}" alt="${nomeAtributo} miniatura ${index + 1}" loading="lazy">
          </button>
        `).join("")}
      </div>` : ""}
    </section>
  `;
}

// #RENDERIZAR_COMPRA_MODAL
function renderizarCompraModal(produto, semEstoque, preco5) {
  const nomeAtributo = escaparAtributoLoja(produto.nome);
  return `
    <aside class="modal-compra-premium">
      <div class="modal-beneficios-premium" aria-label="Benef&iacute;cios da compra">
        <span><i class="fa-solid fa-truck-fast" aria-hidden="true"></i><strong>Frete gr&aacute;tis</strong><small>Todo o Brasil acima de R$ 299.</small></span>
        <span><i class="fa-solid fa-lock" aria-hidden="true"></i><strong>Pagamento seguro</strong><small>Seus dados 100% protegidos.</small></span>
        <span><i class="fa-solid fa-shield-halved" aria-hidden="true"></i><strong>Produtos originais</strong><small>Qualidade garantida.</small></span>
      </div>

      <div class="modal-preco-final">
        <span>A partir de</span>
        <strong id="modalPrecoSelecionado">R$ ${escaparHtmlLoja(preco5)}</strong>
      </div>

      <div class="modal-quantidade" aria-label="Quantidade">
        <button type="button" aria-label="Diminuir quantidade" onclick="alterarQuantidadeModal(-1)">-</button>
        <strong id="modalQuantidade">1</strong>
        <button type="button" aria-label="Aumentar quantidade" onclick="alterarQuantidadeModal(1)">+</button>
      </div>

      <button class="modal-btn-principal" type="button" data-produto="${nomeAtributo}" onclick="comprar(this.dataset.produto)" ${semEstoque ? "disabled" : ""}>
        <i class="fa-solid fa-bag-shopping" aria-hidden="true"></i>
        ${semEstoque ? "Produto esgotado" : "Adicionar ao carrinho"}
      </button>

      <button class="modal-btn-whatsapp" type="button" data-produto="${nomeAtributo}" onclick="comprarViaWhatsAppProduto(this.dataset.produto)" ${semEstoque ? "disabled" : ""}>
        <i class="fa-brands fa-whatsapp" aria-hidden="true"></i>
        Comprar via WhatsApp
      </button>
    </aside>
  `;
}

function comprarViaWhatsAppProduto(nomeProduto) {
  const produto = produtos[nomeProduto];
  const modal = document.querySelector(".modal-produto-premium");

  if (!produto || !modal) return;

  const volumeAtivo = Number(modal.querySelector(".modal-volume-card.ativo")?.dataset.volume || 5);
  const quantidade = Math.max(
    1,
    Number.parseInt(modal.querySelector("#modalQuantidade")?.textContent || "1", 10)
  );
  const precoUnitario = precoTextoParaNumero(obterPrecoProduto(produto, volumeAtivo));
  const total = precoUnitario * quantidade;
  const mensagem = [
    "OlÃ¡! Quero comprar este perfume:",
    `${produto.nome} - ${volumeAtivo}ml`,
    `Quantidade: ${quantidade}`,
    `Total: ${formatarMoedaLoja(total)}`
  ].join("\n");

  window.open(
    `https://wa.me/558899641605?text=${encodeURIComponent(mensagem)}`,
    "_blank",
    "noopener,noreferrer"
  );
}

// #RENDERIZAR_INFO_MODAL
function renderizarInfoModal(produto, detalhes, acordes, marcaProduto, logoMarca, preco5, preco10) {
  const semEstoque = !produtoDisponivel(produto);
  const categoria = produto.categoria === "masculino" ? "Masculino" : "Feminino";
  const descricao = criarDescricaoCurtaProduto(detalhes);
  const concentracao = normalizarTexto(produto.nome).includes("edt") ? "Eau de Toilette" : "Eau de Parfum";
  const marca = escaparHtmlLoja(marcaProduto);

  return `
    <section class="modal-info-premium">
      <div class="modal-marca-linha">
        <span class="modal-categoria-texto">${categoria}</span>
        <span class="modal-marca-texto">${marca}</span>
        <div class="modal-logo-mini">
          <img src="${escaparAtributoLoja(logoMarca)}" alt="Logo ${escaparAtributoLoja(marcaProduto)}" loading="lazy" onerror="this.hidden=true; this.nextElementSibling.hidden=false;">
          <strong hidden>${marca}</strong>
        </div>
      </div>

      <h2 id="modalProdutoTitulo">${escaparHtmlLoja(produto.nome)}</h2>

      <p class="modal-descricao">${escaparHtmlLoja(descricao)}</p>

      <div class="modal-divisor"></div>

      <div class="modal-secao modal-secao-tamanhos">
        <h3>Escolha o tamanho</h3>
        <div class="modal-opcoes-volume" role="radiogroup" aria-label="Tamanhos disponÃ­veis">
          ${renderizarVolumeModal(5, preco5, true, semEstoque)}
          ${renderizarVolumeModal(10, preco10, false, semEstoque)}
        </div>
      </div>

      <div class="modal-secao modal-secao-acordes">
        <h3>Principais acordes</h3>
        <div class="modal-acordes-premium">
          ${acordes.map(acorde => `<span style="--cor-chip: ${escaparAtributoLoja(acorde.cor)};">${escaparHtmlLoja(acorde.nome)}</span>`).join("")}
        </div>
      </div>

      <div class="modal-atributos-premium">
        <article>
          <i class="fa-regular fa-clock" aria-hidden="true"></i>
          <span>FixaÃ§Ã£o</span>
          <strong>${escaparHtmlLoja(detalhes.intensidade)}</strong>
        </article>
        <article>
          <i class="fa-regular fa-sun" aria-hidden="true"></i>
          <span>OcasiÃ£o</span>
          <strong>${escaparHtmlLoja(detalhes.ocasiao.split(",")[0])}</strong>
        </article>
        <article>
          <i class="fa-solid fa-wand-magic-sparkles" aria-hidden="true"></i>
          <span>Fam&iacute;lia olfativa</span>
          <strong>${escaparHtmlLoja(detalhes.familia)}</strong>
        </article>
        <article>
          <i class="fa-solid fa-bottle-droplet" aria-hidden="true"></i>
          <span>Concentra&ccedil;&atilde;o</span>
          <strong>${concentracao}</strong>
        </article>
      </div>

      <p class="modal-notas"><strong>Notas:</strong> ${escaparHtmlLoja(detalhes.notas)}</p>
    </section>
  `;
}

// #CRIAR_DESCRICAO_CURTA_PRODUTO
function criarDescricaoCurtaProduto(detalhes) {
  const notas = repararTextoCatalogo(detalhes.notas).split(",").map(nota => nota.trim()).filter(Boolean);
  const destaqueNotas = notas.slice(0, 2).join(" e ");
  return `${repararTextoCatalogo(detalhes.familia)}, elegante e marcante${destaqueNotas ? `, com ${destaqueNotas}` : ""}.`;
}

// #RENDERIZAR_VOLUME_MODAL
function renderizarVolumeModal(volume, preco, ativo, semEstoque) {
  const valorMl = precoTextoParaNumero(preco) / volume;
  const precoSeguro = escaparAtributoLoja(preco);

  return `
    <button class="modal-volume-card ${ativo ? "ativo" : ""}" type="button" role="radio" aria-checked="${ativo}" data-volume="${volume}" data-preco="${precoSeguro}" onclick="selecionarVolumeModal(this)" ${semEstoque ? "disabled" : ""}>
      <i class="modal-volume-icone fa-solid fa-bottle-droplet" aria-hidden="true"></i>
      <span>${volume} ml</span>
      <strong>R$ ${escaparHtmlLoja(preco)}</strong>
      <small>R$ ${formatarMoedaLoja(valorMl)} / ml</small>
    </button>
  `;
}

// #FINALIZAR_CARREGAMENTO_IMAGEM_MODAL
function finalizarCarregamentoImagemModal(imagem) {
  const wrapper = imagem.closest(".modal-imagem-destaque, .modal-galeria-imagem");
  if (!wrapper) return;

  wrapper.classList.remove("modal-imagem-carregando", "modal-imagem-falhou");
  aplicarFormatoImagemModal(imagem);
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
  const imagemPrincipal = modal?.querySelector(".modal-galeria-imagem img");
  const imagemArea = modal?.querySelector(".modal-galeria-imagem");
  const novaImagem = botao.dataset.src;

  if (!imagemPrincipal || !imagemArea || !novaImagem || imagemPrincipal.getAttribute("src") === novaImagem) return;

  modal.querySelectorAll("[data-modal-imagem]").forEach(controle => {
    controle.classList.toggle("ativo", controle.dataset.src === novaImagem);
  });
  imagemArea.classList.add("modal-imagem-carregando");
  imagemPrincipal.setAttribute("src", novaImagem);
}

// #NAVEGAR_IMAGEM_MODAL
function navegarImagemModal(direcao) {
  const modal = document.querySelector(".modal-conteudo-premium");
  const thumbs = [...(modal?.querySelectorAll(".modal-thumb") || [])];
  if (!thumbs.length) return;

  const atual = Math.max(0, thumbs.findIndex(thumb => thumb.classList.contains("ativo")));
  const proximo = (atual + direcao + thumbs.length) % thumbs.length;
  selecionarImagemModal(thumbs[proximo]);
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

  if (imagem.complete && imagem.naturalWidth) {
    aplicarFormatoImagemModal(imagem);
  } else {
    imagem.addEventListener("load", () => aplicarFormatoImagemModal(imagem), { once: true });
  }
}

// #APLICAR_FORMATO_IMAGEM_MODAL
function aplicarFormatoImagemModal(imagem) {
  const modal = imagem?.closest(".modal-conteudo");
  if (!modal || !imagem.naturalWidth || !imagem.naturalHeight) return;

  const proporcao = imagem.naturalWidth / imagem.naturalHeight;
  const formato = proporcao > 1.18 ? "paisagem" : proporcao < 0.86 ? "retrato" : "quadrada";

  modal.classList.remove("modal-imagem-paisagem", "modal-imagem-retrato", "modal-imagem-quadrada");
  modal.classList.add(`modal-imagem-${formato}`);
  modal.style.setProperty("--imagem-proporcao", proporcao.toFixed(3));
}

// #MONTAR_DETALHES_PRODUTO
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

// #MONTAR_ACORDES_PRODUTO
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

// #EXTRAIR_MARCA_PRODUTO
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

// #FECHAR_DETALHES_PRODUTO
function fecharDetalhesProduto(event) {
  if (event && !event.target.classList.contains("modal-produto")) return;

  const modal = document.querySelector(".modal-produto");
  if (!modal || modal.classList.contains("modal-saindo")) return;

  modal.classList.add("modal-saindo");
  document.body.classList.remove("modal-aberto");
  window.setTimeout(() => modal.remove(), 220);
}
