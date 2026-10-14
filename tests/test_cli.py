# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 besgen developers
# --------------------------------------------------------------------------------------------------
from pathlib import Path
import importlib.util
from click.testing import CliRunner
from unittest.mock import patch

from besgen.cli import main


def _invoke(args):
    with patch("besgen.generator.subprocess.run") as run:
        result = CliRunner().invoke(main, args)
    return result, run


def test_directory_after_option(tmp_path: Path):
    out = tmp_path / "foo"
    result, vendor = _invoke(["new", "foo", "--template", "cmake", str(out)])
    assert result.exit_code == 0, result.output
    vendor.assert_called_once()
    command = vendor.call_args.args[0]
    assert command[1:4] == ["-m", "besa", "vendor"]
    assert command[4] == str(out)

    cmake = (out / "CMakeLists.txt").read_text()
    assert "project(foo VERSION 0.1.0 LANGUAGES NONE)" in cmake
    assert "besa_finalize_options()" in (out / "cmake/options.cmake").read_text()
    assert "add_subdirectory(src)" in cmake
    src_cmake = (out / "src/CMakeLists.txt").read_text()
    assert "besa_add_library(NAME libfoo INSTALL YES)" in src_cmake
    assert 'besa_add_directory(LIBRARY libfoo ROOT "${CMAKE_CURRENT_SOURCE_DIR}/cpp" TYPE cpp)' in src_cmake
    assert not (out / "cmake/sources.cmake").exists()
    assert "add_subdirectory(test)" in cmake
    assert "besa_test_add_directory(" in (out / "test/CMakeLists.txt").read_text()
    assert "NAME unit" in (out / "test/CMakeLists.txt").read_text()
    assert "TARGET_LIST foo::libtestfoo" in (out / "test/CMakeLists.txt").read_text()
    test_cmake = (out / "test/CMakeLists.txt").read_text()
    assert "besa_add_library(NAME libtestfoo TYPE STATIC INSTALL NO)" in test_cmake
    assert 'besa_add_directory(LIBRARY libtestfoo ROOT "${CMAKE_CURRENT_SOURCE_DIR}" TYPE cpp)' in test_cmake
    assert "SOURCES " not in test_cmake
    assert "PUBLIC_INCLUDE_DIRECTORIES" not in test_cmake
    assert "CMAKE_CXX_STANDARD" not in cmake
    assert "target_compile_features" not in cmake
    assert "find_package(besa CONFIG REQUIRED)" in cmake
    assert "cmake_minimum_required(VERSION 4.3)" in cmake

    assert (out / "src/cpp/include/foo/foo.hh").is_file()
    assert "#ifndef FOO_HH" in (out / "src/cpp/include/foo/foo.hh").read_text()
    assert (out / "src/cpp/lib/foo/foo.cpp").is_file()
    assert (out / "test/unit/foo.t.cpp").is_file()
    assert not (out / "src/cpp/module/readme.md").exists()
    assert (out / "src/cpp/readme.md").is_file()
    assert not (out / "tests/foo.t.cpp").exists()
    assert "__pycache__/" in (out / "dev/.gitignore").read_text()
    assert not list(out.rglob(".gitkeep"))
    assert "BUILD_DEVTOOLS" in (out / "cmake/options.cmake").read_text()
    assert "BUILD_WARNINGS" in (out / "cmake/options.cmake").read_text()
    assert "PROJECT_SHOWCASE" not in (out / "cmake/options.cmake").read_text()
    assert not (out / "include").exists()
    assert not (out / "src/cpp/foo.cpp").exists()

    spack = (out / "dev/spack.yaml").read_text()
    assert "foo-dev+test" in spack
    assert "./share/spack" in spack
    assert not (out / "spack.yaml").exists()
    dev_cli = (out / "dev/src/foo_dev/cli.py").read_text()
    assert 'ROOT / "dev" / "spack.yaml"' in dev_cli

    dev_package = (out / "dev/share/spack/packages/foo-dev/package.py").read_text()
    assert "class FooDev(BundlePackage):" in dev_package
    assert 'variant("test"' in dev_package
    assert 'depends_on("catch2", when="+test")' in dev_package
    assert 'depends_on("foo")' not in dev_package
    assert "languages:\n  - cpp" in (out / ".besgen.yml").read_text()


def test_directory_before_option(tmp_path: Path):
    out = tmp_path / "foo"
    result = CliRunner().invoke(
        main, ["new", "foo", str(out), "--template", "python"]
    )
    assert result.exit_code == 0, result.output
    assert (out / "pyproject.toml").is_file()


def test_cargo_template(tmp_path: Path):
    out = tmp_path / "foo"
    result = CliRunner().invoke(
        main, ["new", "foo", "--template", "cargo", str(out)]
    )
    assert result.exit_code == 0, result.output
    assert (out / "Cargo.toml").is_file()


