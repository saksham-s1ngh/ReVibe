import typer
import os
import fnmatch
from google import genai
from google.genai import types
from dotenv import load_dotenv
from config import NAMES_TO_IGNORE, PATTERNS_TO_IGNORE, CONTEXT_LINES, MAX_FILES_IN_REPORT
import ast
import importlib

app = typer.Typer(help="ReVibe: a CLI-based assistant to revive old projects!")

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    typer.secho("Error: GEMINI_API_KEY not set", err=True, fg="red")
client = genai.Client(api_key=api_key)

def get_file_snippet(base_dir: str, rel_path: str, error_line: int) -> str:
    """Extract ±CONTEXT_LINES around error_line from a file."""
    full = os.path.join(base_dir, rel_path)
    try:
        with open(full, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return f"<ERROR: {e}>"
    start = max(0, error_line - CONTEXT_LINES - 1)
    end = min(len(lines), error_line + CONTEXT_LINES)
    snippet = []
    for i in range(start, end):
        prefix = ">> " if i == error_line - 1 else "   "
        snippet.append(f"{prefix}{i+1:4d}: {lines[i].rstrip()}")
    return "\n".join(snippet)

def pre_scan_python(base_dir: str) -> list[dict]:
    """
    Walk base_dir, flag up to max no. of files specified with MAX_FILES_IN_REPORT variable Python files with:
    - SyntaxError
    - ModuleNotFound (import issues)
    Returns list of { path, errors: [{type, line, message}] }.
    """
    flagged = []
    for root, dirs, files in os.walk(base_dir):
        # apply ignore filters
        dirs[:] = [
            d for d in dirs
            if d not in NAMES_TO_IGNORE and not any(fnmatch.fnmatch(d, pat) for pat in PATTERNS_TO_IGNORE)
        ]
        for fname in files:
            if not fname.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(root, fname), base_dir)
            full = os.path.join(root, fname)
            errors = []
            # syntax check
            try:
                src = open(full, 'r', encoding='utf-8').read()
                ast.parse(src)
            except SyntaxError as e:
                errors.append({"type": "SyntaxError", "line": e.lineno or 0, "message": e.msg})
                flagged.append({"path": rel, "errors": errors})
                continue
            # import checks
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if importlib.util.find_spec(alias.name) is None:
                            errors.append({"type": "ModuleNotFound", "line": node.lineno, "message": alias.name})
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    if importlib.util.find_spec(mod) is None:
                        errors.append({"type": "ModuleNotFound", "line": node.lineno, "message": mod})
            if errors:
                flagged.append({"path": rel, "errors": errors})
            if len(flagged) >= MAX_FILES_IN_REPORT:
                return flagged
    return flagged

def build_mini_reports(base_dir: str, flagged: list[dict]) -> list[dict]:
    """
    From flagged list, build mini-reports:
    {
      path,
      docstring (if present),
      issues: [{type, line, message, snippet}]
    }
    """
    reports = []
    for item in flagged:
        rel = item["path"]
        entry = {"path": rel, "docstring": "", "issues": []}
        full = os.path.join(base_dir, rel)
        # extract top docstring
        try:
            with open(full, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if lines and lines[0].strip().startswith(('"""', "'''")):
                quote = lines[0].strip()[:3]
                docs = []
                for ln in lines:
                    docs.append(ln.rstrip())
                    if ln.strip().endswith(quote) and len(docs) > 1:
                        break
                entry["docstring"] = "\n".join(docs)
        except Exception as e:
            print(f"Error occurred while building mini reports: {e}")
        for err in item["errors"]:
            snippet = get_file_snippet(base_dir, rel, err["line"])
            entry["issues"].append({
                "type": err["type"],
                "line": err["line"],
                "message": err["message"],
                "snippet": snippet
            })
        reports.append(entry)
    return reports

def generate_plan_via_gemini(mini_reports: list[dict], verbose: bool = False) -> str:
    system_prompt = types.Content(role="system", parts=[types.Part(text="You are an experienced software developer with experience in modernizing legacy systems, reducing technical debt and restoring and refining defunct projects.")])
    user_text = "I detected issues in these files:\n\n"
    for rpt in mini_reports:
        user_text += f"File: {rpt['path']}\n"
        if rpt["docstring"]:
            user_text += f"Top docstring:\n```\n{rpt['docstring']}\n```\n"
        for issue in rpt["issues"]:
            user_text += (
                f"- {issue['type']} at line {issue['line']}: {issue['message']}\n"
                f"  Context:\n```\n{issue['snippet']}\n```\n"
            )
        user_text += "\n"
    user_text += "Please layout a plan to fix these issues sequentially, carefully describing each step if required."
    user = types.Content(role="user", parts=[types.Part(text=user_text)])
    resp = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=[system_prompt, user]
    )
    if verbose:
        typer.secho(f"Prompt tokens: {resp.usage_metadata.prompt_token_count}", fg="cyan")
        typer.secho(f"Response tokens: {resp.usage_metadata.candidates_token_count}", fg="cyan")
    return resp.text

@app.command()
def get_current_dir():
    """
    Function to print the current working directory for the script
    """
    # return os.getcwd()
    typer.echo(os.getcwd())

@app.command("scan")
def scan(
    projectdir: str = typer.Argument(None, help="Path to your project (defaults to current working directory)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show token usage info")
):
    "Scan the project for broken/outdated files and generate a plan to fix them via Gemini(for now)"
    if not projectdir:
        projectdir = os.getcwd()
    typer.secho(f"🔍 Scanning: {projectdir}", fg="yellow")
    flagged = pre_scan_python(projectdir)
    if not flagged:
        typer.secho("✅ No issues found in up to {} files.".format(MAX_FILES_IN_REPORT), fg="green")
        return
    typer.secho("🚩 Found issues in the following files:", fg="red")
    for f in flagged:
        typer.echo(f"  • {f['path']}")
    mini_reports = build_mini_reports(projectdir, flagged)
    plan = generate_plan_via_gemini(mini_reports, verbose)
    typer.secho("\n=== Gemini Plan ===\n", fg="blue")
    typer.echo(plan)

@app.command("get_dir_structure")
def get_dir_structure(projectdir: str = typer.Argument(None, help="Path to your project (defaults to current working directory)")):
    """
    Function that creates a visual structure of the project directory
    """
    if not projectdir:
        projectdir = os.getcwd()
    file_tree = {}
    with os.scandir(projectdir) as proj_dir:
        for entry in proj_dir:
            if entry.name in NAMES_TO_IGNORE or any(fnmatch.fnmatch(entry.name, pat) for pat in PATTERNS_TO_IGNORE):
                continue

            if entry.is_dir(follow_symlinks=False):
                file_tree[entry.name] = get_dir_structure(entry.path)
            else:
                file_tree[entry.name] = None
    # return file_tree
    typer.echo(file_tree)

app()