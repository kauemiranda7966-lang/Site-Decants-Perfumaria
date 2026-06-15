const state = {
  csrfToken: "",
  user: "",
  products: [],
  orders: [],
  customers: [],
  requests: [],
  logs: [],
  activeOrderStatus: "all"
};

const routes = {
  "/login": "login",
  "/dashboard": "dashboard",
  "/produtos": "produtos",
  "/pedidos": "pedidos",
  "/clientes": "clientes",
  "/solicitacoes": "solicitacoes",
  "/logs": "logs"
};

const titles = {
  dashboard: ["Operacao", "Dashboard"],
  produtos: ["Catalogo", "Produtos"],
  pedidos: ["Pedidos", "Gerenciamento de pedidos"],
  clientes: ["Clientes", "Base de clientes"],
  solicitacoes: ["Privacidade e pos-venda", "Solicitacoes"],
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
  requestsSection: document.getElementById("requestsSection"),
  logsSection: document.getElementById("logsSection"),
  productForm: document.getElementById("productForm"),
  productMessage: document.getElementById("productMessage"),
  productsList: document.getElementById("productsList"),
  productSearch: document.getElementById("productSearch"),
  newProductButton: document.getElementById("newProductButton"),
  deleteProductButton: document.getElementById("deleteProductButton"),
  ordersList: document.getElementById("ordersList"),
  orderTabs: document.getElementById("orderTabs"),
  orderSearch: document.getElementById("orderSearch"),
  orderSearchResult: document.getElementById("orderSearchResult"),
  customersList: document.getElementById("customersList"),
  customerSearch: document.getElementById("customerSearch"),
  requestsList: document.getElementById("requestsList"),
  requestSearch: document.getElementById("requestSearch"),
  logsList: document.getElementById("logsList"),
  orderDialog: document.getElementById("orderDialog"),
  orderDetail: document.getElementById("orderDetail"),
  requestDialog: document.getElementById("requestDialog"),
  requestDetail: document.getElementById("requestDetail")
};

document.addEventListener("click", handleNavigation);
window.addEventListener("popstate", renderRoute);
els.loginForm.addEventListener("submit", login);
els.logoutButton.addEventListener("click", logout);
els.productForm.addEventListener("submit", saveProduct);
els.newProductButton.addEventListener("click", resetProductForm);
els.deleteProductButton.addEventListener("click", deleteProduct);
els.productSearch.addEventListener("input", renderProducts);
els.orderTabs.addEventListener("click", handleOrderTabClick);
els.orderSearch.addEventListener("input", renderOrders);
els.customerSearch.addEventListener("input", renderCustomers);
els.requestSearch.addEventListener("input", renderRequests);

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
  const [dashboard, products, orders, customers, requests, logs] = await Promise.all([
    api("/api/admin/dashboard"),
    api("/api/products"),
    api("/api/admin/orders"),
    api("/api/admin/customers"),
    api("/api/admin/requests"),
    api("/api/admin/logs")
  ]);
  state.products = products;
  state.orders = orders;
  state.customers = customers;
  state.requests = requests;
  state.logs = logs;
  renderDashboard(dashboard);
  renderProducts();
  renderOrders();
  renderCustomers();
  renderRequests();
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
  els.requestsSection.hidden = route !== "solicitacoes";
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
      <img src="${escapeAttr(product.img)}" alt="${escapeAttr(product.nome)}" loading="lazy">
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
  const search = normalize(els.orderSearch.value);
  const matchedOrder = search
    ? state.orders.find(order => normalize(order.reference).includes(search))
    : null;

  renderOrderSearchResult(matchedOrder, search);
  renderOrderTabs();

  const orders = state.orders.filter(order => {
    const operationalStatus = orderOperationalStatus(order.status);
    const matchesStatus = state.activeOrderStatus === "all" || operationalStatus === state.activeOrderStatus;
    const matchesSearch = !search || normalize(order.reference).includes(search);
    return matchesStatus && matchesSearch;
  });
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

function handleOrderTabClick(event) {
  const tab = event.target.closest("button[data-status]");
  if (!tab) return;
  state.activeOrderStatus = tab.dataset.status;
  renderOrders();
}