def test_generated_docs_use_cpdocs(tmp_path: Path):
    out = tmp_path / "foo"
    result, vendor = _invoke(["new", "foo", "--template", "cmake", str(out)])
    assert result.exit_code == 0, result.output
    vendor.assert_called_once()
    properdocs = (out / "docs/properdocs.yml").read_text()
    cpdocs = (out / "docs/api/cpdocs.yml").read_text()
    docs_project = (out / "docs/pyproject.toml").read_text()
    assert "cpdocs:" in properdocs
    assert "api/cpdocs.yml" in properdocs
    assert "reference/api" in properdocs
    assert 'dependencies = ["cpdocs", "properdocs", "mkdocs-materialx"]' in docs_project
    assert "contract: 3" in cpdocs
    assert "feature-sets:" in cpdocs
    assert "source:" not in cpdocs
    assert "cmake -S ../.." in cpdocs
    assert "BESA_CPDOCS_FEATURE_SETS_OUTPUT" in cpdocs
    assert "BESA_CPDOCS_FEATURE_SET" in cpdocs
    assert "BESA_CPDOCS_MANIFEST_OUTPUT" in cpdocs
    assert "--target besa.cpdocs" in cpdocs


def test_github_docs_ci(tmp_path: Path):
    out = tmp_path / "foo"
    result, _ = _invoke(["new", "foo", "--template", "cmake", "--ci", "github", str(out)])
    assert result.exit_code == 0, result.output
    assert (out / ".github/workflows/pages.yml").is_file()
    assert not (out / ".gitlab-ci.yml").exists()
    assert "ci: github" in (out / ".besgen.yml").read_text()
    workflow = (out / ".github/workflows/pages.yml").read_text()
    assert "properdocs build" in workflow
    assert "docs/web/site" in workflow


def test_gitlab_docs_ci(tmp_path: Path):
    out = tmp_path / "foo"
    result = CliRunner().invoke(
        main, ["new", "foo", "--template", "python", "--ci", "gitlab", str(out)]
    )
    assert result.exit_code == 0, result.output
    assert (out / ".gitlab-ci.yml").is_file()
    assert not (out / ".github").exists()
    assert "ci: gitlab" in (out / ".besgen.yml").read_text()
    workflow = (out / ".gitlab-ci.yml").read_text()
    assert "properdocs build" in workflow
    assert "publish: docs/web/site" in workflow


def test_docs_ci_defaults_to_none(tmp_path: Path):
    out = tmp_path / "foo"
    result = CliRunner().invoke(
        main, ["new", "foo", "--template", "cargo", str(out)]
    )
    assert result.exit_code == 0, result.output
    assert not (out / ".github").exists()
    assert not (out / ".gitlab-ci.yml").exists()
    assert "ci: none" in (out / ".besgen.yml").read_text()


def test_nonempty_directory_is_reported_as_cli_error(tmp_path: Path):
    out = tmp_path / "foo"
    out.mkdir()
    (out / "existing.txt").write_text("keep me")

    result = CliRunner().invoke(
        main, ["new", "foo", "--template", "cmake", str(out)]
    )

    assert result.exit_code != 0
    assert result.exception is not None
    assert "Traceback" not in result.output
    assert f"Error: {out} exists and is not empty" in result.output
    assert (out / "existing.txt").read_text() == "keep me"


def test_language_add_attaches_directory_without_changing_project_languages(tmp_path: Path):
    out = tmp_path / "foo"
    result, _ = _invoke(["new", "foo", "--template", "cmake", str(out)])
    assert result.exit_code == 0, result.output

    # Load the project's generated dev CLI without installing it.
    cli_path = out / "dev/src/foo_dev/cli.py"
    spec = importlib.util.spec_from_file_location("foo_generated_dev_cli", cli_path)
    assert spec and spec.loader
    generated_cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generated_cli)

    project_cmake_before = (out / "CMakeLists.txt").read_text()
    for name in ("fortran", "fortran", "c"):
        result = CliRunner().invoke(generated_cli.main, ["language", "add", name])
        assert result.exit_code == 0, result.output

    src_cmake = (out / "src/CMakeLists.txt").read_text()
    assert src_cmake.count('ROOT "${CMAKE_CURRENT_SOURCE_DIR}/fortran" TYPE fortran') == 1
    assert src_cmake.count('ROOT "${CMAKE_CURRENT_SOURCE_DIR}/c" TYPE c') == 1
    assert src_cmake.count('ROOT "${CMAKE_CURRENT_SOURCE_DIR}/cpp" TYPE cpp') == 1
    assert src_cmake.index("besa_add_library") < src_cmake.index("besa_add_directory")
    assert (out / "CMakeLists.txt").read_text() == project_cmake_before
    assert "LANGUAGES NONE" in project_cmake_before
    assert (out / "src/fortran").is_dir()
    assert (out / "src/c").is_dir()
