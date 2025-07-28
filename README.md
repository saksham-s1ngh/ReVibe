# ReVibe

**AI-Powered Python Project Scanner & Fixer**

ReVibe helps you revive old, outdated, or broken Python codebases by automatically detecting syntax errors, missing imports, and TODO/FIXME markers, then generating a prioritized plan to fix them using Google Gemini's LLM. Perfect for hackathons, demos, and as a resume-worthy project.

---

## 📝 Features

* **Automated Pre-Scan**: Walk your project directory (excluding virtual environments, Git, caches) to flag up to 100 Python files with:

  * Syntax errors
  * Missing-import issues
  * TODO/FIXME markers
* **Contextual Mini-Reports**: For each flagged file, extracts:

  * Top-level docstring (if any)
  * Code snippets ±5 lines around each error or marker
* **Batch LLM Integration**: Sends a single, token-efficient prompt to Gemini to receive a step-by-step fix plan
* **CLI Interface**: Built with Typer for easy commands:

  * `python3 revibe.py scan <project_path>` — run the full scan & plan
  * `python3 revibe.py get-dir-structure <project_path>` — print a filtered directory tree

---

## 🌱 Long-Term Goals

We envision evolving ReVibe into a more flexible, extensible platform:

* **Language-Agnostic Core**: Extend scanning and snippet-generation to multiple languages (JavaScript, Java, Go, etc.) using pluggable language analyzers.
* **Agent-Pluggable Design**: Support multiple LLM backends (Gemini, GPT, Claude) or local open-source models interchangeably via an adapter layer.
* **SLM or Diverse Agentic workflows**: A lightweight version of the application able to run locally on a machine even offline (still need to research the theory first)
* **Interactive Modes**:

  * **Step-by-Step Wizard**: Guide users through fixes interactively (CLI prompts or simple TUI).
  * **Automated Patch Application**: Offer `--apply` to generate and apply diffs directly.
* **Integration Hooks**: Plugins for CI (GitHub Actions), IDE extensions (VSCode), or Git pre-commit hooks for on-the-fly linting and repair recommendations.

---

## 📦 Prerequisites

* Python 3.11 or newer
* [uv package manager](https://docs.astral.sh/uv/) for dependency and environment management
* Google Gemini API key (set in your environment)

---

## ⚙️ Setup & Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/ReVibe.git
   cd ReVibe
   ```
2. **Initialize the project and install dependencies**

   ```bash
   uv init       # bootstraps uv config and lockfile
   uv install    # installs all dependencies into a managed venv
   ```
3. **Set your Gemini API key**

   ```bash
   export GEMINI_API_KEY="your-api-key"
   ```

---

## 🚀 Usage

Run commands via Python directly:

```bash
# 1) Get a visual directory structure
python3 revibe.py get-dir-structure path/to/project

# 2) Scan & generate fix plan (add --verbose for token info)
python3 revibe.py scan path/to/project --verbose
```

*Omit ********************`path/to/project`******************** to default to the current working directory.*

---

## 🧪 Testing with Sample Fixtures

You can generate a small test project containing broken files:

```bash
python3 create_test_project.py
python3 revibe.py scan test_project --verbose
rm -rf test_project
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Please open a GitHub issue or PR.

---

## 👨🏻‍💻 Hackathon Submission

This project was a submission for the Boot.dev 2025 Hackathon: [https://blog.boot.dev/news/hackathon-2025/](https://blog.boot.dev/news/hackathon-2025/)

Thanks to Boot.dev again, for organising this amazing event!
