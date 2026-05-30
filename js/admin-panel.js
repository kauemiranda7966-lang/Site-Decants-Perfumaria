const state = {
  csrfToken: "",
  user: "",
  products: [],
  orders: [],
  customers: [],
  logs: []
};

const routes = {
  "/login": "login",
  "/dashboard": "dashboard",
  "/produtos": "produtos",
  "/pedidos": "pedidos",
  "/clientes": "clientes",
  "/logs": "logs"
};

const titles = {
  dashboard: ["Operacao", "Dashboard"],
  produtos: ["Catalogo", "Produtos"],
  pedidos: ["Pedidos", "Gerenciamento de pedidos"],
  clientes: ["Clientes", "Base de clientes"],
  logs: ["Seguranca", "Logs administrativos"]
};

const els = {
  loginView: document.getElementById("loginView"),
  appView: document.getElementById("appView"),
  loginForm: document.getElementById("loginForm"),
  loginError: document.getElementById("loginError"),
  logoutButton: document.getElementById("logoutButton"),
  sectionEyebrow: document.getElementById("sectionEyebrow"),
  sectionTitle: document.getElementById("sectionTitle"),
  sessionUser: document.getElementById("sessionUser"),
  dashboardSection: document.getElementById("dashboardSection"),
  productsSection: document.getElementById("productsSection"),
  ordersSection: document.getElementById("ordersSection"),
  customersSection: document.getElementById("customersSection"),
  logsSection: document.getElementById("logsSection"),
  productForm: document.getElementById("productForm"),
  productMessage: document.getElementById("productMessage"),
  productsList: document.getElementById("productsList"),
  productSearch: document.getElementById("productSearch"),
  newProductButton: document.getElementById("newProductButton"),
  deleteProductButton: document.getElementById("deleteProductButton"),
  ordersList: document.getElementById("ordersList"),
  orderStatusFilter: document.getElementById("orderStatusFilter"),
  customersList: document.getElementById("customersList"),
  customerSearch: document.getElementById("customerSearch"),
  logsList: document.getElementById("logsList"),
  orderDialog: document.getElementById("orderDialog"),
  orderDetail: document.getElementById("orderDetail")
};

document.addEventListener("click", handleNavigation);
window.addEventListener("popstate", renderRoute);
els.loginForm.addEventListener("submit", login);
els.logoutButton.addEventListener("click", logout);
els.productForm.addEventListener("submit", saveProduct);
els.newProductButton.addEventListener("click", resetProductForm);
els.deleteProductButton.addEventListener("click", deleteProduct);
els.productSearch.addEventListener("input", renderProducts);
els.orderStatusFilter.addEventListener("change", renderOrders);
els.customerSearch.addEventListener("input", renderCustomers);

init();

async function init() {
  const session = await api("/api/session", { public: true });
  state.csrfToken = session.csrfToken || "";
  state.user = session.user || "";

  if (!session.authenticated) {
    showLogin();
    return;
  }

  els.sessionUser.textContent = state.user;
  els.loginView.hidden = true;
  els.appView.hidden = false;
  await loadAll();
  renderRoute();
}

async function loadAll() {
  const [dashboard, products, orders, customers, logs] = await Promise.all([
    api("/api/admin/dashboard"),
    api("/api/products"),
    api("/api/admin/orders"),
    api("/api/admin/customers"),
    api("/api/admin/logs")
  ]);
  state.products = products;
  state.orders = orders;
  state.customers = customers;
  state.logs = logs;
  renderDashboard(dashboard);
  renderProducts();
  renderOrders();
  renderCustomers();
  renderLogs();
}

function showLogin() {
  history.replaceState({}, "", "/login");
  els.loginView.hidden = false;
  els.appView.hidden = true;
}

async function login(event) {
  event.preventDefault();
  els.loginError.hidden = true;
  try {
    const response = await api("/api/login", {
      method: "POST",
      body: JSON.stringify({
        user: document.getElementById("loginEmail").value.trim(),
        password: document.getElementById("loginPassword").value
      })
    });
    state.csrfToken = response.csrfToken || state.csrfToken;
    state.user = response.user || "";
    els.sessionUser.textContent = state.user;
    els.loginForm.reset();
    els.loginView.hidden = true;
    els.appView.hidden = false;
    history.replaceState({}, "", "/dashboard");
    await loadAll();
    renderRoute();
  } catch (error) {
    els.loginError.textContent = error.message;
    els.loginError.hidden = false;
  }
}

