from typing import Dict, List

from config_kernel import config


def _build_status(required: Dict[str, str], optional: Dict[str, str] | None = None) -> Dict[str, object]:
    missing = [name for name, value in required.items() if not value]
    status = {
        "configured": len(missing) == 0,
        "missing": missing,
    }
    if optional is not None:
        status["optional_configured"] = {
            name: bool(value) for name, value in optional.items()
        }
    return status


class IntegrationConfig:
    """Collect integration configuration status for external providers."""

    def summarize(self) -> Dict[str, object]:
        return {
            "swe_agents": {
                "anthropic": _build_status(
                    {"SWE_ANTHROPIC_API_KEY": config.SWE_ANTHROPIC_API_KEY}
                ),
                "github": _build_status(
                    {"SWE_GITHUB_TOKEN": config.SWE_GITHUB_TOKEN}
                ),
                "openai": _build_status(
                    {"SWE_OPENAI_API_KEY": config.SWE_OPENAI_API_KEY}
                ),
            },
            "foundry_local": _build_status(
                {"AZURE_AI_FOUNDRY_LOCAL_ENDPOINT": config.AZURE_AI_FOUNDRY_LOCAL_ENDPOINT},
                optional={
                    "AZURE_AI_PROJECT_ENDPOINT": config.AZURE_AI_PROJECT_ENDPOINT,
                    "AZURE_AI_PROJECT_NAME": config.AZURE_AI_PROJECT_NAME,
                },
            ),
            "m365": _build_status(
                {
                    "M365_TENANT_ID": config.M365_TENANT_ID,
                    "M365_CLIENT_ID": config.M365_CLIENT_ID,
                    "M365_CLIENT_SECRET": config.M365_CLIENT_SECRET,
                },
                optional={
                    "M365_SCOPES": config.M365_SCOPES,
                },
            ),
            "power_platform": _build_status(
                {
                    "POWER_PLATFORM_TENANT_ID": config.POWER_PLATFORM_TENANT_ID,
                    "POWER_PLATFORM_CLIENT_ID": config.POWER_PLATFORM_CLIENT_ID,
                    "POWER_PLATFORM_CLIENT_SECRET": config.POWER_PLATFORM_CLIENT_SECRET,
                    "POWER_PLATFORM_ENVIRONMENT_ID": config.POWER_PLATFORM_ENVIRONMENT_ID,
                },
                optional={
                    "POWER_PLATFORM_REGION": config.POWER_PLATFORM_REGION,
                },
            ),
            "copilot_studio": _build_status(
                {
                    "COPILOT_STUDIO_TENANT_ID": config.COPILOT_STUDIO_TENANT_ID,
                    "COPILOT_STUDIO_CLIENT_ID": config.COPILOT_STUDIO_CLIENT_ID,
                    "COPILOT_STUDIO_CLIENT_SECRET": config.COPILOT_STUDIO_CLIENT_SECRET,
                    "COPILOT_STUDIO_ENDPOINT": config.COPILOT_STUDIO_ENDPOINT,
                }
            ),
        }
