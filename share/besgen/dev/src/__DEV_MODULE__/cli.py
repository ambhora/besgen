# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 __PROJECT__ developers
# --------------------------------------------------------------------------------------------------
from __future__ import annotations

from pathlib import Path
import click
import yaml

ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / ".besgen.yml"

# Besa semantic source types. The declared TYPE, not the project() LANGUAGES
# list, determines which compiler language is enabled for library directories.
LANGUAGES = ("c", "cpp", "fortran", "cuda", "hip")


def config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def save_config(data: dict) -> None:
    CONFIG.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def append_unique(path: Path, text: str) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if text not in current:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(current.rstrip() + "\n\n" + text + "\n", encoding="utf-8")


def add_spack_dependency(spec: str, *, kind: str = "NORMAL", when: str | None = None) -> None:
    """Register dependencies in the bundle instead of adding extra Spack roots.

    Each compiler-specific Spack matrix environment concretizes one bundle,
    so direct roots outside that bundle would not be installed by CI.
    """
    if not spec.strip() or "\n" in spec:
        raise click.UsageError("--spack must be a nonempty, single-line Spack spec")
    package = ROOT / "dev/share/spack/packages/__PROJECT__-dev/package.py"
    if not package.exists():
        raise click.ClickException(f"Development Spack package missing: {package}")
    types = {
        "NORMAL": ("build", "link", "run"),
        "BUILD": ("build", "run"),
        "DEV": ("link", "run"),
    }[kind]
    clause = f"    depends_on({spec!r}, type={types!r}"
    if when:
        clause += f", when={when!r}"
    clause += ")"
    source = package.read_text(encoding="utf-8")
    if clause not in source.splitlines():
        package.write_text(source.rstrip() + "\n" + clause + "\n", encoding="utf-8")


def register_source_language(name: str) -> None:
    """Attach a source tree using Besa's declared semantic source type."""
    path = ROOT / "src" / "CMakeLists.txt"
    declaration = (
        f'besa_add_directory(LIBRARY lib__PROJECT__ ROOT "${{CMAKE_CURRENT_SOURCE_DIR}}/{name}" TYPE {name})'
    )
    # __PROJECT__ is replaced when the project is generated.
    if not path.exists():
        raise click.ClickException("src/CMakeLists.txt is missing")
    source = path.read_text(encoding="utf-8")
    if declaration not in source.splitlines():
        path.write_text(source.rstrip() + "\n" + declaration + "\n", encoding="utf-8")


@click.group()
def main() -> None:
    """Developer tooling for __PROJECT__."""


@main.group()
def language() -> None:
    """Manage implementation languages."""


@language.command("add")
@click.argument("name", type=click.Choice(list(LANGUAGES)))
def language_add(name: str) -> None:
    data = config()
    if data["template"] != "cmake":
        raise click.ClickException("language add is currently supported by the cmake template")
    languages = data.setdefault("languages", [])
    if name not in languages:
        languages.append(name)
        save_config(data)
        (ROOT / "src" / name).mkdir(parents=True, exist_ok=True)
        register_source_language(name)


@main.group()
def project() -> None:
    """Manage shipped constituent projects."""


@project.command("add")
@click.argument("name")
def project_add(name: str) -> None:
    add_constituent("projects", name)


@main.group()
def showcase() -> None:
    """Manage shipped showcases."""


@showcase.command("add")
@click.argument("name")
def showcase_add(name: str) -> None:
    add_constituent("showcases", name)


def add_constituent(kind: str, name: str) -> None:
    data = config()
    base = ROOT / kind / name
    if data["template"] == "cmake":
        for lang in data.get("languages", []):
            (base / "src" / lang).mkdir(parents=True, exist_ok=True)
        (base / "tests/unit").mkdir(parents=True, exist_ok=True)
    elif data["template"] == "python":
        (base / "src").mkdir(parents=True, exist_ok=True)
        (base / "tests/unit").mkdir(parents=True, exist_ok=True)
    else:
        (base / "src").mkdir(parents=True, exist_ok=True)
        (base / "tests").mkdir(parents=True, exist_ok=True)


@main.group()
def feature() -> None:
    """Manage project features."""


@feature.command("add")
@click.argument("name")
def feature_add(name: str) -> None:
    data = config()
    if data["template"] != "cmake":
        raise click.ClickException(
            "feature editing for this template is not implemented yet"
        )
    path = ROOT / "cmake/options.cmake"
    source = path.read_text(encoding="utf-8")
    declaration = f'besa_add_feature("{name}")'
    if declaration in source:
        return
    marker = "# BUILD OPTIONS"
    if marker not in source:
        raise click.ClickException("cmake/options.cmake has no feature section")
    at = source.index(marker)
    # The preceding border is decorative; insert immediately before it.
    at = source.rfind("# ---", 0, at)
    path.write_text(source[:at] + declaration + "\n\n" + source[at:], encoding="utf-8")


@main.group()
def dependency() -> None:
    """Manage external dependencies."""


@dependency.command("add")
@click.option("--cmake")
@click.option("--python", "python_name")
@click.option("--cargo")
@click.option("--spack", required=True, help="Spack spec; preserved verbatim.")
@click.option("--version", help="Build-system dependency version constraint.")
@click.option("--condition", help="BESA project feature condition.")
@click.option("--kind", type=click.Choice(["normal", "build", "dev"], case_sensitive=False), default="normal", show_default=True)
@click.option("--spack-when", help="Optional condition for the Spack bundle dependency, e.g. +test.")
def dependency_add(
    cmake: str | None,
    python_name: str | None,
    cargo: str | None,
    spack: str,
    version: str | None,
    condition: str | None,
    kind: str,
    spack_when: str | None,
) -> None:
    data = config()
    choices = [("cmake", cmake), ("python", python_name), ("cargo", cargo)]
    choices = [(kind, value) for kind, value in choices if value]
    if len(choices) != 1:
        raise click.UsageError("exactly one of --cmake, --python, or --cargo is required")

    backend, name = choices[0]
    expected = {"cmake": "cmake", "python": "python", "cargo": "cargo"}[data["template"]]
    if backend != expected:
        raise click.UsageError(f"{data['template']} projects require --{expected}")

    if backend != "cmake":
        raise click.ClickException("dependency TOML editing for this template is not implemented yet")

    if backend == "cmake":
        args = [f"NAME {name}"]
        if version:
            args.append(f'VERSION "{version}"')
        if condition:
            args.append(f'CONDITION "{condition}"')
        args.append(f"KIND {kind.upper()}")
        add_spack_dependency(spack, kind=kind.upper(), when=spack_when)
        declaration = "besa_dependency_add(\n  " + "\n  ".join(args) + "\n)"
        if spack_when == "+test":
            declaration = "if(BUILD_TESTING)\n  " + declaration.replace("\n", "\n  ") + "\nendif()"
        append_unique(ROOT / "cmake/external.cmake", declaration)
