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
    assert "add_subdirectory(tests)" in cmake
    assert "besa_test_add_directory(" in (out / "tests/CMakeLists.txt").read_text()
    assert "NAME unit" in (out / "tests/CMakeLists.txt").read_text()
    assert "TARGET_LIST foo::libtestfoo" in (out / "tests/CMakeLists.txt").read_text()
    test_cmake = (out / "tests/CMakeLists.txt").read_text()
    assert "besa_add_library(NAME libtestfoo TYPE STATIC INSTALL NO)" in test_cmake
    assert 'add_subdirectory(common)' in test_cmake
    assert 'besa_add_directory(LIBRARY libtestfoo ROOT "${CMAKE_CURRENT_SOURCE_DIR}/cpp" TYPE cpp)' in (out / "tests/common/CMakeLists.txt").read_text()
    assert "find_package(Catch2" not in test_cmake
    assert "besa_dependency_add(NAME Catch2 VERSION 3 KIND DEV)" in (out / "cmake/external.cmake").read_text()
    assert (out / "tests/common/cpp/include/testfoo/kernels.hh").is_file()
    assert (out / "tests/common/cpp/lib/testfoo/kernels.cpp").is_file()
    assert "SOURCES " not in test_cmake
    assert "PUBLIC_INCLUDE_DIRECTORIES" not in test_cmake
    assert "CMAKE_CXX_STANDARD" not in cmake
    assert "target_compile_features" not in cmake
    assert "find_package(besa CONFIG REQUIRED)" in cmake
    assert "cmake_minimum_required(VERSION 4.3)" in cmake

    assert (out / "src/cpp/include/foo/foo.hh").is_file()
    assert "#ifndef FOO_HH" in (out / "src/cpp/include/foo/foo.hh").read_text()
    assert (out / "src/cpp/lib/foo/foo.cpp").is_file()
    assert (out / "tests/unit/foo.t.cpp").is_file()
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
    assert 'ROOT / "dev/share/spack/packages/foo-dev/package.py"' in dev_cli

    dev_package = (out / "dev/share/spack/packages/foo-dev/package.py").read_text()
    assert "class FooDev(BundlePackage):" in dev_package
    assert 'variant("test"' in dev_package
    assert 'depends_on("cmake@4.3:", type=("build", "run"))' in dev_package
    assert 'depends_on("ninja", type=("build", "run"))' in dev_package
    assert 'depends_on("catch2@3:", when="+test", type=("link", "run"))' in dev_package
    assert 'depends_on("foo")' not in dev_package
    assert "languages:\n  - cpp" in (out / ".besgen.yml").read_text()
    assert 'toolchains: none' in (out / '.besgen.yml').read_text()
    assert '"name": "ci"' in (out / 'CMakePresets.json').read_text()
    assert (out / '.clang-format').is_file()
    assert 'build/' in (out / '.gitignore').read_text()


def test_directory_before_option(tmp_path: Path):
    out = tmp_path / "foo"
    result = CliRunner().invoke(
        main, ["new", "foo", str(out), "--template", "python"]
    )
    assert result.exit_code == 0, result.output
    assert (out / "pyproject.toml").is_file()
    assert not (out / "CMakePresets.json").exists()


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
    assert (out / '.github/workflows/test.yml').is_file()
    assert (out / '.github/workflows/reuse.yml').is_file()
    assert (out / '.github/scripts/build-test.sh').is_file()
    assert 'cmake --preset ci' in (out / '.github/scripts/build-test.sh').read_text()


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


def test_managed_toolchains_profile(tmp_path: Path):
    out = tmp_path / 'foo'
    result, vendor = _invoke(['new', 'foo', '--template', 'cmake', '--ci', 'github', '--toolchains', 'rocky10', str(out)])
    assert result.exit_code == 0, result.output
    vendor.assert_called_once()
    assert 'toolchains: rocky10' in (out / '.besgen.yml').read_text()
    assert (out / 'dev/etc/toolchains.toml').is_file()
    assert (out / 'dev/compilers/spack.yaml').is_file()
    assert not (out / 'dev/compilers/spack.lock').exists()
    assert (out / 'dev/src/foo_dev/toolchains.py').is_file()
    assert (out / 'dev/src/foo_dev/toolchain_commands.py').is_file()
    assert (out / 'dev/tests/test_toolchains.py').is_file()
    assert (out / 'dev/containers/rocky10/Dockerfile').is_file()
    assert (out / '.github/workflows/bootstrap-image.yml').is_file()
    assert 'foo-dev deps --backend native install' in (out / '.github/workflows/test.yml').read_text()
    assert 'packages:' in (out / 'dev/spack.yaml').read_text()
    assert 'compiler sync' in (out / 'dev/README-toolchains.md').read_text()
    assert '__PROJECT__' not in (out / 'dev/src/foo_dev/toolchains.py').read_text()


def test_reject_managed_profile_for_non_cmake(tmp_path: Path):
    out = tmp_path / 'foo'
    result = CliRunner().invoke(main, ['new', 'foo', '--template', 'cargo', '--toolchains', 'rocky10', str(out)])
    assert result.exit_code != 0
    assert 'CMake projects only' in result.output
    assert not out.exists()


def test_dependency_add_updates_bundle_not_spack_roots(tmp_path: Path):
    out = tmp_path / 'foo'
    result, _ = _invoke(['new', 'foo', '--template', 'cmake', str(out)])
    assert result.exit_code == 0, result.output
    cli_path = out / 'dev/src/foo_dev/cli.py'
    spec = importlib.util.spec_from_file_location('foo_dependency_cli', cli_path)
    assert spec and spec.loader
    generated = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generated)
    args = ['dependency', 'add', '--cmake', 'Lyra', '--spack', 'lyra@1:', '--version', '1', '--kind', 'normal']
    for _ in range(2):
        response = CliRunner().invoke(generated.main, args)
        assert response.exit_code == 0, response.output
    bundle = (out / 'dev/share/spack/packages/foo-dev/package.py').read_text()
    assert bundle.count("depends_on('lyra@1:'") == 1
    assert 'lyra@1:' not in (out / 'dev/spack.yaml').read_text()
    external = (out / 'cmake/external.cmake').read_text()
    assert external.count('NAME Lyra') == 1
    assert 'KIND NORMAL' in external
    dev_args = ['dependency','add','--cmake','fmt','--spack','fmt','--kind','dev','--spack-when','+test']
    response = CliRunner().invoke(generated.main, dev_args)
    assert response.exit_code == 0, response.output
    assert "when='+test'" in (out / 'dev/share/spack/packages/foo-dev/package.py').read_text()
    assert 'KIND DEV' in (out / 'cmake/external.cmake').read_text()


def test_non_cmake_dependency_errors_without_mutating_spack(tmp_path: Path):
    out = tmp_path / 'foo'
    result = CliRunner().invoke(main, ['new', 'foo', '--template', 'python', str(out)])
    assert result.exit_code == 0, result.output
    path = out / 'dev/spack.yaml'
    original = path.read_text() if path.exists() else None
    cli_path = out / 'dev/src/foo_dev/cli.py'
    spec = importlib.util.spec_from_file_location('foo_python_cli', cli_path)
    assert spec and spec.loader
    generated = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generated)
    response = CliRunner().invoke(generated.main, ['dependency','add','--python','requests','--spack','py-requests'])
    assert response.exit_code != 0
    assert 'not implemented yet' in response.output
    assert (path.read_text() if path.exists() else None) == original
