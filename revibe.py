import typer
import os

app = typer.Typer()

@app.command()
def scan():
    print(f"{os.getcwd()}")

app()