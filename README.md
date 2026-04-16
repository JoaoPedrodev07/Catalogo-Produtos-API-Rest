# Projeto Catálogo de Produtos - AP1

Este projeto consiste em uma API REST para um catálogo de produtos, desenvolvida com Django e Django Rest Framework. A aplicação foi implantada na AWS utilizando o Elastic Beanstalk.

## Integrantes do Grupo

*   João Pedro Lima de Campos
*   Joao Pedro Pingarilho
*   Renan habib Yassin Barbosa
*   Nicholas Vasconcelos Barbosa
*   Douglas Hancock

## Link da API na AWS

A aplicação está disponível no seguinte link:

*   **API Link:** [http://catalogo-produtosap1-env.eba-vpzpjfyt.us-east-1.elasticbeanstalk.com/](http://catalogo-produtosap1-env.eba-vpzpjfyt.us-east-1.elasticbeanstalk.com/)
*   **Endpoint de Produtos:** [http://catalogo-produtosap1-env.eba-vpzpjfyt.us-east-1.elasticbeanstalk.com/api/produtos/](http://catalogo-produtosap1-env.eba-vpzpjfyt.us-east-1.elasticbeanstalk.com/api/produtos/)
*   **Endpoint de Categorias:** [http://catalogo-produtosap1-env.eba-vpzpjfyt.us-east-1.elasticbeanstalk.com/api/categorias/](http://catalogo-produtosap1-env.eba-vpzpjfyt.us-east-1.elasticbeanstalk.com/api/categorias/)

---

## Configuração e Execução Local

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

**Pré-requisitos:**
*   Python 3.11+
*   Git

**Passos:**

1.  **Clone o repositório:**
    ```bash
    git clone [URL do seu repositório no GitHub]
    cd catalogo-produtos
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Para Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # Para macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Aplique as migrações do banco de dados:**
    ```bash
    python manage.py migrate
    ```

5.  **Crie um superusuário para acessar o painel de administração:**
    ```bash
    python manage.py createsuperuser
    ```
    (Siga as instruções para definir nome de usuário, email e senha).

6.  **Execute o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```

7.  Acesse a aplicação em `http://127.0.0.1:8000/` no seu navegador.

---

## Documentação das Etapas de Implementação e Deploy

### 1. Alterações no Código-Fonte

*   **Nova Classe `Categoria`**: Foi adicionado o modelo `Categoria` no arquivo `produtos/models.py` para agrupar os produtos.
*   **Relacionamento**: A classe `Produto` foi atualizada para incluir um relacionamento de chave estrangeira (`ForeignKey`) com a classe `Categoria`.
*   **Serializers**: Foram criados `CategoriaSerializer` e `ProdutoSerializer` em `produtos/serializers.py` para converter os modelos em JSON.
*   **Views e URLs**: Foram implementadas as `ViewSets` para `Produto` e `Categoria` em `produtos/views.py` e as rotas da API foram configuradas em `catalogo/urls.py`.
*   **Frontend Simples**: Um arquivo `index.html` foi criado para consumir a API e exibir os produtos de forma simples, utilizando JavaScript puro (`fetch`).

### 2. Etapas do Deploy na AWS Elastic Beanstalk

O deploy foi configurado para ser automatizado através de arquivos de configuração na pasta `.ebextensions`.

1.  **Inicialização do Ambiente EB:**
    *   O comando `eb init` foi usado para inicializar o ambiente, selecionando a plataforma "Python 3.13 on Amazon Linux 2023".
    *   O comando `eb create` foi usado para criar o ambiente na AWS.

2.  **Configuração do Django para Produção:**
    *   No arquivo `catalogo/settings.py`, a variável `DEBUG` foi definida como `False` e o `ALLOWED_HOSTS` foi configurado para aceitar o domínio do Elastic Beanstalk.
    *   A `SECRET_KEY` foi movida para uma variável de ambiente no EB para maior segurança.

3.  **Criação dos Arquivos de Configuração (`.ebextensions`):**

    *   **`00_django.config`**:
        *   Define o caminho para o arquivo WSGI da aplicação (`catalogo.wsgi:application`).
        *   Configura a variável de ambiente `DJANGO_SETTINGS_MODULE` para `catalogo.settings`.

    *   **`01_django_migrate.config`**:
        *   Executa comandos essenciais durante a implantação:
            *   `collectstatic`: Coleta todos os arquivos estáticos (CSS, JS) do Django.
            *   `migrate`: Aplica as migrações do banco de dados.
        *   Cria o diretório `/media/` e define as permissões corretas para o upload de arquivos.

    *   **`02_media_files.config`**:
        *   Adiciona uma configuração ao servidor Nginx para servir os arquivos de mídia (imagens dos produtos) que são enviados pelos usuários.

4.  **Criação do `Procfile`:**
    *   Um arquivo `Procfile` foi adicionado para instruir o Elastic Beanstalk a usar o `gunicorn` como servidor web para a aplicação Django.
    ```
    web: gunicorn --bind :8000 --workers 3 --threads 2 catalogo.wsgi:application
    ```

5.  **Deploy:**
    *   Após comitar todas as alterações no Git, o comando `eb deploy` foi utilizado para enviar a nova versão para a AWS.
