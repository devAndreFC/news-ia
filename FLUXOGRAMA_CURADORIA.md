# 🔄 Fluxograma: Sistema de Curadoria de Notícias e RabbitMQ

## 📋 Visão Geral do Sistema

O sistema de curadoria de notícias utiliza uma arquitetura baseada em mensageria assíncrona com RabbitMQ para processar a geração, curadoria e distribuição de notícias de forma escalável e desacoplada.

---

## 🏗️ Arquitetura Geral

```mermaid
graph TB
    subgraph "News Curator Service"
        NC[News Curator Agent]
        NG[News Generator]
        OAI[OpenAI Client]
        DB_CUR[Database Manager]
    end
    
    subgraph "RabbitMQ Message Broker"
        Q1[news_generation]
        Q2[newsletter_processing]
        Q3[summary_generation]
    end
    
    subgraph "Backend API"
        API[Django REST API]
        DB_API[PostgreSQL Database]
    end
    
    subgraph "Frontend"
        UI[React SPA]
        USER[Usuário]
    end
    
    NC --> Q1
    NC --> Q2
    NC --> Q3
    Q1 --> NG
    Q2 --> API
    Q3 --> OAI
    NG --> DB_CUR
    API --> DB_API
    UI --> API
    USER --> UI
```

---

## 🔄 Fluxo Principal de Curadoria

### 1. **Inicialização do Sistema**

```mermaid
flowchart TD
    START([Início do Sistema]) --> INIT_CURATOR[Inicializar News Curator]
    INIT_CURATOR --> CONNECT_DB[Conectar ao PostgreSQL]
    CONNECT_DB --> CONNECT_RABBIT[Conectar ao RabbitMQ]
    CONNECT_RABBIT --> SETUP_QUEUES[Configurar Filas]
    SETUP_QUEUES --> SCHEDULE[Agendar Execução Periódica]
    SCHEDULE --> READY([Sistema Pronto])
    
    CONNECT_DB -->|Erro| ERROR_DB[Log: Erro de Conexão DB]
    CONNECT_RABBIT -->|Erro| ERROR_RABBIT[Log: Erro RabbitMQ]
    ERROR_DB --> RETRY_DB[Tentar Novamente]
    ERROR_RABBIT --> RETRY_RABBIT[Tentar Novamente]
    RETRY_DB --> CONNECT_DB
    RETRY_RABBIT --> CONNECT_RABBIT
```

### 2. **Ciclo de Geração de Notícias**

```mermaid
flowchart TD
    TIMER([Timer: 5 minutos]) --> START_BATCH[Iniciar Batch de Geração]
    START_BATCH --> GET_CATEGORIES[Buscar Categorias no DB]
    GET_CATEGORIES --> CHECK_CATEGORIES{Categorias Encontradas?}
    
    CHECK_CATEGORIES -->|Não| LOG_WARNING[Log: Nenhuma categoria encontrada]
    CHECK_CATEGORIES -->|Sim| MESSAGING_CHECK{Messaging Habilitado?}
    
    MESSAGING_CHECK -->|Sim| PUBLISH_REQUEST[Publicar na Fila news_generation]
    MESSAGING_CHECK -->|Não| GENERATE_DIRECT[Gerar Notícias Diretamente]
    
    PUBLISH_REQUEST --> QUEUE_NEWS[Fila: news_generation]
    QUEUE_NEWS --> CONSUME_NEWS[Consumer: Processar Solicitação]
    CONSUME_NEWS --> GENERATE_DIRECT
    
    GENERATE_DIRECT --> OPENAI_CALL[Chamar OpenAI API]
    OPENAI_CALL --> PROCESS_RESPONSE[Processar Resposta IA]
    PROCESS_RESPONSE --> CHECK_DUPLICATES[Verificar Duplicatas]
    CHECK_DUPLICATES --> SAVE_NEWS[Salvar no Banco]
    SAVE_NEWS --> LOG_SUCCESS[Log: Notícias Salvas]
    LOG_SUCCESS --> TIMER
    
    LOG_WARNING --> TIMER
    OPENAI_CALL -->|Erro| LOG_ERROR[Log: Erro OpenAI]
    LOG_ERROR --> TIMER
```

---

## 📨 Sistema de Mensageria RabbitMQ

### **Configuração das Filas**

```mermaid
graph LR
    subgraph "RabbitMQ Queues"
        Q1[news_generation<br/>📰 Geração de Notícias]
        Q2[newsletter_processing<br/>📧 Processamento Newsletter]
        Q3[summary_generation<br/>📝 Geração de Resumos]
    end
    
    subgraph "Propriedades"
        DURABLE[Durable: true<br/>Persistent: true<br/>Auto-delete: false]
    end
    
    Q1 -.-> DURABLE
    Q2 -.-> DURABLE
    Q3 -.-> DURABLE
```

### **Fluxo de Mensagens**

