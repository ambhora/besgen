# SPDX-FileCopyrightText: 2026 __PROJECT__ developers
# SPDX-License-Identifier: Apache-2.0
"""Optional compiler and dependency lifecycle commands."""
from __future__ import annotations

import click

@click.group()
@click.option("--backend", type=click.Choice(["docker", "native"]), default="docker", show_default=True)
@click.option("--volume", help="Persistent Rocky Spack Docker volume.")
@click.option("--image", help="Override the Rocky Linux image.")
@click.option("--cache-image", help="Override the shared GHCR buildcache image.")
@click.pass_context
def deps(ctx: click.Context, backend: str, volume: str | None, image: str | None, cache_image: str | None) -> None:
    """Install, build, publish, or restore development dependencies."""
    ctx.ensure_object(dict)
    ctx.obj.update(backend=backend, volume=volume, image=image, cache_image=cache_image)


def _deps_action(ctx: click.Context, action: str, selector: str) -> None:
    import subprocess

    from . import toolchains

    try:
        toolchains.execute(f"deps-{action}", compilers=(selector,), **ctx.obj)
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError) as error:
        raise click.ClickException(str(error)) from error


@deps.command("build")
@click.option("--compiler", "selector", required=True, help="Exact compiler selector (GCC:14, GCC:15, Clang:22, NVHPC:26.9, ...).")
@click.pass_context
def deps_build(ctx: click.Context, selector: str) -> None:
    """Concretize and build the development DAG on the desktop."""
    _deps_action(ctx, "build", selector)


@deps.command("install")
@click.option("--compiler", "selector", required=True, help="Exact compiler selector (GCC:14, GCC:15, Clang:22, NVHPC:26.9, ...).")
@click.pass_context
def deps_install(ctx: click.Context, selector: str) -> None:
    """Use cached binaries, building missing development dependencies."""
    _deps_action(ctx, "install", selector)


@deps.command("push")
@click.option("--compiler", "selector", required=True, help="Exact compiler selector (GCC:14, GCC:15, Clang:22, NVHPC:26.9, ...).")
@click.pass_context
def deps_push(ctx: click.Context, selector: str) -> None:
    """Publish development dependencies to the shared OCI buildcache."""
    _deps_action(ctx, "push", selector)


@deps.command("restore")
@click.option("--compiler", "selector", required=True, help="Exact compiler selector (GCC:14, GCC:15, Clang:22, NVHPC:26.9, ...).")
@click.pass_context
def deps_restore(ctx: click.Context, selector: str) -> None:
    """Restore locked development dependencies from binaries only."""
    _deps_action(ctx, "restore", selector)


@click.group()
@click.option("--backend", type=click.Choice(["docker", "native"]), default="docker", show_default=True)
@click.option("--volume", help="Persistent Docker volume (defaults to dev/etc/toolchains.toml).")
@click.option("--image", help="Override the Rocky container image.")
@click.option("--cache-image", help="Override the GHCR compiler buildcache image.")
@click.pass_context
def compiler(ctx: click.Context, backend: str, volume: str | None, image: str | None, cache_image: str | None) -> None:
    """Provision x86-64-v3 compilers with Spack (build, restore, publish)."""
    ctx.ensure_object(dict)
    ctx.obj.update(backend=backend, volume=volume, image=image, cache_image=cache_image)


def _compiler_action(ctx: click.Context, action: str, selectors: tuple[str, ...] = ()) -> None:
    import subprocess

    from . import toolchains

    try:
        toolchains.execute(action, compilers=selectors, **ctx.obj)
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError) as error:
        raise click.ClickException(str(error)) from error


@compiler.command("bootstrap")
@click.pass_context
def compiler_bootstrap(ctx: click.Context) -> None:
    """Prepare a Rocky Linux 10 container with pinned Spack repositories."""
    _compiler_action(ctx, "bootstrap")


@compiler.command("system-install")
@click.argument("selector", metavar="GCC:14|GCC:15|Clang:21|NVHPC:26.5|NVHPC:26.9")
@click.pass_context
def compiler_system_install(ctx: click.Context, selector: str) -> None:
    """Install an OS/RPM compiler inside a Rocky container (CI)."""
    _compiler_action(ctx, "system-install", (selector,))


@compiler.command("build")
@click.option("--compiler", "selectors", multiple=True, help="Build just these compiler roots (otherwise all).")
@click.pass_context
def compiler_build(ctx: click.Context, selectors: tuple[str, ...]) -> None:
    """Build compiler toolchains from source, updating the lockfile."""
    _compiler_action(ctx, "build", selectors)


@compiler.command("restore")
@click.option("--compiler", "selectors", multiple=True, help="Restore only selected compiler roots.")
@click.pass_context
def compiler_restore(ctx: click.Context, selectors: tuple[str, ...]) -> None:
    """Cache-only restore; never compile any package."""
    _compiler_action(ctx, "restore", selectors)


@compiler.command("install")
@click.argument("selector", metavar="GCC:15|GCC:16|Clang:22")
@click.pass_context
def compiler_install(ctx: click.Context, selector: str) -> None:
    """Restore one cached compiler and print/export its C++ executable."""
    _compiler_action(ctx, "install", (selector,))


@compiler.command("push")
@click.option("--compiler", "selectors", multiple=True, help="Publish only selected compiler roots.")
@click.pass_context
def compiler_push(ctx: click.Context, selectors: tuple[str, ...]) -> None:
    """Publish installed compilers and dependencies to the OCI buildcache."""
    _compiler_action(ctx, "push", selectors)


@compiler.command("inspect")
@click.pass_context
def compiler_inspect(ctx: click.Context) -> None:
    """Inspect the mirror and installed/remote compiler specifications."""
    _compiler_action(ctx, "inspect")


@compiler.command("sync")
@click.option("--check", is_flag=True, help="Fail when spack.yaml differs from dev/etc configuration.")
def compiler_sync(check: bool) -> None:
    """Generate the compiler Spack manifest from dev/etc/toolchains.toml."""
    from .toolchains import sync

    try:
        sync(check=check)
    except (RuntimeError, ValueError) as error:
        raise click.ClickException(str(error)) from error


@compiler.command("get")
@click.argument("key", metavar="SECTION.KEY")
def compiler_get(key: str) -> None:
    """Print one configuration value (useful in scripts and CI)."""
    from .toolchains import get

    try:
        click.echo(get(key))
    except (ValueError, KeyError) as error:
        raise click.ClickException(str(error)) from error


@compiler.command("set-packages-version")
@click.argument("ref", metavar="vYYYY.MM.PATCH")
def compiler_set_packages_version(ref: str) -> None:
    """Set the pinned spack-packages release for CI and desktop."""
    from .toolchains import set_packages_version

    try:
        set_packages_version(ref)
    except (ValueError, RuntimeError) as error:
        raise click.ClickException(str(error)) from error


def register(main: click.Group) -> None:
    main.add_command(compiler)
    main.add_command(deps)
