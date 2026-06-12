# Documentação AP2 — Catálogo de Produtos

> **Repositório:** Catálogo de Produtos API REST  
> **Disciplina:** Banco de Dados em Nuvem / Extração e Preparação de Dados  
> **Entrega:** 11/06/2026

---

## 1. Etapas Realizadas

### Parte 1 — Preparação e branch AP2

Partindo do projeto funcional da AP1 (Django REST com SQLite e mídia local no Elastic Beanstalk), foi criada a branch `ap2` para isolar as mudanças. Antes de qualquer alteração de infraestrutura, verificamos que o projeto rodava localmente sem erros e que os endpoints de `Produto` e `Categoria` respondiam corretamente.

### Parte 2 — Banco de dados: Amazon RDS PostgreSQL

**Criação da instância**

Criamos uma instância RDS do tipo `db.t3.micro` com engine PostgreSQL 15, na mesma VPC do ambiente Elastic Beanstalk. A instância foi configurada com acesso público desabilitado — a conectividade é feita exclusivamente dentro da VPC, via Security Group.

**Configuração de rede**

No Security Group do RDS, adicionamos uma inbound rule permitindo tráfego na porta 5432 apenas a partir do Security Group associado às instâncias EC2 do Elastic Beanstalk.

**Migração do banco**

O `settings.py` foi reestruturado para suportar múltiplas fontes de configuração do banco, com a seguinte ordem de prioridade:

1. `DATABASE_URL` (formato padrão, compatível com `dj-database-url`)
2. Variáveis `POSTGRES_*` individuais
3. Variáveis `RDS_*` (formato legado AWS)
4. SQLite local (fallback para desenvolvimento)

Essa abordagem permite que o mesmo código rode localmente com SQLite e em produção com RDS, sem nenhuma alteração de código.

Após configurar as variáveis de ambiente no painel do EB, as migrações passaram a ser executadas automaticamente a cada deploy via `.ebextensions/01_django_migrate.config`, com a flag `leader_only: true` para evitar execuções paralelas em ambientes com múltiplas instâncias.

**Criação do superusuário**

O superusuário `root` foi criado via `eb ssh` + `python manage.py createsuperuser` diretamente no ambiente de produção.

### Parte 3 — Armazenamento de mídia: Amazon S3

**Criação do bucket**

Criamos um bucket S3 dedicado à mídia dos produtos, com política de leitura pública para os objetos (GET), permitindo que as URLs das imagens sejam acessíveis diretamente pelo browser.

**Integração com Django**

Instalamos `django-storages[boto3]` e `boto3`. A configuração em `settings.py` é condicional: se as três variáveis `AWS_STORAGE_BUCKET_NAME`, `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` estiverem presentes, o backend de storage é automaticamente trocado para `S3Boto3Storage` e o `MEDIA_URL` passa a apontar para o bucket. Caso contrário, o Django usa o filesystem local — o que mantém o ambiente de desenvolvimento funcional sem credenciais AWS.

**Carregamento das imagens de produto**

As imagens dos produtos do `initial_data.json` foram migradas para o S3. O comando `load_initial_data` foi atualizado para detectar a presença das variáveis de ambiente e construir as URLs S3 no formato correto (`https://bucket.s3.region.amazonaws.com/...`).

Um campo auxiliar `imagem_legada` foi adicionado ao modelo `Produto` para preservar as URLs das imagens já carregadas, mesmo quando não há um arquivo Django `ImageField` associado. A propriedade `imagem_origem` resolve automaticamente a melhor fonte disponível: `imagem` (upload direto), `imagem_legada` (URL pré-carregada) ou `especificacoes["image_url"]` (legado JSON).

**Migration de correção de URLs**

Durante os testes, identificamos que algumas URLs de imagem estavam no formato `s3://bucket/key` em vez de `https://`. A migration `0008_fix_s3_image_urls.py` foi criada para normalizar essas URLs diretamente no banco de dados, tanto no campo `imagem_legada` quanto dentro do `JSONField especificacoes`.

### Parte 4 — Novos modelos: Pedido e ItemPedido

Para evoluir o catálogo para um pequeno e-commerce, adicionamos os modelos `Pedido` e `ItemPedido` ao app `produtos`.

`Pedido` armazena dados do cliente (nome, email), um número de pedido gerado automaticamente (formato `PED{timestamp}{random}`), status (pendente → confirmado → enviado → entregue → cancelado) e o valor total.

`ItemPedido` é a tabela de ligação entre `Pedido` e `Produto`, com quantidade, preço unitário (snapshoteado no momento do pedido) e subtotal calculado automaticamente no `save()`.

O `PedidoViewSet` implementa um `create()` customizado com as seguintes regras de negócio:
- Validação de presença de `cliente_nome` e `cliente_email`
- Validação de que a lista de itens não está vazia
- Verificação de existência de cada `produto_id`
- Cálculo automático do total com base nos subtotais dos itens
- Rollback (delete do pedido) em caso de produto inválido