```mermaid
sequenceDiagram
    participant NC as News Curator
    participant RMQ as RabbitMQ
    participant CONS as Consumer
    participant DB as Database
    participant OAI as OpenAI
    
    Note over NC,OAI: Fluxo de Geração de Notícias
    
    NC->>RMQ: 1. Publish news_generation_request
    Note right of RMQ: Fila: news_generation<br/>Message: {categories, news_per_category}
    
    RMQ->>CONS: 2. Deliver message
    CONS->>OAI: 3. Generate news with AI
    OAI-->>CONS: 4. Return generated content
    CONS->>DB: 5. Save news articles
    DB-->>CONS: 6. Confirm save
    CONS->>RMQ: 7. ACK message
    
    Note over NC,OAI: Fluxo de Newsletter
    
    NC->>RMQ: 8. Publish newsletter_processing
    Note right of RMQ: Fila: newsletter_processing<br/>Message: {user_id, newsletter_data}
    
    RMQ->>CONS: 9. Deliver message
    CONS->>DB: 10. Process user preferences
    CONS->>RMQ: 11. ACK message
    
    Note over NC,OAI: Fluxo de Resumos
    
    NC->>RMQ: 12. Publish summary_generation
    Note right of RMQ: Fila: summary_generation<br/>Message: {news_articles, user_preferences}
    
    RMQ->>CONS: 13. Deliver message
    CONS->>OAI: 14. Generate summary
    OAI-->>CONS: 15. Return summary
    CONS->>DB: 16. Save summary
    CONS->>RMQ: 17. ACK message
```

---

## 🔧 Detalhamento dos Componentes

### **1. News Curator Agent**

```mermaid
flowchart LR
    subgraph "News Curator"
        SCHEDULER[Scheduler<br/>⏰ schedule.every(5).minutes]
        GENERATOR[News Generator<br/>🤖 OpenAI Integration]
        DB_MGR[Database Manager<br/>🗄️ PostgreSQL Connection]
        MSG_MGR[Message Manager<br/>📨 RabbitMQ Integration]
    end
    
    SCHEDULER --> GENERATOR
    GENERATOR --> DB_MGR
    GENERATOR --> MSG_MGR
    MSG_MGR --> SCHEDULER
```

### **2. Message Handler**

```mermaid
flowchart TD
    MSG_RECEIVE[Receber Mensagem] --> PARSE_JSON[Parse JSON]
    PARSE_JSON --> VALIDATE[Validar Estrutura]
    VALIDATE -->|Válida| PROCESS[Processar Mensagem]
    VALIDATE -->|Inválida| NACK[NACK + Log Erro]
    
    PROCESS --> TYPE_CHECK{Tipo de Mensagem}
    TYPE_CHECK -->|news_generation| HANDLE_NEWS[Processar Geração]
    TYPE_CHECK -->|newsletter_processing| HANDLE_NEWSLETTER[Processar Newsletter]
    TYPE_CHECK -->|summary_generation| HANDLE_SUMMARY[Processar Resumo]
    
    HANDLE_NEWS --> SUCCESS_NEWS[Sucesso: ACK]
    HANDLE_NEWSLETTER --> SUCCESS_NEWSLETTER[Sucesso: ACK]
    HANDLE_SUMMARY --> SUCCESS_SUMMARY[Sucesso: ACK]
    
    HANDLE_NEWS -->|Erro| FAIL_NEWS[Falha: NACK + Requeue]
    HANDLE_NEWSLETTER -->|Erro| FAIL_NEWSLETTER[Falha: NACK + Requeue]
    HANDLE_SUMMARY -->|Erro| FAIL_SUMMARY[Falha: NACK + Requeue]
```

### **3. Geração de Notícias com IA**

```mermaid
flowchart TD
    START_GEN[Iniciar Geração] --> GET_TEMPLATES[Carregar Templates]
    GET_TEMPLATES --> SELECT_CATEGORY[Selecionar Categoria]
    SELECT_CATEGORY --> CHOOSE_TEMPLATE[Escolher Template]
    CHOOSE_TEMPLATE --> FILL_VARIABLES[Preencher Variáveis]
    FILL_VARIABLES --> OPENAI_PROMPT[Criar Prompt OpenAI]
    
    OPENAI_PROMPT --> CALL_API[Chamar OpenAI API]
    CALL_API --> PARSE_RESPONSE[Processar Resposta]
    PARSE_RESPONSE --> VALIDATE_CONTENT[Validar Conteúdo]
    VALIDATE_CONTENT --> FORMAT_NEWS[Formatar Notícia]
    FORMAT_NEWS --> RETURN_NEWS[Retornar Notícia]
    
    CALL_API -->|Rate Limit| WAIT_RETRY[Aguardar + Retry]
    CALL_API -->|Erro API| LOG_API_ERROR[Log Erro API]
    WAIT_RETRY --> CALL_API
    LOG_API_ERROR --> RETURN_ERROR[Retornar Erro]
```

---

## ⚙️ Configurações e Parâmetros

### **Configuração do Curator**

```yaml
CURATOR_CONFIG:
  generation_interval: 300  # 5 minutos
  news_per_batch: 3        # Notícias por lote
  max_retries: 3           # Tentativas máximas
  retry_delay: 60          # Delay entre tentativas (segundos)
```

### **Configuração RabbitMQ**

