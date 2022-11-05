import typer
from rich.console import Console
from rich.table import Table

from .utils import (
    execute_toml,
    list_to_dict,
    print_bold,
    readtoml,
    tomltype,
    writetoml,
)

app = typer.Typer()

default_path = "pyproject.toml"
default_group = "yasta-tasks"


@app.command()
def init(path: str = typer.Option(default_path, "-p")):
    content: tomltype = {
        default_group: {"test": "echo 'You do not have any tests.'"},
    }
    writetoml(path, content)


@app.command()
def add(commands: list[str], path: str = typer.Option(default_path, "--path", "-p")):
    commands_dict = list_to_dict(commands)
    file = readtoml(path)
    saved_commands = file[default_group]
    for k, v in commands_dict.items():
        saved_commands[k] = v  # type: ignore
    writetoml(path, file)


@app.command()
def delete(command: str, path: str = typer.Option(default_path)):
    file = readtoml(path)
    commands = file[default_group]
    del commands[command]
    writetoml(path, file)


@app.command()
def run(
    command: str,
    path: str = typer.Option(default_path, "--path", "-p"),
    capture_output: bool = typer.Option(
        False,
        "--caputre-output",
        "-c",
        help="""
        Capturing output waits for the command to finish and then prints the output, coloring the output. \n
        This wouldn't be useful if you're running a webserver and want to see the logs.
        """,
    ),
    ignore_failed: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force running all commands by ignoring failed tests",
    ),
):
    file = readtoml(path)
    commands = file[default_group]
    if not isinstance(commands, dict):
        return
    errors = execute_toml(commands, command, ignore_failed, capture_output)
    if len(errors) == 0:
        print_bold(":white_heavy_check_mark: No errors occured", "green")
        return
    print_bold(f":x: {len(errors)} error(s) occured!", "red")
    table = Table(show_header=True, show_lines=True)
    table.add_column("Command")
    table.add_column("Error") if capture_output else ...
    for error in errors:
        row = {"command": f"[bold red] {error['command']} [/bold red]"}
        if capture_output:
            row["error"] = f"[bold red] {error['error']} [/bold red]"
        table.add_row(*row.values())
    console = Console()
    console.print(table)


@app.command()
def show(
    path: str = typer.Option(default_path, "--path", "-p"),
):
    file = readtoml(path)
    tasks = file[default_group]
    table = Table(show_header=True, show_lines=True)
    table.add_column("Task", style="green")
    table.add_column("Command", style="yellow")
    for k, v in tasks.items():
        table.add_row(k, v if isinstance(v, str) else str(v))
    console = Console()
    console.print(table)
