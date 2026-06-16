# Decant's Perfumaria

Plataforma de comércio eletrônico para venda de perfumes originais em decants, com catálogo público, carrinho, checkout, pagamentos, atendimento via WhatsApp, acompanhamento de pedidos e painel administrativo.

O projeto foi desenvolvido com frontend em HTML, CSS e JavaScript, backend em Python e persistência em SQLite. A aplicação pode ser executada localmente ou publicada em serviços compatíveis com processos web Python e armazenamento persistente, como o Render.

> **Segurança:** este documento utiliza apenas valores ilustrativos. Nunca publique arquivos `.env`, tokens, senhas, chaves privadas, dados reais de clientes, conteúdo do banco SQLite ou credenciais de terceiros.

## Sumário

- [Visão geral](#visão-geral)
- [Principais funcionalidades](#principais-funcionalidades)
- [Jornada de compra](#jornada-de-compra)
- [Integrações](#integrações)
- [Painel administrativo](#painel-administrativo)
- [Arquitetura e organização](#arquitetura-e-organização)
- [Modelo de dados](#modelo-de-dados)
- [API](#api)
- [Instalação local](#instalação-local)
- [Configuração por ambiente](#configuração-por-ambiente)
- [Segurança](#segurança)
- [LGPD e privacidade](#lgpd-e-privacidade)
- [Políticas da loja](#políticas-da-loja)
- [Testes](#testes)
- [Deploy](#deploy)
- [Checklist de produção](#checklist-de-produção)

## Visão geral

A Decant's Perfumaria oferece uma experiência completa para descoberta, seleção e compra de decants de perfumes masculinos e femininos.

Um **decant** é uma fração de uma fragrância original transferida para um frasco menor. Salvo indicação expressa, o produto vendido não corresponde ao frasco comercial completo da fabricante.

A solução reúne:

- vitrine responsiva para desktop e dispositivos móveis;
- catálogo alimentado por API;
- produtos masculinos e femininos;
- opções de 5 ml e 10 ml;
- preços normais e promocionais;
- controle de estoque;
- carrinho persistente no navegador;
- checkout pelo Mercado Pago ou atendimento via WhatsApp;
- cálculo de frete por regra configurável;
- cupom de desconto;
- área de acompanhamento de pedidos;
- Clube de Ofertas;
- painel administrativo protegido;
- gestão de produtos, pedidos, clientes, imagens e logs;
- reserva e devolução automática de estoque;
- páginas públicas de termos, privacidade, entregas, trocas e devoluções.

## Principais funcionalidades

### Loja pública

- Página inicial com banner, destaques e seções por categoria.
- Carrossel de produtos destacados com reprodução automática e navegação manual.
- Catálogo separado entre perfumes masculinos e femininos.
- Busca textual por nome, categoria e características da fragrância.
- Filtros por gênero, família olfativa e intensidade.
- Cards com imagem, preços, promoção, estoque e disponibilidade.
- Identificação visual de produtos esgotados.
- Exibição de preços para 5 ml e 10 ml.
- Preços promocionais configuráveis por volume.
- Layout responsivo e menu adaptado para telas menores.

### Detalhes do produto

- Modal com informações da fragrância.
- Galeria de imagens por produto.
- Navegação entre imagens.
- Marca, família olfativa, intensidade, ocasião e notas.
- Acordes e descrição complementar.
- Seleção de volume e quantidade.
- Cálculo do subtotal.
- Compra direta ou inclusão no carrinho.
- Tratamento de imagem alternativa quando um arquivo não está disponível.

O botão visual de favorito existe na interface do produto, mas atualmente não mantém uma lista de favoritos no servidor.

### Carrinho

- Armazenamento local dos itens no navegador.
- Contador de produtos no cabeçalho.
- Inclusão de produtos em volumes diferentes.
- Alteração de volume e quantidade.
- Limitação da quantidade ao estoque conhecido.
- Seleção individual ou de todos os itens.
- Exclusão de itens selecionados.
- Atualização automática de subtotal, desconto, frete e total.
- Continuidade da compra entre páginas.
- Cupom `DECANTS5`, com 5% de desconto sobre os produtos.
- Finalização pelo Mercado Pago ou WhatsApp.

O backend recalcula preços, promoções, desconto, estoque e total. Valores enviados pelo navegador não são considerados fonte confiável.

### Frete

O cálculo atual utiliza uma regra interna, e não uma cotação em tempo real com transportadoras:

- o CEP deve possuir oito dígitos válidos;
- o frete padrão é definido por `DECANTS_SHIPPING_FEE`;
- o frete fica grátis quando o valor dos produtos atinge `DECANTS_FREE_SHIPPING_THRESHOLD`;
- o limite é inclusivo;
- o desconto do cupom é considerado antes da regra de frete;
- o prazo de transporte não é calculado automaticamente pela API.

Por padrão, o exemplo de configuração usa frete fixo de `R$ 19,90` e gratuidade a partir de `R$ 300,00`. Esses valores podem ser alterados por ambiente.

### Clube de Ofertas

A página inicial possui um formulário para captação voluntária de contatos:

- nome opcional;
- e-mail obrigatório;
- telefone ou WhatsApp obrigatório.

Os dados são validados, enviados para `POST /api/leads` e armazenados sem duplicar a mesma combinação de e-mail e telefone. Leads sem pedidos aparecem na área de clientes do painel administrativo.

### Área “Meus pedidos”

O cliente pode acessar seus pedidos informando simultaneamente:

- e-mail utilizado na compra;
- WhatsApp utilizado na compra.

Após a validação, a aplicação cria uma sessão de cliente e exibe:

- número do pedido;
- data;
- itens, volumes e quantidades;
- valor total;
- situação operacional;
- link de pagamento, quando ainda disponível;
- link de atendimento no WhatsApp.

Também existe consulta pontual por número do pedido e e-mail ou telefone correspondente. O número do pedido sozinho não autoriza o acesso.

## Jornada de compra

1. O cliente escolhe um produto, volume e quantidade.
2. O item pode ser comprado diretamente ou adicionado ao carrinho.
3. O cliente informa nome completo, e-mail, WhatsApp, CEP e endereço.
4. O servidor valida os dados e busca os produtos diretamente no banco.
5. Preços, promoções, cupom e frete são recalculados no backend.
6. O sistema cria um número de pedido no formato `DEC` seguido de oito caracteres hexadecimais.
7. O estoque é reservado imediatamente.
8. No Mercado Pago, é criada uma preferência e o cliente é redirecionado para o pagamento.
9. No WhatsApp, é gerada uma mensagem com pedido, itens, total e referência.
10. O cliente recebe automaticamente uma sessão para consultar a compra.
11. O painel acompanha o pedido até separação, entrega, cancelamento ou reembolso.

### Reserva de estoque

- Todo pedido válido reserva o estoque antes de concluir o checkout.
- Pedidos pagos mantêm a reserva durante o fluxo operacional.
- Pagamentos recusados, cancelados, expirados, reembolsados ou contestados devolvem os itens ao estoque.
- Pedidos iniciados via WhatsApp expiram após o período configurado.
- A expiração padrão do exemplo é de 30 minutos.
- A devolução de estoque é protegida contra execução duplicada.

## Integrações

### Mercado Pago

A integração cria preferências de checkout e recebe atualizações por webhook.

Recursos implementados:

- criação de preferência de pagamento;
- envio dos itens e frete;
- referência externa vinculada ao pedido;
- URLs de retorno para pagamento aprovado, pendente ou recusado;
- webhook para atualização automática;
- consulta do pagamento diretamente na API;
- validação da assinatura do webhook;
- rejeição de webhooks antigos para reduzir repetição maliciosa;
- validação da referência do pedido;
- conferência do e-mail do pagador, quando informado;
- conferência obrigatória do valor integral e da moeda BRL;
- rejeição de pagamentos de teste no ambiente de produção;
- validação opcional do proprietário da credencial por `collector_id`;
- bloqueio de confirmação e reembolso manual para pedidos do Mercado Pago;
- reembolso concluído somente após aprovação explícita da API;
- recebimento de alertas antifraude, reclamações e chargebacks;
- bloqueio automático de etiqueta, separação e envio durante análise de risco;
- alerta no painel, log administrativo e WhatsApp Cloud quando configurado;
- liberação do estoque em resultados negativos;
- mudança automática de pagamento aprovado para `Para separar`.

O checkout real exige uma URL pública HTTPS. Em `localhost`, a loja pode ser navegada e testada, mas a criação de uma preferência de produção não deve ser considerada operacional.

Variáveis relacionadas:

```dotenv
MERCADO_PAGO_PUBLIC_KEY=APP_USR_EXEMPLO
MERCADO_PAGO_ACCESS_TOKEN=APP_USR_EXEMPLO
MERCADO_PAGO_WEBHOOK_SECRET=SEGREDO_EXEMPLO
MERCADO_PAGO_COLLECTOR_ID=ID_EXEMPLO
MERCADO_PAGO_WEBHOOK_MAX_AGE_SECONDS=300
DECANTS_PUBLIC_BASE_URL=https://loja.exemplo.com.br
```

No painel **Suas integrações > Webhooks** do Mercado Pago, use
`https://seu-dominio/api/payments/webhook` e habilite:

- Pagamentos;
- Alertas de fraude (`stop_delivery_op_wh`);
- Reclamações (`topic_claims_integration_wh`);
- Chargebacks (`topic_chargebacks_wh`).

O código registra eventos não conciliados sem bloquear pedidos aleatórios. Eventos vinculados mudam o pedido para **Revisão de risco** ou **Chargeback**. A liberação manual exige uma observação auditável.

### WhatsApp

Há dois usos distintos:

1. **Atendimento e checkout manual:** geração de link `wa.me` com os dados do pedido.
2. **Notificação administrativa automática:** envio pela WhatsApp Cloud API quando o Mercado Pago confirma um pagamento aprovado.

O checkout manual continua disponível mesmo sem credenciais da Cloud API. Sem token da Meta, somente a notificação automática ao administrador fica desativada.

```dotenv
DECANTS_WHATSAPP_NUMBER=55DDDNUMERO
WHATSAPP_ADMIN_NUMBER=55DDDNUMERO
WHATSAPP_CLOUD_PHONE_NUMBER_ID=ID_EXEMPLO
WHATSAPP_CLOUD_TOKEN=TOKEN_EXEMPLO
```

### Render

O repositório contém:

- `render.yaml` com definição do serviço web;
- `Procfile` com o comando de inicialização;
- `runtime.txt` com a versão de Python;
- configuração para banco e uploads em disco persistente.

Em produção, o SQLite e as imagens enviadas pelo painel devem ficar fora do sistema de arquivos efêmero do deploy.

### Serviços externos no frontend

As páginas utilizam recursos visuais hospedados externamente:

- Google Fonts;
- Font Awesome via CDN.

A indisponibilidade desses serviços pode afetar fontes e ícones, mas não deve impedir o funcionamento principal do backend.

## Painel administrativo

O painel é servido pela mesma aplicação e pode ser separado por domínio ou subdomínio administrativo.

Rotas de interface:

- `/login`;
- `/dashboard`;
- `/produtos`;
- `/pedidos`;
- `/clientes`;
- `/logs`.

### Dashboard

Exibe:

- total de vendas consideradas pagas;
- total de pedidos;
- quantidade de produtos;
- quantidade de clientes;
- valor estimado do estoque com base no preço de 10 ml;
- pedidos recentes.

### Produtos

Permite:

- cadastrar;
- editar;
- excluir;
- pesquisar;
- definir categoria;
- controlar estoque;
- configurar preços de 5 ml e 10 ml;
- ativar promoção;
- configurar preços promocionais;
- marcar produto como destaque;
- definir selo e chamada;
- indicar imagem existente;
- enviar nova imagem.

Uploads aceitam arquivos reconhecidos como imagem, usam nomes normalizados e possuem limite efetivo de 5 MB. A exclusão de um produto não remove automaticamente imagens antigas.

### Pedidos

Permite:

- listar e pesquisar pedidos;
- filtrar por situação operacional;
- consultar cliente, endereço, CEP, itens, valores e forma de pagamento;
- alterar status;
- adicionar observação ao histórico;
- visualizar a linha do tempo;
- baixar ou imprimir etiqueta de envio em PDF.

Principais agrupamentos:

- Para separar;
- Separados;
- Entregues;
- Extorno;
- Cancelados.

### Clientes e leads

A área consolida:

- clientes que já realizaram pedidos;
- nome, contato e endereço mais recente;
- número de pedidos;
- total gasto;
- data do último pedido;
- leads do Clube de Ofertas ainda sem compra.

### Logs

O sistema registra até os 100 eventos administrativos mais recentes exibidos no painel, incluindo:

- login bem-sucedido ou recusado;
- logout;
- cadastro, edição e exclusão de produto;
- upload de imagem;
- alteração de status de pedido;
- usuário administrativo;
- IP;
- data;
- detalhes limitados.

## Arquitetura e organização

### Tecnologias

- Python 3.12;
- servidor HTTP da biblioteca padrão;
- SQLite;
- `bcrypt` para verificação de senha administrativa;
- HTML5;
- CSS3;
- JavaScript sem framework;
- APIs HTTP em JSON.

### Backend

```text
server.py             Ponto de entrada compatível
decants_app.py        Configuração, banco e orquestração das regras de negócio
decants_handler.py    Casos de uso e respostas dos endpoints
decants_customer_handler.py Pedidos do cliente, LGPD e pós-venda
decants_routes.py     Despacho das rotas HTTP
decants_http.py       Arquivos públicos, cookies, respostas e proteções HTTP
decants_config.py     Leitura e normalização das variáveis de ambiente
decants_auth.py       Senhas, sessões administrativas e sessões de clientes
decants_orders.py     Itens, cupons, reservas e devoluções de estoque
decants_validation.py Normalização e validação de produtos, leads e checkout
decants_pdf.py        Geração dos documentos PDF
decants_uploads.py    Validação e normalização de uploads
```

Os módulos especializados mantêm regras puras isoladas da camada HTTP. O
`decants_app.py` continua exportando essas funções para preservar
compatibilidade com o ponto de entrada, os testes e integrações existentes.

### Frontend

```text
index.html                         Página inicial
produtos.html                      Catálogo por categoria
carrinho.html                      Carrinho e checkout completo
meus-pedidos.html                  Área do cliente
contatos.html                      Atendimento
admin.html                         Aplicação administrativa
politica-de-privacidade.html       Política de privacidade
termos-de-compra.html              Termos de compra
trocas-e-devolucoes.html           Política de trocas e devoluções
prazos-de-entrega.html             Política de entrega
```

Os módulos `js/store-*.js` separam catálogo, produto, carrinho, checkout,
navegação e inicialização. O carrinho completo possui lógica complementar em
`js/carrinho.js`, enquanto o painel usa `js/admin-panel.js`.

Os agregadores `css/product-modal.css` e `css/responsive.css` mantêm a ordem da
cascata e importam arquivos menores por componente e breakpoint.

### Arquivos estáticos e uploads

```text
css/                  Estilos por responsabilidade
js/                   Scripts da loja e do painel
img/produtos/         Imagens dos cards
img/container/        Galerias de produtos
img/highlights/       Imagens de destaque
img/marcas/           Logos de marcas
img/uploads/          Uploads administrativos
data/                 Banco SQLite local
tests/                Testes automatizados
```

O servidor possui uma lista explícita de arquivos públicos. Arquivos como `.env`, fontes Python, banco de dados e metadados do Git não são entregues pela aplicação.

## Modelo de dados

O SQLite é inicializado automaticamente e contém as seguintes tabelas:

| Tabela | Finalidade |
| --- | --- |
| `products` | Catálogo, preços, estoque, promoções e destaques |
| `leads` | Cadastros voluntários do Clube de Ofertas |
| `orders` | Dados do cliente, entrega, pagamento, valores e status |
| `order_items` | Produtos, volumes, quantidades e preços do pedido |
| `order_history` | Histórico de mudanças de status |
| `payment_alerts` | Alertas antifraude, reclamações e chargebacks do Mercado Pago |
| `admin_logs` | Auditoria de ações administrativas |
| `admin_sessions` | Sessões administrativas persistentes e revogáveis |

O catálogo inicial é carregado de `js/catalog-data.js` quando o banco ainda não possui produtos.

## API

### Rotas públicas

| Método | Rota | Função |
| --- | --- | --- |
| `GET` | `/api/products` | Lista o catálogo |
| `GET` | `/api/shipping/quote` | Calcula o frete pela regra configurada |
| `POST` | `/api/leads` | Cadastra contato no Clube de Ofertas |
| `POST` | `/api/checkout` | Valida e cria um pedido |
| `POST` | `/api/payments/webhook` | Recebe eventos do Mercado Pago |
| `GET` | `/api/orders/{referencia}` | Consulta pontual com contato correspondente |
| `GET` | `/api/customer/session` | Informa a sessão do cliente e fornece token CSRF |
| `POST` | `/api/customer/login` | Inicia sessão com e-mail e WhatsApp |
| `POST` | `/api/customer/logout` | Encerra a sessão do cliente |
| `GET` | `/api/customer/orders` | Lista pedidos autorizados |

### Rotas administrativas

| Método | Rota | Função |
| --- | --- | --- |
| `GET` | `/api/session` | Consulta sessão e obtém token CSRF |
| `POST` | `/api/login` | Autentica administrador |
| `POST` | `/api/logout` | Revoga a sessão |
| `GET` | `/api/admin/dashboard` | Retorna métricas |
| `GET` | `/api/admin/orders` | Lista pedidos |
| `GET` | `/api/admin/orders/{id}` | Exibe detalhes e histórico |
| `PUT` | `/api/admin/orders/{id}/status` | Atualiza status |
| `GET` | `/api/admin/orders/{id}/label.pdf` | Gera kit PDF de endereçamento e declaração de conteúdo |
| `GET` | `/api/admin/customers` | Lista clientes e leads |
| `GET` | `/api/admin/logs` | Lista logs recentes |
| `POST` | `/api/admin/upload` | Envia imagem |
| `POST` | `/api/products` | Cadastra produto |
| `PUT` | `/api/products/{id}` | Edita produto |
| `DELETE` | `/api/products/{id}` | Exclui produto |

Operações administrativas de escrita exigem sessão válida e token CSRF.

## Instalação local

### Pré-requisitos

- Python 3.12 ou versão compatível;
- `pip`;
- navegador moderno.

### Configuração

1. Clone ou abra o projeto.
2. Crie um ambiente virtual:

```powershell
python -m venv .venv
```

3. Ative o ambiente no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Instale as dependências:

```powershell
pip install -r requirements.txt
```

5. Copie `.env.example` para `.env` e substitua somente os valores necessários.
6. Inicie o servidor:

```powershell
python server.py
```

Também estão disponíveis os atalhos `iniciar-servidor.ps1` e `iniciar-servidor.bat`.

### Endereços locais

```text
Loja:    http://localhost:8000/index.html
Painel:  http://localhost:8000/login
```

O banco local padrão fica em `data/decants.sqlite3`. Uploads locais ficam em `img/uploads`.

## Configuração por ambiente

Use `.env.example` como referência. O arquivo `.env` real está ignorado pelo Git e não deve ser compartilhado.

### Aplicação e armazenamento

| Variável | Descrição |
| --- | --- |
| `DECANTS_ENV` | Ambiente, como `development` ou `production` |
| `DECANTS_PUBLIC_BASE_URL` | URL pública HTTPS |
| `DECANTS_DB_PATH` | Caminho do banco SQLite |
| `DECANTS_UPLOAD_DIR` | Diretório persistente de uploads |
| `DECANTS_SQLITE_BUSY_TIMEOUT_SECONDS` | Espera máxima por uma escrita concorrente |
| `DECANTS_SQLITE_WRITE_RETRIES` | Tentativas adicionais para iniciar transações críticas |
| `DECANTS_SQLITE_BACKUP_DIR` | Diretório dos backups online do SQLite |
| `DECANTS_SQLITE_BACKUP_INTERVAL_HOURS` | Intervalo entre backups automáticos em produção |
| `DECANTS_SQLITE_BACKUP_RETENTION_DAYS` | Retenção local dos backups automáticos |
| `DECANTS_MAX_REQUEST_THREADS` | Limite de requisições processadas simultaneamente |
| `DECANTS_ADMIN_DOMAIN` | Host autorizado para o painel |
| `DECANTS_ALLOWED_ORIGINS` | Origens permitidas, separadas por vírgula |

### Administração

| Variável | Descrição |
| --- | --- |
| `DECANTS_ADMIN_USER` | Identificador de login |
| `DECANTS_ADMIN_PASSWORD_HASH` | Hash bcrypt da senha |
| `DECANTS_ADMIN_PASSWORD` | Fallback somente para desenvolvimento |
| `DECANTS_SECRET_KEY` | Chave de assinatura de sessões |

### Frete

| Variável | Descrição |
| --- | --- |
| `DECANTS_SHIPPING_FEE` | Valor padrão do frete |
| `DECANTS_FREE_SHIPPING_THRESHOLD` | Valor mínimo para frete grátis |

### WhatsApp

| Variável | Descrição |
| --- | --- |
| `DECANTS_WHATSAPP_NUMBER` | Canal comercial |
| `DECANTS_WHATSAPP_RESERVATION_MINUTES` | Validade da reserva manual |
| `WHATSAPP_ADMIN_NUMBER` | Destino de alertas administrativos |
| `WHATSAPP_CLOUD_PHONE_NUMBER_ID` | Identificador do número na Meta |
| `WHATSAPP_CLOUD_TOKEN` | Token da WhatsApp Cloud API |

### Mercado Pago

| Variável | Descrição |
| --- | --- |
| `MERCADO_PAGO_PUBLIC_KEY` | Chave pública da aplicação |
| `MERCADO_PAGO_ACCESS_TOKEN` | Token privado da API |
| `MERCADO_PAGO_WEBHOOK_SECRET` | Segredo para validar notificações |
| `MERCADO_PAGO_COLLECTOR_ID` | Identificador esperado da conta recebedora |

### Requisitos de produção

Em produção, a aplicação recusa uma configuração administrativa insegura. É necessário:

- usuário administrativo definido;
- hash bcrypt válido;
- chave secreta com pelo menos 32 caracteres;
- ausência de senha administrativa em texto puro.

Exemplo para gerar o hash sem registrar a senha no histórico do terminal:

```powershell
python -c "import bcrypt, getpass; print(bcrypt.hashpw(getpass.getpass('Senha: ').encode(), bcrypt.gensalt()).decode())"
```

## Segurança

Controles implementados:

- hash bcrypt para senha administrativa;
- comparação segura de assinaturas;
- sessões administrativas com token aleatório;
- armazenamento apenas do hash do token administrativo;
- sessões persistentes e revogáveis;
- cookies de sessão `HttpOnly`;
- `SameSite=Lax` na mesma origem;
- `Secure` em HTTPS ou nos hosts configurados;
- proteção CSRF em login, logout e operações administrativas;
- limitação de tentativas de login por IP;
- validação de origem para o painel;
- validação dos dados no backend;
- recálculo de preços e totais no servidor;
- consultas SQL parametrizadas;
- validação de assinatura do webhook;
- conferência de pedido, valor, pagador e conta recebedora;
- restrição de tipos e tamanho de upload;
- nomes aleatórios para arquivos enviados;
- bloqueio da entrega de arquivos privados;
- auditoria de ações administrativas;
- consulta de pedidos condicionada a múltiplos dados.

### Boas práticas adicionais

- Use sempre HTTPS.
- Rotacione tokens e segredos periodicamente.
- Restrinja o acesso ao painel.
- Faça backups criptografados do banco e dos uploads.
- Não grave dados de cartão na aplicação.
- Não inclua credenciais em commits, logs, capturas de tela ou documentação.
- Revogue imediatamente qualquer segredo exposto.
- Limite o acesso ao banco e aos backups conforme a função de cada pessoa.
- Mantenha dependências e ambiente de execução atualizados.

## LGPD e privacidade

Esta seção descreve o comportamento técnico e operacional atual. Ela não substitui revisão jurídica da Política de Privacidade, dos Termos de Compra e dos procedimentos internos.

### Dados tratados

Durante a operação da loja, podem ser tratados:

- nome;
- e-mail;
- telefone ou WhatsApp;
- CEP;
- endereço de entrega;
- itens, valores e histórico do pedido;
- método, identificador e situação do pagamento;
- dados fornecidos ao Clube de Ofertas;
- IP e registros de ações administrativas;
- cookies estritamente necessários para sessão e segurança.

A aplicação não deve armazenar número completo de cartão, código de segurança ou senha bancária. O pagamento é processado no ambiente do Mercado Pago.

### Finalidades

Os dados são utilizados para:

- identificar o cliente;
- criar, cobrar, separar, enviar e acompanhar pedidos;
- calcular e organizar a entrega;
- prestar atendimento;
- permitir consulta autenticada de compras;
- controlar estoque;
- prevenir fraude e abuso;
- manter trilhas de auditoria;
- cumprir obrigações legais, fiscais, regulatórias e consumeristas;
- enviar ofertas quando houver cadastro voluntário no Clube de Ofertas.

### Bases legais possíveis

Conforme o contexto e mediante validação jurídica, o tratamento pode se apoiar em:

- execução de contrato e procedimentos preliminares;
- cumprimento de obrigação legal ou regulatória;
- exercício regular de direitos;
- legítimo interesse, após avaliação de necessidade e impacto;
- consentimento para comunicações promocionais voluntárias.

O consentimento para marketing não deve ser tratado como condição para realizar uma compra.

### Compartilhamento

Os dados podem ser compartilhados, no limite necessário, com:

- Mercado Pago;
- Meta/WhatsApp;
- provedor de hospedagem;
- transportadoras e operadores logísticos;
- fornecedores técnicos indispensáveis;
- autoridades públicas, quando houver obrigação legal.

A loja declara em sua política pública que não comercializa dados pessoais.

### Direitos do titular

O titular pode solicitar, quando aplicável:

- confirmação da existência de tratamento;
- acesso;
- correção;
- informação sobre compartilhamentos;
- anonimização, bloqueio ou eliminação de dados inadequados;
- portabilidade, observada a regulamentação;
- eliminação de dados tratados com consentimento;
- revogação do consentimento;
- oposição a tratamento irregular;
- revisão de decisões automatizadas, caso venham a existir.

As solicitações podem ser abertas pelo formulário da página de privacidade. Cada envio gera um protocolo `LGPD`, fica registrado no banco e pode ser analisado na área **Solicitações** do painel administrativo.

### Retenção e descarte

O sistema executa a política automática de retenção durante a rotina de manutenção e backup. Os prazos podem ser configurados por variáveis de ambiente e, por padrão, são:

- pedidos: 1.825 dias, com anonimização dos dados pessoais após o prazo;
- cadastros de marketing: 730 dias, com exclusão;
- logs administrativos: 365 dias, com exclusão;
- fotos de solicitações resolvidas: 180 dias, com exclusão do arquivo e do registro.

Encerrada a finalidade e inexistindo obrigação de conservação, os dados devem ser eliminados ou anonimizados de forma segura, inclusive em cópias e backups conforme o ciclo técnico aplicável.

### Operação de trocas e devoluções

- Antes do envio, o cliente precisa ler e aceitar as regras sobre prazo, teste razoável, conservação e análise de consumo expressivo.
- O cancelamento antes da separação é uma categoria própria e só pode ser aberto enquanto o pedido ainda não foi separado, preparado ou enviado.
- O cliente autenticado abre a solicitação em **Meus pedidos**, vinculando o pedido, motivo, relato e até cinco fotos.
- A solicitação recebe protocolo `DEV` e permanece disponível ao cliente e ao administrador.
- O administrador registra o status, a análise e o resultado no painel.
- Ao marcar a solicitação como aguardando devolução, o sistema gera código interno e etiqueta PDF de logística reversa.
- No cancelamento pré-separação não há logística reversa. Pagamentos do Mercado Pago podem ser reembolsados integralmente pelo painel, usando a API oficial e chave de idempotência.
- O pedido e o estoque só são atualizados para reembolsado após a API confirmar a operação. O prazo para o crédito aparecer depende do meio de pagamento.
- Pedidos feitos pelo fluxo manual do WhatsApp continuam exigindo devolução financeira pelo respectivo meio de pagamento.

### Kit de expedição

O painel gera um PDF de duas páginas para cada pedido:

- etiqueta auxiliar de endereçamento com remetente, destinatário, CPF/CNPJ e CEP;
- declaração de conteúdo com itens, quantidades, valores, total e campos de assinatura.

Configure `DECANTS_BUSINESS_LEGAL_NAME`, `DECANTS_BUSINESS_TAX_ID`,
`DECANTS_BUSINESS_ADDRESS` e `DECANTS_BUSINESS_POSTAL_CODE`. O checkout coleta
e valida CPF/CNPJ do destinatário.

Esse PDF não compra a postagem, não gera rastreamento e não substitui a etiqueta
oficial emitida pelos Correios ou transportadora. A declaração de conteúdo
também não substitui nota fiscal quando sua emissão for obrigatória.

### Cookies e armazenamento local

- Cookies de sessão são usados para autenticação e proteção CSRF.
- O carrinho utiliza armazenamento local do navegador.
- Não há, no código atual, uma plataforma dedicada de publicidade comportamental ou perfilamento.
- Caso sejam adicionados analytics, pixels de marketing ou cookies não essenciais, deve ser implementada gestão de consentimento antes da ativação.

### Resposta a incidentes

Em caso de suspeita de incidente:

1. preserve evidências e restrinja o acesso;
2. identifique dados, titulares e sistemas afetados;
3. revogue credenciais comprometidas;
4. avalie risco e impacto;
5. registre decisões e medidas adotadas;
6. comunique titulares e ANPD quando juridicamente aplicável;
7. corrija a causa e acompanhe recorrências.

## Políticas da loja

As versões públicas e vigentes estão nestes arquivos:

- `politica-de-privacidade.html`;
- `termos-de-compra.html`;
- `trocas-e-devolucoes.html`;
- `prazos-de-entrega.html`;
- `contatos.html`.

O README resume essas regras para documentação do projeto. Em caso de divergência, as páginas publicadas ao consumidor e a legislação aplicável devem ser revisadas e harmonizadas.

### Termos de compra

- Os produtos são decants de fragrâncias originais.
- Preços, promoções e disponibilidade são os apresentados no momento da compra.
- O pedido depende de confirmação do pagamento ou atendimento via WhatsApp.
- O cliente deve informar dados completos e verdadeiros.
- Erros de endereço podem causar atraso, devolução e eventual novo frete quando não forem de responsabilidade da loja ou transportadora.
- Indisponibilidade excepcional ou erro material evidente pode resultar em cancelamento e reembolso integral.
- O frete segue a regra apresentada no checkout.
- Os termos não restringem direitos garantidos pelo Código de Defesa do Consumidor.

### Direito de arrependimento

Para compras realizadas pela internet:

- o consumidor pode solicitar cancelamento em até sete dias corridos contados do recebimento;
- a solicitação deve informar o número do pedido;
- a devolução por arrependimento não deve gerar custo ao consumidor;
- o cliente deve aguardar as instruções de envio;
- a política não pode exigir condições que eliminem direitos legais.

### Produto incorreto, avariado ou com vazamento

O cliente deve:

- entrar em contato assim que identificar o problema;
- informar o número do pedido;
- descrever a ocorrência;
- enviar fotos da embalagem e do produto, quando possível;
- conservar o produto e a embalagem de forma adequada para análise.

A exigência de fotos auxilia a apuração, mas não deve ser aplicada para impedir direitos legalmente assegurados.

### Trocas, devoluções e reembolso

- A solução deve observar a natureza da ocorrência e o Código de Defesa do Consumidor.
- Após a devolução ou confirmação do cancelamento, o reembolso é solicitado pelo meio de pagamento aplicável.
- O prazo de crédito pode depender do Mercado Pago, banco ou administradora.
- Defeitos e vícios não aparentes seguem os prazos legais próprios.
- Cancelamentos e reembolsos devem ser refletidos no status do pedido e na liberação do estoque.

### Entrega

- A preparação e postagem estão documentadas em até cinco dias úteis após a confirmação do pagamento.
- Sábados, domingos e feriados não entram nessa contagem.
- O prazo de transporte começa após a postagem.
- O prazo varia por CEP, localidade e transportadora.
- Rastreamento deve ser informado quando a modalidade oferecer esse recurso.
- Atrasos, extravios, avarias e vazamentos devem ser acompanhados pelo canal oficial.
- Antes da publicação, prazos e transportadoras devem ser conferidos com a operação real da loja.

### Atendimento

O canal oficial deve permanecer atualizado em `contatos.html`. CNPJ, razão social, endereço comercial, e-mail e demais informações obrigatórias devem ser publicados quando formalizados e juridicamente aplicáveis.

## Testes

Execute:

```powershell
python -m unittest discover -s tests -v
```

Os testes de navegador usam Playwright em perfis desktop e mobile:

```powershell
npm install
npx playwright install chromium
npm run test:e2e
```

O workflow `.github/workflows/ci.yml` executa automaticamente compilação,
testes de backend e Playwright em pushes para `main`, branches `codex/**` e
pull requests.

A suíte atual cobre, entre outros pontos:

- validação de leads;
- continuidade do servidor após requisição inválida;
- privacidade da consulta de pedidos;
- login do cliente;
- sessão criada pelo checkout;
- persistência e revogação de sessão administrativa;
- bloqueio de arquivos privados;
- entrega de páginas e assets públicos;
- regra inclusiva de frete grátis;
- leitura de preços brasileiros e internacionais;
- expiração de reserva via WhatsApp;
- devolução automática de estoque;
- concorrência entre checkouts pela última unidade;
- rollback integral de reservas com múltiplos itens;
- WAL, timeout de escrita e integridade referencial do SQLite;
- CSP e políticas de cache para HTML, API e assets;
- catálogo, busca, carrinho, modal de produto e menu mobile em navegador real;
- obrigatoriedade do CEP;
- validação do proprietário da conta Mercado Pago;
- rejeição de configuração administrativa insegura em produção.

## Deploy

### Render

O `render.yaml` inicia a aplicação com:

```text
python server.py
```

Recomendações:

- use um plano com disco persistente;
- aponte `DECANTS_DB_PATH` para o disco;
- aponte `DECANTS_UPLOAD_DIR` para o disco;
- configure segredos somente no painel do provedor;
- use uma URL pública HTTPS;
- configure o health check em `/api/products`;
- confirme os domínios público e administrativo;
- teste o webhook após cada alteração de domínio.

Exemplo de caminhos persistentes:

```dotenv
DECANTS_DB_PATH=/var/data/decants.sqlite3
DECANTS_UPLOAD_DIR=/var/data/uploads
DECANTS_SQLITE_BACKUP_DIR=/var/data/backups
```

Em produção, o servidor usa HTTP/1.1, fila ampliada e um limite configurável de
threads. O SQLite opera em WAL com transações imediatas nos fluxos de estoque.
Essa configuração atende uma loja pequena ou média em uma única instância; para
escalabilidade horizontal, migre a persistência para PostgreSQL antes de iniciar
múltiplas instâncias da aplicação.

### DNS e HTTPS

Para um subdomínio administrativo:

1. crie o registro DNS solicitado pelo provedor;
2. cadastre o domínio personalizado na hospedagem;
3. aguarde a emissão do certificado;
4. force redirecionamento de HTTP para HTTPS;
5. atualize `DECANTS_ADMIN_DOMAIN`;
6. inclua apenas origens necessárias em `DECANTS_ALLOWED_ORIGINS`;
7. valide login, cookies e CSRF no domínio final.

## Checklist de produção

- [ ] `.env` não está versionado.
- [ ] Nenhuma credencial real aparece no README ou no histórico do Git.
- [ ] Senha administrativa usa bcrypt.
- [ ] `DECANTS_SECRET_KEY` é longa, aleatória e exclusiva.
- [ ] HTTPS está ativo.
- [ ] Banco e uploads usam armazenamento persistente.
- [ ] Backups e restauração foram testados.
- [ ] Mercado Pago usa a conta correta.
- [ ] `collector_id` foi conferido.
- [ ] Segredo do webhook foi configurado.
- [ ] Webhook foi testado com pagamento aprovado e recusado.
- [ ] Estoque retorna após cancelamento, expiração e reembolso.
- [ ] WhatsApp comercial aponta para o canal oficial.
- [ ] Frete, gratuidade e prazo de postagem correspondem à operação real.
- [ ] Dados empresariais obrigatórios estão publicados.
- [ ] Políticas foram revisadas por profissional jurídico.
- [ ] Existe procedimento interno para solicitações LGPD.
- [ ] Existe política de retenção, descarte e resposta a incidentes.
- [ ] Testes automatizados estão passando.
- [ ] Loja, carrinho, checkout, pedidos e painel foram validados em celular e desktop.

## Licença e uso

O repositório não declara atualmente uma licença pública. Na ausência de uma licença, o código deve ser considerado de uso reservado ao titular do projeto.
