<!--
--------------------------------------------------------------------------------------------------
SPDX-License-Identifier: Apache-2.0
SPDX-FileCopyrightText: 2026 besgen developers
--------------------------------------------------------------------------------------------------
-->
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

A CMake repository starts with a C++ library declared through `besa_add_library`,
source trees attached through `besa_add_directory`, and a separate build-only unit-test
library (`INSTALL NO`). Installation is controlled per library. The CMake template
requires Besa 0.4.7 or newer. Evolve it through its generated developer command:

```console
uv --directory dev run foo-dev language add fortran
uv --directory dev run foo-dev feature add mpi
uv --directory dev run foo-dev project add solver
uv --directory dev run foo-dev showcase add minimal

uv --directory dev run foo-dev dependency add   --cmake MPI   --spack mpi   --condition mpi
```

`projects/` and `showcases/` are constituents of the root distribution, not separate
packages.

The CMake template requires CMake 4.3. Project configuration lives in
`cmake/options.cmake`, with `BUILD_TESTING=OFF` by default. When enabled,
`test/` builds `libtest<project>` independently of `BUILD_SOURCE`; it is never
installed. Besa exports the production library through native CMake and CPS
package descriptions and an installation manifest. The top-level CMake file
adds `src/` when `BUILD_SOURCE` is enabled. Library creation and implementation
directory declarations live together in `src/CMakeLists.txt`, which the generated
developer command updates when you add a language. For C++ module interfaces, create `src/cpp/module/` and
put only compilable module files there. Configure the compiler and language
standard externally through a preset, toolchain file, or command-line options.