function renderOrderTabs() {
  const totals = state.orders.reduce((acc, order) => {
    const status = orderOperationalStatus(order.status);
    acc.all = (acc.all || 0) + 1;
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, {});

  els.orderTabs.querySelectorAll("button[data-status]").forEach(button => {
    const baseLabel = button.dataset.label || button.textContent.replace(/\s+\d+$/, "");
    button.dataset.label = baseLabel;
    button.textContent = `${baseLabel} ${totals[button.dataset.status] || 0}`;
    button.classList.toggle("active", button.dataset.status === state.activeOrderStatus);
  });
}

function renderOrderSearchResult(order, search) {
  if (!search) {
    els.orderSearchResult.hidden = true;
    els.orderSearchResult.innerHTML = "";
    return;
  }

  if (!order) {
    els.orderSearchResult.hidden = false;
    els.orderSearchResult.innerHTML = "Pedido nao encontrado.";
    return;
  }

  const status = orderOperationalStatus(order.status);
  els.orderSearchResult.hidden = false;
  els.orderSearchResult.innerHTML = `
    <strong>${escapeHtml(order.reference)}</strong>
    <span>${escapeHtml(order.customer_name)} esta em <b>${labelStatus(status)}</b>.</span>
    <button class="ghost-btn" type="button" onclick="openOrder(${order.id})">Detalhes</button>
  `;
}

window.openOrder = async function openOrder(id) {
  const order = await api(`/api/admin/orders/${id}`);
  els.orderDetail.innerHTML = `
    <h2>Pedido ${escapeHtml(order.reference)}</h2>
    ${order.payment_risk_status ? `
      <div class="payment-risk-alert">
        <strong>Envio bloqueado por risco financeiro</strong>
        <p>${escapeHtml(order.payment_risk_reason || "Analise o alerta antes de prosseguir.")}</p>
      </div>
    ` : ""}
    <div class="order-detail-actions">
      <a class="primary-btn" href="/api/admin/orders/${order.id}/label.pdf" download>Baixar kit de expedicao</a>
      <button class="ghost-btn" type="button" onclick="printShippingLabel(${order.id})">Imprimir kit</button>
    </div>
    <div class="detail-block order-detail-vertical">
      <article><strong>Número do pedido</strong><p>${escapeHtml(order.reference)}</p></article>
      <article><strong>Valor dos produtos</strong><p>${brl(order.product_amount)}</p></article>
      <article><strong>Valor do frete</strong><p>${brl(order.shipping_amount)}</p></article>
      <article><strong>Valor total</strong><p>${brl(order.total)}</p></article>
      <article><strong>Forma de pagamento</strong><p>${escapeHtml(paymentMethodLabel(order.payment_method))}</p></article>
      <article><strong>Status</strong><p><span class="status-pill ${order.status}">${labelStatus(order.status)}</span></p></article>
      <article><strong>Nome completo</strong><p>${escapeHtml(order.customer_name)}</p></article>
      <article><strong>WhatsApp</strong><p>${escapeHtml(order.customer_phone)}</p></article>
      <article><strong>E-mail</strong><p>${escapeHtml(order.customer_email)}</p></article>
      <article><strong>CPF/CNPJ de postagem</strong><p>${escapeHtml(order.customer_document || "Nao informado")}</p></article>
      <article><strong>CEP</strong><p>${formatPostalCode(order.customer_postal_code)}</p></article>
      <article><strong>Endereço</strong><p>${escapeHtml(order.customer_address || "Não informado")}</p></article>
      <article>
        <strong>Itens</strong>
        ${(order.items || []).map(item => `<p>${item.quantity}x ${escapeHtml(item.product_name)} ${item.volume}ml · ${brl(item.subtotal)}</p>`).join("")}
      </article>
      <article>
        <strong>Alertas de pagamento</strong>
        ${(order.paymentAlerts || []).map(alert => `
          <p><b>${paymentAlertLabel(alert.event_type)}</b> · ${dateTime(alert.created_at)}<br>${escapeHtml(alert.details || "")} · ID ${escapeHtml(alert.event_id)}</p>
        `).join("") || "<p>Nenhum alerta financeiro.</p>"}
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

window.printShippingLabel = function printShippingLabel(id) {
  const popup = window.open(`/api/admin/orders/${id}/label.pdf?print=1`, "_blank", "noopener");
  if (!popup) window.alert("Permita pop-ups para imprimir a etiqueta.");
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

function renderRequests() {
  const search = normalize(els.requestSearch.value);
  const requests = state.requests.filter(item => {
    const haystack = normalize(`${item.protocol} ${item.customer_name} ${item.customer_email} ${item.order_reference || ""}`);
    return !search || haystack.includes(search);
  });
  els.requestsList.innerHTML = requests.map(item => `
    <article class="table-row">
      <div>
        <h3>${escapeHtml(item.protocol)} · ${item.request_type === "privacy" ? "LGPD" : "Devolucao"}</h3>
        <p>${escapeHtml(item.customer_name)} · ${escapeHtml(item.customer_email)} ${item.order_reference ? "· " + escapeHtml(item.order_reference) : ""}</p>
      </div>
      <div>
        <strong>${requestCategoryLabel(item.category)}</strong><br>
        <span class="status-pill ${escapeAttr(item.status)}">${requestStatusLabel(item.status)}</span>
      </div>
      <button class="ghost-btn" type="button" onclick="openRequest(${item.id})">Analisar</button>
    </article>
  `).join("") || empty("Nenhuma solicitacao registrada.");
}

window.openRequest = async function openRequest(id) {
  const item = await api(`/api/admin/requests/${id}`);
  const attachments = (item.attachments || []).map(attachment => `
    <a class="ghost-btn" target="_blank" rel="noopener" href="/api/admin/requests/${item.id}/attachments/${attachment.id}">
      ${escapeHtml(attachment.original_name)}
    </a>
  `).join("") || "<p>Sem fotos anexadas.</p>";
  const isPreSeparationCancellation = item.category === "cancelamento_antes_separacao";
  const reverseLabel = item.reverse_code
    ? `<a class="primary-btn" href="/api/admin/requests/${item.id}/reverse-label.pdf" download>Baixar etiqueta reversa</a>`
    : "";
  const refundButton = item.request_type === "return" && item.payment_id && !item.refund_id
    ? `<button class="danger-btn" type="button" onclick="refundRequest(${item.id})">Reembolsar no Mercado Pago</button>`
    : "";

  els.requestDetail.innerHTML = `
    <h2>${escapeHtml(item.protocol)}</h2>
    <div class="detail-block order-detail-vertical">
      <article><strong>Tipo</strong><p>${item.request_type === "privacy" ? "Solicitacao LGPD" : isPreSeparationCancellation ? "Cancelamento antes da separacao" : "Troca ou devolucao"}</p></article>
      <article><strong>Cliente</strong><p>${escapeHtml(item.customer_name)} · ${escapeHtml(item.customer_email)} · ${escapeHtml(item.customer_phone || "")}</p></article>
      <article><strong>Pedido</strong><p>${escapeHtml(item.order_reference || "Nao vinculado")}</p></article>
      <article><strong>Motivo</strong><p>${requestCategoryLabel(item.category)}${item.reason ? " · " + escapeHtml(item.reason) : ""}</p></article>
      <article><strong>Relato</strong><p>${escapeHtml(item.details)}</p></article>
      <article><strong>Anexos</strong><div class="request-attachments">${attachments}</div></article>
      <article>
        <strong>Analise e resultado</strong>
        <label>Status<select id="requestStatus">${requestStatusOptions(item.status)}</select></label>
        <label>Resposta ao cliente<textarea id="requestResolution" maxlength="4000">${escapeHtml(item.resolution || "")}</textarea></label>
        <button class="primary-btn" type="button" onclick="updateRequest(${item.id})">Salvar analise</button>
      </article>
      ${item.reverse_code ? `<article><strong>Codigo reverso</strong><p>${escapeHtml(item.reverse_code)}</p>${reverseLabel}</article>` : ""}
      ${item.refund_id ? `<article><strong>Reembolso</strong><p>${escapeHtml(item.refund_id)} · ${escapeHtml(item.refund_status)}</p></article>` : ""}
      ${refundButton ? `<article><strong>Financeiro</strong><p>${isPreSeparationCancellation ? "Confirme que o pedido ainda nao foi separado. Nao ha devolucao fisica nesse caso." : "Confirme a elegibilidade e o recebimento quando aplicavel antes de reembolsar."} O Mercado Pago recebe o pedido de reembolso imediatamente, mas o prazo para o cliente visualizar o credito depende do meio de pagamento.</p>${refundButton}</article>` : ""}
    </div>
  `;
  if (!els.requestDialog.open) els.requestDialog.showModal();
};

window.updateRequest = async function updateRequest(id) {
  await api(`/api/admin/requests/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      status: document.getElementById("requestStatus").value,
      resolution: document.getElementById("requestResolution").value
    })
  });
  state.requests = await api("/api/admin/requests");
  renderRequests();
  await window.openRequest(id);
};

