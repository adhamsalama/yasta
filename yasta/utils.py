import subprocess
from typing import TypedDict

import toml
import typer
from rich import print

allowedtypes = str | list[str]

tomltype = dict[str, dict[str, allowedtypes]]


class ExecutionResult(TypedDict):
    code: int
    output: str
    error: str
    command: str


def readtoml(path: str) -> tomltype:
    with open(path) as file:
        return toml.loads(file.read())


def writetoml(path: str, content: tomltype) -> bool:
    try:
        with open(path, "w") as file:
            dumped = toml.dumps(content)
            file.write(dumped)
            return True
    except:
        return False


def execute_shell_command(command: str, caputre_output: bool = True) -> ExecutionResult:
    result = subprocess.run(command, shell=True, capture_output=caputre_output)
    return {
        "command": result.args,
        "code": result.returncode,
        "output": result.stdout.decode("utf-8") if caputre_output else "",
        "error": result.stderr.decode("utf-8") if caputre_output else "",
    }


def execute_toml(
    commands: dict[str, allowedtypes], target: str, ignore_failed: bool
) -> list[ExecutionResult]:
    target_to_execute = commands[target]
    print_bold(f"Running [blue]'{target}'[/blue] command", "yellow")
    errors: list[ExecutionResult] = []
    execute_toml_commands(commands, target_to_execute, errors, ignore_failed)
    return errors


def execute_toml_commands(
    commands: dict[str, allowedtypes],
    current_command: str | list[str],
    errors: list,
    ignore_failed: bool,
    indent: int = 1,
):
    if isinstance(current_command, str):
        if current_command in commands:
            execute_toml_commands(
                commands, commands[current_command], errors, ignore_failed, indent + 2
            )
        else:
            result = execute_shell_command(current_command)
            if result["code"] == 0:
                # Add spaces in case result is multiline
                indented_output = result["output"].replace("\n", "\n" + " " * indent)
                print_bold(indented_output, "", indent)
                print_bold(":white_heavy_check_mark: Success", "green", indent)
            else:
                print_bold(":x: Error: " + result["error"], "red", indent)
                errors.append(
                    {
                        "command": current_command,
                        "error": result["error"],
                    }
                )
                return
    else:
        for command in current_command:
            print_bold(
                f"Running [blue]'{command}'[/blue] command",
                "yellow",
                indent,
            )
            execute_toml_commands(commands, command, errors, ignore_failed, indent + 2)
            if len(errors) != 0 and not ignore_failed:
                return


def list_to_dict(commands: list[str]) -> dict[str, str | list[str]]:
    commands_dict: dict[str, str | list[str]] = {}
    for command in commands:
        if command.count("=") != 1:
            raise typer.Abort("Please enter key=value pairs correctly.")
        key, value = command.split("=")
        if len(value) > 1 and value[0] == "[" and value[-1] == "]":  # value="[a,b]"
            value = value[1:-1]  # value="a,b"
            value_list = [c for c in value.split(",")]
            commands_dict[key] = value_list
        else:
            commands_dict[key] = value
    return commands_dict


def print_bold(content: str, color: str = "", indent=0):
    print(" " * indent + f"[bold {color}] {content} [/bold {color}]")
