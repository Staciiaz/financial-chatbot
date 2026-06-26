# financial-chatbot

A financial chatbot application built with a Python (FastAPI) backend and a TypeScript (Next.JS) frontend, orchestrated with Docker Compose. The project integrates with OpenAI for chat completions and LangSmith for tracing/observability, and uses Pinecone and Postgres as backing data stores (set up via migration scripts).

## Project Structure

```
financial-chatbot/
├── backend/             # Backend service
├── data/                # Data files
├── frontend/            # Frontend application
├── images/              # Images
├── scripts/             # Migration scripts
├── .env.example         # Environment variable template
├── .gitignore           # Git ignore rules
├── docker-compose.yml   # Docker Compose configuration
├── LICENSE              # License file
└── sample-qa.md         # Sample questions and answers
```

## Tech Stack

- **Backend:** Python, FastAPI
- **Frontend:** TypeScript, Next.JS
- **Infrastructure:** Docker, Docker Compose
- **LLM Provider:** OpenAI
- **Observability:** LangSmith
- **Data stores:** Pinecone (vector store), PostgreSQL

## Prerequisites

- Docker & Docker Compose installed
- Bash shell (for running migration scripts)
- API keys:
  - `OPENAI_API_KEY`
  - `LANGSMITH_API_KEY` (for observability)

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

4. Open <http://localhost:3000> in your browser.

## Observability Setup (LangSmith)

This project uses [LangSmith](https://smith.langchain.com) for tracing and observability.

1. Sign up / log in at <https://smith.langchain.com>
2. Go to **Settings** → **API Keys** and create a new API key
3. Set it to `LANGSMITH_API_KEY` in your `.env` file
4. Traces will automatically appear in your LangSmith dashboard at <https://smith.langchain.com>

## Sample Questions

See [`sample-qa.md`](./sample-qa.md) for example questions and answers the chatbot can handle.

## Project Status

This project currently has no description, website, or topics set on GitHub. Contributions, issues, and stars are welcome.

## License

This project is licensed under the [MIT License](./LICENSE).