window.refundRequest = async function refundRequest(id) {
  if (!window.confirm("Confirmar reembolso integral deste pagamento no Mercado Pago?")) return;
  await api(`/api/admin/requests/${id}/refund`, { method: "POST", body: "{}" });
  state.requests = await api("/api/admin/requests");
  state.orders = await api("/api/admin/orders");
  renderRequests();
  renderOrders();
  await window.openRequest(id);
};

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
    "creating_payment", "whatsapp_pending", "awaiting_payment", "pending", "approved",
    "to_separate", "separated", "preparing", "shipped", "delivered",
    "risk_review", "refunded", "charged_back", "cancelled", "rejected", "expired"
  ].map(status => `<option value="${status}" ${status === selected ? "selected" : ""}>${labelStatus(status)}</option>`).join("");
}

function labelStatus(status) {
  const labels = {
    creating_payment: "Criando pagamento",
    whatsapp_pending: "WhatsApp pendente",
    awaiting_payment: "Aguardando pagamento",
    pending: "Pendente",
    approved: "Aprovado",
    to_separate: "Para separar",
    separated: "Separado",
    preparing: "Preparando",
    shipped: "Enviado",
    delivered: "Entregue",
    risk_review: "Revisao de risco",
    cancelled: "Cancelado",
    rejected: "Recusado",
    expired: "Expirado",
    charged_back: "Chargeback",
    refunded: "Extorno",
    paid: "Pago",
    completed: "Concluido",
    payment_error: "Erro no pagamento"
  };
  return labels[status] || status || "Sem status";
}

