"""ScaffAI CLI - AI-powered project scaffolding."""

import os
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Prompt

from .agent import ScaffAgent
from .hil import HILPrompt

app = typer.Typer(help="ScaffAI - AI-powered project scaffolding")
console = Console()


def get_agent() -> ScaffAgent:
    """Get or create the ScaffAI agent."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        api_key = Prompt.ask("Enter your Anthropic API key")
        os.environ["ANTHROPIC_API_KEY"] = api_key
    return ScaffAgent(api_key)


@app.command()
def new(
    name: str | None = typer.Argument(None, help="Project name"),
    template: str = typer.Option(None, help="Template to use"),
    output: Path = typer.Option(None, help="Output directory"),
    username: str = typer.Option(None, help="GitHub username for Go projects"),
    db: str = typer.Option(None, help="Database type (pgx, sqlx, pocketbase)"),
    interactive: bool = typer.Option(None, help="Force interactive mode"),
):
    """Create a new project from template"""
    agent = get_agent()
    hil = HILPrompt(agent)

    # Check if we should use HIL
    params = {
        "name": name,
        "template": template,
        "output": output,
        "username": username,
        "db": db,
    }

    if interactive or hil.should_use_hil("new", params):
        params = hil.ask_project_details(name)

    response = agent.chat(
        f"Create a new project named '{params['name']}' using the {params['template']} template. "
        f"Output directory: {params['output']}"
        + (f", GitHub username: {params['username']}" if params.get("username") else "")
        + (f", database: {params['db']}" if params.get("db") else "")
    )
    console.print(response)


@app.command()
def add_snippet(
    snippet: str | None = typer.Argument(None, help="Snippet name"),
    template: str | None = typer.Argument(
        None, help="Template type (python, golang, etc.)"
    ),
    project_dir: Path = typer.Option(None, help="Project directory"),
    interactive: bool = typer.Option(None, help="Force interactive mode"),
):
    """Add a snippet to an existing project"""
    agent = get_agent()
    hil = HILPrompt(agent)

    # Check if we should use HIL
    params = {
        "snippet": snippet,
        "template": template,
        "project_dir": project_dir,
    }

    if interactive or hil.should_use_hil("add_snippet", params):
        params = hil.ask_snippet_details(template)

    response = agent.chat(
        f"Add the {params['snippet']} snippet for {params['template']} to the project in {params['project_dir']}"
    )
    console.print(response)


@app.command()
def analyze(
    project_dir: Path = typer.Option(None, help="Project directory to analyze"),
    interactive: bool = typer.Option(None, help="Force interactive mode"),
):
    """Analyze project structure and suggest improvements"""
    agent = get_agent()
    hil = HILPrompt(agent)

    # Check if we should use HIL
    params = {"project_dir": project_dir}

    if interactive or hil.should_use_hil("analyze", params):
        params = hil.ask_analysis_details()

    response = agent.chat(
        f"Analyze the project in {params['project_dir']}"
        + (
            f" focusing on: {', '.join(params['focus_areas'])}"
            if params.get("focus_areas")
            else ""
        )
        + " and suggest improvements"
    )
    console.print(response)


@app.command()
def chat(
    message: str = typer.Argument(..., help="Message for the AI agent"),
):
    """Chat with the AI agent"""
    agent = get_agent()
    response = agent.chat(message)
    console.print(response)


def main():
    app()
