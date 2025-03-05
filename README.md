# Ngor-AI - Code Review Bot

Ngor-AI est un agent de revue de code automatique basé sur GPT-4 qui s'intègre à GitLab via des webhooks.

## Architecture

- `core/` : Logiciel métier (interaction avec GitLab et LLM)
- `handlers/` : Webhook FastAPI
- `config/` : Configuration centralisée via Pydantic
- `prompts/` : Template de prompt modifiable
- `main.py` : Point d'entrée principal

## Lancer

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
