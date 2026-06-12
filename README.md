# Projeto Catálogo de Produtos - Evolução de Arquitetura (AP1 para AP2)

Este repositório documenta a evolução da nossa API REST de Catálogo de Produtos, desenvolvida com **Django** e **Django Rest Framework (DRF)**, e implantada na nuvem da **AWS**.

O projeto foi dividido em duas grandes etapas de evolução (AP1 e AP2), saindo de uma estrutura inicial com armazenamento volátil e banco local para uma arquitetura em nuvem desacoplada, persistente e escalável.

---

## 👥 Integrantes do Grupo
*   Nicholas Vasconcelos
*   João Pedro Lima de Campos
*   Joao Pedro Pingarilho
*   Renan habib Yassin Barbosa
*   Douglas Hancock

---

## 🔗 Links da API na AWS (Elastic Beanstalk)

A aplicação está disponível nos seguintes endereços públicos:

*   **Página Principal (Frontend Consumindo API):** [http://ap2-jonh.us-east-1.elasticbeanstalk.com/](http://ap2-jonh.us-east-1.elasticbeanstalk.com/)
*   **API - Endpoint de Produtos:** [http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/produtos/](http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/produtos/)
*   **API - Endpoint de Categorias:** [http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/categorias/](http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/categorias/)
*   **API - Endpoint de Pedidos:** [http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/pedidos/](http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/pedidos/)
*   **API - Endpoint de Itens de Pedido:** [http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/itens-pedido/](http://ap2-jonh.us-east-1.elasticbeanstalk.com/api/itens-pedido/)

---

## 🚀 Linha do Tempo e Evolução do Projeto

### 📊 Comparação de Recursos

| Recurso | Fase 1 (AP1) | Fase 2 (AP2) |
| :--- | :--- | :--- |
| **Escopo do App** |AP1 Apenas backend de produtos/categorias (`catalogo` e `produtos`) | pra AP2 foi adicionado o frontend e o fluxo de vendas com `Pedido` e `ItemPedido` |

| **Banco de Dados** | SQLite local (arquivo local no servidor) | **Amazon RDS** (PostgreSQL ou MySQL dedicado) |
| **Armazenamento de Mídia** | LOCAL | AP2 **Amazon S3** para armazenar imagens(Bucket dedicado persistente) |
| **Serviço AWS** | Somente **AWS Elastic Beanstalk (EB)** | **EB** + **Amazon RDS** + **Amazon S3** |
| **Persistência de Dados** | Volátil (dados e imagens perdidos em novos deploys/escalabilidade) | Persistência total e desacoplada em nuvem |

---

### 🗺️ Arquitetura Visual

#### Fase 1 (AP1): AWS Elastic Beanstalk Isolado
Na fase 1, toda a aplicação (backend Django, banco de dados SQLite e arquivos de mídia) residia localmente na mesma máquina virtual EC2 gerenciada pelo Elastic Beanstalk.
```mermaid
graph TD
    User([Usuário]) --> Nginx[Nginx / EC2 no Elastic Beanstalk]
    Nginx --> Django[Django Application]
    Django --> SQLite[(SQLite - Arquivo Local)]
    Django --> Media[Media - Pasta Local /media/]
```

#### Fase 2 (AP2): Desacoplamento com RDS e S3
Na fase 2, a arquitetura evoluiu para uma infraestrutura resiliente de produção. O banco de dados e os arquivos estáticos/mídia foram desacoplados da instância de execução.
```mermaid
graph TD
    User([Usuário]) --> EB[AWS Elastic Beanstalk / EC2]
    EB --> Django[Django Application]
    Django --> RDS[(Amazon RDS - Banco de Dados Dedicado)]
    Django --> S3[[Amazon S3 - Bucket de Imagens/Mídia]]
```

---

## 📝 Detalhes de Implementação por Fase

### 1. Fase 1 (AP1): Fundação do Backend e Deploy com Elastic Beanstalk
Nesta fase inicial, implementamos a base estrutural da aplicação e o pipeline de deploy simplificado utilizando somente o **AWS Elastic Beanstalk**.

*   **Estrutura de Modelos**:
    *   Criação da classe `Categoria` para agrupar os itens do sistema.
    *   Criação da classe `Produto` com um relacionamento de chave estrangeira (`ForeignKey`) referenciando `Categoria`, além de suporte para cadastro de preços, estoque e imagens.
*   **Serializers & ViewSets**:
    *   Configuração do Django Rest Framework (DRF) com serializers dinâmicos e ViewSets para automatizar as operações CRUD das categorias e produtos.
*   **Deploy Automatizado com Elastic Beanstalk**:
    *   Inicialização e configuração do ambiente utilizando a ferramenta CLI `eb init` e `eb create`.
    *   Criação da pasta `.ebextensions` para gerenciar comandos automáticos durante o deploy:
        *   `00_django.config`: Configura o caminho WSGI e as variáveis globais de configurações do Django.
        *   `01_django_migrate.config`: Executa o `collectstatic` e as migrações do banco SQLite local na instância.
        *   `02_media_files.config`: Mapeia o servidor Nginx interno para servir os arquivos de mídia armazenados localmente na instância.
    *   Criação do `Procfile` instruindo o Elastic Beanstalk a usar o `gunicorn` como servidor de aplicação com múltiplos workers/threads.

---

### 2. Fase 2 (AP2): Persistência, Escalabilidade e Novas Funcionalidades
Evoluímos a infraestrutura para atender requisitos de escalabilidade horizontal, desacoplamento de banco de dados/mídia e novas funcionalidades comerciais.

*   **Migração para Amazon RDS**:
    *   Para evitar a perda de dados a cada redeploy ou redimensionamento de instâncias, substituímos o banco SQLite local pelo **Amazon RDS** (MySQL ou PostgreSQL dedicado).
    *   Implementamos suporte a variáveis de ambiente em `settings.py` para ler automaticamente conexões seguras tanto via `DATABASE_URL` (com `dj-database-url`) quanto via variáveis tradicionais de ambiente injetadas pelo EB.
*   **Armazenamento de Mídia em Nuvem com Amazon S3**:
    *   Instalação e configuração da biblioteca `django-storages[boto3]` e SDK `boto3`.
    *   Quando as credenciais AWS (`AWS_STORAGE_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) são fornecidas no ambiente, os arquivos e imagens de produtos enviados pelos usuários são salvos e servidos diretamente a partir de um Bucket do **Amazon S3**, garantindo durabilidade e disponibilidade ilimitada.
*   **Adição de Fluxo de Compras (Novos Modelos)**:
    *   Para além de um catálogo passivo, implementamos os modelos `Pedido` e `ItemPedido` no app `produtos` para controle de vendas.
    *   Customização do método `create` em `PedidoViewSet` contendo regras de negócio importantes:
        *   Geração automática de número exclusivo de pedido (`PED` + timestamp + sufixo randômico).
        *   Validação da existência dos produtos adicionados e cálculo dinâmico de subtotais e valor total do pedido.
        *   Prevenção contra a criação de pedidos sem itens ou sem identificação de cliente.

---

## ⚙️ Configuração e Execução Local

### Pré-requisitos
*   Python 3.11+
*   Git

### Passo a Passo

1.  **Clonar o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd Catalogo-Produtos-API-Rest
    ```

2.  **Configurar ambiente virtual:**
    ```bash
    # No Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # No macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instalar pacotes dependentes:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Variáveis de Ambiente (Opcional para Integrações na Nuvem):**
    Para rodar localmente utilizando SQLite e armazenamento local padrão, nenhuma variável é necessária.
    Para apontar para o banco de dados RDS e o storage S3 localmente, defina as variáveis de ambiente:
    ```bash
    # Banco de Dados
    DATABASE_URL=postgres://usuario:senha@rds-endpoint:5432/db_name

    # AWS S3 (Mídia)
    AWS_ACCESS_KEY_ID=sua_chave_de_acesso
    AWS_SECRET_ACCESS_KEY=sua_chave_secreta
    AWS_STORAGE_BUCKET_NAME=nome_do_seu_bucket_s3
    AWS_S3_REGION_NAME=us-east-1
    ```

5.  **Aplicar migrações:**
    ```bash
    python manage.py migrate
    ```

6.  **Criar superusuário (Painel Admin):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Iniciar servidor local:**
    ```bash
    python manage.py runserver
    ```
    Acesse:
    *   API navegável: `http://127.0.0.1:8000/api/`
    *   Painel Administrativo: `http://127.0.0.1:8000/admin/`

---

## 🛠️ Configurações Recomendadas no Elastic Beanstalk (Produção)

Para que a evolução (Fase 2) funcione corretamente no deploy, garanta que as seguintes variáveis estejam configuradas no console do Elastic Beanstalk:

1.  **Configurações do Django**:
    *   `SECRET_KEY`: Chave secreta de produção.
    *   `DEBUG`: `False`.
    *   `ALLOWED_HOSTS`: `catalogo-produtosap1-env.eba-vpzpjfyt.us-east-1.elasticbeanstalk.com` (ou correspondente).
2.  **Variáveis de RDS**:
    *   `DATABASE_URL`: URL no formato `postgresql://usuario:senha@endpoint:porta/banco` ou `mysql://usuario:senha@endpoint:porta/banco`.
3.  **Variáveis de S3**:
    *   `AWS_ACCESS_KEY_ID`: ID de acesso do usuário IAM da AWS.
    *   `AWS_SECRET_ACCESS_KEY`: Chave de acesso secreta correspondente.
    *   `AWS_STORAGE_BUCKET_NAME`: Nome do bucket S3 destinado à mídia.
    *   `AWS_S3_REGION_NAME`: Região do seu bucket (ex: `us-east-1`).
