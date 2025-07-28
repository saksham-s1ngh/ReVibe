NAMES_TO_IGNORE = {
    ".git", ".gitignore", ".env", "__pycache__", ".venv", "venv"
}
PATTERNS_TO_IGNORE = {
    "*.pyc", "node_modules", ".DS_Store"
}
MAX_FILES_IN_REPORT = 100 # arbitrary value to cap the max amount of files scanned
CONTEXT_LINES = 5 # no. of lines before/after error that will be stored for context