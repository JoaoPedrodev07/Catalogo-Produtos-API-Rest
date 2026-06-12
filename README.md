# Catálogo de Produtos — Evolução de Arquitetura AP1 → AP2

API REST de catálogo de produtos com carrinho de compras, desenvolvida em **Django + Django REST Framework** e implantada na **AWS**.

Projeto desenvolvido para a disciplina Big Data and Cloud Computing — Professor Jonh Carvalho.

---

## Integrantes do Grupo

| Nome |
|------|
| Nicholas Vasconcelos |
| João Pedro Lima de Campos |
| João Pedro Pingarilho |
| Renan Habib Yassin Barbosa |
| Douglas Hancock |

---

### Website Online - Hosted no AWS EB
![Website - Catálogo de Produtos](media/screenshots/website_image.png)

## Links da API em Produção (Elastic Beanstalk)

| Recurso | URL |
|---------|-----|
| Frontend (página principal) | [http://ap2-jonh.us-east-1.elasticbeanstalk.com/](http://ap2-jonh.us-east-1.elasticbeanstalk.com/) |
| Produtos | [http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/produtos/](http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/produtos/) |
| Categorias | [http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/categorias/](http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/categorias/) |
| Pedidos | [http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/pedidos/](http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/pedidos/) |
| Itens de Pedido | [http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/itens-pedido/](http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/itens-pedido/) |
| Django Admin | [http://ap2-jonh.us-east-1.elasticbeanstalk.com/admin/](http://ap2-jonh.us-east-1.elasticbeanstalk.com/admin/) |

---

## Arquitetura da Solução

### Comparativo AP1 → AP2

| Recurso | AP1 | AP2 |
|---------|-----|-----|
| **Banco de dados** | SQLite (arquivo local na instância) | **Amazon RDS PostgreSQL** (gerenciado, persistente) |
| **Armazenamento de mídia** | Pasta `/media/` local (volátil) | **Amazon S3** (bucket dedicado, durável) |
| **Serviços AWS** | Elastic Beanstalk apenas | EB + RDS + S3 |
| **Persistência** | Dados perdidos a cada redeploy | Totalmente desacoplada e persistente |
| **Modelos de dados** | `Categoria` + `Produto` | + `Pedido` + `ItemPedido` + `JSONField` |
| **Frontend** | Apenas API | Frontend integrado consumindo a API |

### Diagrama AP1 — Elastic Beanstalk Isolado

```mermaid
graph TD
  User["Usuário"] --> EB["Nginx / EC2 no Elastic Beanstalk"]
  EB --> Django["Django Application"]
  Django --> SQLite["SQLite — arquivo local"]
  Django --> Media["/media/ — pasta local"]
```

### Diagrama AP2 — Arquitetura Desacoplada

```mermaid
graph TD
  User["Usuário"] --> EB["AWS Elastic Beanstalk / EC2"]
  EB --> Django["Django Application"]
  Django --> RDS["Amazon RDS<br/>PostgreSQL"]
  Django --> S3["Amazon S3<br/>Bucket de mídia"]
  Django --> Admin["Django Admin"]
```

---

## Execução Local

### Pré-requisitos

- Python 3.11+
- Git
- (Opcional) Credenciais AWS para testar com RDS/S3 localmente

### Passo a passo

**1. Clonar o repositório**

```bash
git clone https://github.com/seu-usuario/Catalogo-Produtos-API-Rest.git
cd Catalogo-Produtos-API-Rest
```

**2. Criar e ativar ambiente virtual**

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.\.venv\Scripts\activate
```

**3. Instalar dependências**

```bash
pip install -r requirements.txt
```

**4. Configurar variáveis de ambiente**

Para rodar localmente com **SQLite** e mídia local (sem AWS), nenhuma variável é necessária — o projeto detecta automaticamente a ausência das variáveis e usa os defaults.

Para apontar para **RDS + S3** localmente, crie um arquivo `.env` na raiz (nunca commite este arquivo):

```bash
# Django
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de dados (RDS PostgreSQL)
DATABASE_URL=postgresql://usuario:senha@endpoint-rds:5432/nome_do_banco

# Mídia no S3
AWS_STORAGE_BUCKET_NAME=nome-do-bucket
AWS_S3_REGION_NAME=us-east-1
```

**5. Aplicar migrações**

```bash
python manage.py migrate
```

**6. Criar superusuário administrador (root)**

```bash
python manage.py createsuperuser
# Informe username: root (ou o de sua preferência), email e senha
```

**7. (Opcional) Carregar dados iniciais**

```bash
python manage.py load_initial_data --fixture initial_data.json
```

**8. Iniciar servidor**

```bash
python manage.py runserver
```

Acesse:
- API navegável: `http://127.0.0.1:8000/api/`
- Frontend: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`

---

## Deploy no Elastic Beanstalk

### Pré-requisitos de deploy

- AWS CLI instalada e configurada (`aws configure`)
- EB CLI instalada (`pip install awsebcli`)
- Instância RDS PostgreSQL já criada (ver seção RDS abaixo)
- Bucket S3 já criado (ver seção S3 abaixo)

### Passo a passo

**1. Inicializar o projeto EB (apenas na primeira vez)**

```bash
eb init
# Escolha a região us-east-1
# Selecione a plataforma: Python 3.11
# Nome da aplicação: catalogo-produtos
```

**2. Criar o ambiente de produção (apenas na primeira vez)**

```bash
eb create ap2-jonh \
  --instance-type t3.micro \
  --database.engine postgres \
  --database.username admin \
  --database.password SuaSenhaAqui
```

> Se o RDS já foi criado separadamente, omita os flags `--database.*` e configure via variáveis de ambiente (ver passo 4).

**3. Gerar o pacote `app.zip` para deploy**

```bash
# Na raiz do projeto — exclui arquivos desnecessários
zip -r app.zip . \
  -x "*.git*" \
  -x ".venv/*" \
  -x "__pycache__/*" \
  -x "*.pyc" \
  -x "db.sqlite3" \
  -x "media/*" \
  -x ".env"
```

**4. Configurar variáveis de ambiente no console EB**

Acesse o console AWS → Elastic Beanstalk → seu ambiente → *Configuration → Environment properties* e adicione:

| Variável | Valor |
|----------|-------|
| `SECRET_KEY` | Chave secreta de produção (longa e aleatória) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `ap2-jonh.us-east-1.elasticbeanstalk.com` |
| `DATABASE_URL` | `postgresql://user:senha@endpoint-rds:5432/db` |
| `AWS_STORAGE_BUCKET_NAME` | Nome do bucket S3 de mídia |
| `AWS_S3_REGION_NAME` | `us-east-1` |

Ou via CLI:

```bash
eb setenv \
  SECRET_KEY="..." \
  DEBUG=False \
  ALLOWED_HOSTS="ap2-jonh.us-east-1.elasticbeanstalk.com" \
  DATABASE_URL="postgresql://..." \
  AWS_ACCESS_KEY_ID="..." \
  AWS_SECRET_ACCESS_KEY="..." \
  AWS_STORAGE_BUCKET_NAME="..." \
  AWS_S3_REGION_NAME="us-east-1"
```

**5. Realizar o deploy**

```bash
eb deploy --staged
# Ou usando o app.zip gerado:
eb deploy --label ap2-v1
```

**6. Criar superusuário no ambiente de produção**

```bash
eb ssh
# Dentro da instância:
source /var/app/venv/*/bin/activate
cd /var/app/current
python manage.py createsuperuser
# username: root | defina email e senha segura
```

**7. Verificar o deploy**

```bash
eb status        # Verifica saúde do ambiente
eb logs          # Visualiza logs em tempo real
eb open          # Abre a aplicação no browser
```

---

## 🗄️ Configuração do Amazon RDS PostgreSQL

**1. Criar instância no console AWS**

- Engine: PostgreSQL 15+
- Template: Free tier (para desenvolvimento) ou Production
- Instance: `db.t3.micro`
- DB name: `catalogo`
- Username: `admin`
- Habilitar: *Public access → No* (acesso apenas pela VPC do EB)

**2. Configurar Security Group**

No Security Group do RDS, adicione uma inbound rule:
- Type: `PostgreSQL`
- Port: `5432`
- Source: Security Group do Elastic Beanstalk

**3. Executar migrações no ambiente de produção**

As migrações são executadas automaticamente via `.ebextensions/01_django_migrate.config` a cada deploy (`leader_only: true`).

Para executar manualmente:

```bash
eb ssh
source /var/app/venv/*/bin/activate
cd /var/app/current
python manage.py migrate
```

---

## 🪣 Configuração do Amazon S3

**1. Criar bucket**

```bash
aws s3 mb s3://nome-do-bucket --region us-east-1
```

**2. Configurar política de acesso público para mídia**

No console S3 → seu bucket → *Permissions → Bucket policy*:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadMedia",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::nome-do-bucket/*"
    }
  ]
}
```

**3. Configurar CORS (para uploads via browser)**

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedOrigins": ["http://ap2-jonh.us-east-1.elasticbeanstalk.com"],
    "ExposeHeaders": []
  }
]
```

