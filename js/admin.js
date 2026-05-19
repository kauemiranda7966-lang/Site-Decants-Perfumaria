let produtosAdmin = [];
let autenticado = false;
let filtroAdmin = "todos";

const campos = {
  indice: document.getElementById("produtoIndice"),
  nome: document.getElementById("nome"),
  categoria: document.getElementById("categoria"),
  img: document.getElementById("img"),
  estoque: document.getElementById("estoque"),
  preco5: document.getElementById("preco5"),
  preco10: document.getElementById("preco10"),
  promocao: document.getElementById("promocao"),
  precoPromocional5: document.getElementById("precoPromocional5"),
  precoPromocional10: document.getElementById("precoPromocional10"),
  destaque: document.getElementById("destaque"),
  selo: document.getElementById("selo"),
  chamada: document.getElementById("chamada")
};

const produtoForm = document.getElementById("produtoForm");
const adminProdutos = document.getElementById("adminProdutos");
const buscaAdmin = document.getElementById("buscaAdmin");
const formTitulo = document.getElementById("formTitulo");
const excluirProduto = document.getElementById("excluirProduto");
const loginAdmin = document.getElementById("loginAdmin");
const loginForm = document.getElementById("loginForm");
const loginErro = document.getElementById("loginErro");
const adminConteudo = document.getElementById("adminConteudo");
const adminStatus = document.getElementById("adminStatus");
const adminKicker = document.getElementById("adminKicker");
const adminTitulo = document.getElementById("adminTitulo");
const sairAdmin = document.getElementById("sairAdmin");
const resetarCatalogoBotao = document.getElementById("resetarCatalogo");
const leadCapture = document.getElementById("leadCapture");
const leadForm = document.getElementById("leadForm");
const leadMensagem = document.getElementById("leadMensagem");
const leadTelefone = document.getElementById("leadTelefone");
const filtrosAdmin = document.querySelectorAll(".admin-filtro");

produtoForm.addEventListener("submit", salvarProduto);
document.getElementById("limparForm").addEventListener("click", limparFormulario);
resetarCatalogoBotao.addEventListener("click", resetarCatalogo);
excluirProduto.addEventListener("click", excluirProdutoSelecionado);
buscaAdmin.addEventListener("input", renderizarAdmin);
filtrosAdmin.forEach(botao => botao.addEventListener("click", filtrarAdmin));
loginForm.addEventListener("submit", entrarAdmin);
sairAdmin.addEventListener("click", sair);
leadForm.addEventListener("submit", salvarLead);
leadTelefone.addEventListener("input", mascararTelefone);

iniciarAdmin();

// #INICIAR_ADMIN
async function iniciarAdmin() {
  try {
    const sessao = await api("/api/session");
    autenticado = Boolean(sessao.authenticated);
    alternarAcesso(autenticado, sessao.user);
    if (autenticado) await carregarProdutosAdmin();
  } catch (error) {
    adminStatus.textContent = "Cadastre-se para receber novidades assim que o clube estiver online.";
    leadCapture.hidden = false;
    loginAdmin.hidden = true;
    adminConteudo.hidden = true;
    resetarCatalogoBotao.hidden = true;
  }
}

// #SALVAR_LEAD
async function salvarLead(event) {
  event.preventDefault();
  leadMensagem.hidden = true;
  leadMensagem.classList.remove("erro");

  const acessoDono = await tentarAcessoDono();
  if (acessoDono) return;

  try {
    await api("/api/leads", {
      method: "POST",
      body: JSON.stringify({
        email: document.getElementById("leadEmail").value,
        telefone: leadTelefone.value
      })
    });

    leadForm.reset();
    leadMensagem.textContent = "Pronto! Voce entrou na lista VIP de ofertas.";
    leadMensagem.hidden = false;
  } catch (error) {
    leadMensagem.textContent = error.message || "Nao foi possivel cadastrar agora.";
    leadMensagem.classList.add("erro");
    leadMensagem.hidden = false;
  }
}

// #TENTAR_ACESSO_DONO
async function tentarAcessoDono() {
  const usuario = document.getElementById("leadEmail").value.trim();
  const senha = leadTelefone.value.trim();

  try {
    const sessao = await api("/api/login", {
      method: "POST",
      body: JSON.stringify({ user: usuario, password: senha })
    });

    autenticado = true;
    alternarAcesso(true, sessao.user);
    leadForm.reset();
    await carregarProdutosAdmin();
    return true;
  } catch (error) {
    return false;
  }
}

