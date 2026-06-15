const { test, expect } = require("@playwright/test");

test("carrega catalogo, filtra e adiciona produto ao carrinho", async ({ page }) => {
  const pageErrors = [];
  page.on("pageerror", error => pageErrors.push(error.message));

  await page.goto("/index.html");
  await expect(page).toHaveTitle(/Decant's Perfumaria/);
  await expect(page.locator("h1")).toContainText("Decant's Perfumaria");
  await expect(page.locator("#masculinosContainer .card").first()).toBeVisible();

  await page.locator("#searchInput").fill("Dior Sauvage");
  await expect(page.locator("#masculinosContainer .card")).toHaveCount(1);

  await page.locator("#masculinosContainer .btn-comprar").click();
  await expect(page.locator(".carrinho-confirmacao")).toBeVisible();
  await page.locator(".carrinho-confirmacao a").click();

  await expect(page).toHaveURL(/carrinho\.html/);
  await expect(page.locator(".carrinho-item")).toHaveCount(1);
  await expect(page.locator("#carrinhoTotal")).not.toHaveText("R$ 0,00");
  expect(pageErrors).toEqual([]);
});

test("abre detalhes do produto e mantem cabecalhos de seguranca", async ({ page }) => {
  const response = await page.goto("/produtos.html?categoria=masculino");
  expect(response.headers()["content-security-policy"]).toContain("default-src 'self'");
  expect(response.headers()["cache-control"]).toBe("no-cache, must-revalidate");

  await expect(page.locator("#catalogoPagina .catalogo-card").first()).toBeVisible();
  await page.locator("#catalogoPagina .btn-ver-mais").first().click();
  await expect(page.locator(".modal-produto")).toBeVisible();
  await expect(page.locator(".modal-produto h2")).not.toBeEmpty();
});

test("menu mobile abre e fecha de forma acessivel", async ({ page }, testInfo) => {
  test.skip(!testInfo.project.name.includes("mobile"), "Fluxo exclusivo do projeto mobile");
  await page.goto("/index.html");

  const button = page.locator(".menu-mobile-botao");
  await button.click();
  await expect(button).toHaveAttribute("aria-expanded", "true");
  await expect(page.locator("#menuPrincipal")).toHaveClass(/menu-aberto/);

  await button.click();
  await expect(button).toHaveAttribute("aria-expanded", "false");
});

test("registra solicitacao LGPD e exibe protocolo", async ({ page }) => {
  await page.goto("/politica-de-privacidade.html");
  await page.locator("#lgpdNome").fill("Titular Navegador");
  await page.locator("#lgpdEmail").fill("titular-navegador@example.com");
  await page.locator("#lgpdTelefone").fill("(88) 99999-1234");
  await page.locator("#lgpdCategoria").selectOption("access");
  await page.locator("#lgpdDetalhes").fill("Solicito uma copia dos dados pessoais mantidos pela loja.");
  await page.locator("#lgpdForm button[type='submit']").click();
  await expect(page.locator("#lgpdMensagem")).toContainText(/Protocolo LGPD/);
});

test("cliente autenticado registra devolucao pelo pedido", async ({ page }, testInfo) => {
  const suffix = testInfo.project.name.includes("mobile") ? "mobile" : "desktop";
  await page.goto("/index.html");
  const checkout = await page.request.post("/api/checkout", {
    data: {
      customer: {
        name: "Cliente Navegador",
        email: `cliente-${suffix}@example.com`,
        phone: suffix === "mobile" ? "(88) 98765-1112" : "(88) 98765-1111",
        address: "Rua Teste, 123",
        document: "52998224725",
        postalCode: "60000-000"
      },
      items: [{ productId: 1, volume: 5, quantity: 1 }],
      paymentMethod: "whatsapp"
    }
  });
  expect(checkout.ok()).toBeTruthy();

  await page.goto("/meus-pedidos.html");
  await expect(page.locator("#devolucaoPedido option").first()).toBeAttached();
  await page.locator("#devolucaoCategoria").selectOption("vazamento");
  await page.locator("#devolucaoMotivo").fill("Frasco com vazamento");
  await page.locator("#devolucaoDetalhes").fill("O produto chegou com liquido dentro da embalagem.");
  await page.locator("#devolucaoAceite").check();
  await page.locator("#devolucaoForm button[type='submit']").click();
  await expect(page.locator("#devolucaoMensagem")).toContainText(/Protocolo DEV/);
  await expect(page.locator("#solicitacoesLista .solicitacao-card")).toHaveCount(1);
});

test("administrador consulta e analisa solicitacao", async ({ page }) => {
  await page.goto("/politica-de-privacidade.html");
  await page.locator("#lgpdNome").fill("Titular Painel");
  await page.locator("#lgpdEmail").fill("titular-painel@example.com");
  await page.locator("#lgpdCategoria").selectOption("correction");
  await page.locator("#lgpdDetalhes").fill("Preciso corrigir uma informacao cadastral mantida pela loja.");
  await page.locator("#lgpdForm button[type='submit']").click();
  await expect(page.locator("#lgpdMensagem")).toContainText(/Protocolo LGPD/);
  const protocolText = await page.locator("#lgpdMensagem").textContent();
  const protocol = protocolText.match(/LGPD[A-F0-9]+/)?.[0];
  expect(protocol).toBeTruthy();

  await page.goto("/login");
  await page.locator("#loginEmail").fill("admin@example.com");
  await page.locator("#loginPassword").fill("SenhaE2E123!");
  await Promise.all([
    page.waitForResponse(
      response => response.url().endsWith("/api/login") && response.status() === 200
    ),
    page.locator("#loginForm button[type='submit']").click()
  ]);
  await expect(page).toHaveURL(/dashboard/);
  await page.locator('a[data-route="solicitacoes"]').click();
  await page.locator("#requestSearch").fill(protocol);
  await expect(page.locator("#requestsList")).toContainText(protocol);
  await page.locator("#requestsList button").click();
  await page.locator("#requestStatus").selectOption("completed");
  await page.locator("#requestResolution").fill("Dados corrigidos e confirmados ao titular.");
  await page.locator("#requestDetail button.primary-btn").click();
  await expect(page.locator("#requestStatus")).toHaveValue("completed");
});
