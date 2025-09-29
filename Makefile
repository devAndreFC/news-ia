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
FRONTEND_SERVICE = frontend
BACKEND_SERVICE = backend
DB_SERVICE = db
CURATOR_SERVICE = news-curator

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
	@echo "  make setup          - Sobe todos os serviços (frontend + backend + banco)"
	@echo "  make up             - Sobe os containers"
	@echo "  make down           - Para os containers"
	@echo "  make migrate        - Aplica migrações do backend"
	@echo "  make update         - Atualiza todos os containers"
	@echo "  make update_backend - Atualiza apenas o container do backend"
	@echo "  make update_frontend- Atualiza apenas o container do frontend"
	@echo "  make logs           - Mostra logs dos serviços"
	@echo "  make logs_frontend  - Mostra logs apenas do frontend"
	@echo "  make logs_curator   - Mostra logs do agente curador"
	@echo "  make status         - Mostra status dos containers"
	@echo "  make clean          - Para e remove todos os containers"
	@echo "  make shell          - Acessa shell do container backend"
	@echo "  make shell_frontend - Acessa shell do container frontend"
	@echo "  make shell_curator  - Acessa shell do agente curador"
	@echo "  make curator_test   - Executa o curador uma vez (teste)"
	@echo "  make curator_restart- Reinicia o agente curador"
	@echo "  make curator_consumer - Run curator as RabbitMQ consumer"
	@echo "  make curator_publish  - Publish news generation request"
	@echo "  make rabbitmq_logs    - Show RabbitMQ logs"
	@echo "  make rabbitmq_status  - Show RabbitMQ status"

# Sobe todos os serviços
setup:
	$(call show_message,Subindo todos os serviços...)
	$(DOCKER_COMPOSE) up -d --build
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) python manage.py migrate
	$(call show_message,Serviços iniciados com sucesso!)
	$(call show_message,Frontend disponível em: http://localhost:3000)
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

# Atualiza apenas o frontend
update_frontend:
	$(call show_message,Atualizando container do frontend...)
	$(DOCKER_COMPOSE) stop $(FRONTEND_SERVICE)
	$(DOCKER_COMPOSE) build --no-cache $(FRONTEND_SERVICE)
	$(DOCKER_COMPOSE) up -d $(FRONTEND_SERVICE)
	$(call show_message,Frontend atualizado com sucesso!)

# Mostra logs dos serviços
logs:
	$(call show_message,Mostrando logs dos serviços...)
	$(DOCKER_COMPOSE) logs -f

# Mostra logs apenas do backend
logs_backend:
	$(call show_message,Mostrando logs do backend...)
	$(DOCKER_COMPOSE) logs -f $(BACKEND_SERVICE)

# Mostra logs apenas do frontend
logs_frontend:
	$(call show_message,Mostrando logs do frontend...)
	$(DOCKER_COMPOSE) logs -f $(FRONTEND_SERVICE)

# Mostra logs do agente curador
logs_curator:
	$(call show_message,Mostrando logs do agente curador...)
	$(DOCKER_COMPOSE) logs -f $(CURATOR_SERVICE)

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
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) /bin/bash

# Acessa shell do container frontend
shell_frontend:
	$(call show_message,Acessando shell do frontend...)
	$(DOCKER_COMPOSE) exec $(FRONTEND_SERVICE) /bin/sh

# Acessa shell do agente curador
shell_curator:
	$(call show_message,Acessando shell do agente curador...)
	$(DOCKER_COMPOSE) exec $(CURATOR_SERVICE) /bin/bash

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

# Executa o curador uma vez (teste)
curator_test:
	$(call show_message,Executando agente curador em modo teste...)
	$(DOCKER_COMPOSE) exec $(CURATOR_SERVICE) python curator.py --once
	$(call show_message,Teste do curador concluído!)

# Reinicia o agente curador
curator_restart:
	$(call show_message,Reiniciando agente curador...)
	$(DOCKER_COMPOSE) restart $(CURATOR_SERVICE)
	$(call show_message,Agente curador reiniciado com sucesso!)

# Run curator as RabbitMQ consumer
curator_consumer:
	$(DOCKER_COMPOSE) exec $(CURATOR_SERVICE) python curator.py --consumer

# Publish news generation request
curator_publish:
	$(DOCKER_COMPOSE) exec $(CURATOR_SERVICE) python curator.py --publish

# Show RabbitMQ logs
rabbitmq_logs:
	$(DOCKER_COMPOSE) logs -f rabbitmq

# Show RabbitMQ status
rabbitmq_status:
	$(DOCKER_COMPOSE) exec rabbitmq rabbitmq-diagnostics status