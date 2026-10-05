from __future__ import annotations
import argparse, os, shutil, subprocess
from pathlib import Path

def run(*args: str, cwd: Path | None = None) -> None:
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    subprocess.run(args, cwd=cwd, env=env, check=True)

def dev(project: Path, name: str, *args: str) -> None:
    run("uv", "--directory", str(project / "dev"), "run", f"{name}-dev", *args)

def generate(root: Path, name: str, template: str, ci: str = "none") -> Path:
    project = root / name
    run("besgen", "new", name, "--template", template, "--ci", ci, str(project))
    return project

def verify_cmake(project: Path) -> None:
    cmake = (project / "CMakeLists.txt").read_text()
    external = (project / "cmake/external.cmake").read_text()
    features = (project / "cmake/features.cmake").read_text()
    assert "LANGUAGES CXX Fortran" in cmake
    assert 'besa_add_feature("mpi")' in features
    assert 'besa_add_feature("cuda")' in features
    assert "NAME MPI" in external and 'CONDITION "mpi"' in external
    assert "NAME HDF5" in external and 'VERSION "1.14"' in external
    assert (project / "projects/solver/src/cpp").is_dir()
    assert (project / "projects/solver/src/fortran").is_dir()
    assert (project / "showcases/hello/src/cpp").is_dir()
    properdocs = (project / "docs/properdocs.yml").read_text()
    assert "cpdocs:" in properdocs and "reference/api" in properdocs

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=Path("examples"))
    p.add_argument("--clean", action="store_true")
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    # `uv --directory` changes directory before running the generated
    # developer command, so generated project paths must be absolute.
    output = a.output.resolve()

    if a.clean and output.exists(): shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    cmake = generate(output, "cmake-example", "cmake", "github")
    dev(cmake, "cmake-example", "language", "add", "cpp")
    dev(cmake, "cmake-example", "language", "add", "fortran")
    dev(cmake, "cmake-example", "feature", "add", "mpi")
    dev(cmake, "cmake-example", "feature", "add", "cuda")
    dev(cmake, "cmake-example", "dependency", "add", "--cmake", "MPI", "--spack", "mpi", "--condition", "mpi")
    dev(cmake, "cmake-example", "dependency", "add", "--cmake", "HDF5", "--spack", "hdf5@1.14:", "--version", "1.14", "--condition", "mpi")
    dev(cmake, "cmake-example", "project", "add", "solver")
    dev(cmake, "cmake-example", "showcase", "add", "hello")
    python = generate(output, "python-example", "python", "gitlab")
    cargo = generate(output, "cargo-example", "cargo")
    if a.verify:
        verify_cmake(cmake)
        assert (cmake / ".github/workflows/pages.yml").is_file()
        assert (python / ".gitlab-ci.yml").is_file()
        assert not (cargo / ".github").exists()
        assert not (cargo / ".gitlab-ci.yml").exists()
if __name__ == "__main__": main()
