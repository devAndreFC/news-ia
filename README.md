# Newsletter Inteligente 

Sistema completo de newsletter com curadoria automática de notícias usando IA, arquitetura de microsserviços e comunicação assíncrona.

## Visão Geral

Este projeto implementa uma plataforma de newsletter inteligente que combina:
- **Backend REST API** em Django com autenticação JWT
- **Frontend SPA** em React com interface responsiva
- **Agente Curador IA** para geração automática de notícias
- **Sistema de Mensageria** com RabbitMQ para processamento assíncrono
- **Banco PostgreSQL** para persistência de dados
- **Containerização** completa com Docker

## Arquitetura do Sistema

### Componentes Principais

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │  News Curator   │
│   (React SPA)   │◄──►│  (Django REST)  │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │   PostgreSQL    │    │    RabbitMQ     │
         └──────────────►│   (Database)    │    │ (Message Broker)│
                        └─────────────────┘    └─────────────────┘
```

### Fluxo de Dados

1. **Geração de Notícias**: O News Curator gera notícias automaticamente usando templates e IA
2. **Processamento Assíncrono**: Notícias são enviadas via RabbitMQ para processamento
3. **Persistência**: Dados são armazenados no PostgreSQL após processamento
4. **API REST**: Backend expõe endpoints para consulta e manipulação
5. **Interface**: Frontend consome a API e apresenta dados ao usuário

## Configuração e Instalação

### Pré-requisitos
- Docker e Docker Compose instalados
- Git
- Chave da OpenAI API (opcional, para funcionalidades de IA)

### 1. Clone e Configure
```bash
git clone <url-do-repositorio>
cd teste

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações
```

### 2. Inicie o Sistema
```bash
# Usando Makefile (recomendado)
make setup

