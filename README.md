This project uses Docker Compose and requires a few setup steps before running.

## Prerequisites
- Docker & Docker Compose installed
- Bash shell (for running migration scripts)
- API keys:
  - OPENAI_API_KEY
  - LANGSMITH_API_KEY (for observability)

## Setup Instructions

1. Copy `.env.example` to `.env` and fill in `OPENAI_API_KEY` and `LANGSMITH_API_KEY`.

```bash
   cp .env.example .env
```

2. Start the services

```bash
   docker compose up -d
```

3. Run database migrations

```bash
   ./scripts/pinecone_migration.sh
   ./scripts/postgres_migration.sh
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Observability Setup (LangSmith)

This project uses [LangSmith](https://smith.langchain.com) for tracing and observability.

1. Sign up / log in at https://smith.langchain.com
2. Go to **Settings** → **API Keys** and create a new API key
3. Set it to `LANGSMITH_API_KEY` on your `.env` file
4. Traces will automatically appear in your LangSmith dashboard at https://smith.langchain.com.
