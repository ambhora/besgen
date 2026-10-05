# besgen

A uv-friendly Python project generator. Its templates are installed as package data
under `<prefix>/share/besgen`.

## Create a repository

The directory is a positional argument, so Click accepts it before or after options:

```console
besgen new foo newdir --template cmake
besgen new foo --template cmake newdir
besgen new foo . --template python
besgen new foo --template cargo ./foo
```

A CMake repository starts as a small, buildable C++ library with a unit test and
install/export rules. Evolve it through its generated developer command:

```console
uv --directory dev run foo-dev language add fortran
uv --directory dev run foo-dev feature add mpi
uv --directory dev run foo-dev project add solver
uv --directory dev run foo-dev showcase add minimal

uv --directory dev run foo-dev dependency add   --cmake MPI   --spack mpi   --condition mpi
```

`projects/` and `showcases/` are constituents of the root distribution, not separate
packages.
