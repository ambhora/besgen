from __future__ import annotations

from importlib.resources import files
from pathlib import Path
import re
import subprocess
import sys


def _module(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", name).strip("_").lower()


def _project_class(name: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", name)
    return "".join(part[:1].upper() + part[1:] for part in parts if part)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _copy_tree(source, destination: Path, replacements: dict[str, str]) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for entry in source.iterdir():
        name = entry.name
        for old, new in replacements.items():
            name = name.replace(old, new)
        target = destination / name
        if entry.is_dir():
            _copy_tree(entry, target, replacements)
        else:
            text = entry.read_text(encoding="utf-8")
            for old, new in replacements.items():
                text = text.replace(old, new)
            _write(target, text)


def generate(directory: Path, name: str, template_name: str, ci_name: str = "none") -> None:
    if directory.exists() and any(directory.iterdir()):
        raise FileExistsError(f"{directory} exists and is not empty")
    directory.mkdir(parents=True, exist_ok=True)

    module = _module(name)
    replacements = {
        "__PROJECT__": name,
        "__MODULE__": module,
        "__DEV_MODULE__": f"{module}_dev",
        "__PROJECT_CLASS__": _project_class(name),
        "__TEMPLATE__": template_name,
        "__CI__": ci_name,
    }

    share = files("besgen").joinpath("../../share/besgen").resolve()
    _copy_tree(share / "common", directory, replacements)
    _copy_tree(share / template_name, directory, replacements)
    _copy_tree(share / "dev", directory / "dev", replacements)

    if template_name == "cmake":
        subprocess.run(
            [sys.executable, "-m", "besa", "vendor", str(directory)],
            check=True,
        )

    if ci_name == "github":
        _copy_tree(share / "ci" / "github", directory / ".github" / "workflows", replacements)
    elif ci_name == "gitlab":
        _copy_tree(share / "ci" / "gitlab", directory, replacements)