// #ENTRAR_ADMIN
async function entrarAdmin(event) {
  event.preventDefault();
  loginErro.hidden = true;

  try {
    const sessao = await api("/api/login", {
      method: "POST",
      body: JSON.stringify({
        user: document.getElementById("loginUsuario").value.trim(),
        password: document.getElementById("loginSenha").value
      })
    });

    autenticado = true;
    alternarAcesso(true, sessao.user);
    loginForm.reset();
    await carregarProdutosAdmin();
  } catch (error) {
    loginErro.textContent = error.message || "Nao foi possivel entrar.";
    loginErro.hidden = false;
  }
}

// #SAIR
async function sair() {
  await api("/api/logout", { method: "POST" });
  autenticado = false;
  produtosAdmin = [];
  alternarAcesso(false);
  limparFormulario();
}

// #ALTERNAR_ACESSO
function alternarAcesso(permitido, usuario = "") {
  leadCapture.hidden = permitido;
  loginAdmin.hidden = true;
  adminConteudo.hidden = !permitido;
  sairAdmin.hidden = !permitido;
  resetarCatalogoBotao.hidden = !permitido;
  adminKicker.textContent = permitido ? "Painel do dono" : "Clube Decant's";
  adminTitulo.textContent = permitido ? "Controle de estoque e vitrine" : "Receba ofertas secretas primeiro";
  adminStatus.textContent = permitido ? `Conectado como ${usuario}` : "Novidades, promocoes e alertas de perfumes selecionados.";
}

// #CARREGAR_PRODUTOS_ADMIN
async function carregarProdutosAdmin() {
  produtosAdmin = await api("/api/products");
  renderizarAdmin();
}

// #SALVAR_PRODUTO
async function salvarProduto(event) {
  event.preventDefault();
  if (!autenticado) return;

  const produto = {
    nome: campos.nome.value.trim(),
    categoria: campos.categoria.value,
    img: campos.img.value.trim(),
    estoque: Math.max(0, Number(campos.estoque.value || 0)),
    preco5: campos.preco5.value.trim(),
    preco10: campos.preco10.value.trim(),
    promocao: campos.promocao.checked,
    precoPromocional5: campos.precoPromocional5.value.trim(),
    precoPromocional10: campos.precoPromocional10.value.trim(),
    destaque: campos.destaque.checked,
    selo: campos.selo.value.trim(),
    chamada: campos.chamada.value.trim()
  };

  const indice = campos.indice.value;
  const produtoAtual = indice === "" ? null : produtosAdmin[Number(indice)];
  const url = produtoAtual ? `/api/products/${produtoAtual.id}` : "/api/products";

  await api(url, {
    method: produtoAtual ? "PUT" : "POST",
    body: JSON.stringify(produto)
  });

  limparFormulario();
  await carregarProdutosAdmin();
}