```yaml
RABBITMQ_CONFIG:
  host: rabbitmq
  port: 5672
  username: admin
  password: admin123
  enable_messaging: true
  
QUEUES:
  - name: news_generation
    durable: true
    auto_delete: false
  - name: newsletter_processing  
    durable: true
    auto_delete: false
  - name: summary_generation
    durable: true
    auto_delete: false
```

### **Configuração OpenAI**

```yaml
OPENAI_CONFIG:
  model: gpt-3.5-turbo
  max_tokens: 1000
  temperature: 0.7
  timeout: 30
```

---

## 🔄 Estados e Tratamento de Erros

### **Estados das Mensagens**

```mermaid
stateDiagram-v2
    [*] --> Published: Publicar na Fila
    Published --> Delivered: RabbitMQ Entrega
    Delivered --> Processing: Consumer Processa
    Processing --> Success: Processamento OK
    Processing --> Failed: Erro no Processamento
    Success --> Acknowledged: ACK Enviado
    Failed --> Requeued: NACK + Requeue
    Requeued --> Delivered: Tentar Novamente
    Failed --> DeadLetter: Max Retries Excedido
    Acknowledged --> [*]
    DeadLetter --> [*]
```

### **Tratamento de Erros**

```mermaid
flowchart TD
    ERROR[Erro Detectado] --> TYPE{Tipo de Erro}
    
    TYPE -->|Conexão DB| DB_ERROR[Erro Database]
    TYPE -->|RabbitMQ| RABBIT_ERROR[Erro Messaging]
    TYPE -->|OpenAI API| API_ERROR[Erro IA]
    TYPE -->|Parsing| PARSE_ERROR[Erro Parsing]
    
    DB_ERROR --> RETRY_DB[Retry Conexão DB]
    RABBIT_ERROR --> RETRY_RABBIT[Retry RabbitMQ]
    API_ERROR --> RETRY_API[Retry OpenAI]
    PARSE_ERROR --> LOG_PARSE[Log + Skip Message]
    
    RETRY_DB --> CHECK_DB{Max Retries?}
    RETRY_RABBIT --> CHECK_RABBIT{Max Retries?}
    RETRY_API --> CHECK_API{Max Retries?}
    
    CHECK_DB -->|Não| WAIT_DB[Wait + Retry]
    CHECK_DB -->|Sim| FAIL_DB[Falha Crítica DB]
    CHECK_RABBIT -->|Não| WAIT_RABBIT[Wait + Retry]
    CHECK_RABBIT -->|Sim| FAIL_RABBIT[Falha Crítica Messaging]
    CHECK_API -->|Não| WAIT_API[Wait + Retry]
    CHECK_API -->|Sim| SKIP_API[Skip + Log]
    
    WAIT_DB --> RETRY_DB
    WAIT_RABBIT --> RETRY_RABBIT
    WAIT_API --> RETRY_API
```

---

## 📊 Monitoramento e Logs

### **Logs do Sistema**

```mermaid
flowchart LR
    subgraph "Tipos de Log"
        INFO[INFO: Operações Normais]
        WARN[WARNING: Situações Atenção]
        ERROR[ERROR: Falhas Recuperáveis]
        CRITICAL[CRITICAL: Falhas Críticas]
    end
    
    subgraph "Destinos"
        CONSOLE[Console Output]
        FILE[Log Files]
        MONITORING[Sistema Monitoramento]
    end
    
    INFO --> CONSOLE
    WARN --> CONSOLE
    ERROR --> CONSOLE
    CRITICAL --> CONSOLE
    
    INFO --> FILE
    WARN --> FILE
    ERROR --> FILE
    CRITICAL --> FILE
    
    ERROR --> MONITORING
    CRITICAL --> MONITORING
```

### **Métricas Importantes**

- **Taxa de Geração**: Notícias geradas por minuto
- **Taxa de Sucesso**: % de mensagens processadas com sucesso
- **Latência**: Tempo médio de processamento
- **Tamanho das Filas**: Número de mensagens pendentes
- **Uso de API**: Calls para OpenAI por período
- **Erros**: Contagem de erros por tipo

---

## 🚀 Escalabilidade e Performance

### **Estratégias de Escalabilidade**

```mermaid
graph TB
    subgraph "Horizontal Scaling"
        CURATOR1[News Curator 1]
        CURATOR2[News Curator 2]
        CURATOR3[News Curator N]
    end
    
    subgraph "Load Balancing"
        LB[Load Balancer]
        RABBIT[RabbitMQ Cluster]
    end
    
    subgraph "Database"
        DB_MASTER[PostgreSQL Master]
        DB_REPLICA[PostgreSQL Replica]
    end
    
    CURATOR1 --> LB
    CURATOR2 --> LB
    CURATOR3 --> LB
    LB --> RABBIT
    RABBIT --> DB_MASTER
    DB_MASTER --> DB_REPLICA
```

---

**Este fluxograma documenta completamente o sistema de curadoria de notícias, desde a inicialização até o processamento final, incluindo todos os aspectos de mensageria, tratamento de erros e monitoramento.**