**4. Criar IAM user com permissões mínimas**

Política inline para o IAM user que o Django usa:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::nome-do-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::nome-do-bucket"
    }
  ]
}
```

---

## 📦 JSONField — Atributos Dinâmicos de Produto (Bônus)

O modelo `Produto` inclui um campo `especificacoes` do tipo `JSONField`, persistido no PostgreSQL como `JSONB`. Isso permite armazenar atributos variáveis por tipo de produto sem alterar o schema relacional.

### Estrutura do campo

```json
{
  "brand": "Dell",
  "item_type": "notebook",
  "price_tier": "high-end",
  "featured": true,
  "name_en": "Dell XPS 15 Laptop",
  "description_en": "Premium laptop...",
  "image_url": "https://bucket.s3.amazonaws.com/media/..."
}
```

### Consultas com filtro em JSONB

**Filtrar por marca:**
```python
Produto.objects.filter(especificacoes__brand="Dell")
```

**Filtrar por tipo de item (case-insensitive):**
```python
Produto.objects.filter(especificacoes__item_type__icontains="notebook")
```

**Filtro combinado: categoria relacional + atributo JSON:**
```python
Produto.objects.filter(
    categoria__nome="Programação & Desenvolvimento",
    especificacoes__price_tier="premium"
)
```

**Via API (endpoint com filtro por marca):**
```
GET /api/produtos/?marca=Samsung
GET /api/produtos/?marca=Dell&categoria=1
```

### Quando usar JSONField vs campo relacional

| Situação | Recomendação |
|----------|-------------|
| Atributo presente em **todos** os produtos (ex.: preço, nome) | Campo relacional (`CharField`, `DecimalField`) |
| Atributo que varia por **tipo** de produto (ex.: RAM só em notebooks) | `JSONField` |
| Necessidade de joins, integridade referencial ou constraints | Campo relacional |
| Metadados flexíveis, variáveis, sem schema fixo | `JSONField` (JSONB no PostgreSQL) |

---

## Evidências de Funcionamento

> **Nota:** As capturas de tela abaixo devem ser inseridas após o deploy e validação em produção.

### Elastic Beanstalk - Console
![Elastic Beanstalk Console](media/screenshots/beanstalk_image.png)

### RDS PostgreSQL — Console AWS
![RDS Console](media/screenshots/rds_image.png)

### S3 — Bucket com arquivos de mídia
![S3 Bucket - product_photos](media/screenshots/s3_image.png)

### API em produção — Pagina de API produtos
![API - Produtos endpoint](media/screenshots/api_image.png)


---

## Troubleshooting

| Problema | Causa provável | Solução |
|----------|---------------|---------|
| `OperationalError: could not connect to server` | Security group do RDS não permite conexão do EB | Adicionar inbound rule do SG do EB no SG do RDS |
| Imagens não aparecem em produção | Variáveis S3 não configuradas no EB | Verificar `eb printenv` e confirmar as 4 variáveis AWS |
| `ALLOWED_HOSTS` error (400 Bad Request) | Host do EB não está na lista | Adicionar URL do EB em `ALLOWED_HOSTS` no EB env vars |
| Admin sem CSS | `collectstatic` não rodou | Verificar `.ebextensions/django.config` e rodar `eb deploy` |
| Migrações não aplicadas | `migrate` falhou no deploy | Verificar logs com `eb logs` e checar conexão com RDS |
| `django.db.utils.ProgrammingError` após migrate | Migration com typo (ver `0008_fix_s3_image_urls.py`) | Corrigir `rom` → `from` na linha 1 da migration |

---

## Referências

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Deploy Django no AWS Elastic Beanstalk](https://docs.aws.amazon.com/pt_br/elasticbeanstalk/latest/dg/create-deploy-python-django.html)
- [Amazon RDS para PostgreSQL](https://docs.aws.amazon.com/pt_br/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [Amazon S3 — Guia do usuário](https://docs.aws.amazon.com/pt_br/AmazonS3/latest/userguide/Welcome.html)
- [django-storages — S3](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)
- [Roteiro de aula — Elastic Beanstalk](https://jonh-carvalho.github.io/BDCC_CDIA_26.1_8001/Disciplina/roteiros/07%20-%20eb/)