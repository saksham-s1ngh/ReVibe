#!/usr/bin/env python3
import os
import textwrap

def main():
    base = "test_project"
    sub = os.path.join(base, "subdir")

    if os.path.exists(base):
        print(f"Directory '{base}' already exists. Please remove or rename it first.")
        return

    os.makedirs(sub, exist_ok=True)

    # Root‐level fixtures
    root_files = {
        "broken_syntax.py": textwrap.dedent("""\
            def greet()
                print("Missing colon here")
        """),
        "missing_import.py": textwrap.dedent("""\
            import totally_nonexistent_module

            print("This import will fail")
        """),
        "todo_marker.py": "# TODO: implement the core logic here\n\npass\n",
    }

    # Subdirectory fixtures
    sub_files = {
        "nested_syntax.py": 'if True print("Forgot colon in nested file")\n',
        "nested_import.py": "from nowhere import nothing_here\n",
        "nested_todo.py": "# TODO: fix nested issues\n\nx = 42\n",
    }

    # Write the files
    for name, content in root_files.items():
        with open(os.path.join(base, name), "w", encoding="utf-8") as f:
            f.write(content)

    for name, content in sub_files.items():
        with open(os.path.join(sub, name), "w", encoding="utf-8") as f:
            f.write(content)

    print(f"✅ Created test fixtures in ./{base}/")

if __name__ == "__main__":
    main()