# Ou manualmente
docker compose up -d --build
```

### 3. Configure Banco de Dados
```bash
make migrate
make createsuperuser  # Opcional
```

## 🛠️ Decisões Técnicas e Justificativas

### Backend - Django REST Framework
**Por que Django?**
- Framework maduro com ORM robusto
- Django REST Framework oferece serialização automática
- Sistema de autenticação JWT integrado
- Admin interface para gerenciamento
- Excelente para APIs REST

### Frontend - React SPA
**Por que React?**
- Componentização e reutilização de código
- Virtual DOM para performance
- Ecossistema rico de bibliotecas
- Hot reload para desenvolvimento ágil
- Hooks para gerenciamento de estado

### Banco de Dados - PostgreSQL
**Por que PostgreSQL?**
- ACID compliance para consistência
- Suporte a JSON para dados flexíveis
- Performance superior para consultas complexas
- Extensibilidade e funcionalidades avançadas
- Integração nativa com Django

### Message Broker - RabbitMQ
**Por que RabbitMQ?**
- Processamento assíncrono de notícias
- Desacoplamento entre serviços
- Garantia de entrega de mensagens
- Padrões de mensageria robustos
- Monitoramento via interface web

### Containerização - Docker
**Por que Docker?**
- Ambiente consistente entre desenvolvimento e produção
- Isolamento de dependências
- Facilita deploy e escalabilidade
- Orquestração com Docker Compose
- Reprodutibilidade do ambiente

## Estrutura Detalhada do Projeto

```
teste/
├── backend/                    # API Django REST
│   ├── app/                   # Configurações principais
│   │   ├── settings.py       # Configurações Django
│   │   ├── urls.py          # Roteamento principal
│   │   └── wsgi.py          # WSGI application
│   ├── news/                 # App de notícias
│   │   ├── models.py        # Modelos de dados
│   │   ├── serializers.py   # Serialização DRF
│   │   ├── views.py         # Views da API
│   │   └── urls.py          # Rotas do app
│   ├── categories/          # App de categorias
│   ├── authentication/      # Sistema de auth JWT
│   ├── profiles/           # Perfis de usuário
│   └── requirements.txt    # Dependências Python
│
├── frontend/               # SPA React
│   ├── src/
│   │   ├── components/    # Componentes reutilizáveis
│   │   ├── pages/        # Páginas da aplicação
│   │   ├── config/       # Configurações da API
│   │   ├── utils/        # Utilitários
│   │   └── App.jsx       # Componente principal
│   ├── public/           # Arquivos estáticos
│   └── package.json      # Dependências Node.js
│
├── news-curator/          # Agente curador de notícias
│   ├── curator.py        # Lógica principal
│   ├── config.py         # Configurações
│   ├── templates/        # Templates de notícias
│   └── requirements.txt  # Dependências Python
│
├── docker-compose.yml     # Orquestração de serviços
├── Makefile              # Comandos automatizados
└── README.md            # Documentação
```

## Comandos Disponíveis

### Makefile (Recomendado)
```bash
make setup          # Configuração inicial completa
make up            # Inicia todos os serviços
make down          # Para todos os serviços
make restart       # Reinicia todos os serviços
make build         # Reconstrói as imagens
make migrate       # Executa migrações
make createsuperuser # Cria superusuário
make logs          # Mostra logs de todos os serviços
make clean         # Remove containers e volumes
```

### Docker Compose Manual
```bash
docker compose up -d --build    # Inicia com rebuild
docker compose down            # Para serviços
docker compose logs -f         # Logs em tempo real
docker compose exec backend python manage.py [command]
```

### Acessos
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Documentação API**: http://localhost:8000/api/docs/
- **Django Admin**: http://localhost:8000/admin/
- **RabbitMQ Management**: http://localhost:15672 (admin/admin123)

## Funcionalidades Implementadas

### Backend API
- ✅ **Autenticação JWT** completa (login, registro, refresh)
- ✅ **CRUD de Notícias** com paginação e filtros
- ✅ **Sistema de Categorias** para organização
- ✅ **Filtros por Período** (dia, semana, mês)
- ✅ **Perfis de Usuário** com preferências
- ✅ **Paginação** otimizada para performance
- ✅ **Validação** robusta de dados
- ✅ **CORS** configurado para frontend

### Frontend SPA
- ✅ **Interface Responsiva** para todos os dispositivos
- ✅ **Autenticação** com JWT e refresh automático
- ✅ **Listagem de Notícias** com cards visuais
- ✅ **Filtros Dinâmicos** por categoria e período
- ✅ **Paginação** com navegação intuitiva
- ✅ **Gerenciamento de Estado** com React Hooks
- ✅ **Feedback Visual** para loading e erros
- ✅ **Navegação SPA** com React Router

### News Curator (IA)
- ✅ **Geração Automática** de notícias usando templates
- ✅ **Integração OpenAI** para conteúdo inteligente
- ✅ **Processamento Assíncrono** via RabbitMQ
- ✅ **Categorização Automática** de notícias
- ✅ **Agendamento** de execução periódica

### Infraestrutura
- ✅ **Containerização** completa com Docker
- ✅ **Orquestração** com Docker Compose
- ✅ **Message Broker** RabbitMQ configurado
- ✅ **Banco PostgreSQL** com migrações
- ✅ **Volumes Persistentes** para dados
- ✅ **Rede Interna** entre serviços

## API Endpoints

### Autenticação
```http
POST /api/auth/register/     # Registro de usuário
POST /api/auth/login/        # Login
POST /api/auth/refresh/      # Refresh token
POST /api/auth/logout/       # Logout
```

### Notícias
```http
GET    /api/news/           # Listar notícias (com filtros)
POST   /api/news/           # Criar notícia
GET    /api/news/{id}/      # Detalhes da notícia
PUT    /api/news/{id}/      # Atualizar notícia
DELETE /api/news/{id}/      # Deletar notícia

# Parâmetros de filtro:
# ?category=tech&period=week&page=1&page_size=10
```

### Categorias
```http
GET    /api/categories/     # Listar categorias
POST   /api/categories/     # Criar categoria
GET    /api/categories/{id}/ # Detalhes da categoria
PUT    /api/categories/{id}/ # Atualizar categoria
DELETE /api/categories/{id}/ # Deletar categoria
```

### Perfis
```http
GET    /api/profiles/me/              # Perfil do usuário
PUT    /api/profiles/me/              # Atualizar perfil
GET    /api/profiles/me/preferences/  # Preferências
PUT    /api/profiles/me/preferences/  # Atualizar preferências
```

## Configuração de Ambiente

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

### Variáveis de Ambiente (.env)
```env
# Database
POSTGRES_DB=newsletter_db
POSTGRES_USER=newsletter_user
POSTGRES_PASSWORD=newsletter_pass
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# RabbitMQ
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=admin123
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672