function orderOperationalStatus(status) {
  const map = {
    creating_payment: "to_separate",
    awaiting_payment: "to_separate",
    whatsapp_pending: "to_separate",
    pending: "to_separate",
    approved: "to_separate",
    paid: "to_separate",
    preparing: "to_separate",
    to_separate: "to_separate",
    separated: "separated",
    shipped: "separated",
    risk_review: "risk_review",
    delivered: "delivered",
    completed: "delivered",
    refunded: "refunded",
    charged_back: "risk_review",
    rejected: "cancelled",
    expired: "cancelled",
    payment_error: "cancelled",
    cancelled: "cancelled"
  };
  return map[status] || status;
}

function paymentAlertLabel(eventType) {
  const labels = {
    stop_delivery_op_wh: "Alerta antifraude",
    topic_claims_integration_wh: "Reclamacao ou disputa",
    topic_chargebacks_wh: "Chargeback"
  };
  return labels[eventType] || eventType;
}

function requestStatusOptions(selected) {
  return ["pending", "in_review", "awaiting_customer", "awaiting_return", "approved", "rejected", "refunded", "completed"]
    .map(status => `<option value="${status}" ${status === selected ? "selected" : ""}>${requestStatusLabel(status)}</option>`)
    .join("");
}

function requestStatusLabel(status) {
  const labels = {
    pending: "Pendente",
    in_review: "Em analise",
    awaiting_customer: "Aguardando cliente",
    awaiting_return: "Aguardando devolucao",
    approved: "Aprovada",
    rejected: "Recusada",
    refunded: "Reembolsada",
    completed: "Concluida"
  };
  return labels[status] || status;
}

function requestCategoryLabel(category) {
  const labels = {
    access: "Acesso aos dados", correction: "Correcao", deletion: "Eliminacao",
    anonymization: "Anonimizacao", sharing: "Compartilhamento",
    marketing_opt_out: "Cancelar marketing", other: "Outro",
    cancelamento_antes_separacao: "Cancelamento antes da separacao",
    arrependimento: "Arrependimento", produto_incorreto: "Produto incorreto",
    avaria: "Avaria", vazamento: "Vazamento", defeito: "Qualidade", outro: "Outro"
  };
  return labels[category] || category;
}

function priceOf(product, volume) {
  if (volume === 10) return product.promocao && product.precoPromocional10 ? product.precoPromocional10 : product.preco10;
  return product.promocao && product.precoPromocional5 ? product.precoPromocional5 : product.preco5;
}

function brl(value) {
  return Number(value || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function paymentMethodLabel(value) {
  const labels = {
    credit_card: "Cartão de crédito",
    debit_card: "Cartão de débito",
    bank_transfer: "Pix / transferência",
    ticket: "Boleto",
    pix: "Pix",
    mercado_pago: "Mercado Pago"
  };
  return labels[String(value || "").toLowerCase()] || value || "Mercado Pago";
}

function formatPostalCode(value) {
  const digits = String(value || "").replace(/\D/g, "");
  return escapeHtml(digits.length === 8 ? `${digits.slice(0, 5)}-${digits.slice(5)}` : digits || "Não informado");
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
