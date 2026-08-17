from pathlib import Path

import click

from agentaudit.scanner.discovery import discover_files


@click.group()
def app():
    """Repository-aware AI reliability testing platform."""


@app.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False))
def scan(path: str):
    """Scan and inspect a repository."""

    root = Path(path).resolve()

    try:
        files = discover_files(root)
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise click.ClickException(str(exc))

    click.echo(f"Repository: {root}")
    click.echo(f"Files discovered: {len(files)}")

    for file in files:
        click.echo(f"  {file.relative_to(root)}")


if __name__ == "__main__":
    app()