# News Curator
OPENAI_API_KEY=your-openai-api-key-here
CURATOR_INTERVAL=3600  # seconds
```

## Fluxo de Desenvolvimento

### 1. Desenvolvimento Local
```bash
# Clone e configure
git clone <repo>
cd teste
cp .env.example .env

# Inicie o ambiente
make setup

# Desenvolva com hot reload
# Frontend: http://localhost:3000 (auto-reload)
# Backend: http://localhost:8000 (auto-reload com volume)
```

### 2. Ciclo de Desenvolvimento
```bash
# Faça suas alterações
# Frontend: src/ (React hot reload automático)
# Backend: backend/ (Django auto-reload com volume)

# Teste suas alterações
make logs  # Monitore logs em tempo real

# Commit suas mudanças
git add .
git commit -m "feat: nova funcionalidade"
```

### 3. Deploy e Produção
```bash
# Build para produção
docker compose -f docker-compose.prod.yml up -d --build

# Ou usando Makefile
make prod-deploy
```

## Testes e Qualidade

### Testes Backend
```bash
# Executar todos os testes
docker compose exec backend python manage.py test

# Testes com coverage
docker compose exec backend coverage run manage.py test
docker compose exec backend coverage report
docker compose exec backend coverage html

# Testes específicos
docker compose exec backend python manage.py test news.tests
```

### Testes Frontend
```bash
# Executar testes React
docker compose exec frontend npm test

# Testes com coverage
docker compose exec frontend npm run test:coverage

# Build de produção
docker compose exec frontend npm run build
```

### Linting e Formatação
```bash
# Python (Backend)
docker compose exec backend flake8 .
docker compose exec backend black .
docker compose exec backend isort .

# JavaScript (Frontend)
docker compose exec frontend npm run lint
docker compose exec frontend npm run format
```

## Debugging e Logs

### Monitoramento
```bash
# Logs em tempo real
make logs

# Logs específicos
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f news-curator
docker compose logs -f rabbitmq

# Status dos containers
docker compose ps
```

### Debug Backend
```bash
# Django shell
docker compose exec backend python manage.py shell

# Executar comandos Django
docker compose exec backend python manage.py [command]

# Acessar container
docker compose exec backend bash
```

### Debug Frontend
```bash
# Acessar container frontend
docker compose exec frontend sh

# Instalar dependências
docker compose exec frontend npm install

# Build manual
docker compose exec frontend npm run build
```

## Troubleshooting

### Problemas Comuns

#### 1. Portas em Uso
```bash
# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Parar e reiniciar
make down
make up
```

#### 2. Problemas de Build
```bash
# Limpar cache Docker
docker system prune -a
make clean
make build
```

#### 3. Erro de Banco de Dados
```bash
# Reset completo (APAGA DADOS!)
docker compose down -v
make setup

# Apenas migrações
make migrate
```

#### 4. Problemas de Rede
```bash
# Recriar rede Docker
docker network prune
docker compose down
docker compose up -d
```

#### 5. Problemas de Permissão
```bash
# Linux/Mac - ajustar permissões
sudo chown -R $USER:$USER .
chmod -R 755 .
```

### Logs de Debug
```bash
# Habilitar debug verbose
export DEBUG=True
export DJANGO_LOG_LEVEL=DEBUG

# Logs detalhados do RabbitMQ
docker compose logs rabbitmq | grep ERROR

# Logs do News Curator
docker compose logs news-curator --tail 50
```

## Próximos Passos

### Melhorias Planejadas
- [ ] Implementar cache Redis para performance
- [ ] Adicionar testes de integração E2E
- [ ] Implementar CI/CD com GitHub Actions
- [ ] Adicionar monitoramento com Prometheus
- [ ] Implementar rate limiting na API
- [ ] Adicionar suporte a WebSockets para notificações
- [ ] Implementar busca full-text com Elasticsearch

### Contribuindo
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

**Desenvolvido com Django, React, RabbitMQ e Docker**
