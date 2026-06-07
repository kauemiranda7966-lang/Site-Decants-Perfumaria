# Decant Perfumaria

Loja em Python com catalogo publico, checkout, Clube de Ofertas e painel administrativo separado para gerenciar produtos, pedidos, clientes, imagens e logs.

## Como rodar localmente

1. Instale as dependencias:

```bash
pip install -r requirements.txt
```

2. Inicie o servidor:

```bash
python server.py
```

3. Acesse a loja publica:

```text
http://localhost:8000/index.html
```

O banco SQLite local fica em `data/decants.sqlite3`, salvo quando `DECANTS_DB_PATH` aponta para outro caminho.

## Painel administrativo

URL local:

```text
http://localhost:8000/login
```

URL de producao configurada:

```text
https://admin.decantperfumaria.com.br/login
```

Usuario padrao de desenvolvimento:

```text
decantsperfumaria1@gmail.com
```

Senha padrao de desenvolvimento:

```text
Wellida123 senha
```

Rotas principais:

- `/login`: tela de entrada.
- `/dashboard`: resumo financeiro, pedidos recentes, produtos e clientes.
- `/produtos`: cadastro, edicao, exclusao e upload de imagens.
- `/pedidos`: acompanhamento e atualizacao de status.
- `/clientes`: clientes de pedidos e leads do Clube de Ofertas.
- `/logs`: historico de acoes administrativas.

Na tela `/pedidos`, pedidos pagos entram em `Para separar`. O painel tambem tem as abas `Separados`, `Entregues`, `Extorno` e `Cancelados`, alem da busca pelo numero do pedido.

## WhatsApp automatico de pedidos pagos

Quando o Mercado Pago confirma um pagamento aprovado pelo webhook, o pedido muda para `Para separar` e o servidor tenta enviar o numero do pedido para o WhatsApp administrativo via WhatsApp Cloud API. Configure:

```bash
WHATSAPP_ADMIN_NUMBER=558899641605
WHATSAPP_CLOUD_PHONE_NUMBER_ID=seu_phone_number_id
WHATSAPP_CLOUD_TOKEN=seu_token_da_meta
```

Sem essas credenciais, o painel continua funcionando e o link manual do WhatsApp continua sendo gerado.

## Como alterar credenciais

Em producao, use variaveis de ambiente e evite senha em texto puro:

```bash
DECANTS_ADMIN_USER=admin@decantperfumaria.com.br
DECANTS_ADMIN_PASSWORD_HASH=$2b$12$...
DECANTS_SECRET_KEY=uma-chave-longa-aleatoria
```

Para gerar o hash bcrypt:

```bash
python -c "import bcrypt, getpass; print(bcrypt.hashpw(getpass.getpass('Senha: ').encode(), bcrypt.gensalt()).decode())"
```

O fallback `DECANTS_ADMIN_PASSWORD` existe apenas para desenvolvimento local. Em producao, use sempre `DECANTS_ADMIN_PASSWORD_HASH`.

## Como cadastrar produtos

1. Acesse `/produtos` no painel.
2. Clique em `Novo`.
3. Preencha nome, categoria, estoque, preco 5ml, preco 10ml e imagem atual.
4. Opcionalmente marque promocao, destaque, selo e chamada.
5. Para enviar uma imagem nova, use `Upload de imagem`; o painel salva em `img/uploads`.
6. Clique em `Salvar`.

O produto aparece na loja publica via API `/api/products`.

## Como editar produtos

1. Acesse `/produtos`.
2. Busque o produto na lista.
3. Clique em `Editar`.
4. Ajuste campos, estoque, precos, promocao, destaque ou imagem.
5. Clique em `Salvar`.

## Como remover produtos

1. Acesse `/produtos`.
2. Clique em `Editar` no produto desejado.
3. Clique em `Excluir`.
4. Confirme a remocao.

A exclusao remove o produto do catalogo carregado pela API. As imagens antigas nao sao apagadas automaticamente.

## Como gerenciar imagens

- Produtos cadastrados pelo painel podem usar caminhos existentes, como `img/produtos/masculinos/dior-sauvage.png`.
- Uploads feitos no painel sao salvos em `img/uploads`.
- A loja tambem detecta imagens disponiveis em `img/modal` e usa essas imagens nos cards e modais quando o nome do produto corresponde ao mapeamento do catalogo.
- Para evitar imagem quebrada, confirme que o caminho nao comeca com barra e que o arquivo existe dentro do projeto.

## Clube de Ofertas

A secao `Clube de Ofertas` fica na pagina inicial. Ela coleta:

- Nome opcional.
- E-mail obrigatorio.
- Telefone/WhatsApp obrigatorio.

Os cadastros sao enviados para `/api/leads` e armazenados na tabela `leads` com nome, e-mail, telefone e data. No painel, esses contatos aparecem em `/clientes` quando ainda nao possuem pedidos.

## Como publicar alteracoes

1. Rode os testes/verificacoes locais.
2. Confirme que a loja abre sem erros em `http://localhost:8000/index.html`.
3. Confirme o painel em `http://localhost:8000/login`.
4. Faça commit das alteracoes.
5. Envie para o remoto com `git push`.
6. Na hospedagem, confirme que as variaveis de ambiente estao configuradas.

## Variaveis de ambiente principais

```bash
DECANTS_ADMIN_DOMAIN=admin.decantperfumaria.com.br
DECANTS_ADMIN_USER=admin@decantperfumaria.com.br
DECANTS_ADMIN_PASSWORD_HASH=$2b$12$...
DECANTS_SECRET_KEY=uma-chave-longa-aleatoria
DECANTS_DB_PATH=/var/data/decants.sqlite3
DECANTS_WHATSAPP_NUMBER=558899641605
DECANTS_PUBLIC_BASE_URL=https://decantperfumaria.com.br
```

## DNS e SSL

No provedor de DNS do dominio `decantperfumaria.com.br`, crie um registro para o subdominio:

- Tipo: `CNAME`
- Nome/Host: `admin`
- Valor/Destino: hostname informado pelo provedor do servidor, por exemplo `decants-perfumaria.onrender.com`
- TTL: automatico ou 300 segundos

Depois que o DNS propagar:

1. Cadastre `admin.decantperfumaria.com.br` como dominio customizado no servico de hospedagem.
2. Aguarde a emissao automatica do certificado Let's Encrypt.
3. Ative redirect HTTP para HTTPS.
4. Confirme que `https://admin.decantperfumaria.com.br/login` abre sem alerta de certificado.

Em um VPS com Nginx, use Certbot:

```bash
sudo certbot --nginx -d admin.decantperfumaria.com.br
```

## Exemplo de proxy reverso

```nginx
server {
    listen 80;
    server_name admin.decantperfumaria.com.br;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name admin.decantperfumaria.com.br;

    ssl_certificate /etc/letsencrypt/live/admin.decantperfumaria.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admin.decantperfumaria.com.br/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

O mesmo processo pode servir a loja principal em outro `server_name`, mantendo a separacao pelo host. O backend identifica `admin.decantperfumaria.com.br` e entrega o painel para as rotas administrativas.