async function logout() {
  await api("/api/logout", { method: "POST" });
  showLogin();
}

function handleNavigation(event) {
  const link = event.target.closest("a[data-route]");
  if (!link) return;
  event.preventDefault();
  history.pushState({}, "", link.getAttribute("href"));
  renderRoute();
}

function renderRoute() {
  const route = routes[window.location.pathname] || "dashboard";
  if (route === "login") {
    showLogin();
    return;
  }

  document.querySelectorAll(".nav-menu a").forEach(link => {
    link.classList.toggle("active", link.dataset.route === route);
  });

  const [eyebrow, title] = titles[route] || titles.dashboard;
  els.sectionEyebrow.textContent = eyebrow;
  els.sectionTitle.textContent = title;

  els.dashboardSection.hidden = route !== "dashboard";
  els.productsSection.hidden = route !== "produtos";
  els.ordersSection.hidden = route !== "pedidos";
  els.customersSection.hidden = route !== "clientes";
  els.logsSection.hidden = route !== "logs";
}

function renderDashboard(data) {
  setText("metricSales", brl(data.totalSales));
  setText("metricOrders", data.totalOrders);
  setText("metricProducts", data.productCount);
  setText("metricCustomers", data.customerCount);
  setText("metricPaid", brl(data.paidSales));
  setText("metricStock", brl(data.stockValue));
  setText("financeSales", brl(data.totalSales));
  setText("financePaid", brl(data.paidSales));
  setText("financeStock", brl(data.stockValue));

  document.getElementById("recentOrders").innerHTML = (data.recentOrders || []).map(order => `
    <article>
      <strong>${escapeHtml(order.reference)}</strong>
      <p>${escapeHtml(order.customer_name)} · ${brl(order.total)} · <span class="status-pill ${order.status}">${labelStatus(order.status)}</span></p>
    </article>
  `).join("") || empty("Nenhum pedido registrado.");
}

function renderProducts() {
  const search = normalize(els.productSearch.value);
  const products = state.products.filter(product => !search || normalize(product.nome).includes(search));
  els.productsList.innerHTML = products.map(product => `
    <article class="product-card">
      <img src="${escapeAttr(product.img)}" alt="${escapeAttr(product.nome)}">
      <div>
        <h3>${escapeHtml(product.nome)}</h3>
        <p>${escapeHtml(product.categoria)} · Estoque ${product.estoque} · 5ml R$ ${priceOf(product, 5)} · 10ml R$ ${priceOf(product, 10)}</p>
      </div>
      <button class="ghost-btn" type="button" onclick="editProduct(${product.id})">Editar</button>
    </article>
  `).join("") || empty("Nenhum produto encontrado.");
}

window.editProduct = function editProduct(id) {
  const product = state.products.find(item => item.id === id);
  if (!product) return;
  setValue("productId", product.id);
  setValue("productName", product.nome);
  setValue("productCategory", product.categoria);
  setValue("productStock", product.estoque);
  setValue("productPrice5", product.preco5);
  setValue("productPrice10", product.preco10);
  setValue("productImage", product.img);
  setValue("productPromo5", product.precoPromocional5);
  setValue("productPromo10", product.precoPromocional10);
  setValue("productBadge", product.selo);
  setValue("productCallout", product.chamada);
  document.getElementById("productPromo").checked = Boolean(product.promocao);
  document.getElementById("productFeatured").checked = Boolean(product.destaque);
  document.getElementById("productFormTitle").textContent = "Editar produto";
  els.deleteProductButton.hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
};

