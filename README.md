# ScaffAI

AI-powered project scaffolding tool that helps generate project structures based on predefined rules and snippets, with Human-in-the-Loop capabilities.

## Features

- 🤖 AI-powered project scaffolding with Claude 3
- 🧑‍💻 Interactive mode with Human-in-the-Loop (HIL)
- 📦 Support for multiple languages and frameworks
- 🔌 Intelligent dependency management
- 📚 Built-in snippets for common patterns
- 🔄 GitHub Actions workflow generation
- ✨ Customizable templates and rules

## Requirements

- Python 3.12 or higher
- [Anthropic API key](https://console.anthropic.com/) for Claude
- [uv](https://github.com/astral-sh/uv) for dependency management

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/scaffai.git
cd scaffai
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Unix
# or
.venv\Scripts\activate     # On Windows
```

3. Install the package:

```bash
uv pip install -e ".[dev]"
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your Anthropic API key
```

## Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
ANTHROPIC_API_KEY=           # Required: Your Anthropic API key
SCAFFAI_DEFAULT_TEMPLATE=    # Optional: Default template (python)
SCAFFAI_RULES_DIR=          # Optional: Rules directory (./rules)
SCAFFAI_SNIPPETS_DIR=       # Optional: Snippets directory (./snippets)
SCAFFAI_INTERACTIVE=        # Optional: Default to interactive mode (false)
```

⚠️ Note: Do not add comments in your actual `.env` file as they may cause issues with some environment variable parsers.

## Usage

ScaffAI can be used in two modes:

1. **Interactive Mode** - AI-driven conversation to guide you through the process
2. **Command Mode** - Direct command-line usage with specific parameters

### Interactive Mode

Just run the commands without parameters or with `--interactive`:

```bash
# Create a new project interactively
scaffai new

# Add a snippet with guidance
scaffai add-snippet

# Analyze project with focused areas
scaffai analyze
```

The AI agent will:

- Ask relevant questions
- Suggest best practices
- Validate your choices
- Provide helpful feedback
- Guide you through the process

### Command Mode

When you know exactly what you want:

```bash
# Create a new project
scaffai new myproject --template golang --username myuser --db pgx

# Add a snippet
scaffai add-snippet auth golang --project-dir ./myproject

# Analyze a project
scaffai analyze --project-dir ./myproject
```

### Chat Mode

Direct conversation with the AI agent:

```bash
# Ask anything
scaffai chat "How can I add logging to my Go project?"

# Get recommendations
scaffai chat "What's the best database for my Python FastAPI project?"
```

## Project Structure

```
scaffai/
├── rules/              # Project templates/rules
│   ├── python.txt      # Python project rules
│   ├── golang.txt      # Go project rules
│   └── typescript.txt  # TypeScript project rules
├── snippets/           # Reusable code snippets
│   ├── golang/
│   │   ├── auth/       # Authentication snippets
│   │   ├── db/         # Database snippets
│   │   └── api/        # API snippets
│   └── python/
│       ├── auth/
│       └── api/
└── cli.py             # Main CLI tool
```

## Rules Format

Rules are written in plain text with natural documentation style:

```
Project Template: My Application
Description: Project description
Version: 1.0.0

Directory Structure:
-------------------
src/
  main.go:
    package main
    // ... code here ...

Dependencies:
------------
Core:
- package1
- package2

Additional Files:
---------------
README.md:
  # Project content
```

## Snippets

Snippets are modular code pieces that can be added to existing projects:

```bash
# List available snippets
scaffai chat "What snippets are available for golang?"

# Add authentication to a Go project
scaffai add-snippet auth golang

# Add database support
scaffai add-snippet db/pgx golang
```

## Development

1. Install development dependencies:

```bash
uv pip install -e ".[dev]"
```

2. Run tests:

```bash
pytest
```

3. Run linters:

```bash
ruff check .
mypy .
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add your rules or snippets
4. Submit a pull request

## License

MIT
