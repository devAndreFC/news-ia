# Newsletter API

Sistema de newsletter com backend Django REST Framework e frontend React.

## 🚀 Configuração Inicial

### Pré-requisitos
- Docker e Docker Compose instalados
- Git

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd teste
```

### 2. Configure as variáveis de ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env conforme necessário
# As configurações padrão funcionam para desenvolvimento local
```

### 3. Inicie o projeto
```bash
# Usando o Makefile (recomendado)
make setup

# Ou manualmente
docker compose up -d --build
```

### 4. Configure o banco de dados
```bash
# Execute as migrações
make migrate

# Ou manualmente
docker compose exec backend python manage.py migrate
```

### 5. Crie um superusuário (opcional)
```bash
# Usando o Makefile
make createsuperuser

# Ou manualmente
docker compose exec backend python manage.py createsuperuser
```

## 📋 Comandos Disponíveis

### Makefile
- `make setup` - Configura e inicia todo o projeto
- `make up` - Inicia os serviços
- `make down` - Para os serviços
- `make migrate` - Executa migrações do banco
- `make createsuperuser` - Cria superusuário Django
- `make logs` - Mostra logs dos serviços
- `make status` - Mostra status dos containers
- `make clean` - Remove containers e volumes
- `make shell` - Acessa shell do backend

### Acessos
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:9000
- **Documentação API**: http://localhost:9000/api/docs/
- **Django Admin**: http://localhost:9000/admin/

## 🔧 Configuração de Ambiente

O projeto usa variáveis de ambiente para configuração. Principais variáveis:

### Docker Compose
- `COMPOSE_PROJECT_NAME` - Nome do projeto (padrão: newsletter)
- `FRONTEND_PORT` - Porta do frontend (padrão: 3000)
- `BACKEND_PORT` - Porta do backend (padrão: 9000)
- `DB_PORT` - Porta do banco (padrão: 5432)

### Banco de Dados
- `POSTGRES_USER` - Usuário do PostgreSQL
- `POSTGRES_PASSWORD` - Senha do PostgreSQL
- `POSTGRES_DB` - Nome do banco de dados

### Django
- `DEBUG` - Modo debug (1 para ativo)
- `SECRET_KEY` - Chave secreta do Django
- `DJANGO_ALLOWED_HOSTS` - Hosts permitidos
- `DATABASE_URL` - URL de conexão com o banco

## 🏗️ Estrutura do Projeto

```
├── backend/          # API Django REST Framework
│   ├── app/         # Configurações do Django
│   ├── common/      # App principal com models, views, etc.
│   └── requirements.txt
├── frontend/        # Aplicação React
│   ├── src/
│   └── package.json
├── docker-compose.yml
├── .env.example     # Exemplo de configuração
├── .env            # Configuração local (não versionado)
└── Makefile        # Comandos automatizados
```

## 🔐 Autenticação

A API usa JWT (JSON Web Tokens) para autenticação:

1. **Registro**: `POST /api/users/register/`
2. **Login**: `POST /api/auth/token/`
3. **Refresh**: `POST /api/auth/token/refresh/`

## 📚 Endpoints da API

### Autenticação
- `POST /api/users/register/` - Registro de usuário
- `POST /api/users/login/` - Login com sessão Django
- `POST /api/users/logout/` - Logout
- `POST /api/auth/token/` - Obter token JWT
- `POST /api/auth/token/refresh/` - Renovar token

### Notícias
- `GET /api/news/` - Listar notícias
- `POST /api/news/` - Criar notícia (admin)
- `GET /api/news/{id}/` - Detalhes da notícia
- `PUT/PATCH /api/news/{id}/` - Atualizar notícia (admin)
- `DELETE /api/news/{id}/` - Excluir notícia (admin)
- `GET /api/news/my_preferences/` - Notícias baseadas em preferências

### Categorias
- `GET /api/categories/` - Listar categorias
- `POST /api/categories/` - Criar categoria (admin)
- `GET /api/categories/{id}/` - Detalhes da categoria
- `PUT/PATCH /api/categories/{id}/` - Atualizar categoria (admin)
- `DELETE /api/categories/{id}/` - Excluir categoria (admin)

### Perfil do Usuário
- `GET /api/profiles/me/` - Meu perfil
- `PATCH /api/profiles/me/` - Atualizar meu perfil
- `GET /api/profiles/` - Listar perfis (admin vê todos)

## 🛠️ Desenvolvimento

### Logs
```bash
# Ver logs de todos os serviços
make logs

# Ver logs apenas do backend
make logs_backend
```

### Testes
```bash
# Executar testes
make test
```

### Shell do Django
```bash
# Acessar shell do Django
make shell
```

## 🚨 Solução de Problemas

### Erro "unable to get image"
Se você encontrar erros relacionados a imagens Docker:
1. Certifique-se de que o Docker Desktop está rodando
2. Execute `make clean` para limpar containers antigos
3. Execute `make setup` novamente

### Problemas de porta
Se as portas estiverem em uso, altere no arquivo `.env`:
```env
FRONTEND_PORT=3001
BACKEND_PORT=9001
DB_PORT=5433
```
