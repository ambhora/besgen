from pathlib import Path
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
    assert "besa_configure_complete()" in cmake
    assert "besa_add_subdirectory(DIRECTORY src/cpp TYPE cpp)" in cmake
    assert "besa_test_add_directory(" in cmake
    assert "NAME tests/unit" in cmake
    assert "TARGET_LIST foo::libfoo" in cmake
    assert "CMAKE_CXX_STANDARD" not in cmake
    assert 'include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/besa/besaConfig.cmake")' in cmake
    assert "find_package(besa" not in cmake

    assert (out / "src/cpp/include/foo/foo.hpp").is_file()
    assert (out / "src/cpp/lib/foo/foo.cpp").is_file()
    assert (out / "tests/unit/foo.t.cpp").is_file()
    assert not (out / "tests/foo.t.cpp").exists()
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
