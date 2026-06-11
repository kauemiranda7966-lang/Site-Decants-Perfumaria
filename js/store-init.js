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
const clubeOfertasForm = document.getElementById("clubeOfertasForm");
const clubeTelefone = document.getElementById("clubeTelefone");

if (masculinosContainer && femininosContainer) {
  preencherFiltrosAvancados();
  mostrarTodos();
  iniciarNavegacaoCatalogo();
}

if (catalogoPagina) {
  renderizarPaginaCatalogo();
}

if (carouselPremium) {
  iniciarCarouselDestaques();
}

if (clubeTelefone) {
  clubeTelefone.addEventListener("input", mascararTelefoneLoja);
}

if (clubeOfertasForm) {
  clubeOfertasForm.addEventListener("submit", cadastrarClubeOfertas);
}

document.querySelectorAll("#menuPrincipal a").forEach(link => {
  link.addEventListener("click", () => {
    const menu = document.getElementById("menuPrincipal");
    const botao = document.querySelector(".menu-mobile-botao");
    if (!menu || !botao) return;

    menu.classList.remove("menu-aberto");
    botao.setAttribute("aria-expanded", "false");
    botao.setAttribute("aria-label", "Abrir menu");
    botao.querySelector("i")?.classList.replace("fa-xmark", "fa-bars");
  });
});

carregarProdutosLoja();
exibirRetornoPagamento();
atualizarContadoresCarrinho();

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
