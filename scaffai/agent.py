"""ScaffAI Agent - AI-powered project scaffolding."""

from pathlib import Path

from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatAnthropic
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.tools import Tool

SYSTEM_PROMPT = """You are an AI-powered command-line agent that assists users in managing project structures, running commands, and applying predefined rules and snippets. Your role is to understand the project directory, access configuration files, and execute actions based on user requests. Follow best practices, maintain efficiency, and provide recommendations when necessary. If a file or rule is missing, suggest a fix or a suitable alternative. You can execute commands, analyze code, and automate tasks efficiently.

You have access to the following tools:
1. read_rule - Read a project rule template
2. read_snippet - Read a code snippet
3. create_project - Create a new project from a rule
4. apply_snippet - Apply a snippet to an existing project
5. list_rules - List available project rules
6. list_snippets - List available snippets
7. analyze_project - Analyze current project structure
8. run_command - Run a shell command

Always think step by step:
1. Understand the user's request
2. Check available rules/snippets if needed
3. Plan the necessary actions
4. Execute actions one by one
5. Verify the results
6. Provide helpful feedback

Remember to:
- Use proper error handling
- Suggest improvements when applicable
- Follow project-specific best practices
- Keep the user informed of progress
"""


class ScaffAgent:
    def __init__(self, anthropic_api_key: str):
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            anthropic_api_key=anthropic_api_key,
            temperature=0,
        )

        self.tools = [
            Tool(
                name="read_rule",
                func=self._read_rule,
                description="Read a project rule template. Input should be the rule name (e.g., 'python', 'golang')",
            ),
            Tool(
                name="read_snippet",
                func=self._read_snippet,
                description="Read a code snippet. Input should be 'language/category/name' (e.g., 'golang/auth/jwt')",
            ),
            Tool(
                name="create_project",
                func=self._create_project,
                description="Create a new project from a rule. Input should be a JSON string with: name, template, output_dir, username (optional), db (optional)",
            ),
            Tool(
                name="apply_snippet",
                func=self._apply_snippet,
                description="Apply a snippet to an existing project. Input should be a JSON string with: snippet, template, project_dir",
            ),
            Tool(
                name="list_rules",
                func=self._list_rules,
                description="List available project rules",
            ),
            Tool(
                name="list_snippets",
                func=self._list_snippets,
                description="List available snippets for a language. Input should be the language name",
            ),
            Tool(
                name="analyze_project",
                func=self._analyze_project,
                description="Analyze current project structure. Input should be the project directory path",
            ),
            Tool(
                name="run_command",
                func=self._run_command,
                description="Run a shell command. Input should be the command to run",
            ),
        ]

        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            agent_kwargs={
                "system_message": SYSTEM_PROMPT,
                "extra_prompt_messages": [
                    MessagesPlaceholder(variable_name="chat_history")
                ],
            },
            verbose=True,
        )

    def _read_rule(self, rule_name: str) -> str:
        """Read a project rule template."""
        rule_path = Path(__file__).parent / "rules" / f"{rule_name}.txt"
        if not rule_path.exists():
            return f"Rule '{rule_name}' not found"
        return rule_path.read_text()

    def _read_snippet(self, snippet_path: str) -> str:
        """Read a code snippet."""
        full_path = Path(__file__).parent / "snippets" / f"{snippet_path}.txt"
        if not full_path.exists():
            return f"Snippet '{snippet_path}' not found"
        return full_path.read_text()

    def _create_project(self, params: str) -> str:
        """Create a new project from a rule."""
        import json

        from .cli import new

        try:
            p = json.loads(params)
            new(
                name=p["name"],
                template=p["template"],
                output=Path(p.get("output_dir", ".")),
                username=p.get("username"),
                db=p.get("db"),
            )
            return f"Project '{p['name']}' created successfully"
        except Exception as e:
            return f"Failed to create project: {e!s}"

    def _apply_snippet(self, params: str) -> str:
        """Apply a snippet to an existing project."""
        import json

        from .cli import add_snippet

        try:
            p = json.loads(params)
            add_snippet(
                snippet=p["snippet"],
                template=p["template"],
                project_dir=Path(p["project_dir"]),
            )
            return f"Snippet '{p['snippet']}' applied successfully"
        except Exception as e:
            return f"Failed to apply snippet: {e!s}"

    def _list_rules(self) -> str:
        """List available project rules."""
        rules_dir = Path(__file__).parent / "rules"
        rules = [p.stem for p in rules_dir.glob("*.txt")]
        return f"Available rules: {', '.join(rules)}"

    def _list_snippets(self, language: str) -> str:
        """List available snippets for a language."""
        snippets_dir = Path(__file__).parent / "snippets" / language
        if not snippets_dir.exists():
            return f"No snippets found for {language}"

        result = []
        for category in snippets_dir.iterdir():
            if category.is_dir():
                snippets = [s.stem for s in category.glob("*.txt")]
                if snippets:
                    result.append(f"{category.name}: {', '.join(snippets)}")

        return "\n".join(result) if result else f"No snippets found for {language}"

    def _analyze_project(self, project_dir: str) -> str:
        """Analyze current project structure."""

        def scan_dir(path: Path, prefix: str = "") -> list[str]:
            result = []
            for item in sorted(path.iterdir()):
                if item.name.startswith(".") or item.name == "__pycache__":
                    continue
                if item.is_file():
                    result.append(f"{prefix}📄 {item.name}")
                elif item.is_dir():
                    result.append(f"{prefix}📁 {item.name}/")
                    result.extend(scan_dir(item, prefix + "  "))
            return result

        try:
            path = Path(project_dir)
            if not path.exists():
                return f"Directory '{project_dir}' not found"

            structure = scan_dir(path)
            return "Project Structure:\n" + "\n".join(structure)
        except Exception as e:
            return f"Failed to analyze project: {e!s}"

    def _run_command(self, command: str) -> str:
        """Run a shell command."""
        import subprocess

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                return f"Command executed successfully:\n{result.stdout}"
            else:
                return f"Command failed with error:\n{result.stderr}"
        except Exception as e:
            return f"Failed to run command: {e!s}"

    def chat(self, message: str) -> str:
        """Chat with the agent."""
        try:
            response = self.agent.run(message)
            return response
        except Exception as e:
            return f"Error: {e!s}"
