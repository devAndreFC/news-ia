# News Curator Agent

Agente autônomo para geração automática de notícias usando OpenAI GPT, integrado ao sistema de newsletter.

## Funcionalidades

- **Geração com IA**: Cria notícias realistas usando OpenAI GPT-3.5/4
- **Execução Periódica**: Roda automaticamente em intervalos configuráveis
- **Múltiplas Categorias**: Suporte para diferentes tipos de notícias
- **Detecção de Duplicatas**: Evita notícias repetidas no banco de dados
- **Logging Completo**: Monitoramento detalhado de todas as operações
- **Prompts Especializados**: Templates otimizados para cada categoria

## Estrutura do Projeto

```
news-curator/
├── curator.py          # Aplicação principal
├── config.py           # Configurações
├── database.py         # Gerenciamento do banco de dados
├── news_generator.py   # Gerador de notícias
├── requirements.txt    # Dependências Python
├── Dockerfile         # Container Docker
├── .env.example       # Exemplo de configuração
└── README.md          # Esta documentação
```

## Configuração

Copie o arquivo `.env.example` para `.env` e configure as variáveis:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=newsletter_db
DB_USER=postgres
DB_PASSWORD=postgres

# Curator Configuration
GENERATION_INTERVAL=300  # 5 minutes
NEWS_PER_BATCH=3
MAX_RETRIES=3

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# Logging
LOG_LEVEL=INFO
```

### Configuração da OpenAI

1. Obtenha sua API key em: https://platform.openai.com/api-keys
2. Configure a variável `OPENAI_API_KEY` no arquivo `.env`
3. Ajuste o modelo (`gpt-3.5-turbo` ou `gpt-4`) conforme necessário

## Execução

### Modo Contínuo (Produção)
```bash
python curator.py
```

### Modo Teste (Execução Única)
```bash
python curator.py --once
```

### Docker
```bash
docker build -t news-curator .
docker run --env-file .env news-curator
```

## Categorias Suportadas

- **Tecnologia**: Inovações, startups, produtos tecnológicos
- **Economia**: Indicadores econômicos, mercado financeiro
- **Política**: Projetos de lei, decisões governamentais
- **Esportes**: Resultados de jogos, competições
- **Saúde**: Pesquisas médicas, descobertas científicas

## Templates de Notícias

O sistema utiliza templates predefinidos para cada categoria, com variáveis que são preenchidas aleatoriamente para criar notícias diversificadas e realistas.

## Monitoramento

O agente registra todas as atividades em logs, incluindo:
- Inicialização e shutdown
- Geração de notícias
- Erros e exceções
- Estatísticas de execução

## Configurações Principais

- `GENERATION_INTERVAL`: Intervalo entre gerações (segundos)
- `NEWS_PER_BATCH`: Número de notícias por categoria por execução
- `LOG_LEVEL`: Nível de logging (DEBUG, INFO, WARNING, ERROR)