# Backend – Darbot Agent Engine

## Overview
FastAPI-based service providing all server-side capabilities for the Darbot multi-agent platform.

Key features  
- Task / plan generation via Azure OpenAI (`Phi-4-reasoning`)  
- Cosmos DB persistence layer (plan & task documents)  
- Health probes (`/health`, `/api/health/live`, `/api/health/ready`)  
- Modular agent factory (`kernel_agents/`) with Semantic Kernel integration  
- Azure AD protected endpoints (bearer token validation middleware)

---

## Folder layout
```
src/backend/
├── app_kernel.py            # FastAPI application instance
├── app_config.py            # config loader + helpers (Cosmos, OpenAI, etc.)
├── kernel_agents/           # agent implementations + factory
├── middleware/              # auth, health-check, logging
├── models/                  # Pydantic models / error types
├── utils/                   # logging & general helpers
└── tests/                   # backend unit / integration tests
```

---

## Quick start (local)

```bash
# 1. create venv & install deps
python -m venv .venv
. .venv/Scripts/activate      # Windows
pip install -r requirements.txt

# 2. set env vars (example) – see next section
copy .env.sample .env

# 3. run dev server (autorefresh)
uvicorn src.backend.app_kernel:app --reload
```

Visit:  
• Swagger UI → http://localhost:8000/docs  
• Health probe → http://localhost:8000/health

---

## Required environment variables
| Variable | Purpose |
|----------|---------|
| `AZURE_OPENAI_ENDPOINT` | your OpenAI resource endpoint |
| `AZURE_OPENAI_KEY`      | API key / managed identity |
| `AZURE_OPENAI_DEPLOYMENT` | deployment name (`Phi-4-reasoning`) |
| `COSMOS_ENDPOINT`       | Cosmos DB account URI |
| `COSMOS_KEY`            | Primary key |
| `COSMOS_DATABASE_NAME`  | DB name (`darbot`) |
| `AZURE_TENANT_ID`       | AAD tenant for token validation |

---

## Health checks
Route | What it does | Expected response
------|--------------|------------------
`/health` | shallow legacy probe | `{"status":"ok"}`
`/api/health/live` | liveness | `{"live":true}`
`/api/health/ready` | readiness + dependency checks | `{"ready":true,"cosmos":true,...}`

---

## Testing
```bash
pytest -q src/backend/tests
```
All current tests pass (0 failures).

---

## Azure deployment notes
The backend complies with best-practice guidance for Azure App Service / Container Apps:
1. Uses `uvicorn` with `--workers $(WEBSITES_PORT)` override detection.  
2. Reads secrets from `AZURE_APP_CONFIGURATION` or Key Vault when present.  
3. Cosmos connectivity via SDK v4 (`get_cosmos_database_client`).  
4. OpenAI calls routed through Azure OpenAI endpoint.

---

## Troubleshooting
• **ImportError** → ensure every subfolder has `__init__.py` and run from repo root.  
• **Cosmos failures** → verify `COSMOS_*` secrets; container throughput ≥ 400 RU/s.  
• **Auth 401** → client must send AAD access token in `Authorization: Bearer`.

---

## Changelog
• Added `/health` legacy endpoint for automated test-suite compatibility.  
• Introduced `AppConfig.get_cosmos_client()` shim (backwards compatibility).  
• Converted absolute imports to package-relative paths.  
• All backend unit + integration tests green as of _2025-06-04_.