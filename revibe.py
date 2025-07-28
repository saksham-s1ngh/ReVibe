import typer
import os
import fnmatch
from google import genai
from google.genai import types
from dotenv import load_dotenv
from config import NAMES_TO_IGNORE, PATTERNS_TO_IGNORE

app = typer.Typer()

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

@app.command()
def get_current_dir():
    """
    Function to print the current working directory for the script
    """
    # return os.getcwd()
    typer.echo(os.getcwd())

@app.command()
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