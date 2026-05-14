import inspect
from typing import Callable, get_type_hints

from semantic_kernel.functions import kernel_function

from models.messages_kernel import AgentType


class SWEAgentTools:
    """Define Software Engineering (SWE) agent functions (tools)."""

    agent_name = AgentType.SWE_OPENAI.value

    @staticmethod
    @kernel_function(
        description="Analyze a repository and summarize key architecture, risks, and areas to improve."
    )
    async def analyze_repository(repo_url: str) -> str:
        """Analyze a repository and summarize key architecture and risks."""
        return (
            "Repository analysis placeholder. Provide repository URL, tech stack, "
            "and objectives to generate an actionable summary."
        )

    @staticmethod
    @kernel_function(
        description="Triage an issue or feature request into scoped engineering tasks."
    )
    async def triage_issue(issue_description: str) -> str:
        """Triage a software issue or feature request into actionable tasks."""
        return (
            "Issue triage placeholder. Provide acceptance criteria and constraints "
            "to generate a step-by-step task breakdown."
        )

    @staticmethod
    @kernel_function(
        description="Propose a patch plan with key files, test impact, and rollback guidance."
    )
    async def propose_patch(patch_summary: str) -> str:
        """Propose a patch plan with targeted files and test impact."""
        return (
            "Patch plan placeholder. Provide desired changes and constraints to produce "
            "a file-level plan with test and rollout guidance."
        )

    @classmethod
    def get_all_kernel_functions(cls) -> dict[str, Callable]:
        """Return a dictionary of annotated kernel functions."""
        kernel_functions = {}

        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if name.startswith("_") or name == "get_all_kernel_functions":
                continue

            if hasattr(method, "__kernel_function__"):
                kernel_functions[name] = method

        return kernel_functions

    @classmethod
    def generate_tools_json_doc(cls) -> str:
        """Generate a JSON-like string document containing tool metadata."""
        tools_list = []

        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if name.startswith("_") or name == "generate_tools_json_doc":
                continue

            if hasattr(method, "__kernel_function__"):
                description = ""
                if hasattr(method, "__doc__") and method.__doc__:
                    description = method.__doc__.strip()

                if hasattr(method, "__kernel_function__") and getattr(
                    method.__kernel_function__, "description", None
                ):
                    description = method.__kernel_function__.description

                sig = inspect.signature(method)
                args_dict = {}
                type_hints = get_type_hints(method)

                for param_name, param in sig.parameters.items():
                    if param_name in ["cls", "self"]:
                        continue

                    param_type = "string"
                    if param_name in type_hints:
                        type_obj = type_hints[param_name]
                        if hasattr(type_obj, "__name__"):
                            param_type = type_obj.__name__.lower()
                        else:
                            param_type = str(type_obj).lower()
                            if "int" in param_type:
                                param_type = "int"
                            elif "float" in param_type:
                                param_type = "float"
                            elif "bool" in param_type:
                                param_type = "boolean"
                            else:
                                param_type = "string"

                    args_dict[param_name] = {
                        "description": param_name,
                        "title": param_name.replace("_", " ").title(),
                        "type": param_type,
                    }

                tools_list.append(
                    {
                        "agent": cls.agent_name,
                        "function": name,
                        "description": description,
                        "arguments": args_dict,
                    }
                )

        return str(tools_list)