// #EDITAR_PRODUTO
function editarProduto(indice) {
  const produto = produtosAdmin[indice];
  if (!produto) return;

  campos.indice.value = indice;
  campos.nome.value = produto.nome || "";
  campos.categoria.value = produto.categoria || "masculino";
  campos.img.value = produto.img || "";
  campos.estoque.value = produto.estoque ?? 0;
  campos.preco5.value = produto.preco5 || "";
  campos.preco10.value = produto.preco10 || "";
  campos.promocao.checked = Boolean(produto.promocao);
  campos.precoPromocional5.value = produto.precoPromocional5 || "";
  campos.precoPromocional10.value = produto.precoPromocional10 || "";
  campos.destaque.checked = Boolean(produto.destaque);
  campos.selo.value = produto.selo || "";
  campos.chamada.value = produto.chamada || "";

  atualizarModoFormulario("editar");
  excluirProduto.hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// #EXCLUIR_PRODUTO_SELECIONADO
async function excluirProdutoSelecionado() {
  const indice = Number(campos.indice.value);
  if (!Number.isInteger(indice)) return;

  const produto = produtosAdmin[indice];
  const confirmar = window.confirm(`Excluir "${produto.nome}" do catalogo?`);
  if (!confirmar) return;

  await api(`/api/products/${produto.id}`, { method: "DELETE" });
  limparFormulario();
  await carregarProdutosAdmin();
}

// #LIMPAR_FORMULARIO
function limparFormulario() {
  produtoForm.reset();
  campos.indice.value = "";
  campos.estoque.value = 10;
  campos.categoria.value = "masculino";
  atualizarModoFormulario("adicionar");
  excluirProduto.hidden = true;
  produtoForm.scrollIntoView({ behavior: "smooth", block: "start" });
}

// #ATUALIZAR_MODO_FORMULARIO
function atualizarModoFormulario(modo) {
  const editando = modo === "editar";
  formTitulo.textContent = editando ? "Editar produto" : "Adicionar produto";
  formTitulo.classList.toggle("editar", editando);
  formTitulo.classList.toggle("adicionar", !editando);
}

// #RESETAR_CATALOGO
async function resetarCatalogo() {
  const confirmar = window.confirm("Restaurar o catalogo original? As alteracoes salvas no banco serao apagadas.");
  if (!confirmar) return;

  await api("/api/products/reset", { method: "POST" });
  limparFormulario();
  await carregarProdutosAdmin();
}

// #RENDERIZAR_ADMIN
function renderizarAdmin() {
  atualizarResumo();

  const busca = normalizarAdmin(buscaAdmin.value);
  const produtosFiltrados = produtosAdmin
    .map((produto, indice) => ({ produto, indice }))
    .filter(item => filtrarProdutoAdmin(item.produto))
    .filter(item => !busca || normalizarAdmin(item.produto.nome).includes(busca));

  if (!produtosFiltrados.length) {
    adminProdutos.innerHTML = '<p class="admin-vazio">Nenhum produto encontrado para esse filtro.</p>';
    return;
  }

  adminProdutos.innerHTML = produtosFiltrados.map(({ produto, indice }) => `
    <article class="admin-produto-card ${produto.estoque > 0 ? "" : "sem-estoque"}">
      <div class="admin-produto-imagem">
        <img src="${produto.img}" alt="${produto.nome}">
      </div>
      <div>
        <div class="admin-produto-titulo">
          <h3>${produto.nome}</h3>
          <span>${produto.categoria}</span>
        </div>
        <p>5ml R$ ${precoFinalAdmin(produto, 5)} <strong>|</strong> 10ml R$ ${precoFinalAdmin(produto, 10)}</p>
        <div class="admin-flags">
          <strong>${produto.estoque > 0 ? `Estoque ${produto.estoque}` : "Esgotado"}</strong>
          ${produto.promocao ? "<strong>Promocao</strong>" : ""}
          ${produto.destaque ? "<strong>Destaque</strong>" : ""}
        </div>
      </div>
      <button class="admin-btn secundario" type="button" onclick="editarProduto(${indice})">Editar</button>
    </article>
  `).join("");
}

// #FILTRAR_ADMIN
function filtrarAdmin(event) {
  filtroAdmin = event.currentTarget.dataset.filtro || "todos";
  filtrosAdmin.forEach(botao => botao.classList.toggle("ativo", botao.dataset.filtro === filtroAdmin));
  renderizarAdmin();
}

// #FILTRAR_PRODUTO_ADMIN
function filtrarProdutoAdmin(produto) {
  if (filtroAdmin === "estoque") return Number(produto.estoque || 0) > 0;
  if (filtroAdmin === "promocao") return Boolean(produto.promocao);
  if (filtroAdmin === "destaque") return Boolean(produto.destaque);
  if (filtroAdmin === "esgotado") return Number(produto.estoque || 0) <= 0;
  return true;
}

// #ATUALIZAR_RESUMO
function atualizarResumo() {
  document.getElementById("totalProdutos").textContent = produtosAdmin.length;
  document.getElementById("totalEstoque").textContent = produtosAdmin.reduce((total, produto) => total + Number(produto.estoque || 0), 0);
  document.getElementById("totalPromocoes").textContent = produtosAdmin.filter(produto => produto.promocao).length;
  document.getElementById("totalDestaques").textContent = produtosAdmin.filter(produto => produto.destaque).length;
}

// #PRECO_FINAL_ADMIN
function precoFinalAdmin(produto, volume) {
  if (volume === 10) {
    return produto.promocao && produto.precoPromocional10 ? produto.precoPromocional10 : produto.preco10;
  }

  return produto.promocao && produto.precoPromocional5 ? produto.precoPromocional5 : produto.preco5;
}

// #NORMALIZAR_ADMIN
function normalizarAdmin(texto) {
  return String(texto || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

// #MASCARAR_TELEFONE
function mascararTelefone(event) {
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

// #API
async function api(url, options = {}) {
  const resposta = await fetch(url, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });

  const texto = await resposta.text();
  const dados = texto ? JSON.parse(texto) : {};

  if (!resposta.ok) {
    throw new Error(dados.error || "Erro ao comunicar com o servidor.");
  }

  return dados;
}
