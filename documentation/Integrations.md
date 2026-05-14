# Integrations Guide

This guide outlines how to enable external provider integrations and SWE agent providers in the Darbot Agent Engine.

## Software Engineering (SWE) agents

The engine now supports SWE-focused agent types aligned to industry-standard providers:

- `SWE_Anthropic_Agent`
- `SWE_GitHub_Agent`
- `SWE_OpenAI_Agent`

Configure provider credentials via environment variables:

| Provider | Required variables |
| --- | --- |
| Anthropic | `SWE_ANTHROPIC_API_KEY` |
| GitHub | `SWE_GITHUB_TOKEN` |
| OpenAI | `SWE_OPENAI_API_KEY` |

These agents use shared SWE tooling for repository analysis, issue triage, and patch planning.

## Azure AI Foundry Local

To target a local Azure AI Foundry runtime, set:

- `AZURE_AI_FOUNDRY_LOCAL_ENDPOINT`

Optional values used for context:

- `AZURE_AI_PROJECT_ENDPOINT`
- `AZURE_AI_PROJECT_NAME`

## Microsoft 365 integration

Set the Microsoft 365 credentials to enable Graph-backed workflows:

- `M365_TENANT_ID`
- `M365_CLIENT_ID`
- `M365_CLIENT_SECRET`

Optional:

- `M365_SCOPES`

## Power Platform integration

Configure Power Platform credentials:

- `POWER_PLATFORM_TENANT_ID`
- `POWER_PLATFORM_CLIENT_ID`
- `POWER_PLATFORM_CLIENT_SECRET`
- `POWER_PLATFORM_ENVIRONMENT_ID`

Optional:

- `POWER_PLATFORM_REGION`

## Copilot Studio integration

Configure Copilot Studio credentials:

- `COPILOT_STUDIO_TENANT_ID`
- `COPILOT_STUDIO_CLIENT_ID`
- `COPILOT_STUDIO_CLIENT_SECRET`
- `COPILOT_STUDIO_ENDPOINT`

## Integration status endpoint

Use the following endpoint to verify integration readiness:

```
GET /api/integrations
```

The response indicates which integrations are configured and which required values are missing.