### Parte 5 — Frontend integrado

Adicionamos um frontend em HTML/CSS/JS puro servido pelo próprio Django (view `home`). O frontend consome a API REST via `fetch` e oferece:

- Listagem de produtos com imagens (S3 quando disponível)
- Filtros por nome, categoria, faixa de preço e ordenação
- Chips de categoria, marca, tipo e destaque por produto
- Carrinho de compras persistido em `localStorage`
- Formulário de checkout que cria um `Pedido` via POST na API
- Modal com listagem dos integrantes do grupo

### Parte 6 — JSONField para metadados dinâmicos (Bônus)

O campo `especificacoes` (`JSONField`) foi adicionado ao modelo `Produto` para armazenar atributos que variam por tipo de produto: marca, tipo de item, faixa de preço, destaque, nome e descrição em inglês, e URL legada da imagem.

O `ProdutoViewSet` expõe dois filtros que operam diretamente sobre o JSONB:

```python
# Filtro por marca (case-insensitive lookup no JSONB)
queryset.filter(especificacoes__brand__icontains=marca)
```

```python
# Filtro combinado: relacional + JSON
queryset.filter(
    categoria_id=categoria_id,
    especificacoes__price_tier="premium"
)
```

Esses filtros usam os operadores de lookup do ORM Django para JSONB, sem necessidade de queries SQL brutas.

---

## 2. Principais Decisões Técnicas
## 2. Principais Decisões Técnicas

- Banco: configuração multi-fonte (`DATABASE_URL`, `POSTGRES_*`, `RDS_*`) com fallback para SQLite — facilita desenvolvimento local e deploy no EB.
- Mídia: ativação condicional do S3 via presença de variáveis de ambiente; sem variáveis usa filesystem local.
- Imagens legadas: campo `imagem_legada` e propriedade `imagem_origem` para manter compatibilidade sem reupload em massa.
- Migrações/estáticos: `leader_only: true` para `migrate` e `collectstatic` no EB, evitando execuções concorrentes.
- Pedidos: `ItemPedido.preco_unitario` armazena snapshot de preço para imutabilidade de pedidos.
- Metadados: uso de `JSONField` (JSONB) para atributos heterogêneos, mantendo flexibilidade e consultas eficientes.

---

## 3. Dificuldades Encontradas e Soluções

### Problema: URLs de imagem em formato `s3://` chegando ao frontend

Durante os testes iniciais de carga de dados, algumas imagens exibiam `s3://bucket/key` como URL no frontend, causando imagens quebradas.

**Causa:** O comando `load_initial_data` construía as URLs S3 antes de o formato correto ser definido. Algumas imagens foram inseridas com o formato `s3://` por um ciclo anterior de desenvolvimento.

**Solução:** Criamos a migration `0008_fix_s3_image_urls.py` que percorre todos os produtos e normaliza qualquer URL no formato `s3://` para `https://`, tanto em `imagem_legada` quanto dentro do campo `especificacoes`. O `ProdutoSerializer` também inclui uma verificação explícita para nunca deixar URLs `s3://` chegarem ao cliente.

---

### Problema: Typo bloqueando migration em produção

A migration `0008` foi criada com `rom django.db import migrations` em vez de `from django.db import migrations`.

**Causa:** Erro de digitação humana.

**Solução:** Corrigir a linha 1 da migration antes do deploy. Identificado nos logs via `eb logs`.

---

### Problema: Imagens não carregando após deploy

Após o primeiro deploy com S3 configurado, as imagens retornavam 403 Forbidden.

**Causa:** O bucket S3 tinha "Block all public access" habilitado por padrão, impedindo acesso público às imagens.

**Solução:** Desabilitar "Block all public access" no bucket e adicionar a Bucket Policy de leitura pública para o path `arn:aws:s3:::nome-do-bucket/*`.

---

### Problema: Django Admin sem CSS em produção

Após o deploy, o painel `/admin/` carregava sem estilos.

**Causa:** O `collectstatic` não havia rodado no ambiente EB, então os arquivos estáticos não estavam disponíveis no path `/static/`.

**Solução:** Garantir a presença do comando `collectstatic --noinput` em `.ebextensions/django.config` com `leader_only: true`. Também verificar que `STATIC_ROOT` e o mapeamento Nginx (`/static → staticfiles`) estão corretamente configurados.

---

### Problema: Conectividade entre EB e RDS

Após criar o RDS, a aplicação no EB não conseguia conectar ao banco.

**Causa:** O Security Group do RDS não permitia tráfego vindo das instâncias EC2 do EB.

**Solução:** Identificar o Security Group associado ao ambiente EB e adicionar uma inbound rule no SG do RDS: protocolo TCP, porta 5432, source = SG do EB.


