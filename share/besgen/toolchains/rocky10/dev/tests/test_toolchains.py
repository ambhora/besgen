# SPDX-FileCopyrightText: 2026 __PROJECT__ developers
# SPDX-License-Identifier: Apache-2.0
"""Offline contract tests for a newly generated managed toolchain project."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from __DEV_MODULE__ import toolchains
from __DEV_MODULE__.cli import main
from click.testing import CliRunner


class ToolchainTests(unittest.TestCase):
    def test_compiler_manifest_matches_configuration(self):
        toolchains.sync(check=True)
        text = toolchains.MANIFEST.read_text(encoding="utf-8")
        self.assertIn("  view: false", text)
        data = toolchains.settings()
        self.assertEqual(data["platform"]["target"], "x86_64_v3")
        for compiler in data["compilers"]:
            self.assertIn(compiler["spec"], text)

    def test_pins_and_bootstrap_are_configured(self):
        self.assertEqual(toolchains.get("spack.packages_version"), "v2026.10.0")
        self.assertEqual(toolchains.get("bootstrap.system_compiler"), "GCC:14")
        self.assertEqual(toolchains.get("spack.install_tree"), "/opt/spack")
        self.assertEqual(toolchains.system_compiler_for(toolchains.settings(), "gcc:14")["cxx"], "/usr/bin/g++")

    def test_missing_compiler_lock_is_explicit(self):
        # No dummy or stale compiler lock is generated. A source build must
        # create and commit the real lock before a cache-only restore.
        self.assertFalse(toolchains.LOCKFILE.exists())
        with self.assertRaisesRegex(RuntimeError, "Missing dev/compilers/spack.lock"):
            toolchains.ensure_lock()

    def test_matrix_environments_are_isolated(self):
        a = toolchains.deps_environment("GCC:14")
        b = toolchains.deps_environment("Clang:22")
        self.assertNotEqual(a, b)
        self.assertEqual(a.name, "gcc-14")
        with self.assertRaises(ValueError):
            toolchains.deps_environment("../../invalid")
        self.assertIn("dev/.spack-matrix/", (toolchains.ROOT / ".gitignore").read_text())

    def test_deps_manifest_has_insertion_point(self):
        source = (toolchains.ROOT / "dev/spack.yaml").read_text()
        self.assertEqual(source.count("  packages:\n"), 1)
        self.assertIn("__PROJECT__-dev@1.1+test", source)

    def test_compiler_selectors_are_validated(self):
        data = toolchains.settings()
        self.assertEqual(toolchains.compiler_for(data, "gcc:15")["cxx"], "bin/g++")
        with self.assertRaises(ValueError):
            toolchains.compiler_for(data, "NotACompiler:99")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            toolchains.execute("deps-install", backend="native")

    def test_offline_cli_commands(self):
        runner = CliRunner()
        for command in (("compiler", "sync", "--check"),
                        ("compiler", "get", "platform.target"),
                        ("deps", "--help")):
            result = runner.invoke(main, command)
            self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("x86_64_v3", runner.invoke(main, ["compiler", "get", "platform.target"]).output)

    def test_configured_desktop_and_ci_backend_use_same_spack_inputs(self):
        path = toolchains.ROOT / ".github/workflows/test.yml"
        if not path.exists():
            self.skipTest("No GitHub CI was selected for this project")
        workflow = path.read_text()
        self.assertIn("compiler --backend native bootstrap", workflow)
        self.assertIn("deps --backend native install --compiler GCC:14", workflow)
        self.assertIn("compiler sync --check", workflow)
        self.assertIn("__MODULE_UPPER___BOOTSTRAP_IMAGE", workflow)
        self.assertIn("dev/compilers/spack.lock", (toolchains.ROOT / "dev/README-toolchains.md").read_text())

    def test_deps_install_can_build_missing_cache_items(self):
        calls = []
        with (
            patch.object(toolchains, "verify_platform"),
            patch.object(toolchains, "configure_spack"),
            patch.object(toolchains, "dependency_compiler", return_value=("gcc@=14.3.1", Path("/usr/bin/g++"))),
            patch.object(toolchains, "prepare_deps_environment", return_value=Path("/tmp/gcc-14")),
            patch.object(toolchains, "validate_deps_lock"),
            patch.object(Path, "is_file", return_value=True),
            patch.object(toolchains.os, "access", return_value=True),
            patch.object(toolchains, "run_command", side_effect=lambda *args: calls.append(args)),
        ):
            toolchains.native_deps("install", selector="GCC:14")
        self.assertTrue(any("install" in c and "--only-concrete" in c for c in calls))
        self.assertFalse(any("--cache-only" in c for c in calls))

    def test_compiler_root_restore_is_cache_only(self):
        calls = []
        with (
            patch.object(toolchains, "verify_platform"),
            patch.object(toolchains, "configure_spack"),
            patch.object(toolchains, "sync"),
            patch.object(toolchains, "ensure_lock"),
            patch.object(toolchains, "validate_compiler_lock"),
            patch.object(toolchains, "run_command", side_effect=lambda *args: calls.append(args)),
        ):
            toolchains.native("restore", compilers=("GCC:15",))
        self.assertTrue(any("--cache-only" in c for c in calls))
        self.assertFalse(any("--no-cache" in c or "concretize" in c for c in calls))

    def test_compiler_closure_rejects_incomplete_lock(self):
        with self.assertRaisesRegex(RuntimeError, "missing dependency"):
            toolchains.compiler_closure(
                {"roots": [{"spec": "gcc@15", "hash": "a"}], "concrete_specs": {}},
                ("gcc@15",),
            )


if __name__ == "__main__":
    unittest.main()
