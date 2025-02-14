"""Human-in-the-Loop prompt system for ScaffAI."""

from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

console = Console()


class HILPrompt:
    """Human-in-the-Loop prompt system."""

    def __init__(self, agent):
        self.agent = agent

    def ask_project_details(self, name: str | None = None) -> dict[str, Any]:
        """Interactive prompt for project details."""
        console.print(Panel.fit("Let me help you create a new project! 🚀"))

        # Get project name if not provided
        if not name:
            name = Prompt.ask("What's your project name")

        # Ask AI for available templates
        templates = self.agent.chat(
            "List available project templates and give a brief description of each"
        )
        console.print(Panel(templates, title="Available Templates"))

        template = Prompt.ask("Which template would you like to use", default="python")

        # Ask AI about template-specific requirements
        requirements = self.agent.chat(
            f"What additional information do I need for a {template} project?"
        )
        console.print(Panel(requirements, title="Template Requirements"))

        # Build parameters based on template
        params = {"name": name, "template": template}

        if "username" in requirements.lower():
            params["username"] = Prompt.ask("What's your GitHub username")

        if "database" in requirements.lower():
            db_options = self.agent.chat(
                f"What database options are available for {template}?"
            )
            console.print(Panel(db_options, title="Database Options"))
            if Confirm.ask("Would you like to add a database"):
                params["db"] = Prompt.ask("Which database would you like to use")

        # Get output directory
        output = Prompt.ask("Where should I create the project", default=".")
        params["output"] = Path(output)

        # Let AI validate the configuration
        validation = self.agent.chat(
            f"Validate this project configuration and suggest any improvements:\n{params}"
        )
        console.print(Panel(validation, title="Configuration Review"))

        if not Confirm.ask("Would you like to proceed with this configuration"):
            return self.ask_project_details(name)

        return params

    def ask_snippet_details(self, template: str | None = None) -> dict[str, Any]:
        """Interactive prompt for snippet details."""
        console.print(Panel.fit("Let me help you add a snippet! 📝"))

        # Get template if not provided
        if not template:
            template = Prompt.ask(
                "Which template/language are you using", default="python"
            )

        # Ask AI for available snippets
        snippets = self.agent.chat(
            f"List available snippets for {template} and describe each"
        )
        console.print(Panel(snippets, title="Available Snippets"))

        snippet = Prompt.ask("Which snippet would you like to add")

        # Get project directory
        project_dir = Prompt.ask("Where's your project located", default=".")

        # Let AI validate the snippet compatibility
        validation = self.agent.chat(
            f"Check if the {snippet} snippet is compatible with the project in {project_dir} "
            f"and suggest any necessary preparations"
        )
        console.print(Panel(validation, title="Compatibility Check"))

        if not Confirm.ask("Would you like to proceed with adding this snippet"):
            return self.ask_snippet_details(template)

        return {
            "snippet": snippet,
            "template": template,
            "project_dir": Path(project_dir),
        }

    def ask_analysis_details(self) -> dict[str, Any]:
        """Interactive prompt for project analysis."""
        console.print(Panel.fit("Let me analyze your project! 🔍"))

        project_dir = Prompt.ask("Where's your project located", default=".")

        # Ask AI what aspects to analyze
        aspects = self.agent.chat("What aspects should I analyze in the project?")
        console.print(Panel(aspects, title="Analysis Aspects"))

        focus_areas = []
        for area in aspects.split("\n"):
            if area.strip() and Confirm.ask(f"Should I analyze {area.strip()}"):
                focus_areas.append(area.strip())

        return {"project_dir": Path(project_dir), "focus_areas": focus_areas}

    def should_use_hil(self, command: str, params: dict[str, Any]) -> bool:
        """Determine if HIL should be used based on command and params."""
        # If all required parameters are provided, no need for HIL
        if command == "new":
            return not (params.get("name") and params.get("template"))
        elif command == "add_snippet":
            return not (params.get("snippet") and params.get("template"))
        elif command == "analyze":
            return not params.get("project_dir")
        return True  # Default to HIL for unknown commands
