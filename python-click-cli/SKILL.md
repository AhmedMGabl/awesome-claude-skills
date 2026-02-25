---
name: python-click-cli
description: Python Click CLI patterns covering commands, groups, options, arguments, prompts, file handling, progress bars, testing, and distribution with setuptools.
---

# Python Click CLI

This skill should be used when building command-line tools with Python Click. It covers commands, groups, options, prompts, progress bars, and testing.

## When to Use This Skill

Use this skill when you need to:

- Build CLI tools with Click decorators
- Define commands, groups, and subcommands
- Handle options, arguments, and prompts
- Add progress bars and colored output
- Test CLI commands with CliRunner

## Setup

```bash
pip install click rich
```

## Basic CLI

```python
import click

@click.command()
@click.option("--name", "-n", required=True, help="Your name")
@click.option("--count", "-c", default=1, help="Number of greetings")
@click.option("--shout/--no-shout", default=False, help="Uppercase output")
def greet(name: str, count: int, shout: bool):
    """Greet someone multiple times."""
    for _ in range(count):
        message = f"Hello, {name}!"
        if shout:
            message = message.upper()
        click.echo(message)

if __name__ == "__main__":
    greet()
```

## Command Groups

```python
@click.group()
@click.option("--verbose", "-v", is_flag=True)
@click.pass_context
def cli(ctx, verbose):
    """A CLI tool for managing resources."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

@cli.command()
@click.argument("name")
@click.option("--email", "-e", required=True)
@click.option("--role", type=click.Choice(["admin", "user", "editor"]), default="user")
@click.pass_context
def create(ctx, name, email, role):
    """Create a new user."""
    if ctx.obj["verbose"]:
        click.echo(f"Creating user: {name}")
    user = create_user(name, email, role)
    click.echo(f"Created user {user.id}: {name} ({role})")

@cli.command()
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table")
@click.option("--limit", default=10)
def list_users(fmt, limit):
    """List all users."""
    users = fetch_users(limit)
    if fmt == "json":
        click.echo(json.dumps(users, indent=2))
    else:
        for u in users:
            click.echo(f"{u['id']}\t{u['name']}\t{u['email']}")

@cli.command()
@click.argument("user_id")
@click.confirmation_option(prompt="Are you sure you want to delete?")
def delete(user_id):
    """Delete a user by ID."""
    delete_user(user_id)
    click.echo(f"Deleted user {user_id}")
```

## Nested Groups

```python
@cli.group()
def config():
    """Manage configuration."""
    pass

@config.command()
@click.argument("key")
@click.argument("value")
def set_value(key, value):
    """Set a config value."""
    save_config(key, value)
    click.echo(f"Set {key} = {value}")

@config.command()
@click.argument("key")
def get_value(key):
    """Get a config value."""
    value = load_config(key)
    click.echo(f"{key} = {value}")
```

## Interactive Prompts

```python
@cli.command()
def init():
    """Initialize a new project."""
    name = click.prompt("Project name", default="my-project")
    description = click.prompt("Description", default="")
    language = click.prompt(
        "Language",
        type=click.Choice(["python", "javascript", "go"]),
        default="python",
    )
    use_docker = click.confirm("Include Docker setup?", default=True)

    click.echo(f"\nCreating project: {name}")
    create_project(name, description, language, use_docker)
    click.secho("Project created!", fg="green", bold=True)
```

## Progress Bars and Output

```python
@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
def process(files):
    """Process multiple files."""
    with click.progressbar(files, label="Processing") as bar:
        for filepath in bar:
            process_file(filepath)

    click.secho("Done!", fg="green")

@cli.command()
def status():
    """Show system status."""
    click.secho("OK", fg="green", bold=True)
    click.secho("WARNING: disk space low", fg="yellow")
    click.secho("ERROR: service unavailable", fg="red", err=True)
```

## File Handling

```python
@cli.command()
@click.option("--input", "-i", type=click.File("r"), default="-")
@click.option("--output", "-o", type=click.File("w"), default="-")
def transform(input, output):
    """Transform input to output."""
    for line in input:
        output.write(line.upper())
```

## Testing

```python
from click.testing import CliRunner

def test_greet():
    runner = CliRunner()
    result = runner.invoke(greet, ["--name", "Alice"])
    assert result.exit_code == 0
    assert "Hello, Alice!" in result.output

def test_create_user():
    runner = CliRunner()
    result = runner.invoke(cli, ["create", "alice", "--email", "alice@example.com"])
    assert result.exit_code == 0
    assert "Created user" in result.output

def test_init_interactive():
    runner = CliRunner()
    result = runner.invoke(cli, ["init"], input="my-app\nA test app\npython\ny\n")
    assert result.exit_code == 0
    assert "Project created!" in result.output
```

## Distribution

```toml
# pyproject.toml
[project.scripts]
myctl = "myapp.cli:cli"
```

## Additional Resources

- Click: https://click.palletsprojects.com/
- API: https://click.palletsprojects.com/en/stable/api/
- Testing: https://click.palletsprojects.com/en/stable/testing/