async function saveProduct(event) {
  event.preventDefault();
  const imageFile = document.getElementById("productImageFile").files[0];
  let imageUrl = document.getElementById("productImage").value.trim();

  if (imageFile) {
    const upload = new FormData();
    upload.append("image", imageFile);
    const result = await api("/api/admin/upload", { method: "POST", body: upload, skipJsonHeader: true });
    imageUrl = result.url;
    setValue("productImage", imageUrl);
  }

  const id = document.getElementById("productId").value;
  const payload = {
    nome: value("productName"),
    categoria: value("productCategory"),
    img: imageUrl,
    estoque: Number(value("productStock") || 0),
    preco5: value("productPrice5"),
    preco10: value("productPrice10"),
    promocao: document.getElementById("productPromo").checked,
    precoPromocional5: value("productPromo5"),
    precoPromocional10: value("productPromo10"),
    destaque: document.getElementById("productFeatured").checked,
    selo: value("productBadge"),
    chamada: value("productCallout")
  };

  await api(id ? `/api/products/${id}` : "/api/products", {
    method: id ? "PUT" : "POST",
    body: JSON.stringify(payload)
  });

  showProductMessage("Produto salvo com sucesso.", true);
  resetProductForm(false);
  state.products = await api("/api/products");
  renderProducts();
}

async function deleteProduct() {
  const id = document.getElementById("productId").value;
  if (!id || !window.confirm("Excluir este produto do catalogo?")) return;
  await api(`/api/products/${id}`, { method: "DELETE" });
  resetProductForm();
  state.products = await api("/api/products");
  renderProducts();
}

function resetProductForm(clearMessage = true) {
  els.productForm.reset();
  setValue("productId", "");
  setValue("productStock", 10);
  document.getElementById("productFormTitle").textContent = "Adicionar produto";
  els.deleteProductButton.hidden = true;
  if (clearMessage) els.productMessage.hidden = true;
}

function renderOrders() {
  const status = els.orderStatusFilter.value;
  const orders = state.orders.filter(order => !status || order.status === status);
  els.ordersList.innerHTML = orders.map(order => `
    <article class="table-row">
      <div>
        <h3>${escapeHtml(order.reference)} · ${escapeHtml(order.customer_name)}</h3>
        <p>${escapeHtml(order.customer_email)} · ${dateTime(order.created_at)}</p>
      </div>
      <div>
        <strong>${brl(order.total)}</strong><br>
        <span class="status-pill ${order.status}">${labelStatus(order.status)}</span>
      </div>
      <button class="ghost-btn" type="button" onclick="openOrder(${order.id})">Detalhes</button>
    </article>
  `).join("") || empty("Nenhum pedido encontrado.");
}

window.openOrder = async function openOrder(id) {
  const order = await api(`/api/admin/orders/${id}`);
  els.orderDetail.innerHTML = `
    <h2>Pedido ${escapeHtml(order.reference)}</h2>
    <p>${escapeHtml(order.customer_name)} · ${escapeHtml(order.customer_email)} · ${escapeHtml(order.customer_phone)}</p>
    <div class="detail-block">
      <article><strong>Total</strong><p>${brl(order.total)} · <span class="status-pill ${order.status}">${labelStatus(order.status)}</span></p></article>
      <article><strong>Endereco</strong><p>${escapeHtml(order.customer_address || "Nao informado")}</p></article>
      <article>
        <strong>Itens</strong>
        ${(order.items || []).map(item => `<p>${item.quantity}x ${escapeHtml(item.product_name)} ${item.volume}ml · ${brl(item.subtotal)}</p>`).join("")}
      </article>
      <article>
        <strong>Atualizar status</strong>
        <div class="form-row">
          <select id="detailStatus">
            ${statusOptions(order.status)}
          </select>
          <input id="detailNote" placeholder="Observacao">
        </div>
        <button class="primary-btn" type="button" onclick="updateOrderStatus(${order.id})">Salvar status</button>
      </article>
      <article>
        <strong>Historico</strong>
        ${(order.history || []).map(item => `<p>${dateTime(item.created_at)} · ${labelStatus(item.old_status)} -> ${labelStatus(item.new_status)} ${item.note ? "· " + escapeHtml(item.note) : ""}</p>`).join("") || "<p>Sem historico.</p>"}
      </article>
    </div>
  `;
  if (!els.orderDialog.open) els.orderDialog.showModal();
};

