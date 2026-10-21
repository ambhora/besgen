# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 besgen developers
# --------------------------------------------------------------------------------------------------
from pathlib import Path
import click

from .generator import generate


@click.group()
def main() -> None:
    """Generate project repositories."""


@main.command()
@click.argument("name")
@click.argument("directory", type=click.Path(path_type=Path))
@click.option(
    "--template",
    "template_name",
    type=click.Choice(["cmake", "python", "cargo"]),
    required=True,
)
@click.option(
    "--ci",
    "ci_name",
    type=click.Choice(["github", "gitlab", "none"]),
    default="none",
    show_default=True,
)
@click.option(
    "--toolchains",
    type=click.Choice(["none", "rocky10"]),
    default="none",
    show_default=True,
    help="Optional managed compiler and Spack development environment (CMake only).",
)
def new(name: str, directory: Path, template_name: str, ci_name: str, toolchains: str) -> None:
    """Create project NAME in DIRECTORY."""
    try:
        generate(directory, name, template_name, ci_name, toolchains=toolchains)
    except (FileExistsError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
