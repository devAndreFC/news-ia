# Makefile para gerenciar o projeto Newsletter
# Compatível com Windows e Linux

# Detecção do sistema operacional
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
    SHELL := cmd.exe
    .SHELLFLAGS := /c
    # Comando de shell específico do Windows
    SHELL_CMD := cmd
    # Comando de data para backup
    DATE_CMD := %date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    BACKUP_RESTORE_MSG := Para restaurar um backup, execute:\ntype backup_YYYYMMDD_HHMMSS.sql ^| docker-compose exec -T db psql -U django newsletter
else
    DETECTED_OS := $(shell uname -s)
    SHELL := /bin/bash
    # Comando de shell específico do Linux
    SHELL_CMD := /bin/bash
    # Comando de data para backup
    DATE_CMD := $(shell date +%Y%m%d_%H%M%S)
    BACKUP_RESTORE_MSG := Para restaurar um backup, execute:\ncat backup_YYYYMMDD_HHMMSS.sql | docker-compose exec -T db psql -U django newsletter
endif

# Variáveis
DOCKER_COMPOSE = docker-compose
BACKEND_SERVICE = backend
DB_SERVICE = db

# Função para exibir mensagens
define show_message
	@echo $(1)
endef

# Comandos principais
.PHONY: help setup migrate update update_backend clean logs status up down

# Comando padrão - mostra ajuda
help:
	@echo "Sistema detectado: $(DETECTED_OS)"
	@echo "Comandos disponíveis:"
	@echo "  make setup          - Sobe todos os serviços (backend + banco)"
	@echo "  make up             - Sobe os containers"
	@echo "  make down           - Para os containers"
	@echo "  make migrate        - Aplica migrações do backend"
	@echo "  make update         - Atualiza todos os containers"
	@echo "  make update_backend - Atualiza apenas o container do backend"
	@echo "  make logs           - Mostra logs dos serviços"
	@echo "  make status         - Mostra status dos containers"
	@echo "  make clean          - Para e remove todos os containers"
	@echo "  make shell          - Acessa shell do container backend"

# Sobe todos os serviços
setup:
	$(call show_message,Subindo todos os serviços...)
	$(DOCKER_COMPOSE) up -d --build
	$(call show_message,Serviços iniciados com sucesso!)
	$(call show_message,Backend disponível em: http://localhost:9000)
	$(call show_message,Banco PostgreSQL em: localhost:5432)

# Sobe os containers
up:
	$(call show_message,Subindo containers...)
	$(DOCKER_COMPOSE) up -d

# Para os containers
down:
	$(call show_message,Parando containers...)
	$(DOCKER_COMPOSE) down

# Aplica migrações do backend
migrate:
	$(call show_message,Aplicando migrações do backend...)
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) python manage.py makemigrations
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) python manage.py migrate
	$(call show_message,Migrações aplicadas com sucesso!)

# Atualiza todos os containers
update:
	$(call show_message,Atualizando todos os containers...)
	$(DOCKER_COMPOSE) down
	$(DOCKER_COMPOSE) build --no-cache
	$(DOCKER_COMPOSE) up -d
	$(call show_message,Containers atualizados com sucesso!)

# Atualiza apenas o backend
update_backend:
	$(call show_message,Atualizando container do backend...)
	$(DOCKER_COMPOSE) stop $(BACKEND_SERVICE)
	$(DOCKER_COMPOSE) build --no-cache $(BACKEND_SERVICE)
	$(DOCKER_COMPOSE) up -d $(BACKEND_SERVICE)
	$(call show_message,Backend atualizado com sucesso!)

# Mostra logs dos serviços
logs:
	$(call show_message,Mostrando logs dos serviços...)
	$(DOCKER_COMPOSE) logs -f

# Mostra logs apenas do backend
logs_backend:
	$(call show_message,Mostrando logs do backend...)
	$(DOCKER_COMPOSE) logs -f $(BACKEND_SERVICE)

# Mostra status dos containers
status:
	$(call show_message,Status dos containers:)
	$(DOCKER_COMPOSE) ps

# Para e remove todos os containers
clean:
	$(call show_message,Parando e removendo containers...)
	$(DOCKER_COMPOSE) down -v
	$(call show_message,Containers removidos com sucesso!)

# Acessa shell do container backend
shell:
	$(call show_message,Acessando shell do backend...)
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) $(SHELL_CMD)

# Cria superusuário Django
createsuperuser:
	$(call show_message,Criando superusuário Django...)
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) python manage.py createsuperuser

# Coleta arquivos estáticos
collectstatic:
	$(call show_message,Coletando arquivos estáticos...)
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) python manage.py collectstatic --noinput

# Executa testes
test:
	$(call show_message,Executando testes...)
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) python manage.py test

# Backup do banco de dados
backup:
	$(call show_message,Fazendo backup do banco de dados...)
	$(DOCKER_COMPOSE) exec $(DB_SERVICE) pg_dump -U django newsletter > backup_$(DATE_CMD).sql
	$(call show_message,Backup criado com sucesso!)

# Restaura backup do banco de dados
restore:
	$(call show_message,$(BACKUP_RESTORE_MSG))