window.updateOrderStatus = async function updateOrderStatus(id) {
  await api(`/api/admin/orders/${id}/status`, {
    method: "PUT",
    body: JSON.stringify({
      status: document.getElementById("detailStatus").value,
      note: document.getElementById("detailNote").value
    })
  });
  state.orders = await api("/api/admin/orders");
  renderOrders();
  await window.openOrder(id);
};

function renderCustomers() {
  const search = normalize(els.customerSearch.value);
  const customers = state.customers.filter(customer => {
    const haystack = normalize(`${customer.name} ${customer.email} ${customer.phone}`);
    return !search || haystack.includes(search);
  });

  els.customersList.innerHTML = customers.map(customer => `
    <article class="table-row">
      <div>
        <h3>${escapeHtml(customer.name || "Cliente")}</h3>
        <p>${escapeHtml(customer.email)} · ${escapeHtml(customer.phone || "")}</p>
      </div>
      <div>
        <strong>${brl(customer.total_spent || 0)}</strong><br>
        <span>${customer.order_count || 0} compras</span>
      </div>
      <span>${dateTime(customer.last_order_at)}</span>
    </article>
  `).join("") || empty("Nenhum cliente encontrado.");
}

function renderLogs() {
  els.logsList.innerHTML = state.logs.map(log => `
    <article class="table-row">
      <div>
        <h3>${escapeHtml(log.action)}</h3>
        <p>${escapeHtml(log.entity)} #${escapeHtml(log.entity_id)} · ${escapeHtml(log.details || "")}</p>
      </div>
      <div><span>${escapeHtml(log.ip || "")}</span></div>
      <span>${dateTime(log.created_at)}</span>
    </article>
  `).join("") || empty("Nenhuma acao registrada.");
}

async function api(url, options = {}) {
  const headers = options.skipJsonHeader ? {} : { "Content-Type": "application/json" };
  if (state.csrfToken && !options.public) headers["X-CSRF-Token"] = state.csrfToken;

  const response = await fetch(url, {
    credentials: "include",
    ...options,
    headers: { ...headers, ...(options.headers || {}) }
  });
  const text = await response.text();
  const data = text ? JSON.parse(text) : {};
  if (!response.ok) throw new Error(data.error || "Erro ao comunicar com o painel.");
  if (data.csrfToken) state.csrfToken = data.csrfToken;
  return data;
}

function statusOptions(selected) {
  return [
    "whatsapp_pending", "awaiting_payment", "pending", "approved",
    "preparing", "shipped", "delivered", "cancelled", "refunded"
  ].map(status => `<option value="${status}" ${status === selected ? "selected" : ""}>${labelStatus(status)}</option>`).join("");
}

function labelStatus(status) {
  const labels = {
    whatsapp_pending: "WhatsApp pendente",
    awaiting_payment: "Aguardando pagamento",
    pending: "Pendente",
    approved: "Aprovado",
    preparing: "Preparando",
    shipped: "Enviado",
    delivered: "Entregue",
    cancelled: "Cancelado",
    refunded: "Reembolsado",
    paid: "Pago",
    completed: "Concluido"
  };
  return labels[status] || status || "Sem status";
}

function priceOf(product, volume) {
  if (volume === 10) return product.promocao && product.precoPromocional10 ? product.precoPromocional10 : product.preco10;
  return product.promocao && product.precoPromocional5 ? product.precoPromocional5 : product.preco5;
}

function brl(value) {
  return Number(value || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function dateTime(value) {
  if (!value) return "";
  return new Date(String(value).replace(" ", "T")).toLocaleString("pt-BR");
}

function normalize(value) {
  return String(value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[char]));
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/`/g, "&#96;");
}

function empty(message) {
  return `<p class="form-message ok">${escapeHtml(message)}</p>`;
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function value(id) {
  return document.getElementById(id).value.trim();
}

function setValue(id, valueToSet) {
  document.getElementById(id).value = valueToSet ?? "";
}

function showProductMessage(message, ok) {
  els.productMessage.textContent = message;
  els.productMessage.classList.toggle("ok", Boolean(ok));
  els.productMessage.hidden = false;
}
