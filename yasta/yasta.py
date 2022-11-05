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
    errors = execute_toml(commands, command, ignore_failed)
    if len(errors) == 0:
        print_bold(":white_heavy_check_mark: No errors occured", "green")
        return
    print_bold(f":x: {len(errors)} error(s) occured!", "red")
    table = Table(show_header=True, show_lines=True)
    table.add_column("Command")
    table.add_column("Error")
    for error in errors:
        table.add_row(
            f"[bold red] {error['command']} [/bold red]",
            f"[bold red] {error['error']} [/bold red]",
        )
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
